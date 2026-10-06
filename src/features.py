"""Season-window weather aggregation, master-table joins, and engineered features.

aggregate_season_weather is the single source of truth for "growing season" --
it is called both by the batch join in notebook 01 and by the live demo
(app/app.py) for a single plot, so the two never drift apart.
"""
import numpy as np
import pandas as pd

from cleaning import MONTH_ORDER, MONTH_NUM

SEASON_LENGTH = 4  # planting month + 3 following months

# Single source of truth for the model's feature contract -- notebook 04 (training)
# and app/app.py (the live demo) both import this, so they can never drift apart.
CATEGORICAL_FEATURES = ["region", "crop_type", "planting_month"]
NUMERIC_FEATURES = [
    "altitude_m", "rainfall_mm_season", "farm_size_ha", "fertilizer_kg_per_ha",
    "improved_seed_used", "pest_disease_flag", "soil_quality_index", "labor_days_per_ha",
    "distance_to_market_km", "season_avg_temp_c", "season_rainfall_mm_total",
    "season_extreme_heat_days", "season_months_matched", "temp_deviation_from_region_avg",
    "fertilizer_x_improved_seed", "planting_month_num", "survey_year",
]
MODEL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES
TARGET_COLUMN = "yield_tons_per_ha"


def season_window_months(planting_month, year, n=SEASON_LENGTH):
    """[(month_name, year), ...] for planting_month..+n-1, with year wraparound."""
    start = MONTH_NUM[planting_month]
    window = []
    for offset in range(n):
        m = start + offset
        y = int(year)
        if m > 12:
            m -= 12
            y += 1
        window.append((MONTH_ORDER[m - 1], y))
    return window


def aggregate_season_weather(weather_clean, region, year, planting_month):
    window = season_window_months(planting_month, year)
    mask = pd.Series(False, index=weather_clean.index)
    for month, yr in window:
        mask |= (
            (weather_clean["region"] == region)
            & (weather_clean["year"] == yr)
            & (weather_clean["month"] == month)
        )
    rows = weather_clean.loc[mask]
    if rows.empty:
        return {
            "season_avg_temp_c": np.nan,
            "season_rainfall_mm_total": np.nan,
            "season_extreme_heat_days": np.nan,
            "season_months_matched": 0,
        }
    return {
        "season_avg_temp_c": float(rows["avg_temp_c"].mean()),
        "season_rainfall_mm_total": float(rows["monthly_rainfall_mm"].sum()),
        "season_extreme_heat_days": float(rows["extreme_heat_days"].sum()),
        "season_months_matched": int(len(rows)),
    }


def build_region_temp_climatology(weather_clean):
    return weather_clean.groupby("region")["avg_temp_c"].mean().to_dict()


def build_master_table(plot_clean, weather_clean):
    region_clim = build_region_temp_climatology(weather_clean)

    season_records = [
        aggregate_season_weather(weather_clean, row["region"], row["survey_year"], row["planting_month"])
        for _, row in plot_clean.iterrows()
    ]
    season_df = pd.DataFrame(season_records, index=plot_clean.index)

    df = pd.concat([plot_clean, season_df], axis=1)
    df["temp_deviation_from_region_avg"] = df["season_avg_temp_c"] - df["region"].map(region_clim)
    df["fertilizer_x_improved_seed"] = df["fertilizer_kg_per_ha"] * df["improved_seed_used"]
    df["planting_month_num"] = df["planting_month"].map(MONTH_NUM)

    # weather join leaves season features NaN only when a plot's window hit no
    # matching weather rows; fall back to that region's overall climatology
    # (documented in the notebook's A4 join audit).
    df["season_avg_temp_c"] = df["season_avg_temp_c"].fillna(df["region"].map(region_clim))
    region_rain = weather_clean.groupby("region")["monthly_rainfall_mm"].mean() * SEASON_LENGTH
    df["season_rainfall_mm_total"] = df["season_rainfall_mm_total"].fillna(df["region"].map(region_rain))
    df["season_extreme_heat_days"] = df["season_extreme_heat_days"].fillna(0)
    df["temp_deviation_from_region_avg"] = df["temp_deviation_from_region_avg"].fillna(0)

    return df


def season_features_for_one_plot(weather_clean, region, year, planting_month):
    """Single-plot version of build_master_table's weather join + fallback, for the
    live demo. Mirrors the same climatology fallback rule (region's overall mean
    temp/rainfall when the season window has no matching weather rows)."""
    agg = aggregate_season_weather(weather_clean, region, year, planting_month)
    region_clim = build_region_temp_climatology(weather_clean)
    region_rain_clim = (weather_clean.groupby("region")["monthly_rainfall_mm"].mean() * SEASON_LENGTH).to_dict()

    if np.isnan(agg["season_avg_temp_c"]):
        agg["season_avg_temp_c"] = region_clim.get(region, 0.0)
    if np.isnan(agg["season_rainfall_mm_total"]):
        agg["season_rainfall_mm_total"] = region_rain_clim.get(region, 0.0)
    if np.isnan(agg["season_extreme_heat_days"]):
        agg["season_extreme_heat_days"] = 0.0

    agg["temp_deviation_from_region_avg"] = agg["season_avg_temp_c"] - region_clim.get(region, agg["season_avg_temp_c"])
    return agg


def attach_price(df, price_clean):
    """Join price onto a copy of df for revenue analysis/demo -- never feed into the model."""
    out = df.merge(
        price_clean[["region", "crop_type", "year", "price_birr_per_quintal"]],
        left_on=["region", "crop_type", "survey_year"],
        right_on=["region", "crop_type", "year"],
        how="left",
    ).drop(columns=["year"])
    if "yield_tons_per_ha" in out.columns:
        out["revenue_birr_per_ha"] = out["yield_tons_per_ha"] * 10 * out["price_birr_per_quintal"]
    return out
