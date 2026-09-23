# AGNI PARIKSHA - QA Disposition Card
**Component ID**: `FINAL_LOT_0050_0020`
**Family**: `DIGITAL_IC`

## 1. Verdict & Risk Tier
**Verdict**: FULL_BURN_IN
**Risk Tier**: MEDIUM

## 2. Quantitative Forecast
- **Measured at 24h**: 32.51
- **Predicted 168h**: 185.33 µA vs Spec Max 50.0 µA ? forecast exceeds limit
- **Conformal Interval (90%)**: +/- 20.54
- **Safety Slope Margin**: -1.0080 (allowed - measured max slope)

## 3. Explanability & Physics Trace
Base model prediction before features: 44.13

**Top Contributing Factors:**
- **slope_24h** (Impact: +87.71): The measured 0-24h drift rate is strongly increasing the forecast.
- **val_24h** (Impact: +36.43): The parameter level at 24h is strongly increasing the forecast.
- **val_0h** (Impact: +17.06): The baseline level at 0h is strongly increasing the forecast.

## Suspected Mechanism (Family Physics Prior)
drift pattern consistent with thermally-accelerated leakage growth (Arrhenius-like)

*Disclaimer: Mechanism hypotheses are family-prior heuristics, not causal identifications.*

## Mandatory Routing
**Reason**: triggered Safety slope breach; disposition overridden to FULL_BURN_IN by capability routing policy.