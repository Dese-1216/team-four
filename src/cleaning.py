"""Cleaning functions for the three raw Qiyas crop-yield tables.

clean_plot_table fits imputation/cap stats on train (stats=None) and applies
the same fitted stats to test (stats=<dict from the train call>), per the
train-only-fitting rule. clean_weather_table and clean_price_table clean a
single shared reference table (not split by train/test), since neither
carries the target and so fitting on their full contents isn't leakage.
"""
import json

import numpy as np
import pandas as pd

CANONICAL_REGIONS = ["amhara", "oromia", "snnpr", "somali", "tigray"]
CANONICAL_CROPS = ["barley", "maize", "sorghum", "teff", "wheat"]

MONTH_ORDER = ["jan", "feb", "mar", "apr", "may", "jun",
               "jul", "aug", "sep", "oct", "nov", "dec"]
MONTH_NUM = {m: i + 1 for i, m in enumerate(MONTH_ORDER)}

_REGION_ABBREV = {"amh": "amhara", "oro": "oromia", "snnp": "snnpr",
                   "som": "somali", "tig": "tigray"}
_CROP_FIXES = {"tef": "teff"}

# fertilizer/labor vary by crop; rainfall is regional; soil quality is plot-specific
_IMPUTE_GROUP_COL = {
    "fertilizer_kg_per_ha": "crop_type",
    "labor_days_per_ha": "crop_type",
    "rainfall_mm_season": "region",
    "soil_quality_index": None,
}
_LOW_PRICE_THRESHOLD = 500  # birr/quintal; real prices observed are all > 2000


def _norm_region(series):
    s = series.astype(str).str.strip().str.lower()
    return s.replace(_REGION_ABBREV)


def _norm_crop(series):
    s = series.astype(str).str.strip().str.lower()
    return s.replace(_CROP_FIXES)


def clean_plot_table(df, stats=None):
    df = df.copy()

    df["region"] = _norm_region(df["region"])
    df["crop_type"] = _norm_crop(df["crop_type"])
    df["planting_month"] = df["planting_month"].astype(str).str.strip().str.lower()

    numeric_cols = ["altitude_m", "rainfall_mm_season", "farm_size_ha",
                     "fertilizer_kg_per_ha", "improved_seed_used", "pest_disease_flag",
                     "soil_quality_index", "labor_days_per_ha", "distance_to_market_km"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # sentinel encodings: -999 (pest_disease_flag) and -999.0 (labor_days_per_ha) -> NaN
    df.loc[df["pest_disease_flag"] == -999, "pest_disease_flag"] = np.nan
    df.loc[df["labor_days_per_ha"] == -999, "labor_days_per_ha"] = np.nan

    fitting = stats is None
    if fitting:
        stats = {
            "fertilizer_cap": float(df["fertilizer_kg_per_ha"].quantile(0.99)),
            "pest_disease_mode": float(df["pest_disease_flag"].mode(dropna=True).iloc[0]),
            "global_medians": {},
            "group_medians": {},
        }
        for col, group_col in _IMPUTE_GROUP_COL.items():
            stats["global_medians"][col] = float(df[col].median())
            if group_col is not None:
                stats["group_medians"][col] = (
                    df.groupby(group_col)[col].median().to_dict()
                )

    df["fertilizer_kg_per_ha"] = df["fertilizer_kg_per_ha"].clip(upper=stats["fertilizer_cap"])
    df["pest_disease_flag"] = df["pest_disease_flag"].fillna(stats["pest_disease_mode"])

    for col, group_col in _IMPUTE_GROUP_COL.items():
        if group_col is not None:
            by_group = df[group_col].map(stats["group_medians"][col])
            df[col] = df[col].fillna(by_group)
        df[col] = df[col].fillna(stats["global_medians"][col])

    return (df, stats) if fitting else df


def clean_weather_table(df):
    df = df.copy()
    df["region"] = _norm_region(df["region"])
    df["month"] = df["month"].astype(str).str.strip().str.lower()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("int64")
    for col in ["avg_temp_c", "monthly_rainfall_mm", "extreme_heat_days"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.drop_duplicates()

    # collapse conflicting duplicate (region, year, month) readings by averaging
    df = df.groupby(["region", "year", "month"], as_index=False).agg({
        "avg_temp_c": "mean",
        "monthly_rainfall_mm": "mean",
        "extreme_heat_days": "mean",
    })

    # fill remaining blanks with that region+month's across-year climatology
    clim = df.groupby(["region", "month"])[["avg_temp_c", "monthly_rainfall_mm"]].transform("mean")
    df["avg_temp_c"] = df["avg_temp_c"].fillna(clim["avg_temp_c"])
    df["monthly_rainfall_mm"] = df["monthly_rainfall_mm"].fillna(clim["monthly_rainfall_mm"])
    df["extreme_heat_days"] = df["extreme_heat_days"].fillna(0)

    return df


def clean_price_table(df):
    df = df.copy()
    df["region"] = _norm_region(df["region"])
    df["crop_type"] = _norm_crop(df["crop_type"])
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("int64")
    df["price_birr_per_quintal"] = pd.to_numeric(df["price_birr_per_quintal"], errors="coerce")

    df = df.drop_duplicates()

    # unit mix-up: a handful of rows recorded birr/kg instead of birr/quintal (~100x too small)
    mixup = df["price_birr_per_quintal"] < _LOW_PRICE_THRESHOLD
    df.loc[mixup, "price_birr_per_quintal"] = df.loc[mixup, "price_birr_per_quintal"] * 100

    df["price_birr_per_quintal"] = df["price_birr_per_quintal"].fillna(
        df.groupby("crop_type")["price_birr_per_quintal"].transform("median")
    )

    return df


def save_stats(stats, path):
    with open(path, "w") as f:
        json.dump(stats, f, indent=2)


def load_stats(path):
    with open(path) as f:
        return json.load(f)
