import React from 'react';

export default function DriftChart({ 
  family = "DIGITAL_IC", 
  val_0h = null, 
  val_24h = null, 
  pred_168h = null, 
  conformal_radius = null,
  measured_slope = null,
  spec_max = null,
  unit = null
}) {
  const chartUnit = unit || "µA";
  const chartSpecMax = spec_max !== null && spec_max !== undefined ? spec_max : 50.0;

  let v0 = val_0h;
  if (v0 === null || v0 === undefined) {
    if (val_24h !== null && measured_slope !== null) {
      v0 = val_24h - (24 * measured_slope);
    } else if (val_24h !== null) {
      v0 = val_24h * 0.9;
    }
  }

  const v24 = val_24h !== null ? val_24h : 0.0;
  const v168 = pred_168h !== null ? pred_168h : v24;
  const conf = conformal_radius !== null ? conformal_radius : 0.0;

  // Dimensions
  const width = 360;
  const height = 180;
  const paddingLeft = 45;
  const paddingRight = 20;
  const paddingTop = 20;
  const paddingBottom = 30;

  const chartW = width - paddingLeft - paddingRight;
  const chartH = height - paddingTop - paddingBottom;

  const getX = (t) => paddingLeft + (t / 168) * chartW;

  const x0 = getX(0);
  const x24 = getX(24);
  const x168 = getX(168);

  // Y mapping values -> Y pixels
  const allY = [0, v0 || 0, v24, v168 + conf, chartSpecMax * 1.15];
  const maxY = Math.max(...allY, chartSpecMax * 1.1);
  const minY = Math.min(0, Math.min(...allY));

  const getY = (val) => {
    if (maxY === minY) return paddingTop + chartH / 2;
    return paddingTop + chartH - ((val - minY) / (maxY - minY)) * chartH;
  };

  const y0 = getY(v0 || 0);
  const y24 = getY(v24);
  const y168 = getY(v168);
  const yConfUpper = getY(v168 + conf);
  const yConfLower = getY(Math.max(0, v168 - conf));
  const ySpec = getY(chartSpecMax);

  const breachesSpec = (v168 + conf) > chartSpecMax;

  const linePath = `M ${x0} ${y0} L ${x24} ${y24} L ${x168} ${y168}`;

  return (
    <div style={{ background: '#0a0a0f', border: '1px solid #1e1e2e', padding: '10px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontSize: '11px', color: '#6b7280' }}>
        <span>DRIFT TRAJECTORY</span>
        <span style={{ color: '#ff1744' }}>SPEC MAX: {chartSpecMax} {chartUnit}</span>
      </div>

      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`}>
        {/* Spec Max Dashed Red Line */}
        <line x1={paddingLeft} y1={ySpec} x2={paddingLeft + chartW} y2={ySpec} stroke="#ff1744" strokeWidth="1" strokeDasharray="4,4" />
        <text x={paddingLeft + chartW - 2} y={ySpec - 4} fill="#ff1744" fontSize="10" textAnchor="end">
          LIMIT
        </text>

        {/* 1px Dashed Conformal Bounds above/below forecast point (no filled region) */}
        {conf > 0 && (
          <g>
            <line x1={x24} y1={y24} x2={x168} y2={yConfUpper} stroke="#4ea1f0" strokeWidth="1" strokeDasharray="2,2" />
            <line x1={x24} y1={y24} x2={x168} y2={yConfLower} stroke="#4ea1f0" strokeWidth="1" strokeDasharray="2,2" />
            <text x={x168 + 4} y={yConfUpper + 3} fill="#6b7280" fontSize="9">
              +/{conf.toFixed(2)} {chartUnit}
            </text>
          </g>
        )}

        {/* Flat 1px Forecast Line */}
        <path d={linePath} fill="none" stroke="#4ea1f0" strokeWidth="1" />

        {/* 0h Data Point (Square) */}
        <rect x={x0 - 3} y={y0 - 3} width="6" height="6" fill="#00e676" />
        <text x={x0} y={y0 - 6} fill="#00e676" fontSize="10" textAnchor="middle">
          {v0 !== null ? v0.toFixed(2) : "0"}
        </text>

        {/* 24h Data Point (Square) */}
        <rect x={x24 - 3} y={y24 - 3} width="6" height="6" fill="#ffab00" />
        <text x={x24} y={y24 - 6} fill="#ffab00" fontSize="10" textAnchor="middle">
          {v24.toFixed(2)}
        </text>

        {/* 168h Forecast Point (Square) */}
        <rect x={x168 - 3.5} y={y168 - 3.5} width="7" height="7" fill={breachesSpec ? "#ff1744" : "#4ea1f0"} />
        <text x={x168 - 6} y={y168 - 6} fill={breachesSpec ? "#ff1744" : "#4ea1f0"} fontSize="10" textAnchor="end">
          {v168.toFixed(2)} {chartUnit}
        </text>

        {/* X Axis & Labels */}
        <line x1={paddingLeft} y1={paddingTop + chartH} x2={paddingLeft + chartW} y2={paddingTop + chartH} stroke="#1e1e2e" strokeWidth="1" />
        <text x={x0} y={paddingTop + chartH + 14} fill="#6b7280" fontSize="10" textAnchor="middle">0h</text>
        <text x={x24} y={paddingTop + chartH + 14} fill="#6b7280" fontSize="10" textAnchor="middle">24h</text>
        <text x={x168} y={paddingTop + chartH + 14} fill="#6b7280" fontSize="10" textAnchor="end">168h</text>
      </svg>
    </div>
  );
}

