# Slide Outline (Deliverable F) — 5 slides, 5 min + 2 min Q&A

Fill in the bracketed numbers after running notebooks 01 and 04; everything else is
ready to present as-is. Build the actual deck (`team_qiyas_slides.pdf` or `.pptx`) from
this once the numbers are in, and keep the demo running in a browser tab for the live
portion.

## Slide 1 — Problem & Data

- Predicting smallholder crop yield (tons/ha) in Ethiopia from plot, weather, and price
  data, to help with input planning (fertilizer, seed) and revenue estimates.
- 3 raw sources: `crop_yield_train.csv` (15,090 plots, 2021-2024), `regional_weather.csv`
  (5 regions x 4 years x 12 months), `market_prices.csv` (5 crops x 5 regions x 4 years).
- Each source had its own data-quality problems — covered next.

## Slide 2 — Cleaning & Integration

- Real issues found and fixed: inconsistent region labels (4+ casing variants, plus
  abbreviations like `AMH`/`SOM` only in the weather file), a `Tef`/`teff` spelling
  mismatch, two different missing-value sentinels (`-999` and `-999.0`), and a
  birr-per-kg vs birr-per-quintal unit mix-up in a handful of price rows.
- Show the join map (`reports/join_diagram.png`): plot table is LEFT in both joins;
  weather aggregates many rows down to one season-level row per plot via a 4-month
  growing-season window (planting month + 3 following months, with year wraparound).
- Join audit numbers (from notebook 01, cell A4): **[fill in: weather full-window match
  %, price match %]**.

## Slide 3 — Key Findings

Pick the 2 most interesting results from notebook 02/03 once run, e.g.:
- **[fill in: which crop/region has the highest yield and by how much — B2.1/B2.2]**
- **[fill in: improved-seed lift or pest/disease gap — B2.4/B2.5]**

Show `figures/fig04_region_crop_heatmap.png` and one more figure from `figures/`.

## Slide 4 — Modeling

- Compared 4 model families (linear regression baseline, random forest, gradient
  boosting, histogram gradient boosting) — see `figures/fig10_model_comparison.png`.
- Final model: **[fill in: best_name from notebook 04, D2]**, validation RMSE
  **[fill in]** tons/ha, 5-fold CV RMSE **[fill in: mean ± std, D3]**.
- Weather ablation (D5): including weather features changed RMSE by **[fill in]**.
- Out-of-time check (D4): validating on 2024 after training on 2021-2023 gave RMSE
  **[fill in]**, versus **[fill in]** for a random split.

## Slide 5 — Error Analysis, Score, Demo, Next Steps

- Worst-predicted plots and the hypothesis for why (D7/D8): **[fill in one sentence]**.
- Final plain-language score (D9): RMSE is **[fill in]** percent of mean yield, or about
  **[fill in]** birr/ha of average prediction error.
- **Live demo**: `streamlit run app/app.py` — enter a plot, get a prediction + revenue
  with weather/price looked up automatically.
- Next steps if given more time: the stretch goal we would pick is **[fill in — see
  PROJECT_PLAN.md's stretch goal list]**.
