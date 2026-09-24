# AGNI PARIKSHA - QA Disposition Card
**Component ID**: `FINAL_LOT_0054_0006`
**Family**: `IMAGE_SENSOR`

## 1. Verdict & Risk Tier
**Verdict**: GREEN
**Risk Tier**: nan

## 2. Quantitative Forecast
- **Measured at 24h**: 4.66
- **Predicted 168h**: 5.13 nA/cm² vs Spec Max 10.0 nA/cm²
- **Conformal Interval (90%)**: +/- 2.55
- **Safety Slope Margin**: -0.0716 (allowed - measured max slope)

## 3. Explanability & Physics Trace
Base model prediction before features: 0.00

**Top Contributing Factors:**
- Explanation physics trace not computed for this record

## Suspected Mechanism (Family Physics Prior)
consistent with dark-current growth (SRH trap generation)

*Disclaimer: Mechanism hypotheses are family-prior heuristics, not causal identifications.*

## Recommended Disposition
**PASS (EARLY termination allowed)**. Component is stable and drift trajectory is safely within physical limits.