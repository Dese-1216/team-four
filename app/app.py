import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import joblib
import streamlit as st

from cleaning import CANONICAL_CROPS, CANONICAL_REGIONS, MONTH_NUM, MONTH_ORDER
from features import MODEL_FEATURES, season_features_for_one_plot

APP_DIR = os.path.dirname(__file__)
ASSETS = os.path.join(APP_DIR, "assets")
MODELS = os.path.join(APP_DIR, "..", "models")
PROCESSED = os.path.join(APP_DIR, "..", "data", "processed")

st.set_page_config(
    page_title="Ethiopian crop yield predictor",
    page_icon=":material/agriculture:",
    layout="wide",
)

st.title("Ethiopian smallholder crop yield predictor", icon=":material/agriculture:")
st.caption(
    "Enter your plot details below. Weather and price are looked up automatically from "
    "the region, crop, and year you pick -- you never type those in."
)

with st.sidebar:
    st.subheader("About this model", icon=":material/insights:")
    st.caption(
        "Gradient-boosted model trained on 15,090 plots across 5 regions, 5 crops, and "
        "4 seasons (2021-2024)."
    )
    st.metric("Validation R2", "0.887")
    st.metric("Validation RMSE", "0.47 t/ha")
    st.caption("See NOTEBOOK_GUIDE.md for how every number here was produced.")


@st.cache_resource
def load_assets():
    model = joblib.load(os.path.join(MODELS, "final_model.joblib"))
    weather_clean = pd.read_csv(os.path.join(ASSETS, "weather_clean.csv"))
    price_clean = pd.read_csv(os.path.join(ASSETS, "price_clean.csv"))
    master_train = pd.read_csv(os.path.join(PROCESSED, "master_train.csv"))
    return model, weather_clean, price_clean, master_train


try:
    model, weather_clean, price_clean, master_train = load_assets()
except FileNotFoundError as exc:
    st.error(
        f"Required file missing: {exc}. Run notebook 01 then notebook 04 first, so "
        "models/final_model.joblib and app/assets/weather_clean.csv + price_clean.csv exist."
    )
    st.stop()

