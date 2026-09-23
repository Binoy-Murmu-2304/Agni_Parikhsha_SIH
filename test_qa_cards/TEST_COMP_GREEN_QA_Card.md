# AGNI PARIKSHA - QA Disposition Card
**Component ID**: `TEST_COMP_GREEN`
**Family**: `DIGITAL_IC`

## 1. Verdict & Risk Tier
**Verdict**: GREEN
**Risk Tier**: GREEN

## 2. Quantitative Forecast
- **Measured at 24h**: 10.10
- **Predicted 168h**: 10.00
- **Conformal Interval (90%)**: +/- 0.00
- **Safety Slope Margin**: 0.0500 (allowed - measured max slope)

## 3. Explanability & Physics Trace
Base model prediction before features: 10.00

**Top Contributing Factors:**
- **val_0h** (Impact: +0.00): Baseline parameter val_0h is decreasing the outcome.
- **val_24h** (Impact: +0.00): Baseline parameter val_24h is decreasing the outcome.
- **slope_24h** (Impact: +0.00): The measured 0-24h drift rate is strongly decreasing the forecast.

## Recommended Disposition
**PASS (EARLY termination allowed)**. Component is stable and drift trajectory is safely within physical limits.