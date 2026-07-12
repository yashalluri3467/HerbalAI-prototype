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
  const [openUpward, setOpenUpward] = useState(true);
  const [panelPosition, setPanelPosition] = useState({ top: 0, left: 0 });
  const controlRef = useRef(null);
  const panelRef = useRef(null);
  const buttonRef = useRef(null);
  const { settings, saveSettings, loading, error } = useSettings();
  const { themeId, setThemeId, themes } = useTheme();

  useEffect(() => {
    if (!open) return undefined;
    
    // Calculate panel position based on button position
    const calculatePosition = () => {
      if (buttonRef.current) {
        const rect = buttonRef.current.getBoundingClientRect();
        const panelHeight = 300; // approximate height
        const panelWidth = 320;
        const minLeftPosition = 280; // sidebar is ~260px, so panel should start after that
        
        // Determine vertical position
        const spaceAbove = rect.top;
        const spaceBelow = window.innerHeight - rect.bottom;
        const openUp = spaceAbove > panelHeight;
        setOpenUpward(openUp);
        
        // Position panel to the right, ensuring it's in the main content area
        let left = Math.max(minLeftPosition, rect.right + 10);
        let top = openUp ? rect.top - panelHeight : rect.bottom + 10;
        
        // Ensure it doesn't go off-screen to the right
        if (left + panelWidth > window.innerWidth) {
          left = window.innerWidth - panelWidth - 10;
        }
        
        // Ensure top is within bounds
        if (top < 10) {
          top = 10;
        }
        if (top + panelHeight > window.innerHeight) {
          top = window.innerHeight - panelHeight - 10;
        }
        
        // Ensure left is not negative
        if (left < 10) {
          left = 10;
        }
        
        setPanelPosition({ top, left });
      }
    };
    
    calculatePosition();
    window.addEventListener('resize', calculatePosition);
    
    const close = (event) => {
      // Check if click is on button or panel - if not, close
      const isClickOnButton = buttonRef.current && buttonRef.current.contains(event.target);
      const isClickOnPanel = panelRef.current && panelRef.current.contains(event.target);
      
      if (!isClickOnButton && !isClickOnPanel) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', close);
    return () => {
      document.removeEventListener('mousedown', close);
      window.removeEventListener('resize', calculatePosition);
    };
  }, [open]);

  const toggle = (key) => {
    saveSettings({ ...settings, [key]: !settings[key] }).catch(() => {});
  };

  return (
    <div className="settings-control" ref={controlRef}>
      <button
        ref={buttonRef}
        className="settings-button"
        type="button"
        aria-label="Open settings"
        title="Settings"
        onClick={() => setOpen((value) => !value)}
      >
        <Settings size={18} />
      </button>
      {open && (
        <div
          ref={panelRef}
          className={`settings-panel ${openUpward ? 'upward' : 'downward'}`}
          style={{
            top: `${panelPosition.top}px`,
            left: `${panelPosition.left}px`,
          }}
        >
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