with st.container(border=True):
    st.subheader("Plot details", icon=":material/edit_note:")

    with st.form("plot_form"):
        col1, col2 = st.columns(2)
        with col1:
            region = st.selectbox("Region", CANONICAL_REGIONS, format_func=str.capitalize)
            crop_type = st.selectbox("Crop", CANONICAL_CROPS, format_func=str.capitalize)
            survey_year = st.number_input("Year", min_value=2021, max_value=2024, value=2024, step=1)
            planting_month = st.selectbox("Planting month", MONTH_ORDER, format_func=str.capitalize)
            altitude_m = st.number_input("Altitude (m)", min_value=0.0, max_value=4500.0, value=1800.0, step=50.0)
            farm_size_ha = st.number_input("Farm size (ha)", min_value=0.01, max_value=100.0, value=1.0, step=0.1)
        with col2:
            fertilizer_kg_per_ha = st.number_input("Fertilizer (kg/ha)", min_value=0.0, max_value=1000.0, value=100.0, step=5.0)
            improved_seed_used = st.checkbox("Improved seed used")
            pest_disease_flag = st.checkbox("Pest/disease observed")
            soil_quality_index = st.slider("Soil quality index", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
            labor_days_per_ha = st.number_input("Labor (days/ha)", min_value=0.0, max_value=200.0, value=40.0, step=1.0)
            distance_to_market_km = st.number_input("Distance to market (km)", min_value=0.0, max_value=300.0, value=15.0, step=1.0)

        submitted = st.form_submit_button("Predict yield", icon=":material/query_stats:")

if submitted:
    try:
        season = season_features_for_one_plot(weather_clean, region, int(survey_year), planting_month)

        row = {
            "region": region,
            "crop_type": crop_type,
            "planting_month": planting_month,
            "altitude_m": altitude_m,
            # the model's rainfall_mm_season feature is normally the farmer's own estimate;
            # the demo must not ask the user to type in a weather number, so it uses the
            # looked-up station season-total as a stand-in instead
            "rainfall_mm_season": season["season_rainfall_mm_total"],
            "farm_size_ha": farm_size_ha,
            "fertilizer_kg_per_ha": fertilizer_kg_per_ha,
            "improved_seed_used": int(improved_seed_used),
            "pest_disease_flag": int(pest_disease_flag),
            "soil_quality_index": soil_quality_index,
            "labor_days_per_ha": labor_days_per_ha,
            "distance_to_market_km": distance_to_market_km,
            "season_avg_temp_c": season["season_avg_temp_c"],
            "season_rainfall_mm_total": season["season_rainfall_mm_total"],
            "season_extreme_heat_days": season["season_extreme_heat_days"],
            "season_months_matched": season["season_months_matched"],
            "temp_deviation_from_region_avg": season["temp_deviation_from_region_avg"],
            "fertilizer_x_improved_seed": fertilizer_kg_per_ha * int(improved_seed_used),
            "planting_month_num": MONTH_NUM[planting_month],
            "survey_year": int(survey_year),
        }
        X_input = pd.DataFrame([row])[MODEL_FEATURES]

        predicted_yield = max(float(model.predict(X_input)[0]), 0.0)

        price_match = price_clean[
            (price_clean["region"] == region)
            & (price_clean["crop_type"] == crop_type)
            & (price_clean["year"] == int(survey_year))
        ]
        if not price_match.empty:
            price = float(price_match["price_birr_per_quintal"].iloc[0])
            price_note = (
                f"{price:.0f} birr/quintal -- exact match for {crop_type.capitalize()} "
                f"in {region.capitalize()}, {int(survey_year)}"
            )
        else:
            crop_prices = price_clean.loc[price_clean["crop_type"] == crop_type, "price_birr_per_quintal"]
            price = float(crop_prices.mean()) if len(crop_prices) else 0.0
            price_note = (
                f"{price:.0f} birr/quintal -- no exact region/year match, using "
                f"{crop_type.capitalize()}'s overall average price"
            )

        revenue = predicted_yield * 10 * price

        st.space("medium")
        with st.container(border=True):
            st.subheader("Prediction", icon=":material/insights:")

            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric("Predicted yield", f"{predicted_yield:.2f} t/ha")
            with metric_col2:
                st.metric("Estimated revenue", f"{revenue:,.0f} birr/ha")

            st.caption("What was looked up for you, automatically:")
            if season["season_months_matched"] > 0:
                st.markdown(
                    f":material/cloud: **Season weather** ({season['season_months_matched']}/4 months "
                    f"matched in {region.capitalize()} starting {planting_month.capitalize()} "
                    f"{int(survey_year)}): avg temp {season['season_avg_temp_c']:.1f} C, "
                    f"total rainfall {season['season_rainfall_mm_total']:.0f} mm "
                    f"(also used as your plot's season rainfall estimate), "
                    f"{season['season_extreme_heat_days']:.0f} extreme-heat days."
                )
            else:
                st.markdown(
                    f":material/cloud_off: **Season weather**: no records matched that exact "
                    f"region/year/month window; fell back to {region.capitalize()}'s overall "
                    f"climate average."
                )
            st.markdown(f":material/payments: **Price**: {price_note}")

            region_crop_avg = master_train.loc[
                (master_train["region"] == region) & (master_train["crop_type"] == crop_type),
                "yield_tons_per_ha",
            ].mean()
            region_crop_avg = 0.0 if np.isnan(region_crop_avg) else region_crop_avg

            fig, ax = plt.subplots(figsize=(5, 3.5))
            ax.bar(
                ["Your plot", f"{region.capitalize()} {crop_type.capitalize()} avg"],
                [predicted_yield, region_crop_avg],
                color=["#2E7D32", "#0277BD"],
            )
            ax.set_ylabel("Yield (tons/ha)")
            ax.set_title("Your prediction vs. historical regional average")
            st.pyplot(fig, alt="Bar chart comparing your predicted yield to the historical regional average")

    except Exception as exc:
        st.error(f"Could not generate a prediction: {exc}", icon=":material/error:")
