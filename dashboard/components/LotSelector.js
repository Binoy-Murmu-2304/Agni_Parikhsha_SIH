import React, { useState } from 'react';

const FAMILY_ABBR = {
  "DIGITAL_IC": "DIGITAL",
  "MIXED_SIGNAL_IC": "MIXED",
  "MEMS_GYROSCOPE": "MEMS",
  "PRECISION_VOLTAGE_REF": "PRECISION",
  "IMAGE_SENSOR": "IMAGE"
};

export default function LotSelector({ lots, selectedLotId, onSelectLot }) {
  const [filterText, setFilterText] = useState('');

  if (!lots || lots.length === 0) {
    return (
      <div style={{ padding: '8px 0', fontSize: '11px', color: '#6b7280' }}>
        LOADING LOT INVENTORY...
      </div>
    );
  }

  const filteredLots = filterText
    ? lots.filter(l => l.lot_id.toLowerCase().includes(filterText.toLowerCase()) || (l.family && l.family.toLowerCase().includes(filterText.toLowerCase())))
    : lots;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', width: '100%', padding: '6px 0', borderBottom: '1px solid #1e1e2e' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
        <span style={{ fontSize: '11px', color: '#6b7280', letterSpacing: '1px', textTransform: 'uppercase' }}>
          LOT INVENTORY ({lots.length} LOTS)
        </span>
        <input
          type="text"
          placeholder="FILTER..."
          value={filterText}
          onChange={(e) => setFilterText(e.target.value)}
          style={{
            padding: '2px 6px',
            background: '#0a0a0f',
            border: '1px solid #1e1e2e',
            color: '#c8ccd4',
            fontSize: '10px',
            width: '100px'
          }}
        />
      </div>

      {/* Horizontal scrollable row of 120px wide lot tiles */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          overflowX: 'auto',
          paddingBottom: '4px'
        }}
      >
        {/* ALL LOTS Button at Front */}
        <div
          onClick={() => onSelectLot('ALL')}
          style={{
            width: '130px',
            minWidth: '130px',
            flexShrink: 0,
            padding: '6px 8px',
            cursor: 'pointer',
            background: selectedLotId === 'ALL' ? '#1a1a24' : '#111118',
            border: selectedLotId === 'ALL' ? '2px solid #4ea1f0' : '1px solid #1e1e2e',
            display: 'flex',
            flexDirection: 'column',
            gap: '2px'
          }}
        >
          <div style={{ fontSize: '11px', fontWeight: 'bold', color: selectedLotId === 'ALL' ? '#4ea1f0' : '#c8ccd4', whiteSpace: 'nowrap' }}>
            [ALL LOTS]
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: selectedLotId === 'ALL' ? '#4ea1f0' : '#6b7280' }}>
            <span>FLEET-WIDE</span>
            <span>({lots.length} LOTS)</span>
          </div>
        </div>
        {filteredLots.map(lot => {
          const isSelected = lot.lot_id === selectedLotId;
          const total = lot.total || 0;
          const red = lot.red || 0;
          const burnIn = lot.full_burn_in || 0;
          const pass = lot.green || 0;
          const famAbbr = FAMILY_ABBR[lot.family] || lot.family || 'IC';

          // Split display: red / total or red / pass
          const splitText = `${red}/${total}`;

          return (
            <div
              key={lot.lot_id}
              onClick={() => onSelectLot(lot.lot_id)}
              style={{
                width: '120px',
                minWidth: '120px',
                flexShrink: 0,
                padding: '6px 8px',
                cursor: 'pointer',
                background: '#111118',
                border: '1px solid #1e1e2e',
                borderLeft: isSelected ? '2px solid #4ea1f0' : '1px solid #1e1e2e',
                display: 'flex',
                flexDirection: 'column',
                gap: '2px'
              }}
            >
              {/* Row 1: lot_id (11px) */}
              <div style={{ fontSize: '11px', fontWeight: 'bold', color: isSelected ? '#4ea1f0' : '#c8ccd4', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                [{lot.lot_id}]
              </div>

              {/* Row 2: family abbreviation + split */}
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: '#6b7280' }}>
                <span>{famAbbr}</span>
                <span style={{ color: red > 0 ? '#ff1744' : '#6b7280' }}>{splitText}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}


