import React, { createContext, useContext, useEffect, useState } from 'react';
import { fetchSettings, updateSettings } from './utils/api';

const DEFAULT_SETTINGS = {
  knowledge_base_enabled: true,
  llm_suggestions_enabled: true,
  image_enhancement_enabled: true,
};

const SettingsContext = createContext(null);

export function SettingsProvider({ children }) {
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSettings()
      .then(setSettings)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const saveSettings = async (nextSettings) => {
    const previous = settings;
    setSettings(nextSettings);
    setError(null);
    try {
      setSettings(await updateSettings(nextSettings));
    } catch (err) {
      setSettings(previous);
      setError(err.message);
      throw err;
    }
  };

  return (
    <SettingsContext.Provider value={{ settings, saveSettings, loading, error }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (!context) throw new Error('useSettings must be used within SettingsProvider');
  return context;
}
