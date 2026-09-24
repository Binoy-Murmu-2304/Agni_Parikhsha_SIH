import React from 'react';

export default function LotSummaryStrip({
  lotSummary,
  lotId,
  lots,
  metrics,
  onExportZip,
  loadingZip,
  onDownloadReport,
  loadingReport
}) {
  const isAllLots = lotId === 'ALL';

  if (isAllLots) {
    let fleetTotal = 0;
    let fleetGreen = 0;
    let fleetBurnIn = 0;
    let fleetRed = 0;

    if (lots && Array.isArray(lots)) {
      lots.forEach(l => {
        fleetTotal += (l.total || 0);
        fleetGreen += (l.green || 0);
        fleetBurnIn += (l.full_burn_in || 0);
        fleetRed += (l.red || 0);
      });
    }

    const savings = metrics && metrics.AGNI && metrics.AGNI.realized_savings !== undefined ? metrics.AGNI.realized_savings : 33.64;

    return (
      <div style={{ borderTop: '1px solid #1e1e2e', paddingTop: '8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', fontSize: '11px' }}>
        <div style={{ display: 'flex', gap: '14px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div>
            <span style={{ color: '#6b7280' }}>SCOPE:</span> <strong style={{ color: '#4ea1f0' }}>ALL LOTS COMBINED</strong>
          </div>
          <div>
            <span style={{ color: '#6b7280' }}>TOTAL:</span> <strong>{fleetTotal}</strong>
          </div>
          <div>
            <span style={{ color: '#6b7280' }}>GREEN:</span> <strong style={{ color: '#00e676' }}>{fleetGreen}</strong>
          </div>
          <div>
            <span style={{ color: '#6b7280' }}>BURN-IN:</span> <strong style={{ color: '#ffab00' }}>{fleetBurnIn}</strong>
          </div>
          <div>
            <span style={{ color: '#6b7280' }}>RED:</span> <strong style={{ color: '#ff1744' }}>{fleetRed}</strong>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ borderLeft: '1px solid #1e1e2e', paddingLeft: '12px' }}>
            <span style={{ color: '#6b7280' }}>COMBINED SAVINGS:</span> <strong style={{ color: '#00e676', fontSize: '13px' }}>{savings}%</strong>
          </div>

          <button
            className="btn-primary"
            onClick={() => onDownloadReport && onDownloadReport('all')}
            disabled={loadingReport}
            style={{
              fontSize: '10px',
              padding: '3px 8px',
              background: 'transparent',
              border: '1px solid #4ea1f0',
              color: '#4ea1f0',
              fontFamily: 'var(--font-mono)',
              cursor: 'pointer'
            }}
          >
            {loadingReport ? "[GENERATING REPORT...]" : "[GENERATE FLEET REPORT (PDF)]"}
          </button>
        </div>
      </div>
    );
  }

  if (!lotSummary) return null;

  const counts = lotSummary.counts || {};
  const green = counts.GREEN || 0;
  const burnIn = counts.FULL_BURN_IN || 0;
  const red = counts.RED || 0;
  const total = lotSummary.total || (green + burnIn + red);
  const savings = lotSummary.realized_savings !== undefined ? lotSummary.realized_savings : 0.0;
  const greenFraction = lotSummary.green_fraction !== undefined ? lotSummary.green_fraction : (total > 0 ? green / total : 0);
  const greenPct = (greenFraction * 100).toFixed(1);

  return (
    <div style={{ borderTop: '1px solid #1e1e2e', paddingTop: '8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', fontSize: '11px' }}>
      <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
        <div>
          <span style={{ color: '#6b7280' }}>LOT:</span> <strong style={{ color: '#4ea1f0' }}>{lotSummary.lot_id || lotId}</strong>
        </div>
        <div>
          <span style={{ color: '#6b7280' }}>TOTAL:</span> <strong>{total}</strong>
        </div>
        <div>
          <span style={{ color: '#6b7280' }}>GREEN:</span> <strong style={{ color: '#00e676' }}>{green}</strong>
        </div>
        <div>
          <span style={{ color: '#6b7280' }}>BURN-IN:</span> <strong style={{ color: '#ffab00' }}>{burnIn}</strong>
        </div>
        <div>
          <span style={{ color: '#6b7280' }}>RED:</span> <strong style={{ color: '#ff1744' }}>{red}</strong>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
        <div style={{ borderLeft: '1px solid #1e1e2e', paddingLeft: '12px' }}>
          <span style={{ color: '#6b7280' }}>REALIZED SAVINGS:</span> <strong style={{ color: '#00e676', fontSize: '14px' }}>{savings}%</strong>
          <span style={{ fontSize: '10px', color: '#6b7280', marginLeft: '6px' }}>
            ({greenFraction.toFixed(4)} × 85.71%, yield: {greenPct}%)
          </span>
        </div>

        <button
          className="btn-primary"
          onClick={() => onDownloadReport && onDownloadReport(lotSummary.lot_id || lotId)}
          disabled={loadingReport}
          style={{
            fontSize: '10px',
            padding: '3px 8px',
            background: 'transparent',
            border: '1px solid #4ea1f0',
            color: '#4ea1f0',
            fontFamily: 'var(--font-mono)',
            cursor: 'pointer'
          }}
        >
          {loadingReport ? "[GENERATING REPORT...]" : "[GENERATE LOT REPORT (PDF)]"}
        </button>

        <button
          className="btn-secondary"
          onClick={() => onExportZip(lotSummary.lot_id || lotId)}
          disabled={loadingZip}
          style={{ fontSize: '10px', padding: '2px 6px' }}
        >
          {loadingZip ? "[GENERATING ZIP...]" : "[EXPORT LOT CERTIFICATES (ZIP)]"}
        </button>
      </div>
    </div>
  );
}
