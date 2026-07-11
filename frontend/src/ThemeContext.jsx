import React, { createContext, useContext, useState, useEffect } from 'react';

const THEMES = [
  { id: 'obsidian-cyber', label: 'Obsidian Cyber', icon: '🔮' },
  { id: 'botanical-serenity', label: 'Botanical Serenity', icon: '🌿' },
  { id: 'aurora-gradient', label: 'Aurora Gradient', icon: '🌌' },
  { id: 'clinical-minimal', label: 'Clinical Minimal', icon: '🏥' },
];

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [themeId, setThemeId] = useState(() => {
    try {
      return localStorage.getItem('herbalai-theme') || 'obsidian-cyber';
    } catch {
      return 'obsidian-cyber';
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
