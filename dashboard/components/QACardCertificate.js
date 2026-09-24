import React from 'react';

const FAMILY_UNITS = {
  "DIGITAL_IC": "µA",
  "MIXED_SIGNAL_IC": "µA",
  "MEMS_GYROSCOPE": "dps",
  "PRECISION_VOLTAGE_REF": "µV",
  "IMAGE_SENSOR": "nA/cm²"
};

const FAMILY_SPEC_MAX = {
  "DIGITAL_IC": 50.0,
  "MIXED_SIGNAL_IC": 75.0,
  "MEMS_GYROSCOPE": 0.5,
  "PRECISION_VOLTAGE_REF": 100.0,
  "IMAGE_SENSOR": 10.0
};

export default function QACardCertificate({ comp }) {
  if (!comp) return null;

  const family = comp.family || "DIGITAL_IC";
  const unit = FAMILY_UNITS[family] || "";
  const specMax = FAMILY_SPEC_MAX[family] || 0;
  const verdict = comp.disposition || "GREEN";
  const riskTier = comp.risk_tier || (verdict === 'RED' ? 'HIGH' : verdict === 'FULL_BURN_IN' ? 'MEDIUM' : 'LOW');

  const measured24 = comp.measured_24h !== null && comp.measured_24h !== undefined ? comp.measured_24h : (comp.value_24h !== null && comp.value_24h !== undefined ? comp.value_24h : null);
  const pred168 = comp.pred_168h !== null && comp.pred_168h !== undefined ? comp.pred_168h : null;
  const confRadius = comp.conformal_interval_95 !== null && comp.conformal_interval_95 !== undefined ? comp.conformal_interval_95 : null;
  const margin = comp.safety_slope_margin !== null && comp.safety_slope_margin !== undefined ? comp.safety_slope_margin : null;

  const exceedsLimit = pred168 !== null && specMax ? (pred168 > specMax ? "YES" : "NO") : "—";

  return (
    <div className="qa-card-doc">
      <div className="qa-card-header">
        AGNI PARIKSHA :: QA DISPOSITION CARD
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div className="stat-row">
          <span className="stat-label">COMPONENT</span>
          <span className="stat-val">{comp.component_id}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">FAMILY</span>
          <span className="stat-val">{family}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">VERDICT</span>
          <span className={`stat-val ${verdict === 'RED' ? 'text-red' : verdict === 'FULL_BURN_IN' ? 'text-amber' : 'text-green'}`}>
            {verdict}
          </span>
        </div>
        <div className="stat-row">
          <span className="stat-label">RISK</span>
          <span className={`stat-val ${riskTier === 'HIGH' ? 'text-red' : riskTier === 'MEDIUM' ? 'text-amber' : 'text-green'}`}>
            {riskTier}
          </span>
        </div>

        <div style={{ borderTop: '1px solid #1e1e2e', paddingTop: '6px', marginTop: '4px' }}>
          <div style={{ fontSize: '10px', color: '#6b7280', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '4px' }}>
            FORECAST
          </div>
          <div className="stat-row">
            <span className="stat-label">MEASURED 24H</span>
            <span className="stat-val">{measured24 !== null ? `${Number(measured24).toFixed(2)} ${unit}` : "—"}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">PREDICTED 168H</span>
            <span className="stat-val">{pred168 !== null ? `${Number(pred168).toFixed(2)} ${unit}` : "—"}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">SPEC MAX</span>
            <span className="stat-val">{specMax} {unit}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">EXCEEDS LIMIT</span>
            <span className={`stat-val ${exceedsLimit === 'YES' ? 'text-red' : 'text-green'}`}>{exceedsLimit}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">CONFORMAL 95%</span>
            <span className="stat-val">{confRadius !== null ? `+/- ${Number(confRadius).toFixed(2)} ${unit}` : "—"}</span>
          </div>
          <div className="stat-row">
            <span className="stat-label">SAFETY MARGIN</span>
            <span className={`stat-val ${margin !== null && margin < 0 ? 'text-red' : 'text-green'}`}>
              {margin !== null ? `${margin >= 0 ? '+' : ''}${Number(margin).toFixed(4)}` : "—"}
            </span>
          </div>
        </div>

        <div style={{ borderTop: '1px solid #1e1e2e', paddingTop: '6px', marginTop: '4px' }}>
          <div style={{ fontSize: '10px', color: '#6b7280', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '4px' }}>
            EXPLANATION (SHAP)
          </div>
          {comp.shap_physics ? (
            Object.entries(comp.shap_physics).map(([k, v]) => (
              <div key={k} className="stat-row">
                <span className="stat-label">{k}</span>
                <span className="stat-val">{String(v)}</span>
              </div>
            ))
          ) : (
            <div style={{ fontSize: '10px', color: '#6b7280' }}>
              slope_24h drift rate forecast · val_24h level at 24h · val_0h baseline
            </div>
          )}
        </div>

        <div style={{ borderTop: '1px solid #1e1e2e', paddingTop: '6px', marginTop: '4px' }}>
          <div style={{ fontSize: '10px', color: '#6b7280', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '4px' }}>
            SUSPECTED MECHANISM
          </div>
          <div style={{ fontSize: '10px', color: '#c8ccd4' }}>
            {family === 'DIGITAL_IC' ? 'thermally-accelerated leakage (Arrhenius)' :
             family === 'MEMS_GYROSCOPE' ? 'mechanical relaxation (viscoelastic creep)' :
             family === 'IMAGE_SENSOR' ? 'dark-current growth (SRH trap generation)' :
             family === 'MIXED_SIGNAL_IC' ? 'current-density stress (electromigration)' :
             'thermal stress / hysteresis drift'}
          </div>
          <div style={{ fontSize: '9px', color: '#6b7280', fontStyle: 'italic' }}>
            [family-prior heuristic, not causal]
          </div>
        </div>

        <div style={{ borderTop: '1px solid #1e1e2e', paddingTop: '6px', marginTop: '4px' }}>
          <div style={{ fontSize: '10px', color: '#6b7280', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '4px' }}>
            ROUTING
          </div>
          <div style={{ fontSize: '10px', color: verdict === 'RED' ? '#ff1744' : verdict === 'FULL_BURN_IN' ? '#ffab00' : '#00e676' }}>
            {verdict === 'RED' ? 'Triggered reject bound; early exit denied.' :
             verdict === 'FULL_BURN_IN' ? 'Triggered Safety slope breach or capability policy override to FULL_BURN_IN.' :
             'Passed 24h screening; 168h exit granted.'}
          </div>
        </div>
      </div>
    </div>
  );
}

