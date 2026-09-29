import React from 'react';

const STEPS = [
  {
    number: '01',
    title: 'See the hidden anomaly',
    body: 'Module A compares every component with its own lot—not only a static datasheet limit—so abnormal behaviour is visible early.'
  },
  {
    number: '02',
    title: 'Forecast the 168-hour outcome',
    body: 'Module B uses 0h and 24h readings to predict the 168h parameter value and attaches a calibrated uncertainty interval.'
  },
  {
    number: '03',
    title: 'Apply a safety boundary',
    body: 'The safety-slope check escalates a component when its measured or predicted drift cannot safely remain inside the specification.'
  },
  {
    number: '04',
    title: 'Abstain when the model is not capable',
    body: 'Families that fail the prediction-accuracy guard are automatically routed to the mandatory 168h process. The system never guesses.'
  }
];

export default function MissionBrief({ metrics, onOpenTriage, onOpenEvidence }) {
  const realizedSavings = metrics?.AGNI?.realized_savings;
  const savings = Number.isFinite(Number(realizedSavings)) ? Number(realizedSavings).toFixed(2) : '33.64';

  return (
    <section className="mission-brief">
      <div className="mission-hero">
        <div className="mission-eyebrow">SIH 2026 · ISRO · PS 26170 · SMART AUTOMATION</div>
        <h1>Find the 24-hour signal.<br /><span>Keep the 168-hour safety gate.</span></h1>
        <p className="mission-lede">
          AGNI PARIKSHA identifies lot-relative anomalies and predicts burn-in drift early—then routes any family outside the model’s proven capability back to the full ESS process.
        </p>
        <div className="mission-actions">
          <button className="mission-primary" onClick={onOpenTriage}>Open live triage board <span>→</span></button>
          <button className="mission-secondary" onClick={onOpenEvidence}>View validation evidence</button>
        </div>
      </div>

      <div className="mission-kpis" aria-label="Project highlights">
        <div className="mission-kpi">
          <span className="mission-kpi-value">{savings}%</span>
          <span className="mission-kpi-label">realized chamber-time saving<br />at the evaluated operating point</span>
        </div>
        <div className="mission-kpi">
          <span className="mission-kpi-value">85.71%</span>
          <span className="mission-kpi-label">time released when a component<br />exits at 24h instead of 168h</span>
        </div>
        <div className="mission-kpi mission-kpi-guard">
          <span className="mission-kpi-value">3 / 5</span>
          <span className="mission-kpi-label">families protected by mandatory<br />full burn-in when accuracy is insufficient</span>
        </div>
      </div>

      <div className="mission-section-heading">
        <span>THE DECISION PIPELINE</span>
        <p>Not a black box: every decision has a measurable reason and an inspector-ready record.</p>
      </div>

      <div className="mission-steps">
        {STEPS.map((step) => (
          <article className="mission-step" key={step.number}>
            <span className="mission-step-number">{step.number}</span>
            <h2>{step.title}</h2>
            <p>{step.body}</p>
          </article>
        ))}
      </div>

      <div className="mission-proof-grid">
        <article className="mission-proof mission-proof-safety">
          <span className="mission-proof-tag">SAFETY BY DESIGN</span>
          <h2>Confidence is a gate, not a promise.</h2>
          <p>
            The capability-routing policy prevents early GREEN decisions for DIGITAL_IC, MIXED_SIGNAL_IC, and PRECISION_VOLTAGE_REF because their model error exceeds the configured 20% specification guard.
          </p>
        </article>
        <article className="mission-proof">
          <span className="mission-proof-tag">AUDITABLE OUTPUT</span>
          <h2>One decision, one QA trail.</h2>
          <p>
            Inspectors can open a component’s trajectory, uncertainty interval, safety-slope margin, trigger list, explainability card, and exportable PDF certificate from the live board.
          </p>
        </article>
        <article className="mission-proof">
          <span className="mission-proof-tag">HONEST VALIDATION</span>
          <h2>Built for a safe transition to plant data.</h2>
          <p>
            The current benchmark uses the frozen AGNI-SIM dataset. Deployment begins with historical 168h data, shadow-mode validation, and a family-by-family capability audit before any early exit.
          </p>
        </article>
      </div>

      <div className="mission-demo-strip">
        <div>
          <span className="mission-proof-tag">60-SECOND DEMO PATH</span>
          <p><strong>1.</strong> Open Triage &nbsp; <strong>2.</strong> Select a lot &nbsp; <strong>3.</strong> Inspect a RED, GREEN, and FULL_BURN_IN decision &nbsp; <strong>4.</strong> Export its QA evidence.</p>
        </div>
        <button className="mission-secondary" onClick={onOpenTriage}>Start demo</button>
      </div>
    </section>
  );
}
