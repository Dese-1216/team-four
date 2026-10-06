# Notebook Guide — What Every Part of This Project Is Actually Doing

Plain-language walkthrough of every notebook (cell by cell, in run order), every function
in `src/cleaning.py` and `src/features.py`, and every section of the demo app
(`app/app.py`). Written so you (or a teammate, or a grader skimming quickly) can
understand what a piece of code is for without reading the code itself first.

---

## Notebook 01 — `01_cleaning_and_integration.ipynb`

**Job of this whole notebook:** take the 3 messy raw CSVs and turn them into two clean,
model-ready tables (`master_train.csv`, `master_test.csv`), while proving every cleaning
decision was reasonable.

1. **Load the raw files** — Reads the 3 original CSVs exactly as downloaded, with zero
   edits. Everything from here on works off these in-memory copies, so the raw files on
   disk are never touched.

2. **A1 — Cataloguing every data problem we found** — Doesn't fix anything yet. Just
   counts and lists every issue in the raw data (inconsistent spelling, sentinel missing
   values, outliers, a price unit mix-up) into one table, with the fix we're about to
   apply and why. This is the "evidence" cell — it proves the cleaning wasn't guesswork.

3. **A2 — Actually cleaning the labels, with before/after proof** — This is where
   cleaning really happens: region and crop names get standardized, two different missing
   -value codes get converted to real NaNs, and the test set gets the exact same
   statistics (medians, caps) that were learned from train — never its own. Prints the
   unique values before and after so you can see the mess disappear.

4. **A3 — Drawing the join map** — A picture (saved to `reports/join_diagram.png`)
   showing which table is on which side of each join, and why. No calculation here, just
   the visual explanation of the plan.

5. **A4 — Checking the join actually worked** — Runs the real join and reports hard
   numbers: what percent of plots got a full 4-month weather match vs. a partial or no
   match, and what percent matched a price row. This is the honesty check — if match
   rates were terrible, this cell would be where you'd find out.

6. **A5 — Showing the join's work for 3 real plots** — Picks 3 specific plots and prints
   exactly which weather rows got pulled in for each one and the resulting season
   averages, so the join logic is auditable by hand, not just trusted as a black box.

7. **A6 — Building the extra features and explaining each one** — Creates the 6
   engineered columns (season temperature, season rainfall, extreme-heat days, a
   temperature-deviation feature, a fertilizer×seed interaction, and a numeric
   planting-month code) and prints a table explaining what each one means and why it
   might help predict yield.

8. **A7 — The integrity checks (pass/fail)** — A list of sanity asserts: no duplicate
   plot IDs, no missing values left in model features, region/crop values all within the
   expected set, row counts unchanged by the joins, etc. If anything here prints `FAIL`,
   stop and fix it before trusting anything downstream.

9. **A8 — Saving everything downstream notebooks need** — Writes `master_train.csv`,
   `master_test.csv`, the data dictionary, the fitted cleaning statistics (so nothing
   downstream has to re-derive them), and copies of the cleaned weather/price tables into
   `app/assets/` for the demo. Nothing after this cell changes any data — it's all reads
   from here on.

---

## Notebook 02 — `02_analysis_report.ipynb`

**Job of this whole notebook:** answer 14 specific analysis questions about the cleaned
data, each with a number/table/chart and a one-sentence takeaway computed directly from
the data (not a number I guessed).

- **Setup** — Loads the master table plus the cleaned weather/price tables.
- **B1.1 / B1.2 — Money questions** — Revenue per hectare by crop, and how crop prices
  moved 2021→2024.
- **B2.1 – B2.5 — Yield questions** — Yield by region, by crop, the region×crop
  combination table, how much improved seed actually helps per crop, and how much pest/
  disease pressure costs per crop.
- **B3.1 – B3.4 — "What drives yield" questions** — Yield vs. fertilizer amount, yield
  vs. altitude (flagging bins with too few plots to trust), yield vs. planting month, and
  whether distance to market correlates with yield at all.
- **B4.1 – B4.3 — Time and data-quality questions** — Yield trend across survey years,
  which region-year combos ran unusually hot, and whether a farmer's own rainfall
  estimate agrees with the station-measured rainfall (a data-trust check, not just an
  analysis one).

Every one of these cells prints its own interpretation sentence computed from whatever
the data actually says — that's deliberate, so the numbers in your report always match
what's really in `master_train.csv`, even if you re-run after a cleaning change.

---

## Notebook 03 — `03_visualizations.ipynb`

