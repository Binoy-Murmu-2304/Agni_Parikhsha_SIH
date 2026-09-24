# AGNI PARIKSHA

**AI-Driven Anomaly Detection & Drift Prediction for Component Burn-In / Environmental Stress Screening (ESS)**

Built for **SIH 2026 Problem Statement #26170** (ISRO) by **Team AGNI PARIKSHA**.

100% original implementation. Released under the MIT License.

---

## Problem

ISRO screens every electronic component through **168-hour Environmental Stress Screening (burn-in)** to catch early-life failures. This is expensive — thermal chambers are limited, and **85.7% of chamber time is spent on parts that are fine**.

**Can we certify safe components at 24 hours instead of 168?**

AGNI PARIKSHA answers: **Yes — where the model is confident. And honestly routes everything else to full burn-in.**

---

## Key Results

| Metric | Value | Notes |
|--------|-------|-------|
| **Realized Chamber Savings** | **33.64%** | At 5% defect prevalence |
| **Chamber Capacity Ratio** | **85.71%** | 24h screen / 168h full burn-in |
| **Conformal Coverage (90%)** | 87.1–89.5% | Per-family, Clopper-Pearson CI |
| **Conformal Coverage (95%)** | 93.1–94.5% | Per-family, Clopper-Pearson CI |
| **Escape Rate (auto-passable)** | **27.53%** | [95% CI: 22.95–32.48%] |
| **Escape Rate (routed families)** | **0%** | Zero by construction |
| **Test Suite** | **22/22 passed** | Full regression |
| **Claims Verified** | **38/38 (100%)** | Reproducible verification pipeline |

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Module A   │     │   Module B   │     │   Safety Slope   │
│  (Outlier   │────►│  (Drift      │────►│  (Capability-    │
│   Detector) │     │   Predictor) │     │   Graded Bounds) │
└─────────────┘     └──────────────┘     └──────────────────┘
       │                    │                       │
       └────────────────────┼───────────────────────┘
                            ▼
                  ┌──────────────────┐
                  │  Capability      │
                  │  Routing Gate    │◄── MAE < 20% of spec?
                  └──────────────────┘
                     │           │
              ┌──────┘           └──────┐
              ▼                         ▼
     ┌──────────────┐          ┌──────────────┐
     │   CAPABLE    │          │   ROUTED     │
     │  GREEN/RED   │          │ FULL_BURN_IN │
     │  at 24h      │          │ at 168h      │
     └──────────────┘          └──────────────┘
```

### Capability Routing (Safety Policy)

| Family | Routing | Rationale |
|--------|---------|-----------|
| DIGITAL_IC | **MANDATORY_FULL_BURN_IN** | Model MAE > 20% of spec max |
| MIXED_SIGNAL_IC | **MANDATORY_FULL_BURN_IN** | Model MAE > 20% of spec max |
| PRECISION_VOLTAGE_REF | **MANDATORY_FULL_BURN_IN** | Model MAE > 20% of spec max |
| MEMS_GYROSCOPE | **CAPABLE** | Model MAE < 20% of spec max |
| IMAGE_SENSOR | **CAPABLE** | Model MAE < 20% of spec max |

**Routed families contribute zero escapes by construction.** The system honestly knows what it cannot predict and routes those parts to full burn-in.

---

## Method Summary

### Module A — Dynamic Outlier Detection
- MAD-based dynamic outlier detection with lot-adaptive thresholds
- K-noise inflation (k=3.5) for measurement noise tolerance
- Guards for MAD=0 (zero-variance lots) and tiny lots

### Module B — Drift Prediction
- Per-family gradient-boosted predictor trained on frozen AGNI-SIM dataset
- Two-checkpoint observation window (0h to 24h)
- Split-conformal prediction intervals (90% and 95% coverage)

### Safety Slope
- Derived slope bounds: (spec_max - value_24h) / remaining_hours
- Capability-graded noise floor accounts for instrument precision
- Triggers RED when measured slope exceeds allowed slope

### Explainability
- SHAP-based feature attribution on real model features
- Hedged family-prior mechanism hypotheses (not causal identification)
- Full trace on QA Disposition Cards

### Evaluation
- False-negative-penalized scoring (5:1 FN:FP ratio)
- Per-family conformal coverage with Clopper-Pearson CIs
- Escape-FN disaggregation (structural zero for routed families)
- Prevalence sweep (1%, 5%, 10%, 20%)

---

## Quick Start

```bash
# Install
pip install -e .[dev]

# Run tests (22 tests)
pytest tests/ -v

# Verify all claims (38 assertions)
python -m agnipariksha.evaluation.verify_claims

# Start API
python -m uvicorn agnipariksha.api.main:app --port 8000

# Start Dashboard
cd dashboard
npm install
npm run dev
# Open http://localhost:3000
```

---

## Dashboard

- **Triage Kanban** — components sorted GREEN / FULL_BURN_IN / RED across lots
- **Drill-Down** — drift trajectory chart, conformal intervals, safety slope margins
- **QA Cards** — SHAP explanations, physics priors, PDF certificate export
- **Results & Metrics** — per-family performance, escape-FN, known limitations

---

## Known Limitations

1. **Synthetic data scope** — trained on AGNI-SIM synthetic dataset. Real-world deployment requires retraining on actual measurements. Safety policies are unchanged.
2. **Two-checkpoint window** — limits physics discrimination (slow creep, late avalanche, non-monotonic drift are blind spots).
3. **Minor conformal under-coverage** — finite-sample effects in tight families (87.1% vs 90% target for IMAGE_SENSOR).
4. **Auto-passable escape rate** — 27.53% [22.95–32.48%] in capable families. Routed families: 0% by construction.
5. **Conformal trigger excluded from final_flag** — design decision (prior "0 detections" justification was retracted as a bug artifact; see CLAIM_HISTORY).

---

## Verification & Integrity

All claims are machine-verified:

```bash
python -m agnipariksha.evaluation.verify_claims
# Output: 100% of claims asserted successfully. All Invariants Verified.
```

Full development history including corrections and retractions:
- `fixes/CLAIM_HISTORY.md` — integrity trail
- `metrics_canonical.json` — single source of truth for all numbers
- `data/manifest.json` — frozen split manifest (seed 42)

---

## License

MIT License. See [LICENSE](LICENSE).

100% original implementation by Team AGNI PARIKSHA for SIH 2026 PS #26170.
