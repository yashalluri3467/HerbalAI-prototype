import React, { useState } from 'react';
import { User, Sparkles, BookOpen, History, Activity } from 'lucide-react';
import SkinDiagnosis from './SkinDiagnosis';
import HerbEvaluator from './HerbEvaluator';
import KnowledgeBase from './KnowledgeBase';
import HistoryTrack from './HistoryTrack';
import SettingsPanel from './SettingsPanel';
import { useSettings } from '../SettingsContext';

/**
 * Layout Four – "Clinical Minimal"
 * Clean white background, blue accents, sharp geometric layout,
 * top horizontal breadcrumb-style tabs, professional medical feel.
 */
const TABS = [
  { key: 'skin', label: 'Skin Diagnosis', icon: User },
  { key: 'herb', label: 'Herb Evaluator', icon: Sparkles },
  { key: 'kb', label: 'Knowledge Base', icon: BookOpen },
  { key: 'history', label: 'Session History', icon: History },
];

export default function LayoutFour({ history, onAddHistory, onClearHistory }) {
  const [activeTab, setActiveTab] = useState('skin');
  const { settings } = useSettings();

  return (
    <div className="layout-four">
      {/* Minimal Top Bar */}
      <header className="l4-header">
        <div className="l4-header-left">
          <div className="l4-logo">
            <Activity size={22} />
            <span className="l4-logo-text">HerbalAI</span>
            <span className="l4-logo-badge">Clinical</span>
          </div>
        </div>

        {/* Horizontal breadcrumb tabs */}
        <nav className="l4-tabs">
          {TABS.filter(({ key }) => key !== 'kb' || settings.knowledge_base_enabled).map(({ key, label, icon: Icon }, i) => (
            <React.Fragment key={key}>
              {i > 0 && <span className="l4-tab-divider">/</span>}
              <button
                className={`l4-tab-btn ${activeTab === key ? 'active' : ''}`}
                onClick={() => setActiveTab(key)}
              >
                <Icon size={14} />
                {label}
                {key === 'history' && history.length > 0 && (
                  <span className="l4-count">{history.length}</span>
                )}
              </button>
            </React.Fragment>
          ))}
        </nav>

        <div className="l4-header-right">
          <SettingsPanel />
        </div>
      </header>

      {/* Section title bar */}
      <div className="l4-section-bar">
        <h2 className="l4-section-title">
          {TABS.find((t) => t.key === activeTab)?.label}
        </h2>
        <p className="l4-section-desc">
          Evidence-based herbal diagnostics powered by artificial intelligence
        </p>
      </div>

      {/* Main Content */}
      <main className="l4-content">
        {activeTab === 'skin' && <SkinDiagnosis onAddHistory={onAddHistory} />}
        {activeTab === 'herb' && <HerbEvaluator onAddHistory={onAddHistory} />}
        {activeTab === 'kb' && settings.knowledge_base_enabled && <KnowledgeBase />}
        {activeTab === 'history' && (
          <HistoryTrack history={history} onClearHistory={onClearHistory} />
        )}
      </main>

      {/* Footer */}
      <footer className="l4-footer">
        <div className="l4-footer-line" />
        <p>© 2026 HerbalAI Clinical — Precision Ayurvedic Intelligence</p>
      </footer>
    </div>
  );
}
