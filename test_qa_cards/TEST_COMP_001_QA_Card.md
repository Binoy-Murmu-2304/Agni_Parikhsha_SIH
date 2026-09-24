# AGNI PARIKSHA - QA Disposition Card
**Component ID**: `TEST_COMP_001`
**Family**: `IMAGE_SENSOR`

## 1. Verdict & Risk Tier
**Verdict**: RED_SAFETY_SLOPE
**Risk Tier**: RED_SAFETY_SLOPE

## 2. Quantitative Forecast
- **Measured at 24h**: 9.00
- **Predicted 168h**: 11.11 nA/cm² vs Spec Max 10.0 nA/cm² ? forecast exceeds limit
- **Conformal Interval (90%)**: +/- 2.98
- **Safety Slope Margin**: -0.0357 (allowed - measured max slope)

## 3. Explanability & Physics Trace
Base model prediction before features: 11.40

**Top Contributing Factors:**
- **slope_24h** (Impact: -0.39): The measured 0-24h drift rate is decreasing the forecast.
- **val_0h** (Impact: +0.29): The baseline level at 0h is increasing the forecast.
- **val_24h** (Impact: -0.19): The parameter level at 24h is decreasing the forecast.

## Suspected Mechanism (Family Physics Prior)
consistent with dark-current growth (SRH trap generation)

*Disclaimer: Mechanism hypotheses are family-prior heuristics, not causal identifications.*

## Recommended Disposition
**REJECT**. Drift exceeds safety bounds and conformal coverage cannot guarantee spec compliance.