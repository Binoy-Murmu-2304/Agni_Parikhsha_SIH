# AGNI PARIKSHA FINAL EVALUATION REPORT
**Protocol executed once.**
**Commit Hash:** c86c4b2f753af149fb561c389515efd5eb8fe8ea
**Tag:** 1.0-final

## 1. Prevalence Sweep (DEVELOPMENT vs FINAL_EVAL)

| Prevalence | N | n_def | TP | FN | Escape-FN | FP | Recall (bound) | FPR (bound) | Precision | FW / 1000 | Sc10 | Sc50 | Sc50 (Escape) | Sc100 | Provenance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **0.5%** | 17090 | 90 | 71 | 19 | 8 | 21 | 78.89% [69.01%, 86.79%] | 0.12% [0.08%, 0.19%] | 77.17% | 1.2 | 98.8 | 94.3 | **97.5** | 88.8 | DEVELOPMENT |
| **5.0%** | 17890 | 890 | 651 | 239 | 94 | 20 | 73.15% [70.10%, 76.03%] | 0.12% [0.07%, 0.18%] | 97.02% | 1.2 | 86.5 | 33.1 | **73.6** | 0.0 | DEVELOPMENT |
| **0.5%** | 17090 | 90 | 66 | 24 | 13 | 9 | 73.33% [62.97%, 82.11%] | 0.05% [0.02%, 0.10%] | 88.00% | 0.5 | 98.5 | 92.9 | **96.1** | 85.9 | FINAL_EVAL |
| **5.0%** | 17890 | 890 | 680 | 210 | 98 | 7 | 76.40% [73.47%, 79.16%] | 0.04% [0.02%, 0.08%] | 98.98% | 0.4 | 88.2 | 41.3 | **72.6** | 0.0 | FINAL_EVAL |

## 2. Realized Chamber Savings

**B3 Exit Rates on FINAL_EVAL (5.0% prevalence): 33.56%**

## 3. Generalization Analysis
- The model generalizes exceptionally well to 10 unseen lots from the same frozen AGNI-SIM physics (synthetic scope unchanged).
- **Recall Variance:** FINAL_EVAL shifted recall from ~78.9% down to ~73.3% at 0.5% prevalence, but shifted *up* from ~73.2% to ~76.4% at 5.0% prevalence. The two-proportion z-test confirms this difference is not statistically significant (5% row: z?1.58, p?0.11; 0.5% row: z?0.87, p?0.38), indicating the variance is purely lot-to-lot sampling variance on a small N_lots=10 set.
- **FPR:** False positives actually *decreased* on the final eval set (down from 0.12% to 0.04%-0.05%).
- **Bottom Line:** There is zero evidence of test-set overfitting. The architecture maintains its structural capability floor on unseen lots from the same physics distribution.

## 4. Escape-FN Disaggregation
| Family | Disposition Path | DEV Escapes | FINAL_EVAL Escapes |
|---|---|---|---|
| DIGITAL_IC | Routed (FULL_BURN_IN) | 0 | 0 |
| MIXED_SIGNAL_IC | Routed (FULL_BURN_IN) | 0 | 0 |
| PRECISION_VOLTAGE_REF | Routed (FULL_BURN_IN) | 0 | 0 |
| MEMS_GYROSCOPE | Auto-Passable (GREEN) | 48 | 51 |
| IMAGE_SENSOR | Auto-Passable (GREEN) | 46 | 47 |

- **Structural statement**: Routed families contribute zero escapes by construction.
- **Auto-passable-family Escape Rate (FINAL_EVAL)**: 98 escapes out of 356 auto-passable family defects = 27.53% [95% Clopper-Pearson CI: 22.95%, 32.48%].
