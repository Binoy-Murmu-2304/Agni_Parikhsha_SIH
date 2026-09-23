import React, { useState, useEffect } from 'react';
import { Search, Filter, AlertTriangle, ShieldCheck, HelpCircle, Eye, EyeOff } from 'lucide-react';

const LotDashboard = ({ lotId, onSelectPart }) => {
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');
  const [search, setSearch] = useState('');
  const [showGroundTruth, setShowGroundTruth] = useState(false);
  const [hasGroundTruth, setHasGroundTruth] = useState(false);

  useEffect(() => {
    const fetchParts = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/lots/${lotId}/parts`);
        if (!response.ok) throw new Error('Failed to fetch parts');
        const data = await response.json();
        
        data.sort((a, b) => b.cri_score - a.cri_score);
        setParts(data);
        
        const hasGT = data.some(p => p.is_defective_gt !== null);
        setHasGroundTruth(hasGT);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (lotId) {
      fetchParts();
    }
  }, [lotId]);

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '3rem' }}>Loading lot data...</div>;
  }

  const filteredParts = parts.filter(p => {
    if (filter !== 'ALL' && p.verdict !== filter) return false;
    if (search && !p.part_id.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const getVerdictIcon = (verdict) => {
    switch(verdict) {
      case 'ACCEPT': return <ShieldCheck size={18} color="var(--success)" />;
      case 'REVIEW': return <HelpCircle size={18} color="var(--warning)" />;
      case 'REJECT': return <AlertTriangle size={18} color="var(--danger)" />;
      default: return null;
    }
  };

  const stats = {
    total: parts.length,
    accept: parts.filter(p => p.verdict === 'ACCEPT').length,
    review: parts.filter(p => p.verdict === 'REVIEW').length,
    reject: parts.filter(p => p.verdict === 'REJECT').length,
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h2 style={{ margin: '0 0 0.5rem 0' }}>Lot: {lotId}</h2>
          <p style={{ color: 'var(--muted)', margin: 0 }}>Showing {filteredParts.length} of {parts.length} parts</p>
        </div>
        
        <div style={{ display: 'flex', gap: '1rem' }}>
          <div className="card" style={{ padding: '0.5rem 1rem', display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: '80px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--muted)', textTransform: 'uppercase' }}>Accept</span>
            <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--success)' }}>{stats.accept}</span>
          </div>
          <div className="card" style={{ padding: '0.5rem 1rem', display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: '80px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--muted)', textTransform: 'uppercase' }}>Review</span>
            <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--warning)' }}>{stats.review}</span>
          </div>
          <div className="card" style={{ padding: '0.5rem 1rem', display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: '80px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--muted)', textTransform: 'uppercase' }}>Reject</span>
            <span style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'var(--danger)' }}>{stats.reject}</span>
          </div>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem', gap: '1rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', position: 'relative', width: '300px' }}>
            <Search size={18} style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--muted)' }} />
            <input 
              type="text" 
              placeholder="Search by Part ID..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{ width: '100%', padding: '0.5rem 0.5rem 0.5rem 2.5rem', borderRadius: '0.375rem', border: '1px solid var(--border-color)', background: 'var(--bg-color)', color: 'var(--text-color)' }}
            />
          </div>
          
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className={`btn ${filter === 'ALL' ? '' : 'inactive'}`} style={filter !== 'ALL' ? {backgroundColor: 'var(--bg-color)', color: 'var(--text-color)', border: '1px solid var(--border-color)'} : {}} onClick={() => setFilter('ALL')}>All</button>
            <button className={`btn ${filter === 'ACCEPT' ? '' : 'inactive'}`} style={filter !== 'ACCEPT' ? {backgroundColor: 'var(--bg-color)', color: 'var(--text-color)', border: '1px solid var(--border-color)'} : {}} onClick={() => setFilter('ACCEPT')}>Accept</button>
            <button className={`btn ${filter === 'REVIEW' ? '' : 'inactive'}`} style={filter !== 'REVIEW' ? {backgroundColor: 'var(--bg-color)', color: 'var(--text-color)', border: '1px solid var(--border-color)'} : {}} onClick={() => setFilter('REVIEW')}>Review</button>
            <button className={`btn ${filter === 'REJECT' ? '' : 'inactive'}`} style={filter !== 'REJECT' ? {backgroundColor: 'var(--bg-color)', color: 'var(--text-color)', border: '1px solid var(--border-color)'} : {}} onClick={() => setFilter('REJECT')}>Reject</button>
          </div>
          
          {hasGroundTruth && (
            <div style={{ marginLeft: 'auto' }}>
              <button 
                onClick={() => setShowGroundTruth(!showGroundTruth)}
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: showGroundTruth ? 'rgba(59, 130, 246, 0.1)' : 'transparent', border: '1px solid var(--primary)', color: 'var(--primary)', padding: '0.5rem 1rem', borderRadius: '0.375rem', cursor: 'pointer', fontWeight: '500' }}
              >
                {showGroundTruth ? <EyeOff size={18} /> : <Eye size={18} />}
                {showGroundTruth ? 'Hide Ground Truth' : 'Show Ground Truth'}
              </button>
            </div>
          )}
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Part ID</th>
                <th>Verdict</th>
                <th>CRI Score</th>
                <th>Anomaly (Mod A)</th>
                <th>Drift (Mod B)</th>
                <th>Key Parameter</th>
                {showGroundTruth && <th>Ground Truth</th>}
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredParts.length === 0 ? (
                <tr>
                  <td colSpan={showGroundTruth ? "8" : "7"} style={{ textAlign: 'center', padding: '2rem' }}>No parts found matching filters.</td>
                </tr>
              ) : (
                filteredParts.map(part => (
                  <tr key={part.id}>
                    <td style={{ fontWeight: '500' }}>{part.part_id}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {getVerdictIcon(part.verdict)}
                        <span className={`badge ${part.verdict.toLowerCase()}`}>{part.verdict}</span>
                      </div>
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ width: '60px', height: '6px', background: 'var(--chart-grid)', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ width: `${part.cri_score}%`, height: '100%', background: part.verdict === 'ACCEPT' ? 'var(--success)' : part.verdict === 'REVIEW' ? 'var(--warning)' : 'var(--danger)' }}></div>
                        </div>
                        <span style={{ fontWeight: '500' }}>{part.cri_score.toFixed(1)}</span>
                      </div>
                    </td>
                    <td>{(part.a_score * 100).toFixed(1)}%</td>
                    <td>{(part.d_score * 100).toFixed(1)}%</td>
                    <td style={{ color: 'var(--muted)' }}>{part.highest_attr_param}</td>
                    
                    {showGroundTruth && (
                      <td>
                        {part.is_defective_gt ? (
                          <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <span style={{ color: 'var(--danger)', fontWeight: 'bold', fontSize: '0.875rem' }}>DEFECTIVE</span>
                            <span style={{ color: 'var(--muted)', fontSize: '0.75rem' }}>{part.defect_type_gt.replace('_', ' ')}</span>
                          </div>
                        ) : (
                          <span style={{ color: 'var(--success)', fontWeight: 'bold', fontSize: '0.875rem' }}>HEALTHY</span>
                        )}
                      </td>
                    )}
                    
                    <td>
                      <button 
                        style={{ background: 'transparent', border: '1px solid var(--border-color)', borderRadius: '0.25rem', padding: '0.25rem 0.5rem', cursor: 'pointer', color: 'var(--text-color)' }}
                        onClick={() => onSelectPart(part.part_id)}
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default LotDashboard;
