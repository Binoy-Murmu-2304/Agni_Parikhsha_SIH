# AGNI PARIKSHA - QA Disposition Card
**Component ID**: `FINAL_LOT_0056_0001`
**Family**: `MIXED_SIGNAL_IC`

## 1. Verdict & Risk Tier
**Verdict**: FULL_BURN_IN
**Risk Tier**: nan

## 2. Quantitative Forecast
- **Measured at 24h**: 25.34
- **Predicted 168h**: 57.63 µA vs Spec Max 75.0 µA
- **Conformal Interval (90%)**: +/- 28.05
- **Safety Slope Margin**: -0.3491 (allowed - measured max slope)

## 3. Explanability & Physics Trace
Base model prediction before features: 0.00

**Top Contributing Factors:**
- Explanation physics trace not computed for this record

## Suspected Mechanism (Family Physics Prior)
consistent with current-density stress (electromigration-like)

*Disclaimer: Mechanism hypotheses are family-prior heuristics, not causal identifications.*

## Mandatory Routing
**Reason**: FULL_BURN_IN. This family/component cannot be certified early. Route to full 168h burn-in.