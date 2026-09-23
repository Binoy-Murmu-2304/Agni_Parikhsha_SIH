import React, { useState, useEffect } from 'react';
import { Sun, Moon, Upload as UploadIcon, Settings } from 'lucide-react';
import './styles/theme.css';
import UploadView from './components/UploadView';
import GenerateView from './components/GenerateView';
import LotDashboard from './components/LotDashboard';
import PartDetail from './components/PartDetail';

function App() {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');
  const [currentView, setCurrentView] = useState('upload'); // 'upload', 'generate', 'dashboard', 'part'
  const [lotId, setLotId] = useState(null);
  const [selectedPart, setSelectedPart] = useState(null);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  const handleSuccess = (uploadedLotId) => {
    setLotId(uploadedLotId);
    setCurrentView('dashboard');
  };

  const handleSelectPart = (partId) => {
    setSelectedPart(partId);
    setCurrentView('part');
  };

  const handleBackToDashboard = () => {
    setSelectedPart(null);
    setCurrentView('dashboard');
  };
  
  const handleNav = (view) => {
    setLotId(null);
    setSelectedPart(null);
    setCurrentView(view);
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ padding: '1rem 2rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: 'var(--card-bg)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--primary)', cursor: 'pointer' }} onClick={() => handleNav('upload')}>
            AGNI-PARIKSHA
          </h1>
          
          <nav style={{ display: 'flex', gap: '1rem' }}>
            <button 
              onClick={() => handleNav('upload')} 
              style={{ background: 'transparent', border: 'none', color: currentView === 'upload' ? 'var(--primary)' : 'var(--muted)', fontWeight: currentView === 'upload' ? 'bold' : 'normal', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1rem' }}
            >
              <UploadIcon size={18} /> Upload CSV
            </button>
            <button 
              onClick={() => handleNav('generate')} 
              style={{ background: 'transparent', border: 'none', color: currentView === 'generate' ? 'var(--primary)' : 'var(--muted)', fontWeight: currentView === 'generate' ? 'bold' : 'normal', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1rem' }}
            >
              <Settings size={18} /> Generate Data
            </button>
          </nav>
        </div>
        
        <button onClick={toggleTheme} style={{ background: 'transparent', border: 'none', color: 'var(--text-color)', cursor: 'pointer' }}>
          {theme === 'light' ? <Moon size={24} /> : <Sun size={24} />}
        </button>
      </header>

      <main style={{ flex: 1, padding: '2rem', maxWidth: '1200px', margin: '0 auto', width: '100%', boxSizing: 'border-box' }}>
        {currentView === 'upload' && <UploadView onSuccess={handleSuccess} />}
        {currentView === 'generate' && <GenerateView onSuccess={handleSuccess} />}
        {currentView === 'dashboard' && <LotDashboard lotId={lotId} onSelectPart={handleSelectPart} />}
        {currentView === 'part' && <PartDetail partId={selectedPart} onBack={handleBackToDashboard} theme={theme} />}
      </main>
    </div>
  );
}

export default App;