**Job of this whole notebook:** produce figures 1–9 (figures 10–12 need the trained
model, so they're made at the end of notebook 04 instead) and auto-write their captions.

- **Setup** — Loads the raw train file (to show "before"), the master table ("after"),
  and the cleaned weather/price tables.
- **Figure 1 — Where the missing data was** — A bar chart of percent-missing per raw
  column, including the `-999` sentinels, before anything got cleaned.
- **Figure 2 — Fertilizer, before vs. after cleaning** — Two histograms side by side
  showing the outlier cap doing its job without distorting the rest of the distribution.
- **Figure 3 — Overall yield distribution** — A plain histogram of the target variable,
  so you know its shape before judging any model's error against it.
- **Figure 4 — Yield heatmap by region and crop** — The single most "where should I
  farm what" figure in the whole project.
- **Figure 5 — Correlation heatmap** — Shows that no single raw feature is strongly
  correlated with yield alone — the justification for using a non-linear model later.
- **Figure 6 — Climate differences by region** — Box plots of temperature and rainfall
  per region, justifying why weather was joined per-region instead of nationally.
- **Figure 7 — Yield vs. season temperature** — A scatter plot of the clearest single
  weather relationship.
- **Figure 8 — Price trends** — Same price-over-time data as B1.2, saved as a standalone
  figure for the figures/ folder requirement.
- **Figure 9 — Revenue by crop and region** — Combines yield and price into one view,
  showing that "highest yield" and "highest revenue" aren't always the same crop.
- **Caption-writing cell** — Reads `figure_captions.md`, fills in the 9 captions this
  notebook owns (computed from the real numbers above, not hand-written guesses), and
  leaves the other 3 lines untouched for notebook 04 to fill in.

---

## Notebook 04 — `04_modeling_and_evaluation.ipynb`

**Job of this whole notebook:** find the best model, prove it's actually good (not just
lucky), explain where it still struggles, and produce the real submission file.

- **Setup** — Loads the master tables, defines which columns are model inputs
  (imported from `src/features.py` so this list can never drift from what the demo app
  uses), and splits off a validation set.
- **D1 — How much does a "dumb" model get wrong?** — A mean-only predictor and plain
  linear regression, to set the floor any real model must beat.
- **D2 — The actual model bake-off** — Trains 4 real candidates and ranks them by
  validation RMSE. Whichever wins here is not decided by me in advance — it's decided by
  this cell, from your data.
- **D3 — Is the winner just lucky?** — Re-checks the top 2 models with 5-fold
  cross-validation. A low standard deviation here means "no, it's a consistently good
  model," not a fluke of one lucky train/validation split.
- **D4 — Does it still work on data from the future?** — Trains only on 2021-2023 and
  tests on 2024, to catch a model that's secretly just memorizing year-specific patterns.
- **D5 — Do the weather features we worked hard to build actually help?** — Re-trains
  the same model with the 4 weather-derived features removed, to put a real number on
  whether that join effort was worth it.
- **D6 — Squeezing more accuracy out of the winner** — A hyperparameter search
  (`RandomizedSearchCV`) tries several settings of the winning model and keeps the best
  one it finds.
- **D6.5 — Does averaging two models beat one?** — Blends the tuned winner with the
  runner-up model 50/50 and only switches to that blend if it genuinely beats the single
  model on validation RMSE. If it doesn't help, the single model stays — the cell tells
  you either way.
- **D7 — Where does the model still get it wrong?** — Breaks down prediction error by
  crop and by region, plots error against altitude, and lists the 10 single worst
  predictions with hypotheses for why.
- **D8 — So what did we do about it?** — A direct, data-driven response to D7: whichever
  gap (crop or region) is largest gets called out by name, with a concrete next-step
  suggestion.
- **D9 — Translating the error into plain language** — Converts RMSE/MAE from "tons per
  hectare" into "percent of a typical yield" and "birr of revenue error per hectare" —
  the number a non-technical judge or farmer would actually understand.
- **Final model, predictions, submission** — Refits the chosen model on 100% of the
  training data (more data = a better final model than the 80% split used for honest
  evaluation), saves it to `models/final_model.joblib`, predicts on the real leaderboard
  test set, and writes `submission/team_qiyas_submission.csv`. This is the cell that
  actually produces your prediction-score deliverable.
- **Figures 10, 11, 12** — Model comparison bar chart, predicted-vs-actual + residual
  plots, and permutation-based feature importance — all needed the trained model to
  exist, which is why they're here and not in notebook 03.
- **Final caption-writing cell** — Fills in the last 3 lines of `figure_captions.md`,
  so after this notebook runs, all 12 figures have real captions.

---

## `src/cleaning.py` — shared cleaning functions

