# 🌾 Ethiopian smallholder crop-yield predictor

**Team Farm · Qiyas AI Hackathon 2026**

Predicts smallholder crop yield (tons/ha) across 5 Ethiopian regions and 5 crops from
plot survey data, regional weather, and market prices — then turns that prediction into
an estimated revenue, through a live demo that looks up weather and price automatically.

[Key results](#-key-results) ·
[Project structure](#-project-structure) ·
[Setup](#-setup-anaconda--jupyter) ·
[Run order](#-run-order) ·
[Testing checkpoints](#-testing-checkpoints-one-per-build-phase) ·
[Where everything lives](#-where-each-deliverable-lives) ·
[Docs](#-documentation)

---

## Team

- **Team Farm**
- *(add member names here before submitting)*

## Summary

Notebook 01 cleans and joins three raw sources — a 15,090-plot survey, regional
monthly weather, and 4-year crop prices — fixing inconsistent region/crop labels, two
different missing-value sentinels, and a price unit mix-up along the way, then builds a
4-month growing-season weather window per plot. Notebooks 02-03 analyze the cleaned data
across 14 numbered tasks and produce 12 figures. Notebook 04 compares 4 model families,
tunes and blends the best one, runs a full error/equity analysis, and fills in the
leaderboard submission. `app/app.py` is a themed Streamlit demo that predicts yield and
revenue for a single plot in real time.

## 🏆 Key results

- **Best model:** `hist_gradient_boosting`, tuned — **RMSE 0.474 t/ha, R² 0.887** on a
  held-out validation split, confirmed stable by 5-fold cross-validation (std 0.012).
- **Weather is worth it:** removing the 4 weather-derived features costs +0.040 RMSE
  (~8% relative) — the growing-season join measurably improves predictions.
- **Plain-language score (D9):** error is roughly **12-17% of a typical plot's yield**,
  or about **15,900 birr/ha** of average prediction error at today's average price.
- **Regional equity finding (stretch goal):** Tigray has the worst *absolute* error, but
  once error is measured relative to each region's own yield scale, **Somali is actually
  the worst-served region** (13.4% vs. 11.4-12.8% elsewhere) — see
  [`reports/stretch_regional_equity.md`](reports/stretch_regional_equity.md).

## 📁 Project structure

```
team_farm/
├── app/                 Streamlit demo (app.py + cleaned-data assets + theme)
├── data/
│   ├── raw/              the 5 original CSVs, never edited
│   └── processed/        master_train.csv, master_test.csv, data_dictionary_master.csv
├── figures/              the 12 required PNGs + figure_captions.md
├── models/               final_model.joblib
├── notebooks/            01_cleaning → 02_analysis → 03_visualizations → 04_modeling
├── presentation/         team_farm_slides.pptx / .pdf
├── reports/              exported A/B/D reports + the regional-equity stretch memo
├── src/                  cleaning.py, features.py — shared by the notebooks and the app
├── submission/           team_farm_submission.csv  (the graded prediction file)
├── NOTEBOOK_GUIDE/Documenation.md   plain-language explanation of every notebook cell, function, and app section
├── PROJECT_PLAN.md       the build plan this project followed
└── requirements.txt
```

## 🔧 Setup (Anaconda / Jupyter)

```bash
conda create -n farm-hackathon python=3.10 -y
conda activate farm-hackathon
pip install -r requirements.txt
```

Launch notebooks with JupyterLab (via Anaconda Navigator, or from this environment):

```bash
jupyter lab
```

## ▶️ Run order

Open and run each notebook top to bottom, in this order, from JupyterLab:

1. `notebooks/01_cleaning_and_integration.ipynb`
2. `notebooks/02_analysis_report.ipynb`
3. `notebooks/03_visualizations.ipynb`
4. `notebooks/04_modeling_and_evaluation.ipynb`
5. `streamlit run app/app.py` (demo — run from an Anaconda Prompt / terminal with the
   `farm-hackathon` environment active, not from inside Jupyter)

## ✅ Testing checkpoints (one per build phase)

Run these in order; each should pass before moving to the next.

1. **Phase 1 — `01_cleaning_and_integration.ipynb`**: run top to bottom. Check: no
   exceptions, the A7 integrity-checks cell prints all `[PASS]`, and
   `data/processed/master_train.csv`, `master_test.csv`, `data_dictionary_master.csv`,
   `cleaning_stats.json` exist, plus `app/assets/weather_clean.csv` and `price_clean.csv`.
2. **Phase 2 — `02_analysis_report.ipynb` then `03_visualizations.ipynb`**: run top to
   bottom. Check: `figures/` has 9 PNGs (`fig01_...png` through
   `fig09_revenue_by_crop_region.png`) and `figures/figure_captions.md` has those 9 entries
   filled in. Figures 10-12 (model comparison, residuals, feature importance) are generated
   by notebook 04 instead, since they need the trained model.
3. **Phase 3 — `04_modeling_and_evaluation.ipynb`**: run top to bottom. Check:
   `models/final_model.joblib` exists, `submission/team_farm_submission.csv` has all
   3,750 rows filled with numeric predictions, `figures/` now has all 12 PNGs, and
   `figures/figure_captions.md` has all 12 entries filled in.
4. **Phase 4 — demo**: `streamlit run app/app.py`, enter a plot's details, confirm you get
   a predicted yield and a revenue estimate with no crash.

## 📤 Exporting the written reports (A, B, D)

Each report deliverable is just the matching notebook exported, run after that notebook
executes cleanly:

```bash
jupyter nbconvert --to html notebooks/01_cleaning_and_integration.ipynb --output-dir reports --output A_cleaning_and_integration
jupyter nbconvert --to html notebooks/02_analysis_report.ipynb --output-dir reports --output B_analysis_report
jupyter nbconvert --to html notebooks/04_modeling_and_evaluation.ipynb --output-dir reports --output D_model_evaluation
```

## 🗂️ Where each deliverable lives

| Deliverable | Location |
|---|---|
| Prediction score | `submission/team_farm_submission.csv` |
| A — Pipeline | `notebooks/01_...`, `reports/A_...`, `data/processed/` |
| B — Analysis | `reports/B_analysis_report.*`, `notebooks/02_...` |
| C — Visualizations | `figures/`, `notebooks/03_...` |
| D — Modeling | `reports/D_...`, `notebooks/04_...`, `models/` |
| E — Demo | `app/`, URL below |
| F — Slides | `presentation/team_farm_slides.pptx` + `.pdf` |
| G — Structure | project root |
| Stretch (regional equity) | `reports/stretch_regional_equity.md` + `.png` |

## 📚 Documentation

- **[`NOTEBOOK_GUIDE/Documenation.md`](NOTEBOOK_GUIDE/Documenation.md)** — a plain-language walkthrough of *every*
  notebook cell, every function in `src/cleaning.py` and `src/features.py`, and every
  section of `app/app.py`. Start here if you need to understand or present any part of
  this project without reading code first.
- **[`PROJECT_PLAN.md`](PROJECT_PLAN.md)** — the phase-by-phase plan this project was
  built against.
- **[`reports/stretch_regional_equity.md`](reports/stretch_regional_equity.md)** — the
  stretch-goal writeup (see [Key results](#-key-results) above).
- **`presentation/team_farm_slides.pptx`** (and matching `.pdf`) — the 5-slide deck,
  filled with this project's real numbers, ready to present as-is.

## 🎯 Final validation score

Best model (`hist_gradient_boosting`, tuned): **RMSE 0.474 t/ha, MAE 0.344 t/ha, R²
0.887** on held-out validation, 5-fold CV mean RMSE 0.480 (std 0.012). In plain language
(D9): roughly **12-17% of mean yield**, or **~15,900 birr/ha** of average prediction
error. *(These are approximate for the birr figure and the percent-of-mean-yield figure,
computed from the full training mean as a stand-in for the exact validation-split mean —
swap in the exact numbers notebook 04's D9 cell prints once it runs end to end on your
machine.)*

## 🔗 Demo link

**Live demo (recommended): https://team-four-main-dtesvxj7tpxpwtflecschh.streamlit.app/**
— no manual rainfall input; weather (including rainfall) is looked up automatically from
region/year/month, matching deliverable E's rule that no weather number is ever typed in
by hand.

Also deployed: https://jshtrhmerdng7xvxlv4fhj.streamlit.app/ — an earlier version with a
manual rainfall input field. Kept here for reference, but the first link above is the one
that satisfies E's "no weather numbers typed in" requirement and should be the one used
for grading/demo.

Run locally instead: `streamlit run app/app.py`.
