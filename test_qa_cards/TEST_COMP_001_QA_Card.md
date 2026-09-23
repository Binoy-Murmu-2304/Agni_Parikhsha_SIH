# AGNI PARIKSHA - QA Disposition Card
**Component ID**: `TEST_COMP_001`
**Family**: `IMAGE_SENSOR`

## 1. Verdict & Risk Tier
**Verdict**: RED_SAFETY_SLOPE
**Risk Tier**: RED_SAFETY_SLOPE

## 2. Quantitative Forecast
- **Measured at 24h**: 9.00
- **Predicted 168h**: 9.79
- **Conformal Interval (90%)**: +/- 3.16
- **Safety Slope Margin**: -0.0357 (allowed - measured max slope)

## 3. Explanability & Physics Trace
Base model prediction before features: 10.93

**Top Contributing Factors:**
- **val_0h** (Impact: -0.98): Baseline parameter val_0h is decreasing the outcome.
- **val_24h** (Impact: -0.24): Baseline parameter val_24h is decreasing the outcome.
- **slope_24h** (Impact: +0.08): The measured 0-24h drift rate is strongly increasing the forecast.

## Recommended Disposition
**REJECT**. Drift exceeds safety bounds and conformal coverage cannot guarantee spec compliance.