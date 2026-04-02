import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from '@/components/ui/Navbar';
import PlaygroundPage from '@/pages/PlaygroundPage';
import IdePage from '@/pages/IdePage';
import SettingsPage from '@/pages/SettingsPage';
import PluginsPage from '@/pages/PluginsPage';
import SessionsPage from '@/pages/SessionsPage';
import ThemeProvider from '@/context/ThemeProvider';
import { SettingsProvider } from '@/context/SettingsContext';
import { SessionProvider } from '@/context/SessionContext';

const App: React.FC = () => {
  return (
    <SessionProvider>
      <SettingsProvider>
        <ThemeProvider>
          <Router>
            <div className="flex flex-col h-screen">
              <Navbar />
              <main className="flex-grow overflow-hidden">
                <Routes>
                  <Route path="/" element={<IdePage />} />
                  <Route path="/playground" element={<PlaygroundPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                  <Route path="/plugins" element={<PluginsPage />} />
                  <Route path="/sessions" element={<SessionsPage />} />
                </Routes>
              </main>
            </div>
          </Router>
        </ThemeProvider>
      </SettingsProvider>
    </SessionProvider>
  );
};

export default App;
