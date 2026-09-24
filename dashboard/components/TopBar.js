import React from 'react';

export default function TopBar({ activeTab, setActiveTab, commitHash = "c86c4b28" }) {
  return (
    <header className="top-bar">
      <div className="brand-section">
        <span className="brand-title">AGNI PARIKSHA :: ESS ANOMALY SCREENING</span>
        <div className="sys-status">
          <span className="sys-dot"></span>
          SYS: NOMINAL
        </div>
        <span className="commit-hash">[{commitHash.substring(0, 8)}]</span>
      </div>

      <nav className="nav-tabs">
        <button
          className={`tab-link ${activeTab === 'triage' ? 'active' : ''}`}
          onClick={() => setActiveTab('triage')}
        >
          TRIAGE BOARD
        </button>
        <span className="tab-separator">|</span>
        <button
          className={`tab-link ${activeTab === 'results' ? 'active' : ''}`}
          onClick={() => setActiveTab('results')}
        >
          RESULTS & METRICS
        </button>
      </nav>
    </header>
  );
}

