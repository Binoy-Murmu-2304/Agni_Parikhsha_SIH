# AGNI PARIKSHA - QA Disposition Card
**Component ID**: `TEST_COMP_001`
**Family**: `IMAGE_SENSOR`

## 1. Verdict & Risk Tier
**Verdict**: RED_SAFETY_SLOPE
**Risk Tier**: RED_SAFETY_SLOPE

## 2. Quantitative Forecast
- **Measured at 24h**: 9.00
- **Predicted 168h**: 11.43
- **Conformal Interval (90%)**: +/- 2.97
- **Safety Slope Margin**: -0.0357 (allowed - measured max slope)

## 3. Explanability & Physics Trace
Base model prediction before features: 11.05

**Top Contributing Factors:**
- **val_0h** (Impact: +0.20): Baseline parameter val_0h is increasing the outcome.
- **val_24h** (Impact: +0.15): Baseline parameter val_24h is increasing the outcome.
- **slope_24h** (Impact: +0.03): The measured 0-24h drift rate is strongly increasing the forecast.

## Recommended Disposition
**REJECT**. Drift exceeds safety bounds and conformal coverage cannot guarantee spec compliance.