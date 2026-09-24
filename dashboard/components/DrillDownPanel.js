import React from 'react';
import DriftChart from './DriftChart';
import QACardCertificate from './QACardCertificate';

export default function DrillDownPanel({ selectedComp, cardData, onClose, onDownloadPdf, loadingPdf }) {
  if (!selectedComp) {
    return (
      <div style={{ padding: '20px', border: '1px solid #1e1e2e', background: '#111118', color: '#6b7280', fontSize: '11px', textAlign: 'center' }}>
        SELECT COMPONENT FROM TRIAGE BOARD
      </div>
    );
  }

  const family = selectedComp.family || "DIGITAL_IC";
  const unit = selectedComp.unit || "";
  const specMax = selectedComp.spec_max || 50.0;

  const measured24 = selectedComp.measured_24h !== null && selectedComp.measured_24h !== undefined ? selectedComp.measured_24h : (selectedComp.value_24h !== null && selectedComp.value_24h !== undefined ? selectedComp.value_24h : null);
  const pred168 = selectedComp.pred_168h !== null && selectedComp.pred_168h !== undefined ? selectedComp.pred_168h : null;
  const margin = selectedComp.safety_slope_margin !== null && selectedComp.safety_slope_margin !== undefined ? selectedComp.safety_slope_margin : null;
  const confRadius = selectedComp.conformal_interval_95 !== null && selectedComp.conformal_interval_95 !== undefined ? selectedComp.conformal_interval_95 : null;

  // Triggers fired as plain colored text
  const triggers = [];
  if (selectedComp.trigger_module_a === 1) triggers.push("MODULE_A_OUTLIER");
  if (selectedComp.trigger_safety_slope === 1) triggers.push("SAFETY_SLOPE_BREACH");
  
  const isRoutingOverride = selectedComp.disposition === "FULL_BURN_IN" && triggers.length === 0;
  if (isRoutingOverride) {
    triggers.push("CAPABILITY_ROUTING_OVERRIDE");
  }

  return (
    <div style={{ width: '380px', borderLeft: '1px solid #1e1e2e', padding: '12px', background: '#111118', display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #1e1e2e', paddingBottom: '6px' }}>
        <div style={{ fontSize: '11px', fontWeight: 'bold', color: '#4ea1f0', letterSpacing: '1px' }}>
          DRILL-DOWN :: {selectedComp.component_id} [{family}]
        </div>
        {onClose && (
          <button className="btn-secondary" onClick={onClose} style={{ padding: '2px 6px', fontSize: '10px' }}>[CLOSE]</button>
        )}
      </div>

      {/* DRIFT CHART */}
      <div>
        <DriftChart
          family={family}
          val_0h={selectedComp.value_0h}
          val_24h={measured24}
          pred_168h={pred168}
          conformal_radius={confRadius}
          measured_slope={selectedComp.measured_slope}
          spec_max={specMax}
          unit={unit}
        />
      </div>

      {/* METRICS SECTION */}
      <div style={{ borderTop: '1px solid #1e1e2e', borderBottom: '1px solid #1e1e2e', padding: '8px 0' }}>
        <div style={{ fontSize: '11px', color: '#6b7280', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '6px' }}>
          METRICS
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
          <span className="stat-label">SAFETY-SLOPE MARGIN</span>
          <span className={`stat-val ${margin !== null && margin < 0 ? 'text-red' : 'text-green'}`}>
            {margin !== null ? `${margin >= 0 ? '+' : ''}${Number(margin).toFixed(4)}` : "—"}
          </span>
        </div>

        <div className="stat-row">
          <span className="stat-label">CONFORMAL (95%)</span>
          <span className="stat-val">{confRadius !== null ? `+/- ${Number(confRadius).toFixed(2)} ${unit}` : "—"}</span>
        </div>

        <div className="stat-row" style={{ borderBottom: 'none' }}>
          <span className="stat-label">TRIGGERS</span>
          <span className="stat-val" style={{ color: selectedComp.disposition === 'RED' ? '#ff1744' : selectedComp.disposition === 'FULL_BURN_IN' ? '#ffab00' : '#00e676' }}>
            {triggers.length > 0 ? triggers.join(', ') : 'NONE'}
          </span>
        </div>
      </div>

      {/* QA CARD WITH DOWNLOAD PDF CERTIFICATE BUTTON */}
      <div>
        <div style={{ marginBottom: '8px', display: 'flex', justifyContent: 'flex-start' }}>
          <button
            className="btn-primary"
            onClick={() => onDownloadPdf(selectedComp.component_id)}
            disabled={loadingPdf}
            style={{ fontSize: '11px' }}
          >
            {loadingPdf ? "[GENERATING PDF...]" : "[DOWNLOAD PDF CERTIFICATE]"}
          </button>
        </div>

        <QACardCertificate comp={selectedComp} cardMarkdown={cardData ? cardData.markdown : null} />
      </div>
    </div>
  );
}

