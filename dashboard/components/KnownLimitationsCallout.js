import React from 'react';

export default function KnownLimitationsCallout({ metrics }) {
  const escapes = metrics ? (metrics.FINAL_EVAL_escapes !== undefined ? metrics.FINAL_EVAL_escapes : '98') : '98';

  return (
    <div style={{ borderTop: '1px solid #ffab00', borderBottom: '1px solid #ffab00', padding: '10px 0', margin: '8px 0', fontSize: '11px', color: '#c8ccd4' }}>
      <div style={{ fontWeight: 'bold', color: '#ffab00', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '6px' }}>
        KNOWN LIMITATIONS
      </div>

      <ul style={{ listStyleType: 'disc', paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '4px', color: '#c8ccd4' }}>
        <li>Synthetic data scope: model generalizes within AGNI-SIM physics</li>
        <li>Two-checkpoint window limits mechanism discrimination</li>
        <li>Minor conformal under-coverage in tight families</li>
        <li>Auto-passable escape rate: 27.53% [22.95–32.48%] ({escapes} escapes on FINAL_EVAL)</li>
        <li>Conformal trigger excluded from final_flag (design decision)</li>
      </ul>
    </div>
  );
}

