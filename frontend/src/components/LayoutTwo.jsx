import React, { useState } from 'react';
import { User, Sparkles, BookOpen, History, Sun, Flower2 } from 'lucide-react';
import SkinDiagnosis from './SkinDiagnosis';
import HerbEvaluator from './HerbEvaluator';
import KnowledgeBase from './KnowledgeBase';
import HistoryTrack from './HistoryTrack';
import SettingsPanel from './SettingsPanel';
import { useSettings } from '../SettingsContext';

/**
 * Layout Two – "Botanical Serenity"
 * Warm cream background, earthy green/brown tones, left sidebar navigation,
 * soft rounded cards, organic feel. Completely different from Layout One.
 */
const TABS = [
  { key: 'skin', label: 'Skin Diagnosis', icon: User },
  { key: 'herb', label: 'Herb Evaluator', icon: Sparkles },
  { key: 'kb', label: 'Knowledge Base', icon: BookOpen },
  { key: 'history', label: 'Session History', icon: History },
];

export default function LayoutTwo({ history, onAddHistory, onClearHistory }) {
  const [activeTab, setActiveTab] = useState('skin');
  const { settings } = useSettings();

  return (
    <div className="layout-two">
      {/* Left Sidebar */}
      <aside className="l2-sidebar">
        <div className="l2-brand">
          <div className="l2-brand-icon">
            <Flower2 size={32} />
          </div>
          <h1 className="l2-brand-title">HerbalAI</h1>
          <p className="l2-brand-subtitle">Ayurvedic Healing</p>
        </div>

        <nav className="l2-nav">
          {TABS.filter(({ key }) => key !== 'kb' || settings.knowledge_base_enabled).map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              className={`l2-nav-btn ${activeTab === key ? 'active' : ''}`}
              onClick={() => setActiveTab(key)}
            >
              <Icon size={18} />
              <span>{label}</span>
              {key === 'history' && history.length > 0 && (
                <span className="l2-badge">{history.length}</span>
              )}
            </button>
          ))}
        </nav>

        <div className="l2-sidebar-footer">
          <SettingsPanel />
        </div>
      </aside>

      {/* Main Area */}
      <div className="l2-main">
        {/* Top Bar */}
        <header className="l2-topbar">
          <div>
            <h2 className="l2-page-title">
              {TABS.find((t) => t.key === activeTab)?.label}
            </h2>
            <p className="l2-page-desc">
              Nature's wisdom meets modern AI diagnostics
            </p>
          </div>
          <div className="l2-topbar-right">
            <Sun size={18} />
            <span>Botanical Dashboard</span>
          </div>
        </header>

        {/* Content */}
        <main className="l2-content">
          {activeTab === 'skin' && <SkinDiagnosis onAddHistory={onAddHistory} />}
          {activeTab === 'herb' && <HerbEvaluator onAddHistory={onAddHistory} />}
          {activeTab === 'kb' && settings.knowledge_base_enabled && <KnowledgeBase />}
          {activeTab === 'history' && (
            <HistoryTrack history={history} onClearHistory={onClearHistory} />
          )}
        </main>

        {/* Footer */}
        <footer className="l2-footer">
          © 2026 HerbalAI Botanical Lab · AI-Powered Ayurvedic Analysis
        </footer>
      </div>
    </div>
  );
}
