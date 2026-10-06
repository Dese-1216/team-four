# Notebook Guide — What Every Cell Is Actually Doing

Plain-language walkthrough of each notebook, cell by cell, in the order they run. Written
so you (or a teammate, or a grader skimming quickly) can understand the point of a cell
without reading the code first.

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

## `app/app.py` (not covered above, per your request — kept here only as a map pointer)

If you want this one explained the same way later, just ask — it wasn't included since
you said to check everything *other than* `app.py`.
