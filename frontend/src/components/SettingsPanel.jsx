import React, { useEffect, useRef, useState } from 'react';
import { Settings, X } from 'lucide-react';
import { useSettings } from '../SettingsContext';
import { useTheme } from '../ThemeContext';

const TOGGLES = [
  ['knowledge_base_enabled', 'Knowledge base'],
  ['llm_suggestions_enabled', 'LLM suggestions'],
  ['image_enhancement_enabled', 'Image enhancement'],
];

export default function SettingsPanel() {
  const [open, setOpen] = useState(false);
  const panelRef = useRef(null);
  const { settings, saveSettings, loading, error } = useSettings();
  const { themeId, setThemeId, themes } = useTheme();

  useEffect(() => {
    if (!open) return undefined;
    const close = (event) => {
      if (panelRef.current && !panelRef.current.contains(event.target)) setOpen(false);
    };
    document.addEventListener('mousedown', close);
    return () => document.removeEventListener('mousedown', close);
  }, [open]);

  const toggle = (key) => {
    saveSettings({ ...settings, [key]: !settings[key] }).catch(() => {});
  };

  return (
    <div className="settings-control" ref={panelRef}>
      <button
        className="settings-button"
        type="button"
        aria-label="Open settings"
        title="Settings"
        onClick={() => setOpen((value) => !value)}
      >
        <Settings size={18} />
      </button>
      {open && (
        <div className="settings-panel">
          <div className="settings-header">
            <h2>Settings</h2>
            <button type="button" onClick={() => setOpen(false)} aria-label="Close settings">
              <X size={17} />
            </button>
          </div>

          <label className="settings-field">
            <span>Theme</span>
            <select value={themeId} onChange={(event) => setThemeId(event.target.value)}>
              {themes.map((theme) => (
                <option key={theme.id} value={theme.id}>{theme.label}</option>
              ))}
            </select>
          </label>

          <div className="settings-list">
            {TOGGLES.map(([key, label]) => (
              <label className="settings-toggle" key={key}>
                <span>{label}</span>
                <input
                  type="checkbox"
                  checked={settings[key]}
                  disabled={loading}
                  onChange={() => toggle(key)}
                />
                <span className="settings-switch" aria-hidden="true" />
              </label>
            ))}
          </div>
          {error && <p className="settings-error">{error}</p>}
        </div>
      )}
    </div>
  );
}
