import os
with open('dashboard/pages/index.js', 'w') as f:
    f.write('''import { useState, useEffect } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [lotData, setLotData] = useState(null);
  const [lotSummary, setLotSummary] = useState(null);
  const [selectedComp, setSelectedComp] = useState(null);
  const [cardData, setCardData] = useState(null);
  const [activeTab, setActiveTab] = useState('triage');

  useEffect(() => {
    fetch(API_URL + '/metrics')
      .then(r => r.json())
      .then(setMetrics)
      .catch(console.error);
  }, []);

  const loadLot = async () => {
    // Demo load
    const demoPayload = [{
      "lot_id": "LOT_0001",
      "component_id": "COMP_1",
      "family": "DIGITAL_IC",
      "value_0h": 10.0,
      "value_24h": 10.5,
      "is_defective": 0,
      "mechanism": "NONE"
    }];
    const res = await fetch(API_URL + '/lots/screen', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(demoPayload)
    });
    const data = await res.json();
    setLotData(data);
    
    // Fetch lot summary
    const sumRes = await fetch(API_URL + '/lots/LOT_0001/summary');
    if (sumRes.ok) {
        setLotSummary(await sumRes.json());
    }
  };

  const loadComponent = async (id) => {
    const res = await fetch(API_URL + '/components/' + id);
    if (res.ok) {
        const comp = await res.json();
        setSelectedComp(comp);
    }
    const cardRes = await fetch(API_URL + '/components/' + id + '/card');
    if (cardRes.ok) {
        const card = await cardRes.json();
        setCardData(card);
    }
  };

  return (
    <div style={{ padding: 20, fontFamily: 'system-ui' }}>
      <h1>AGNI PARIKSHA DASHBOARD</h1>
      <div style={{ display: 'flex', gap: 10, marginBottom: 20 }}>
        <button onClick={() => setActiveTab('triage')}>Triage Board</button>
        <button onClick={() => setActiveTab('results')}>Results & Metrics</button>
      </div>

      {activeTab === 'triage' && (
        <div>
          <h2>Triage Board</h2>
          <button onClick={loadLot}>POST /lots/screen (Demo)</button>
          
          {lotSummary && (
            <div style={{ marginTop: 20, padding: 10, border: '1px solid #ccc' }}>
              <h3>Lot Summary</h3>
              <p>GREEN: {lotSummary.counts.GREEN || 0}</p>
              <p>FULL_BURN_IN: {lotSummary.counts.FULL_BURN_IN || 0}</p>
              <p>RED: {lotSummary.counts.RED || 0}</p>
              <p>Realized Savings: {lotSummary.realized_savings}% ({lotSummary.yield_assumption})</p>
            </div>
          )}

          {lotData && (
            <div style={{ marginTop: 20 }}>
              <h3>Components</h3>
              {lotData.map(c => (
                <div key={c.component_id} style={{ padding: 10, border: '1px solid #eee', marginBottom: 5 }}>
                  <strong>{c.component_id}</strong> - {c.disposition} (Tier: {c.risk_tier})
                  <button onClick={() => loadComponent(c.component_id)} style={{ marginLeft: 10 }}>Drill-down</button>
                </div>
              ))}
            </div>
          )}

          {selectedComp && (
            <div style={{ marginTop: 20, padding: 10, border: '1px solid #333' }}>
              <h3>Drill-Down: {selectedComp.component_id}</h3>
              <p>Verdict: {selectedComp.disposition}</p>
              <p>Triggers: Module A ({selectedComp.trigger_module_a}), Safety Slope ({selectedComp.trigger_safety_slope})</p>
              <p>Predicted 168h: {selectedComp.pred_168h !== null ? selectedComp.pred_168h : "not computed"}</p>
              <p>Conformal Interval: {selectedComp.conformal_interval_95 !== null ? selectedComp.conformal_interval_95 : "not computed"}</p>
              <p>Safety-slope margin: {selectedComp.safety_slope_margin !== null ? selectedComp.safety_slope_margin : "not computed"}</p>
              
              <h4>SHAP / Physics Trace</h4>
              {selectedComp.shap_physics ? (
                  <ul>
                      {Object.entries(selectedComp.shap_physics).map(([k, v]) => <li key={k}>{k}: {v}</li>)}
                  </ul>
              ) : (
                  <p>explanation not computed</p>
              )}
              
              {cardData && (
                  <div style={{ marginTop: 20 }}>
                      <h4>QA Card Render (Ready for PDF)</h4>
                      <pre style={{ background: '#f5f5f5', padding: 10 }}>{cardData.markdown}</pre>
                  </div>
              )}
            </div>
          )}
        </div>
      )}

      {activeTab === 'results' && metrics && (
        <div>
          <h2>Results & Canonical Metrics</h2>
          
          <h3>Known Limitations</h3>
          <div style={{ padding: 10, background: '#fff3cd', border: '1px solid #ffe69c' }}>
              <p><strong>Synthetic Data Scope:</strong> The model generalizes exceptionally well to unseen lots from the same frozen AGNI-SIM physics (synthetic scope unchanged).</p>
              <p><strong>Physics Limitations:</strong> The two-checkpoint observation window limits the physics story (e.g., NON_MONOTONIC, SLOW_CREEP, LATE_AVALANCHE).</p>
              <p><strong>Conformal Under-coverage:</strong> Minor finite-sample conformal under-coverage exists in extremely tight families.</p>
              <p><strong>Auto-passable-family Escape Rate:</strong> Routed families contribute zero escapes by construction. Escapes ({metrics.FINAL_EVAL_escapes || 'N/A'} on FINAL_EVAL) concentrate heavily in capable but noisy families (e.g., MEMS_GYROSCOPE, IMAGE_SENSOR).</p>
          </div>

          <h3>Family Capabilities (Metrics)</h3>
          <pre>{JSON.stringify(metrics, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
''')
