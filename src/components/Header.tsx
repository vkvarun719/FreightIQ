import React from 'react';
import { Sun, Moon, Radio } from 'lucide-react';

interface HeaderProps {
  darkMode: boolean;
  onToggleDarkMode: () => void;
  onOpenNotifications?: () => void;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export const Header: React.FC<HeaderProps> = ({
  darkMode,
  onToggleDarkMode,
  activeTab,
  onTabChange,
}) => {
  return (
    <header className="fixed top-0 w-full z-40 pt-safe bg-surface/90 backdrop-blur-xl border-b border-outline shadow-[0_10px_40px_rgba(0,0,0,0.5)] transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-3 flex flex-col gap-2.5">
        {/* Top bar */}
        <div className="flex items-center justify-between gap-4">
          {/* Logo & Brand with Sophisticated Dark serif identity */}
          <div 
            className="flex items-center gap-3 cursor-pointer select-none group"
            onClick={() => onTabChange('what-if')}
          >
            <img
              alt="FreightIQ 2026 Logo"
              className="h-7 w-auto object-contain shrink-0 opacity-90 transition-transform duration-200 group-hover:scale-105"
              src="https://lh3.googleusercontent.com/aida/AEtjO1XDXtEpDowWkfWOUgzTHq9YYeEkxRoPhHxuyD2WEvCrCuWSZ8h8ZI5FjIBRGJ-fuqgHAUzyYypEFIikh1_1BVfyDE4xJQOIDnNj6mkFIli_-R4dNRxp_3EwMSZPPWpVKHfSUiHdaPRLVO3lvqcY0DKGxvKE2pLcne0xbqx1hhqnneSLOlcCFk-adZT66Ogi6ihaBIzjyJr2_qJT73lrlyXJk2jl1LptT75ZiDEjCgyiqz7BhzvI3aszzHcB"
              onError={(e) => {
                (e.target as HTMLElement).style.display = 'none';
              }}
            />
            <div className="flex flex-col min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-serif text-lg sm:text-xl font-bold tracking-[0.25em] text-on-surface uppercase">
                  FreightIQ
                </span>
                <span className="text-[9px] font-mono tracking-[0.2em] font-bold text-primary bg-primary/10 px-2 py-0.5 rounded-sm border border-primary/20 uppercase">
                  2026
                </span>
              </div>
              <span className="text-[10px] uppercase tracking-[0.2em] text-on-surface-variant font-medium truncate hidden sm:inline">
                Stochastic What-If &amp; Fleet Intelligence
              </span>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6 text-[10px] uppercase tracking-[0.25em] font-medium text-on-surface-variant">
            {[
              { id: 'what-if', label: 'What-If' },
              { id: 'radar', label: 'Radar AIS' },
              { id: 'contracts', label: 'Contracts' },
              { id: 'intel', label: 'Market Intel' },
              { id: 'contact', label: 'Contact' },
            ].map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => onTabChange(tab.id)}
                  className={`py-1.5 transition-colors duration-200 border-b relative ${
                    isActive
                      ? 'text-primary font-bold border-primary'
                      : 'border-transparent hover:text-on-surface'
                  }`}
                >
                  {tab.label}
                </button>
              );
            })}
          </nav>

          {/* Action buttons & Sophisticated Dark Mode Toggle */}
          <div className="flex items-center gap-3 shrink-0">
            {/* Dark Mode Switcher (Matched to Sophisticated Dark Theme HTML) */}
            <div 
              onClick={onToggleDarkMode}
              className="flex items-center gap-2 cursor-pointer select-none py-1 px-2 rounded-sm hover:bg-surface-container-high/40 transition-colors"
              title={darkMode ? "Switch to Light Mode" : "Switch to Sophisticated Dark"}
            >
              <span className={`text-[9px] uppercase tracking-[0.2em] font-medium hidden sm:inline ${!darkMode ? 'text-primary font-bold' : 'opacity-30'}`}>
                Light
              </span>
              <div className="w-10 h-5 bg-surface-container-highest/60 rounded-full flex items-center px-0.5 border border-outline transition-colors">
                <div 
                  className={`w-3.5 h-3.5 rounded-full transition-all duration-200 ${
                    darkMode 
                      ? 'ml-auto bg-primary shadow-[0_0_8px_rgba(212,175,55,0.6)]' 
                      : 'mr-auto bg-amber-500 shadow-[0_0_6px_rgba(245,158,11,0.5)]'
                  }`} 
                />
              </div>
              <span className={`text-[9px] uppercase tracking-[0.2em] font-medium hidden sm:inline ${darkMode ? 'text-on-surface font-bold' : 'opacity-30'}`}>
                Dark
              </span>
            </div>

            {/* Live Fleet Radar Radar Button */}
            <button
              onClick={() => onTabChange('radar')}
              aria-label="Fleet Radar AIS"
              className={`w-8 h-8 sm:w-9 sm:h-9 flex items-center justify-center rounded-sm border transition-all duration-150 relative ${
                activeTab === 'radar'
                  ? 'bg-primary/10 border-primary text-primary'
                  : 'bg-surface-container border-outline text-on-surface-variant hover:text-primary hover:border-primary/40'
              }`}
              title="Open AIS Fleet Radar"
            >
              <Radio className="w-3.5 h-3.5" />
              <span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
            </button>

            {/* Profile Avatar */}
            <div 
              className="relative flex items-center justify-center cursor-pointer"
              onClick={() => onTabChange('contact')}
              title="Chartering Officer Profile & Business Info"
            >
              <img
                alt="Profile"
                className="w-7 h-7 sm:w-8 sm:h-8 rounded-full object-cover border border-outline shadow-sm grayscale hover:grayscale-0 transition-all duration-200"
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuD6lQX_X3-s2ThNtChQIe-Egr9oPzFLDPJGjwwM6U0FLqrWVxICg33F0G7nWNNFRxi3auSgG9nNRh1fpRZLGEh80c5j_tfF22aI4Xk_ZhEdCcC9U0mIUcbhHLp1lzaHTn2HjnOSymcZYVP8ZirAWxXJZBq9fPg1_BkDHzpCboAGIvsiyUwNURsOtRzGTnz6fEYYxP6XTOTpuToHJipN2lfsZkTm6lbNjW0i7GdbG9oG3XA2rozgK1-PbA"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80";
                }}
              />
              <span className="absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full bg-tertiary shadow-[0_0_6px_#10b981]" />
            </div>
          </div>
        </div>

        {/* Live Market Tickers Header Sub-bar with gold and ivory accents */}
        <div className="flex items-center gap-2 overflow-x-auto no-scrollbar py-0.5">
          <div className="flex items-center gap-1.5 bg-surface-container px-2.5 py-1 rounded-sm border border-outline text-xs shrink-0">
            <span className="font-mono text-[9px] uppercase tracking-[0.2em] text-on-surface-variant font-bold">BDI</span>
            <span className="font-mono font-semibold text-on-surface">1,942</span>
            <span className="font-mono text-tertiary flex items-center text-[10px] font-medium">
              ▲ +2.4%
            </span>
          </div>

          <div className="flex items-center gap-1.5 bg-surface-container px-2.5 py-1 rounded-sm border border-outline text-xs shrink-0">
            <span className="font-mono text-[9px] uppercase tracking-[0.2em] text-on-surface-variant font-bold">BRENT</span>
            <span className="font-mono font-semibold text-on-surface">$82.40</span>
            <span className="font-mono text-error flex items-center text-[10px] font-medium">
              ▼ -0.8%
            </span>
          </div>

          <div className="flex items-center gap-1.5 bg-surface-container px-2.5 py-1 rounded-sm border border-outline text-xs shrink-0">
            <span className="font-mono text-[9px] uppercase tracking-[0.2em] text-on-surface-variant font-bold">VLSFO</span>
            <span className="font-mono font-semibold text-on-surface">$612</span>
            <span className="font-mono text-tertiary flex items-center text-[10px] font-medium">
              ▲ +0.3%
            </span>
          </div>

          <div className="flex items-center gap-1.5 bg-surface-container px-2.5 py-1 rounded-sm border border-outline text-xs shrink-0">
            <span className="font-mono text-[9px] uppercase tracking-[0.2em] text-on-surface-variant font-bold">CAPE 5TC</span>
            <span className="font-mono font-semibold text-on-surface">$24,850/d</span>
            <span className="font-mono text-tertiary flex items-center text-[10px] font-medium">
              ▲ +4.1%
            </span>
          </div>

          <div className="flex items-center gap-1.5 bg-surface-container px-2.5 py-1 rounded-sm border border-outline text-xs shrink-0">
            <span className="font-mono text-[9px] uppercase tracking-[0.2em] text-on-surface-variant font-bold">PANAMAX 4TC</span>
            <span className="font-mono font-semibold text-on-surface">$16,210/d</span>
            <span className="font-mono text-on-surface-variant flex items-center text-[10px] font-medium">
              ― 0.0%
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
