import React, { useState, useEffect } from 'react';
import { ArrowLeft, Download, AlertTriangle, ShieldCheck, HelpCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const PartDetail = ({ partId, onBack, theme }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPartDetails = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/parts/${partId}`);
        if (!response.ok) throw new Error('Failed to fetch part details');
        const result = await response.json();
        setData(result);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (partId) {
      fetchPartDetails();
    }
  }, [partId]);

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '3rem' }}>Loading part details...</div>;
  }

  if (!data || !data.result) {
    return <div style={{ textAlign: 'center', padding: '3rem' }}>Failed to load part data.</div>;
  }

  const { result, readings } = data;

  // Prepare chart data
  const chartData = [];
  const param = result.highest_attr_param || "Unknown";
  
  const paramReadings = readings.filter(r => r.parameter_name === param).sort((a, b) => a.timepoint_hours - b.timepoint_hours);
  paramReadings.forEach(r => {
    chartData.push({
      time: r.timepoint_hours,
      value: r.value
    });
  });

  const getVerdictIcon = (verdict) => {
    switch(verdict) {
      case 'ACCEPT': return <ShieldCheck size={24} color="var(--success)" />;
      case 'REVIEW': return <HelpCircle size={24} color="var(--warning)" />;
      case 'REJECT': return <AlertTriangle size={24} color="var(--danger)" />;
      default: return null;
    }
  };

  const handleDownloadPDF = () => {
    window.open(`http://localhost:8000/api/parts/${partId}/certificate`, '_blank');
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
        <button 
          onClick={onBack}
          style={{ background: 'transparent', border: '1px solid var(--border-color)', borderRadius: '0.375rem', padding: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: 'var(--text-color)' }}
        >
          <ArrowLeft size={20} />
        </button>
        <div>
          <h2 style={{ margin: '0 0 0.25rem 0' }}>Part Details: {partId}</h2>
          <p style={{ color: 'var(--muted)', margin: 0 }}>Lot: {result.lot_id}</p>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '1rem' }}>
          {result.verdict !== 'ACCEPT' && (
            <button className="btn" onClick={handleDownloadPDF} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', backgroundColor: 'var(--card-bg)', color: 'var(--text-color)', border: '1px solid var(--border-color)' }}>
              <Download size={18} />
              Download Certificate
            </button>
          )}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
        {/* Left Column: Stats */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', padding: '2rem' }}>
            {getVerdictIcon(result.verdict)}
            <div>
              <h3 style={{ margin: '0 0 0.25rem 0', color: 'var(--muted)', fontSize: '0.875rem', textTransform: 'uppercase' }}>Verdict</h3>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: result.verdict === 'ACCEPT' ? 'var(--success)' : result.verdict === 'REVIEW' ? 'var(--warning)' : 'var(--danger)' }}>
                {result.verdict}
              </div>
            </div>
          </div>

          <div className="card">
            <h3 style={{ marginTop: 0, marginBottom: '1.5rem' }}>CRI Breakdown</h3>
            
            <div style={{ marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                <span style={{ fontWeight: '500' }}>Overall CRI Score</span>
                <span style={{ fontWeight: 'bold' }}>{result.cri_score.toFixed(1)} / 100</span>
              </div>
              <div style={{ width: '100%', height: '8px', background: 'var(--chart-grid)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: `${result.cri_score}%`, height: '100%', background: result.verdict === 'ACCEPT' ? 'var(--success)' : result.verdict === 'REVIEW' ? 'var(--warning)' : 'var(--danger)' }}></div>
              </div>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                <span style={{ color: 'var(--muted)' }}>Module A: Anomaly Evidence</span>
                <span>{(result.a_score * 100).toFixed(1)}%</span>
              </div>
              <div style={{ width: '100%', height: '4px', background: 'var(--chart-grid)', borderRadius: '2px', overflow: 'hidden' }}>
                <div style={{ width: `${result.a_score * 100}%`, height: '100%', background: 'var(--primary)' }}></div>
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
                <span style={{ color: 'var(--muted)' }}>Module B: Drift Evidence</span>
                <span>{(result.d_score * 100).toFixed(1)}%</span>
              </div>
              <div style={{ width: '100%', height: '4px', background: 'var(--chart-grid)', borderRadius: '2px', overflow: 'hidden' }}>
                <div style={{ width: `${result.d_score * 100}%`, height: '100%', background: 'var(--primary)' }}></div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 style={{ marginTop: 0, marginBottom: '1rem' }}>Key Attributions</h3>
            <p style={{ margin: '0 0 1rem 0', fontSize: '0.875rem', color: 'var(--muted)' }}>Parameters contributing most to the anomaly score (Mahalanobis Distance).</p>
            
            <div style={{ padding: '0.75rem', background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.2)', borderRadius: '0.375rem', display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ fontWeight: '500' }}>1. {result.highest_attr_param}</span>
              <span style={{ color: 'var(--primary)', fontWeight: '500' }}>Primary Driver</span>
            </div>
          </div>
        </div>

        {/* Right Column: Chart */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ marginTop: 0, marginBottom: '0.5rem' }}>Trajectory vs Lot</h3>
          <p style={{ margin: '0 0 2rem 0', fontSize: '0.875rem', color: 'var(--muted)' }}>Displaying parameter: <strong>{param}</strong></p>
          
          <div style={{ flex: 1, minHeight: '400px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={theme === 'dark' ? '#374151' : '#e5e7eb'} vertical={false} />
                <XAxis 
                  dataKey="time" 
                  stroke={theme === 'dark' ? '#9ca3af' : '#6b7280'}
                  label={{ value: 'Timepoint (Hours)', position: 'insideBottom', offset: -10, fill: theme === 'dark' ? '#9ca3af' : '#6b7280' }}
                />
                <YAxis 
                  stroke={theme === 'dark' ? '#9ca3af' : '#6b7280'}
                  label={{ value: 'Value', angle: -90, position: 'insideLeft', fill: theme === 'dark' ? '#9ca3af' : '#6b7280' }}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--card-bg)', borderColor: 'var(--border-color)', color: 'var(--text-color)' }}
                  itemStyle={{ color: 'var(--text-color)' }}
                />
                <Legend verticalAlign="top" height={36}/>
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  name="This Part" 
                  stroke="var(--danger)" 
                  strokeWidth={3}
                  activeDot={{ r: 8 }} 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PartDetail;
