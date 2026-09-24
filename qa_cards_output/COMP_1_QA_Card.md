# AGNI PARIKSHA - QA Disposition Card
**Component ID**: `COMP_1`
**Family**: `DIGITAL_IC`

## 1. Verdict & Risk Tier
**Verdict**: FULL_BURN_IN
**Risk Tier**: MEDIUM

## 2. Quantitative Forecast
- **Measured at 24h**: 10.50
- **Predicted 168h**: 34.99 µA vs Spec Max 50.0 µA
- **Conformal Interval (90%)**: +/- 20.54
- **Safety Slope Margin**: 0.0089 (allowed - measured max slope)

## 3. Explanability & Physics Trace
Base model prediction before features: 0.00

**Top Contributing Factors:**
- Explanation physics trace not computed for this record

## Suspected Mechanism (Family Physics Prior)
drift pattern consistent with thermally-accelerated leakage growth (Arrhenius-like)

*Disclaimer: Mechanism hypotheses are family-prior heuristics, not causal identifications.*

## Mandatory Routing
**Reason**: FULL_BURN_IN. This family/component cannot be certified early. Route to full 168h burn-in.