**Job of this file:** every cleaning rule that notebook 01 uses, written once as plain
functions so the exact same logic can be reused and never silently drifts between train
and test.

- **`CANONICAL_REGIONS`, `CANONICAL_CROPS`** — the single list of "correct" spellings
  (`amhara, oromia, snnpr, somali, tigray` and the 5 crop names) that every table gets
  normalized to. If a grader asks "what's the allowed set of labels," this is it.
- **`MONTH_ORDER`, `MONTH_NUM`** — the 12 month abbreviations (`jan`...`dec`) and their
  1-12 numeric position. Used anywhere a month needs to become a number, or a number
  needs to become the next/previous month (season-window math).
- **`_REGION_ABBREV`, `_CROP_FIXES`** — the two small lookup dicts that do the actual
  relabeling: `{"amh": "amhara", "oro": "oromia", ...}` for the weather file's
  abbreviations, and `{"tef": "teff"}` for the one misspelling found in the plot file.
- **`_IMPUTE_GROUP_COL`** — for each column that had missing values, which other column
  to group by when filling them in: fertilizer and labor by `crop_type` (they vary a lot
  by crop), rainfall by `region` (it's a climate effect, not a crop effect), soil quality
  by nothing (just the overall median) since it's plot-specific noise.
- **`_LOW_PRICE_THRESHOLD = 500`** — the cutoff used to spot the birr-per-kg vs.
  birr-per-quintal mix-up: any price below 500 is assumed to be in the wrong unit and
  gets multiplied by 100.
- **`_norm_region(series)` / `_norm_crop(series)`** — tiny helpers that strip whitespace,
  lowercase, and apply the abbreviation/misspelling fix for one column at a time. Every
  other function in this file calls these rather than repeating the logic.
- **`clean_plot_table(df, stats=None)`** — the most important function here. Call it
  once with `stats=None` on the **train** file: it cleans the labels, converts the two
  missing-value sentinels (`-999` and `-999.0`) to real NaNs, computes the fertilizer
  outlier cap and the imputation medians/mode *from this data*, fills everything in, and
  **returns both the cleaned table and those computed stats**. Call it again with
  `stats=<the dict you just got back>` on the **test** file: this time it skips
  recomputing anything and just applies the same train-derived numbers. That's the whole
  mechanism behind "fit on train only" (Rule 6) — one function, two modes, driven by
  whether you pass `stats`.
- **`clean_weather_table(df)`** — cleans region labels, drops the one exact duplicate
  row, averages the 6 region-year-month keys that had two conflicting readings, and
  fills any remaining blank weather cells with that region+month's own across-year
  average. No train/test split here — weather is a shared reference table, not
  per-plot data, so there's nothing to leak.
- **`clean_price_table(df)`** — cleans labels, fixes the unit mix-up, and fills blank
  prices with that crop's median price. Same reasoning as weather: a shared lookup
  table, not something that can leak the target.
- **`save_stats(stats, path)` / `load_stats(path)`** — just read/write the fitted-stats
  dict as JSON, so `cleaning_stats.json` is a plain, inspectable file rather than a
  pickle.

## `src/features.py` — the season-window join and the model's feature contract

**Job of this file:** turn cleaned weather into per-plot season features, and define,
in exactly one place, which columns the model is trained and predicted on — so training
(notebook 04) and the live demo (`app.py`) can never disagree about what a "feature" is.

- **`CATEGORICAL_FEATURES`, `NUMERIC_FEATURES`, `MODEL_FEATURES`, `TARGET_COLUMN`** —
  the feature contract. `MODEL_FEATURES` is just the two lists concatenated; everything
  downstream (the training pipeline, the permutation importance chart, the demo's input
  row) builds its column list from these constants instead of retyping it.
- **`SEASON_LENGTH = 4`** — the growing-season window length: planting month plus the
  3 months after it.
- **`season_window_months(planting_month, year, n=4)`** — given a start month and year,
  returns the list of `(month, year)` pairs the season covers, correctly rolling over
  into the next calendar year if the window crosses December (e.g. planting in November
  gives Nov/Dec of this year, then Jan/Feb of next year). This is the one place that
  wraparound logic lives.
- **`aggregate_season_weather(weather_clean, region, year, planting_month)`** — the
  single source of truth for "what was the weather during this plot's growing season."
  Pulls the matching rows from the cleaned weather table for that region and season
  window, and returns the mean temperature, total rainfall, total extreme-heat days, and
  how many of the 4 months actually had a matching weather row. Both the batch join in
  notebook 01 and the live single-plot lookup in `app.py` call this exact function —
  that's the guarantee that "growing season" means the same thing in both places.
- **`build_region_temp_climatology(weather_clean)`** — each region's average temperature
  across every month and year it has data for. Used as the baseline that
  `temp_deviation_from_region_avg` measures against, and as the fallback value when a
  plot's exact season window has no matching weather rows at all.
- **`build_master_table(plot_clean, weather_clean)`** — runs
  `aggregate_season_weather` for every plot (this is the actual batch join), attaches
  the results as new columns, computes the 2 remaining engineered features
  (`fertilizer_x_improved_seed`, `planting_month_num`), and fills in the rare
  no-weather-match gaps using the region climatology. This is what produces
  `master_train.csv` / `master_test.csv` in notebook 01's A8 step.
- **`season_features_for_one_plot(weather_clean, region, year, planting_month)`** — the
  demo app's version of the same fallback logic, but for a single plot instead of a
  whole table (so it can run instantly when you click "Predict" rather than looping over
  15,000 rows). Deliberately mirrors `build_master_table`'s fallback rule rather than
  sharing code with it, since one works on a DataFrame and the other on a single dict.
- **`attach_price(df, price_clean)`** — joins price onto a *copy* of a table, purely for
  revenue math (notebook 02's analysis, the demo's revenue number). Never called from
  the training notebook's feature-building path, which is what physically prevents price
  from ever becoming a model feature rather than just promising it won't.

## `app/app.py` — the live demo

**Job of this file:** let someone who has never seen the code enter a plot's details and
get back a predicted yield and revenue, with weather and price looked up automatically.

- **Setup and imports** — adds `src/` to the Python path so it can import the same
  `cleaning.py` / `features.py` the notebooks use, then loads matplotlib, pandas,
  joblib, and streamlit.
- **`st.set_page_config(...)`** — sets the browser tab title/icon and switches to
  `layout="wide"` for a dashboard feel. Paired with `app/.streamlit/config.toml`, which
  holds the actual color theme (white background, green/blue farming palette, Inter
  font) — kept in `config.toml` rather than custom CSS so it survives Streamlit upgrades.
- **Sidebar "About this model"** — a small always-visible panel showing the real
  validation R² and RMSE, so anyone opening the app immediately sees how trustworthy the
  model is without digging through notebooks.
- **`load_assets()`** — loads the trained model (`final_model.joblib`), the cleaned
  weather/price tables, and `master_train.csv`, all wrapped in `@st.cache_resource` so
  they're read from disk once per server session, not on every click. Wrapped in a
  `try/except FileNotFoundError` that shows a friendly message and stops instead of
  crashing if notebooks 01/04 haven't been run yet.
- **The "Plot details" form** — every input the rubric requires (region, crop, year,
  planting month, altitude, farm size, fertilizer, improved seed, pest/disease, soil
  quality, labor, distance to market), and nothing that counts as a weather number or a
  price — those are looked up, never typed. Number inputs use `min_value`/`max_value` so
  most nonsensical values are physically impossible to enter in the first place.
- **On submit — building the model's input row** — calls
  `season_features_for_one_plot` to get the looked-up season weather, then assembles a
  single-row table with exactly the columns in `MODEL_FEATURES` (imported from
  `features.py`, not retyped) and hands it to `model.predict(...)`.
- **Price lookup** — looks for an exact region+crop+year match in the cleaned price
  table; if there isn't one (e.g. a year outside 2021-2024), falls back to that crop's
  overall average price and says so explicitly, rather than silently guessing.
- **The output card** — two `st.metric` tiles (predicted yield, estimated revenue), a
  plain-language line stating exactly which weather and price numbers were looked up and
  for what region/year/month, and a bar chart comparing the prediction against the
  historical average for that same region+crop.
- **The outer `try/except`** — wraps the entire prediction step, so any unexpected error
  (a bad lookup, a missing file) shows a friendly `st.error` instead of crashing the app
  — the "handle nonsensical input without crashing" requirement.

---

## Other project docs worth knowing about

- **`reports/stretch_regional_equity.md`** — the stretch-goal writeup. Shows that
  Tigray has the worst *absolute* prediction error, but Somali has the worst *relative*
  error once you account for its much lower typical yield — and proposes a concrete
  fix (region-calibrated error bands) rather than just flagging the finding.
- **`presentation/team_qiyas_slides.pptx` / `.pdf`** — the 5-slide deck, filled with the
  real numbers from your own notebook run, not placeholders.
- **`app/.streamlit/config.toml`** — the demo's visual theme. Edit colors here, not with
  CSS, if you want to adjust the look further.
