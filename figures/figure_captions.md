# Figure Captions

One or two sentences per figure: what it shows, and the takeaway ("so what").

- **fig01_missingness.png:** Shows percent missing (including -999 sentinels) across all three raw tables; fertilizer_kg_per_ha, soil_quality_index, labor_days_per_ha are the most affected columns in the plot file, which is why they get train-fit median/mode imputation in deliverable A.
- **fig02_before_after_cleaning.png:** Compares fertilizer_kg_per_ha and price_birr_per_quintal before and after cleaning; capping fertilizer at the train 99th percentile and multiplying the mispriced rows by 100 both fix the problem without distorting the rest of each distribution.
- **fig03_yield_distribution.png:** Yield is right-skewed overall (mean 2.76 tons/ha); the by-crop panel shows that skew is not uniform -- some crops have a wider spread than others.
- **fig04_region_crop_heatmap.png:** Mean yield varies more by crop than by region; the darkest cell marks the single best-performing region-crop combination, and the (n=...) labels show which cells have enough plots to trust.
- **fig05_correlation_heatmap.png:** No single feature correlates strongly with yield on its own, which is the motivation for using a non-linear model rather than plain linear regression in D.
- **fig06_climate_by_region.png:** Temperature follows a clear seasonal curve that differs by region; the shaded band shows one example growing-season window, illustrating why the join aggregates weather per region and per season rather than using a single national number.
- **fig07_yield_vs_season_temp.png:** Each crop's binned-mean trend line shows its own relationship with season temperature -- some crops have a visible sweet spot, others are closer to flat across the observed range.
- **fig08_price_trends.png:** Crop prices generally trended upward from 2021 to 2024, with teff consistently the most expensive crop per quintal.
- **fig09_revenue_by_crop_region.png:** Revenue per hectare reflects both yield and price, so the highest-yield crop is not always the highest-revenue crop once price is factored in.
- **fig10_model_comparison.png:** hist_gradient_boosting has the lowest validation RMSE among the compared families; see D2 in notebook 04 for the full comparison table.
- **fig11_predicted_vs_actual_residuals.png:** Points cluster around the diagonal in the predicted-vs-actual panel; the residual panel shows whether errors grow at high or low predicted yield.
- **fig12_feature_importance.png:** crop_type contributes the most to predictive accuracy by permutation importance, meaning shuffling it hurts the model's R2 the most.
