import React, { useState } from 'react';
import { useTheme } from './ThemeContext';
import LayoutOne from './components/LayoutOne';
import LayoutTwo from './components/LayoutTwo';
import LayoutThree from './components/LayoutThree';
import LayoutFour from './components/LayoutFour';

export default function App() {
  const { themeId } = useTheme();
  const [history, setHistory] = useState([]);

  const handleAddHistory = (log) => {
    setHistory((prev) => [log, ...prev]);
  };

  const handleClearHistory = () => {
    setHistory([]);
  };

  const layoutProps = {
    history,
    onAddHistory: handleAddHistory,
    onClearHistory: handleClearHistory,
  };

  // Render the layout that matches the active theme
  switch (themeId) {
    case 'botanical-serenity':
      return <LayoutTwo {...layoutProps} />;
    case 'aurora-gradient':
      return <LayoutThree {...layoutProps} />;
    case 'clinical-minimal':
      return <LayoutFour {...layoutProps} />;
    case 'obsidian-cyber':
    default:
      return <LayoutOne {...layoutProps} />;
  }
}
