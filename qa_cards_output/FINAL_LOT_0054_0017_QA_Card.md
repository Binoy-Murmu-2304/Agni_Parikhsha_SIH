# AGNI PARIKSHA - QA Disposition Card
**Component ID**: `FINAL_LOT_0054_0017`
**Family**: `IMAGE_SENSOR`

## 1. Verdict & Risk Tier
**Verdict**: RED
**Risk Tier**: HIGH

## 2. Quantitative Forecast
- **Measured at 24h**: 8.03
- **Predicted 168h**: 11.96 nA/cm² vs Spec Max 10.0 nA/cm² ? forecast exceeds limit
- **Conformal Interval (90%)**: +/- 2.55
- **Safety Slope Margin**: -0.2222 (allowed - measured max slope)

## 3. Explanability & Physics Trace
Base model prediction before features: 0.00

**Top Contributing Factors:**
- Explanation physics trace not computed for this record

## Suspected Mechanism (Family Physics Prior)
consistent with dark-current growth (SRH trap generation)

*Disclaimer: Mechanism hypotheses are family-prior heuristics, not causal identifications.*

## Recommended Disposition
**REJECT**. Drift exceeds safety bounds and conformal coverage cannot guarantee spec compliance.