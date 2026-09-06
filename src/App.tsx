/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { Header } from './components/Header';
import { BottomNav } from './components/BottomNav';
import { WhatIfScreen } from './components/WhatIfScreen';
import { RadarScreen } from './components/RadarScreen';
import { ContractsScreen } from './components/ContractsScreen';
import { IntelScreen } from './components/IntelScreen';
import { ContactScreen } from './components/ContactScreen';

export default function App() {
  const [activeTab, setActiveTab] = useState<string>('what-if');
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    // Default to dark mode as prescribed by the tactical maritime design system
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('freightiq_theme');
      if (saved) return saved === 'dark';
    }
    return true;
  });

  // Keep dark class on <html> element in sync
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('freightiq_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('freightiq_theme', 'light');
    }
  }, [darkMode]);

  const handleToggleDarkMode = () => {
    setDarkMode((prev) => !prev);
  };

  return (
    <div className="min-h-screen bg-surface text-on-surface flex flex-col selection:bg-primary selection:text-on-primary font-sans transition-colors duration-200">
      {/* Fixed Header with Tickers & Dark Mode Toggle */}
      <Header
        darkMode={darkMode}
        onToggleDarkMode={handleToggleDarkMode}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {/* Main Content Area with Smooth Page Transitions */}
      <main className="flex-1 w-full pt-28 sm:pt-32 flex flex-col items-center">
        <AnimatePresence mode="wait">
          {activeTab === 'what-if' && (
            <motion.div
              key="what-if"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.22, ease: 'easeOut' }}
              className="w-full"
            >
              <WhatIfScreen 
                onNavigateToContracts={() => setActiveTab('contracts')}
                onNavigateToRadar={() => setActiveTab('radar')}
              />
            </motion.div>
          )}

          {activeTab === 'radar' && (
            <motion.div
              key="radar"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.22, ease: 'easeOut' }}
              className="w-full"
            >
              <RadarScreen />
            </motion.div>
          )}

          {activeTab === 'contracts' && (
            <motion.div
              key="contracts"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.22, ease: 'easeOut' }}
              className="w-full"
            >
              <ContractsScreen />
            </motion.div>
          )}

          {activeTab === 'intel' && (
            <motion.div
              key="intel"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.22, ease: 'easeOut' }}
              className="w-full"
            >
              <IntelScreen />
            </motion.div>
          )}

          {activeTab === 'contact' && (
            <motion.div
              key="contact"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.22, ease: 'easeOut' }}
              className="w-full"
            >
              <ContactScreen />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Mobile Fixed Bottom Navigation */}
      <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />
    </div>
  );
}
