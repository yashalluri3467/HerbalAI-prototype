import React, { useState } from 'react';
import { Leaf, User, Sparkles, BookOpen, History, Heart } from 'lucide-react';
import SkinDiagnosis from './SkinDiagnosis';
import HerbEvaluator from './HerbEvaluator';
import KnowledgeBase from './KnowledgeBase';
import HistoryTrack from './HistoryTrack';
import SettingsPanel from './SettingsPanel';
import { useSettings } from '../SettingsContext';

/**
 * Layout One – "Obsidian Cyber"
 * Original floating pill nav, dark glassmorphic, cyan holographic accents.
 * Keeps existing design exactly.
 */
export default function LayoutOne({ history, onAddHistory, onClearHistory }) {
  const [activeTab, setActiveTab] = useState('skin');
  const { settings } = useSettings();

  return (
    <div className="layout-one">
      {/* Premium Glassmorphic Floating Pill Nav */}
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
          {settings.knowledge_base_enabled && <button
            className={`tab-button ${activeTab === 'kb' ? 'active' : ''}`}
            onClick={() => setActiveTab('kb')}
          >
            <BookOpen size={16} />
            Knowledge Base
          </button>}
          <button
            className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <History size={16} />
            Session History
            {history.length > 0 && (
              <span className="history-badge">{history.length}</span>
            )}
          </button>
        </div>

        <div className="nav-right">
          <SettingsPanel />
          <div className="nav-subtitle">
            <Heart size={14} />
            <span>Decision Support System</span>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {activeTab === 'skin' && <SkinDiagnosis onAddHistory={onAddHistory} />}
        {activeTab === 'herb' && <HerbEvaluator onAddHistory={onAddHistory} />}
        {activeTab === 'kb' && settings.knowledge_base_enabled && <KnowledgeBase />}
        {activeTab === 'history' && (
          <HistoryTrack history={history} onClearHistory={onClearHistory} />
        )}
      </main>

      {/* Footer */}
      <footer className="layout-footer">
        © 2026 HerbalAI Skincare. Computer Vision + Ayurvedic Knowledge Graph.
        <br />
        <span className="footer-disclaimer">
          Disclaimer: AI decision-support only — does not replace clinical advice.
        </span>
      </footer>
    </div>
  );
}
