import React, { useState } from 'react';
import { Settings, Play, Download, Plus, Trash2, Loader } from 'lucide-react';

const GenerateView = ({ onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [lotSize, setLotSize] = useState(50);
  const [partType, setPartType] = useState('SN74HC00');
  const [checkpoints, setCheckpoints] = useState('0, 24, 96, 168');
  const [prevalence, setPrevalence] = useState(2.0);
  const [seed, setSeed] = useState('');
  
  const [archetypes, setArchetypes] = useState({
    elevated_drift: true,
    shape_change: true,
    knee_defect: true
  });
  
  const [parameters, setParameters] = useState([
    { name: 'Iddq_uA', baseline: 10.0, spread: 0.5, limit: 15.0 }
  ]);

  const handleAddParam = () => {
    setParameters([...parameters, { name: 'New_Param', baseline: 5.0, spread: 0.2, limit: 10.0 }]);
  };

  const handleRemoveParam = (index) => {
    if (parameters.length > 1) {
      setParameters(parameters.filter((_, i) => i !== index));
    }
  };

  const updateParam = (index, field, value) => {
    const newParams = [...parameters];
    newParams[index][field] = value;
    setParameters(newParams);
  };

  const buildPayload = () => {
    const chkpts = checkpoints.split(',').map(s => parseFloat(s.trim())).filter(n => !isNaN(n));
    const archs = Object.keys(archetypes).filter(k => archetypes[k]);
    
    return {
      lot_size: parseInt(lotSize) || 20,
      part_type: partType,
      checkpoints: chkpts,
      parameters: parameters.map(p => ({
        name: p.name,
        baseline: parseFloat(p.baseline) || 0,
        spread: parseFloat(p.spread) || 0,
        limit: p.limit ? parseFloat(p.limit) : null
      })),
      defect_prevalence: parseFloat(prevalence) || 2.0,
      archetypes: archs,
      seed: seed ? parseInt(seed) : null
    };
  };

  const handleGenerate = async (downloadOnly = false) => {
    setLoading(true);
    setError('');
    
    try {
      const payload = buildPayload();
      
      if (downloadOnly) {
        const response = await fetch('http://localhost:8000/api/generate/csv', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        
        if (!response.ok) throw new Error("Failed to generate CSV");
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `synthetic_data_${Date.now()}.csv`;
        a.click();
      } else {
        const response = await fetch('http://localhost:8000/api/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Generation failed');
        
        onSuccess(data.lot_id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card" style={{ maxWidth: '800px', margin: '0 auto', marginTop: '2rem' }}>
      <h2 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Settings size={24} color="var(--primary)" />
        Synthetic Data Generator
      </h2>
      <p style={{ color: 'var(--muted)', marginBottom: '2rem' }}>
        Configure and generate a synthetic ESS dataset with known ground-truth defects.
      </p>

      {error && (
        <div style={{ padding: '1rem', marginBottom: '1.5rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', borderRadius: '0.375rem', border: '1px solid var(--danger)' }}>
          {error}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
        <div>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>Lot Size</label>
          <input 
            type="number" min="10" max="1000" 
            value={lotSize} onChange={e => setLotSize(e.target.value)}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-color)', boxSizing: 'border-box' }}
          />
        </div>
        <div>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>Part Type</label>
          <input 
            type="text" 
            value={partType} onChange={e => setPartType(e.target.value)}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-color)', boxSizing: 'border-box' }}
          />
        </div>
        <div style={{ gridColumn: '1 / -1' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>Checkpoints (comma-separated hours)</label>
          <input 
            type="text" 
            value={checkpoints} onChange={e => setCheckpoints(e.target.value)}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-color)', boxSizing: 'border-box' }}
          />
        </div>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ margin: 0 }}>Parameters</h3>
          <button onClick={handleAddParam} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', background: 'transparent', border: '1px solid var(--primary)', color: 'var(--primary)', padding: '0.25rem 0.5rem', borderRadius: '0.25rem', cursor: 'pointer', fontSize: '0.875rem' }}>
            <Plus size={16} /> Add Param
          </button>
        </div>
        
        {parameters.map((p, idx) => (
          <div key={idx} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end', marginBottom: '1rem', padding: '1rem', background: 'var(--bg-color)', borderRadius: '0.5rem', border: '1px solid var(--border-color)' }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Name</label>
              <input type="text" value={p.name} onChange={e => updateParam(idx, 'name', e.target.value)} style={{ width: '100%', padding: '0.5rem', borderRadius: '0.25rem', border: '1px solid var(--border-color)', background: 'var(--card-bg)', color: 'var(--text-color)' }} />
            </div>
            <div style={{ width: '80px' }}>
              <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Baseline</label>
              <input type="number" step="0.1" value={p.baseline} onChange={e => updateParam(idx, 'baseline', e.target.value)} style={{ width: '100%', padding: '0.5rem', borderRadius: '0.25rem', border: '1px solid var(--border-color)', background: 'var(--card-bg)', color: 'var(--text-color)' }} />
            </div>
            <div style={{ width: '80px' }}>
              <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Spread</label>
              <input type="number" step="0.1" value={p.spread} onChange={e => updateParam(idx, 'spread', e.target.value)} style={{ width: '100%', padding: '0.5rem', borderRadius: '0.25rem', border: '1px solid var(--border-color)', background: 'var(--card-bg)', color: 'var(--text-color)' }} />
            </div>
            <div style={{ width: '100px' }}>
              <label style={{ display: 'block', fontSize: '0.75rem', marginBottom: '0.25rem' }}>Limit (opt)</label>
              <input type="number" step="0.1" value={p.limit || ''} onChange={e => updateParam(idx, 'limit', e.target.value)} style={{ width: '100%', padding: '0.5rem', borderRadius: '0.25rem', border: '1px solid var(--border-color)', background: 'var(--card-bg)', color: 'var(--text-color)' }} />
            </div>
            {parameters.length > 1 && (
              <button onClick={() => handleRemoveParam(idx)} style={{ padding: '0.5rem', background: 'transparent', border: 'none', color: 'var(--danger)', cursor: 'pointer' }}>
                <Trash2 size={20} />
              </button>
            )}
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
        <div>
          <h3 style={{ margin: '0 0 1rem 0' }}>Defect Profile</h3>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>Prevalence (%)</label>
            <input 
              type="number" step="0.1" 
              value={prevalence} onChange={e => setPrevalence(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-color)', boxSizing: 'border-box' }}
            />
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={archetypes.elevated_drift} onChange={e => setArchetypes({...archetypes, elevated_drift: e.target.checked})} />
              Elevated Drift
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={archetypes.shape_change} onChange={e => setArchetypes({...archetypes, shape_change: e.target.checked})} />
              Shape Change (Exponent)
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={archetypes.knee_defect} onChange={e => setArchetypes({...archetypes, knee_defect: e.target.checked})} />
              Knee Defect (Accelerated)
            </label>
          </div>
        </div>
        
        <div>
          <h3 style={{ margin: '0 0 1rem 0' }}>Reproducibility</h3>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem' }}>Random Seed (Optional)</label>
          <input 
            type="number" 
            value={seed} onChange={e => setSeed(e.target.value)} placeholder="e.g. 42"
            style={{ width: '100%', padding: '0.5rem', borderRadius: '0.375rem', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-color)', boxSizing: 'border-box' }}
          />
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border-color)', paddingTop: '1.5rem' }}>
        <button 
          className="btn" 
          disabled={loading} 
          onClick={() => handleGenerate(true)}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'transparent', color: 'var(--text-color)', border: '1px solid var(--border-color)', opacity: loading ? 0.5 : 1 }}
        >
          <Download size={18} /> Download as CSV
        </button>
        
        <button 
          className="btn" 
          disabled={loading} 
          onClick={() => handleGenerate(false)}
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', opacity: loading ? 0.5 : 1 }}
        >
          {loading ? <Loader className="spin" size={18} /> : <Play size={18} />}
          {loading ? 'Processing...' : 'Generate & Analyze'}
        </button>
      </div>
    </div>
  );
};

export default GenerateView;
