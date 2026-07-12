import React, { createContext, useContext, useState, useEffect } from 'react';

const THEMES = [
  { id: 'obsidian-cyber', label: 'Obsidian Cyber', icon: '🔮' },
  { id: 'botanical-serenity', label: 'Botanical Serenity', icon: '🌿' },
  { id: 'clinical-minimal', label: 'Clinical Minimal', icon: '🏥' },
];

const ThemeContext = createContext();

const THEME_IDS = new Set(THEMES.map((t) => t.id));

export function ThemeProvider({ children }) {
  const [themeId, setThemeId] = useState(() => {
    try {
      const stored = localStorage.getItem('herbalai-theme');
      return stored && THEME_IDS.has(stored) ? stored : 'clinical-minimal';
    } catch {
      return 'clinical-minimal';
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem('herbalai-theme', themeId);
    } catch {}
    // Apply theme class to document element for CSS variable scoping
    document.documentElement.setAttribute('data-theme', themeId);
  }, [themeId]);

  return (
    <ThemeContext.Provider value={{ themeId, setThemeId, themes: THEMES }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
}

export { THEMES };
