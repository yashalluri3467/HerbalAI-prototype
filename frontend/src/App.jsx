import React, { useState } from 'react';
import { Leaf, User, Heart, Sparkles, BookOpen, History } from 'lucide-react';
import SkinDiagnosis from './components/SkinDiagnosis';
import HerbEvaluator from './components/HerbEvaluator';
import KnowledgeBase from './components/KnowledgeBase';
import HistoryTrack from './components/HistoryTrack';

export default function App() {
  const [activeTab, setActiveTab] = useState('skin');
  const [history, setHistory] = useState([]);

  const handleAddHistory = (log) => {
    setHistory((prev) => [log, ...prev]);
  };

  const handleClearHistory = () => {
    setHistory([]);
  };

  return (
    <div className="app-container">
      {/* Premium Glassmorphic Header Nav */}
      <nav className="nav-bar">
        <div className="brand-container">
          <Leaf className="brand-logo" size={28} />
          <span className="brand-name">HerbalAI</span>
        </div>

        <div className="nav-tabs">
          <button 
            className={`tab-button ${activeTab === 'skin' ? 'active' : ''}`}
            onClick={() => setActiveTab('skin')}
          >
            <User size={16} />
            Skin Diagnosis
          </button>
          <button 
            className={`tab-button ${activeTab === 'herb' ? 'active' : ''}`}
            onClick={() => setActiveTab('herb')}
          >
            <Sparkles size={16} />
            Herb Evaluator
          </button>
          <button 
            className={`tab-button ${activeTab === 'kb' ? 'active' : ''}`}
            onClick={() => setActiveTab('kb')}
          >
            <BookOpen size={16} />
            Knowledge Base
          </button>
          <button 
            className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <History size={16} />
            Session History
            {history.length > 0 && (
              <span style={{ 
                background: 'rgba(255,255,255,0.2)', 
                color: '#fff', 
                fontSize: '0.65rem', 
                padding: '0.1rem 0.4rem', 
                borderRadius: '9999px',
                fontWeight: '700'
              }}>
                {history.length}
              </span>
            )}
          </button>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', opacity: 0.8 }}>
          <Heart size={16} style={{ color: 'var(--primary)' }} />
          <span style={{ fontSize: '0.8rem', fontWeight: '600', color: 'var(--text-secondary)' }}>
            Decision Support System
          </span>
        </div>
      </nav>

      {/* Main Dashboard Area */}
      <main className="main-content">
        {activeTab === 'skin' && <SkinDiagnosis onAddHistory={handleAddHistory} />}
        {activeTab === 'herb' && <HerbEvaluator onAddHistory={handleAddHistory} />}
        {activeTab === 'kb' && <KnowledgeBase />}
        {activeTab === 'history' && (
          <HistoryTrack history={history} onClearHistory={handleClearHistory} />
        )}
      </main>

      {/* Footer */}
      <footer style={{ 
        borderTop: '1px solid var(--border-light)', 
        padding: '1.5rem', 
        textAlign: 'center', 
        fontSize: '0.75rem', 
        color: 'var(--text-muted)',
        background: 'rgba(4, 8, 6, 0.9)'
      }}>
        © 2026 HerbalAI Skincare. Designed using Computer Vision + Ayurvedic Herbal Knowledge Graph. 
        <br />
        <span style={{ color: 'var(--primary)', marginTop: '0.25rem', display: 'inline-block' }}>
          Disclaimer: This system acts as an AI decision-support platform and does not replace professional clinical dermatology advice.
        </span>
      </footer>
    </div>
  );
}
