# AGNI PARIKSHA — 3-Minute SIH Demo Guide

## The one-sentence positioning

**AGNI PARIKSHA is a safety-first ESS triage system that finds lot-relative anomalies at 24 hours, forecasts 168-hour drift, and refuses early release whenever its prediction capability is insufficient.**

Do not describe it as a replacement for qualification or a guarantee of zero field failures. Describe it as an auditable decision-support layer that preserves the 168-hour process whenever the evidence is not strong enough.

## Recommended demo flow

### 0:00–0:25 — The operational pain

“Static pass/fail limits miss a component that is still below the limit but drifting differently from the rest of its lot. Waiting for every healthy component to complete 168 hours also occupies limited thermal-chamber capacity.”

Open **Mission Brief**. Point to the statement: *Find the 24-hour signal. Keep the 168-hour safety gate.*

### 0:25–0:55 — The differentiation

“Our differentiator is not just predicting a number. We have a capability gate. If a family exceeds 20% MAE relative to its specification, it is never given an early GREEN disposition—it is routed back to mandatory full burn-in.”

Point to **3 / 5 protected families** and the **Safety by design** card.

### 0:55–1:35 — Show one live decision

Open **Triage Board** and select a lot. Open one **RED** component and explain:

1. Module A compares it against its lot’s robust baseline.
2. Module B forecasts its 168-hour value from 0h and 24h readings.
3. The safety-slope margin and triggers state why it was escalated.

Then open a **FULL_BURN_IN** component with no trigger. Explain that this is the intentional abstention path: the software does not turn uncertainty into a pass.

### 1:35–2:05 — Show traceability

Download the component’s **PDF certificate**. Mention that the same QA trace is available for the inspector: observed values, prediction, uncertainty, safety margin, triggers, and routing rationale.

### 2:05–2:35 — Show measurable value, carefully

Open **Results & Metrics**. State:

- A component released at 24h frees **85.71%** of the 168-hour chamber duration.
- At the evaluated 5% defect-prevalence operating point, realized saving is **33.64%**.
- The current benchmark uses frozen AGNI-SIM data; the dashboard says this plainly.

Do not imply that 33.64% is a universal deployment result. It is an evaluation result that will change with the real family mix and operating point.

### 2:35–3:00 — Close with the deployment path

“The next step is controlled adoption: ingest historical 168-hour data, run in shadow mode, calibrate family-specific thresholds, complete the capability audit, and only then enable early-exit recommendations for qualifying families.”

## Questions judges are likely to ask

| Question | Answer to give |
|---|---|
| Why not use a static threshold? | Static limits only say whether a part has already crossed a bound. AGNI also compares it to its lot and detects abnormal drift before that crossing. |
| Why should ISRO trust the ML model? | It should not trust it blindly. Split-conformal intervals, per-family metrics, a capability audit, traceable QA cards, and the mandatory full-burn-in fallback make the limits explicit. |
| What happens when data is missing or the model is uncertain? | The safe disposition is FULL_BURN_IN. The product is designed to abstain rather than issue an unsupported early GREEN decision. |
| Is the current data real ISRO data? | No. It is a frozen synthetic benchmark, clearly labelled as AGNI-SIM. We use it to prove the workflow and validation discipline; plant deployment requires historical ISRO measurements and shadow-mode validation. |
| What is technically novel here? | The combination of lot-adaptive anomaly detection, drift forecasting with uncertainty, a physics-inspired safety slope, and capability-based abstention in one inspector workflow. |

## Avoid these avoidable mistakes

- Do not lead with “AI”. Lead with the operational safety problem and the decision it improves.
- Do not claim “zero escapes”; explain the routing policy and report the auto-passable-family limitation if asked.
- Do not hide that AGNI-SIM is synthetic. Transparency strengthens a high-reliability pitch.
- Do not demo every screen. Show one RED decision, one routed FULL_BURN_IN decision, and one PDF QA trace.
