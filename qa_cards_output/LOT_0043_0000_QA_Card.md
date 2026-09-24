# AGNI PARIKSHA - QA Disposition Card
**Component ID**: `LOT_0043_0000`
**Family**: `PRECISION_VOLTAGE_REF`

## 1. Verdict & Risk Tier
**Verdict**: FULL_BURN_IN
**Risk Tier**: nan

## 2. Quantitative Forecast
- **Measured at 24h**: 14.38
- **Predicted 168h**: 67.95 µV vs Spec Max 100.0 µV
- **Conformal Interval (90%)**: +/- 37.48
- **Safety Slope Margin**: 0.2518 (allowed - measured max slope)

## 3. Explanability & Physics Trace
Base model prediction before features: 0.00

**Top Contributing Factors:**
- Explanation physics trace not computed for this record

## Suspected Mechanism (Family Physics Prior)
consistent with thermal stress / hysteresis drift

*Disclaimer: Mechanism hypotheses are family-prior heuristics, not causal identifications.*

## Mandatory Routing
**Reason**: FULL_BURN_IN. This family/component cannot be certified early. Route to full 168h burn-in.