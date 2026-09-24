import React from 'react';

const ROUTED_FAMILIES = ["DIGITAL_IC", "MIXED_SIGNAL_IC", "PRECISION_VOLTAGE_REF"];

export default function FleetSummaryStrip({ lots, dispositionFilter, onSelectDispositionFilter }) {
  if (!lots || !Array.isArray(lots) || lots.length === 0) {
    return null;
  }

  let totalParts = 0;
  let totalGreen = 0;
  let totalBurnIn = 0;
  let totalRed = 0;

  const familyStats = {};

  lots.forEach(lot => {
    const total = lot.total || 0;
    const green = lot.green || 0;
    const burnIn = lot.full_burn_in || 0;
    const red = lot.red || 0;
    const fam = lot.family || 'UNKNOWN';

    totalParts += total;
    totalGreen += green;
    totalBurnIn += burnIn;
    totalRed += red;

    if (!familyStats[fam]) {
      familyStats[fam] = { total: 0, green: 0, full_burn_in: 0, red: 0 };
    }
    familyStats[fam].total += total;
    familyStats[fam].green += green;
    familyStats[fam].full_burn_in += burnIn;
    familyStats[fam].red += red;
  });

  const routedFams = Object.keys(familyStats).filter(f => ROUTED_FAMILIES.includes(f));
  const capableFams = Object.keys(familyStats).filter(f => !ROUTED_FAMILIES.includes(f));

  const greenPct = totalParts > 0 ? (totalGreen / totalParts) * 100 : 0;
  const burnInPct = totalParts > 0 ? (totalBurnIn / totalParts) * 100 : 0;
  const redPct = totalParts > 0 ? (totalRed / totalParts) * 100 : 0;

  const handleToggle = (disp) => {
    if (onSelectDispositionFilter) {
      onSelectDispositionFilter(dispositionFilter === disp ? null : disp);
    }
  };

  return (
    <div style={{ padding: '8px 0', borderBottom: '1px solid #1e1e2e', display: 'flex', flexDirection: 'column', gap: '6px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '11px', letterSpacing: '1px', textTransform: 'uppercase' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ color: '#4ea1f0', fontWeight: 'bold' }}>FLEET STATUS</span>
          {dispositionFilter && (
            <span
              onClick={() => onSelectDispositionFilter(null)}
              style={{ fontSize: '9px', color: '#ffab00', border: '1px solid #ffab00', padding: '1px 4px', cursor: 'pointer' }}
            >
              [FILTER: {dispositionFilter} (CLEAR)]
            </span>
          )}
        </div>
        <span style={{ color: '#6b7280' }}>
          <span
            onClick={() => handleToggle('GREEN')}
            style={{
              color: '#00e676',
              cursor: 'pointer',
              textDecoration: dispositionFilter === 'GREEN' ? 'underline' : 'none',
              fontWeight: dispositionFilter === 'GREEN' ? 'bold' : 'normal'
            }}
          >
            {totalGreen} PASS
          </span> &nbsp;
          <span
            onClick={() => handleToggle('FULL_BURN_IN')}
            style={{
              color: '#ffab00',
              cursor: 'pointer',
              textDecoration: dispositionFilter === 'FULL_BURN_IN' ? 'underline' : 'none',
              fontWeight: dispositionFilter === 'FULL_BURN_IN' ? 'bold' : 'normal'
            }}
          >
            {totalBurnIn} BURN-IN
          </span> &nbsp;
          <span
            onClick={() => handleToggle('RED')}
            style={{
              color: '#ff1744',
              cursor: 'pointer',
              textDecoration: dispositionFilter === 'RED' ? 'underline' : 'none',
              fontWeight: dispositionFilter === 'RED' ? 'bold' : 'normal'
            }}
          >
            {totalRed} REJECT
          </span>
        </span>
      </div>

      {/* Thin 6px interactive stacked bar */}
      <div style={{ display: 'flex', height: '6px', width: '100%', background: '#1e1e2e', cursor: 'pointer' }}>
        <div
          onClick={() => handleToggle('GREEN')}
          style={{ width: `${greenPct}%`, backgroundColor: '#00e676', opacity: !dispositionFilter || dispositionFilter === 'GREEN' ? 1 : 0.3 }}
          title={`Click to filter PASS (${totalGreen})`}
        />
        <div
          onClick={() => handleToggle('FULL_BURN_IN')}
          style={{ width: `${burnInPct}%`, backgroundColor: '#ffab00', opacity: !dispositionFilter || dispositionFilter === 'FULL_BURN_IN' ? 1 : 0.3 }}
          title={`Click to filter BURN-IN (${totalBurnIn})`}
        />
        <div
          onClick={() => handleToggle('RED')}
          style={{ width: `${redPct}%`, backgroundColor: '#ff1744', opacity: !dispositionFilter || dispositionFilter === 'RED' ? 1 : 0.3 }}
          title={`Click to filter REJECT (${totalRed})`}
        />
      </div>

      {/* Summary lines */}
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#6b7280', flexWrap: 'wrap', gap: '8px', paddingTop: '2px' }}>
        <div>
          <strong style={{ color: '#ffab00' }}>ROUTED:</strong> {routedFams.join(' ')}
        </div>
        <div>
          <strong style={{ color: '#00e676' }}>CAPABLE:</strong> {capableFams.join(' ')}
        </div>
      </div>
    </div>
  );
}

