# AGNI PARIKSHA - QA Disposition Card
**Component ID**: `FINAL_LOT_0052_0005`
**Family**: `MEMS_GYROSCOPE`

## 1. Verdict & Risk Tier
**Verdict**: RED
**Risk Tier**: HIGH

## 2. Quantitative Forecast
- **Measured at 24h**: 0.45
- **Predicted 168h**: 0.47 dps vs Spec Max 0.5 dps ? forecast is near limit
- **Conformal Interval (90%)**: +/- 0.08
- **Safety Slope Margin**: -0.0016 (allowed - measured max slope)

## 3. Explanability & Physics Trace
Base model prediction before features: 0.22

**Top Contributing Factors:**
- **val_24h** (Impact: +0.27): The parameter level at 24h is increasing the forecast.
- **slope_24h** (Impact: -0.03): The measured 0-24h drift rate is slightly decreasing the forecast.
- **val_0h** (Impact: +0.00): The baseline level at 0h is slightly increasing the forecast.

## Suspected Mechanism (Family Physics Prior)
consistent with mechanical relaxation (viscoelastic creep)

*Disclaimer: Mechanism hypotheses are family-prior heuristics, not causal identifications.*

## Recommended Disposition
**REJECT**. Drift exceeds safety bounds and conformal coverage cannot guarantee spec compliance.