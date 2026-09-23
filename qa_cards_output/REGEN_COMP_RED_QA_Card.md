# AGNI PARIKSHA - QA Disposition Card
**Component ID**: `REGEN_COMP_RED`
**Family**: `DIGITAL_IC`

## 1. Verdict & Risk Tier
**Verdict**: RED_SAFETY_SLOPE
**Risk Tier**: RED_SAFETY_SLOPE

## 2. Quantitative Forecast
- **Measured at 24h**: 20.50
- **Predicted 168h**: 38.91
- **Conformal Interval (90%)**: +/- 20.54
- **Safety Slope Margin**: -0.0995 (allowed - measured max slope)

## 3. Explanability & Physics Trace
Base model prediction before features: 44.13

**Top Contributing Factors:**
- **val_0h** (Impact: -2.44): Baseline parameter val_0h is decreasing the outcome.
- **val_24h** (Impact: -2.40): Baseline parameter val_24h is decreasing the outcome.
- **slope_24h** (Impact: -0.37): The measured 0-24h drift rate is strongly decreasing the forecast.

## Recommended Disposition
**REJECT**. Drift exceeds safety bounds and conformal coverage cannot guarantee spec compliance.