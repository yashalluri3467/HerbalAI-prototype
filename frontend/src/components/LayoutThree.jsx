import React, { useState } from 'react';
import { User, Sparkles, BookOpen, History, Zap } from 'lucide-react';
import SkinDiagnosis from './SkinDiagnosis';
import HerbEvaluator from './HerbEvaluator';
import KnowledgeBase from './KnowledgeBase';
import HistoryTrack from './HistoryTrack';
import SettingsPanel from './SettingsPanel';
import { useSettings } from '../SettingsContext';

/**
 * Layout Three – "Aurora Gradient"
 * Vibrant purple-pink-blue gradients, dark background, neon glow effects,
 * bottom tab bar (mobile-inspired), fullscreen card panels.
 */
const TABS = [
  { key: 'skin', label: 'Diagnosis', icon: User },
  { key: 'herb', label: 'Evaluator', icon: Sparkles },
  { key: 'kb', label: 'Knowledge', icon: BookOpen },
  { key: 'history', label: 'History', icon: History },
];

export default function LayoutThree({ history, onAddHistory, onClearHistory }) {
  const [activeTab, setActiveTab] = useState('skin');
  const { settings } = useSettings();

  return (
    <div className="layout-three">
      {/* Top gradient header */}
      <header className="l3-header">
        <div className="l3-header-bg" />
        <div className="l3-header-content">
          <div className="l3-brand">
            <Zap size={24} className="l3-brand-icon" />
            <span className="l3-brand-name">HerbalAI</span>
            <span className="l3-brand-tag">AURORA</span>
          </div>
          <SettingsPanel />
        </div>
      </header>

      {/* Main Content Panel */}
      <main className="l3-content">
        <div className="l3-panel">
          {activeTab === 'skin' && <SkinDiagnosis onAddHistory={onAddHistory} />}
          {activeTab === 'herb' && <HerbEvaluator onAddHistory={onAddHistory} />}
          {activeTab === 'kb' && settings.knowledge_base_enabled && <KnowledgeBase />}
          {activeTab === 'history' && (
            <HistoryTrack history={history} onClearHistory={onClearHistory} />
          )}
        </div>
      </main>

      {/* Bottom Tab Bar */}
      <nav className="l3-bottom-bar">
        {TABS.filter(({ key }) => key !== 'kb' || settings.knowledge_base_enabled).map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            className={`l3-tab ${activeTab === key ? 'active' : ''}`}
            onClick={() => setActiveTab(key)}
          >
            <Icon size={20} />
            <span className="l3-tab-label">{label}</span>
            {key === 'history' && history.length > 0 && (
              <span className="l3-notif">{history.length}</span>
            )}
          </button>
        ))}
      </nav>
    </div>
  );
}
