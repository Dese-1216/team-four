# Stretch Goal: Regional Equity Analysis

## Does the model perform worse in any region?

The honest answer depends on how you ask the question.

| Region | Mean absolute error (tons/ha) | Regional mean yield (tons/ha) | Error as % of regional mean |
|---|---|---|---|
| Tigray | 0.400 | 3.131 | 12.79% |
| Amhara | 0.397 | 3.129 | 12.68% |
| Oromia | 0.386 | 3.073 | 12.57% |
| SNNPR | 0.346 | 3.041 | **11.38% (best)** |
| Somali | 0.196 | 1.464 | **13.38% (worst)** |

**Ranked by absolute error (worst first): Tigray, Amhara, Oromia, SNNPR, Somali.**
**Ranked by relative error (worst first): Somali, Tigray, Amhara, Oromia, SNNPR.**

Deliverable D's error analysis (D7/D8) reported Tigray as the region with the highest
error and flagged it as the one needing attention. That is true in absolute tons/ha —
but it is misleading on its own. Somali's plots have a fundamentally different, lower
yield scale (mean 1.46 tons/ha, versus roughly 3.0-3.1 tons/ha in every other region) and
less plot-to-plot spread (std 0.77 vs. 1.2-1.5 elsewhere). Once error is expressed as a
percentage of each region's own typical yield — the number that actually matters for a
"how much should I trust this prediction" decision — **Somali is the worst-served
region, not the best-served one.** Tigray's absolute-error problem is real but smaller in
relative terms than it first appeared.

## Ruling out the obvious explanations

Before concluding this is a real regional effect rather than a data artifact, three
alternative explanations were checked directly against `master_train.csv`:

- **Sample size imbalance**: regions have 2,969-3,090 plots each — essentially balanced.
  Not the cause.
- **Altitude variability**: each region's altitude standard deviation is 666-686m —
  nearly identical. Not the cause.
- **Crop mix imbalance**: each region has 550-650 plots per crop, no region is
  dominated by one crop. Not the cause.
- **Join completeness**: average `season_months_matched` is 3.66-3.91 across regions
  (out of a possible 4) — Somali (3.66) and Tigray (3.66) are both slightly below the
  regional average, a minor plausible contributor to both regions' error, but far too
  small a gap to explain a result this size on its own.

The remaining, most plausible explanation: Somali's agro-climatic zone produces
inherently lower and more drought-constrained yields, where the plot-level features in
this dataset (fertilizer, seed, labor, soil quality) carry proportionally less
predictive signal relative to the baseline yield level than they do in the ~3 ton/ha
regions. That is a property of the region's agronomy, not a bug in the pipeline.

## Would this underserve Somali if used for real fertilizer allocation?

Yes, plausibly — and in a way that is easy to miss. A point prediction of, say, 1.5
tons/ha for a Somali plot looks precise (small absolute error historically), so a
decision-maker might treat it with the same confidence as a 3.1 tons/ha prediction for a
Tigray plot. But proportionally, the Somali prediction carries *more* relative
uncertainty (13.4% vs. 11.4-12.8%). If fertilizer or input budgets are allocated in
proportion to predicted yield without adjusting for that relative uncertainty, Somali
farmers are the ones most likely to receive an allocation sized to a prediction that is,
relatively speaking, the least reliable one in the dataset — on top of already having
the lowest predicted yields and likely the tightest margins to begin with. That is a
real equity risk, not just a modeling footnote.

## Mitigation

Report every prediction with a **region-calibrated relative-error band**, not a bare
point estimate: alongside "predicted yield: 1.5 tons/ha," show "typical error for this
region: ±13%" (Somali) vs. "±11%" (SNNPR), computed once from this same error table and
looked up per region exactly like weather and price already are in `app/app.py`. A
decision-maker allocating fertilizer could then apply a wider safety margin specifically
in Somali rather than trusting the point estimate equally everywhere, and flag the
widest-band predictions for manual agronomist review before input decisions are
finalized. This requires no new model, no new features, and no retraining -- only
surfacing a number this analysis already computed.

See `reports/stretch_regional_equity.png` for the side-by-side absolute vs. relative
error chart.
