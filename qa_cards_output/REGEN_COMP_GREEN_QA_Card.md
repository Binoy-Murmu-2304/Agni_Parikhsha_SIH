# AGNI PARIKSHA - QA Disposition Card
**Component ID**: `REGEN_COMP_GREEN`
**Family**: `DIGITAL_IC`

## 1. Verdict & Risk Tier
**Verdict**: GREEN
**Risk Tier**: GREEN

## 2. Quantitative Forecast
- **Measured at 24h**: 14.18
- **Predicted 168h**: 34.82
- **Conformal Interval (90%)**: +/- 20.54
- **Safety Slope Margin**: 0.3184 (allowed - measured max slope)

## 3. Explanability & Physics Trace
Base model prediction before features: 44.13

**Top Contributing Factors:**
- **slope_24h** (Impact: -7.01): The measured 0-24h drift rate is strongly decreasing the forecast.
- **val_24h** (Impact: -4.41): Baseline parameter val_24h is decreasing the outcome.
- **val_0h** (Impact: +2.12): Baseline parameter val_0h is increasing the outcome.

## Recommended Disposition
**PASS (EARLY termination allowed)**. Component is stable and drift trajectory is safely within physical limits.