import React from 'react';
import { SlidersHorizontal, Compass, FileText, BarChart3, Building2 } from 'lucide-react';

interface BottomNavProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export const BottomNav: React.FC<BottomNavProps> = ({ activeTab, onTabChange }) => {
  const navItems = [
    { id: 'what-if', label: 'What-If', icon: SlidersHorizontal },
    { id: 'radar', label: 'Radar', icon: Compass },
    { id: 'contracts', label: 'Contracts', icon: FileText },
    { id: 'intel', label: 'Intel', icon: BarChart3 },
    { id: 'contact', label: 'Contact', icon: Building2 },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 pb-safe bg-surface/95 backdrop-blur-xl border-t border-outline shadow-[0_-10px_30px_rgba(0,0,0,0.7)]">
      <div className="flex items-center justify-around h-16 px-2 max-w-md mx-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`flex flex-col items-center justify-center min-w-[56px] min-h-[44px] py-1 gap-1 transition-all duration-200 relative ${
                isActive
                  ? 'text-primary scale-105'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'stroke-[2.2px] text-primary' : 'stroke-[1.6px]'}`} />
              <span className={`text-[9px] uppercase tracking-[0.2em] font-medium ${isActive ? 'font-bold text-primary' : ''}`}>
                {item.label}
              </span>
              {isActive && (
                <span className="w-1 h-1 rounded-full bg-primary mt-0.5 shadow-[0_0_6px_#D4AF37]" />
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
};
