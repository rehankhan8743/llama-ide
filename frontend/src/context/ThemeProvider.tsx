import React, { createContext, useState, useContext, useEffect } from 'react';
import { useSettings } from './SettingsContext';

interface ThemeContextType {
  theme: 'dark' | 'light';
  actualTheme: string;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType>({
  theme: 'dark',
  actualTheme: 'dark',
  toggleTheme: () => {},
});

export const useTheme = () => useContext(ThemeContext);

const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { settings } = useSettings();
  const [actualTheme, setActualTheme] = useState<'dark' | 'light'>('dark');

  // Map theme names to dark/light
  useEffect(() => {
    const theme = settings.theme;
    if (theme === 'light') {
      setActualTheme('light');
    } else {
      // dark, blue, green, purple all map to dark mode
      setActualTheme('dark');
    }
  }, [settings.theme]);

  useEffect(() => {
    // Apply theme class to document
    document.documentElement.className = actualTheme;
  }, [actualTheme]);

  const toggleTheme = () => {
    // This is now handled via settings but kept for compatibility
    setActualTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  return (
    <ThemeContext.Provider value={{ theme: actualTheme, actualTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeProvider;
