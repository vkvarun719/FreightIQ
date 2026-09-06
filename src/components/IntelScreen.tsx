import React, { useState } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Fuel, 
  Globe2, 
  Layers, 
  Clock, 
  ArrowUpRight, 
  ArrowDownRight,
  Anchor
} from 'lucide-react';

export const IntelScreen: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'indices' | 'bunkers' | 'congestion'>('indices');

  return (
    <div className="flex flex-col w-full max-w-3xl mx-auto px-4 sm:px-6 py-4 pb-28 gap-4">
      {/* Screen Title */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-primary" />
            <h1 className="text-xl sm:text-2xl font-bold text-on-surface">
              Baltic &amp; Bunker Market Intel
            </h1>
          </div>
          <span className="text-[11px] font-mono bg-surface-container-high border border-surface-container-highest px-2 py-0.5 rounded text-secondary font-bold">
            FEED: REUTERS / BALTIC EXCHANGE
          </span>
        </div>
        <p className="text-xs text-on-surface-variant">
          Live freight assessment curves, VLSFO/HSFO fuel spreads, and global bulk trade lane indices
        </p>
      </div>

      {/* Sub-tab Switcher */}
      <div className="flex items-center bg-surface-container-lowest p-1 rounded-xl border border-surface-container-high/60 gap-1">
        <button
          onClick={() => setActiveSubTab('indices')}
          className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeSubTab === 'indices'
              ? 'bg-surface-container-high text-primary shadow-sm border border-primary/30'
              : 'text-on-surface-variant hover:text-on-surface'
          }`}
        >
          Baltic Indices
        </button>
        <button
          onClick={() => setActiveSubTab('bunkers')}
          className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeSubTab === 'bunkers'
              ? 'bg-surface-container-high text-primary shadow-sm border border-primary/30'
              : 'text-on-surface-variant hover:text-on-surface'
          }`}
        >
          Bunker Spreads
        </button>
        <button
          onClick={() => setActiveSubTab('congestion')}
          className={`flex-1 py-1.5 rounded-lg text-xs font-semibold transition-all ${
            activeSubTab === 'congestion'
              ? 'bg-surface-container-high text-primary shadow-sm border border-primary/30'
              : 'text-on-surface-variant hover:text-on-surface'
          }`}
        >
          Port Congestion
        </button>
      </div>

      {activeSubTab === 'indices' && (
        <div className="flex flex-col gap-3">
          {/* Main BDI Card */}
          <div className="bg-surface-container rounded-xl border border-surface-container-high p-4 flex flex-col gap-3 shadow-md">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-mono text-on-surface-variant uppercase font-bold">
                  BENCHMARK
                </span>
                <h3 className="text-lg font-bold text-on-surface">
                  Baltic Dry Index (BDI)
                </h3>
              </div>
              <div className="flex items-center gap-1 bg-tertiary/15 text-tertiary px-2 py-1 rounded-lg border border-tertiary/30 text-xs font-mono font-bold">
                <TrendingUp className="w-3.5 h-3.5" />
                +2.4% Today
              </div>
            </div>

            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-mono font-bold text-primary">
                1,942
              </span>
              <span className="text-xs text-on-surface-variant font-mono">
                points (+46 pts)
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-surface-container-high/40 text-xs font-mono">
              <div className="bg-surface-container-low p-2 rounded-lg">
                <span className="text-on-surface-variant text-[10px] block">BCI CAPESIZE</span>
                <span className="font-bold text-on-surface">3,120</span>
                <span className="text-tertiary block text-[10px]">▲ +5.2%</span>
              </div>
              <div className="bg-surface-container-low p-2 rounded-lg">
                <span className="text-on-surface-variant text-[10px] block">BPI PANAMAX</span>
                <span className="font-bold text-on-surface">1,740</span>
                <span className="text-error block text-[10px]">▼ -0.4%</span>
              </div>
              <div className="bg-surface-container-low p-2 rounded-lg">
                <span className="text-on-surface-variant text-[10px] block">BSI SUPRAMAX</span>
                <span className="font-bold text-on-surface">1,385</span>
                <span className="text-tertiary block text-[10px]">▲ +1.1%</span>
              </div>
              <div className="bg-surface-container-low p-2 rounded-lg">
                <span className="text-on-surface-variant text-[10px] block">BHSI HANDYSIZE</span>
                <span className="font-bold text-on-surface">790</span>
                <span className="text-tertiary block text-[10px]">▲ +0.8%</span>
              </div>
            </div>
          </div>

          {/* Forward Assessment Trend */}
          <div className="bg-surface-container rounded-xl border border-surface-container-high p-4 flex flex-col gap-2 shadow-md">
            <span className="text-xs font-semibold text-on-surface">
              Q2 - Q3 2026 Freight Forward Assessments (FFA)
            </span>
            <div className="space-y-2 text-xs font-mono">
              <div className="flex items-center justify-between p-2 rounded bg-surface-container-low border border-surface-container-high/40">
                <span className="text-on-surface">Cal 26 Cape 5TC</span>
                <span className="font-bold text-primary">$23,800 / day</span>
                <span className="text-tertiary">+3.4%</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-surface-container-low border border-surface-container-high/40">
                <span className="text-on-surface">Cal 26 Panamax 4TC</span>
                <span className="font-bold text-primary">$15,450 / day</span>
                <span className="text-tertiary">+1.2%</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded bg-surface-container-low border border-surface-container-high/40">
                <span className="text-on-surface">Cal 26 Supramax 10TC</span>
                <span className="font-bold text-primary">$13,900 / day</span>
                <span className="text-on-surface-variant">0.0%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeSubTab === 'bunkers' && (
        <div className="flex flex-col gap-3">
          <div className="bg-surface-container rounded-xl border border-surface-container-high p-4 flex flex-col gap-3 shadow-md">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Fuel className="w-4 h-4 text-secondary" />
                <h3 className="text-sm font-semibold text-on-surface">
                  Singapore Marine Fuel Benchmark
                </h3>
              </div>
              <span className="text-[10px] font-mono text-tertiary font-bold">
                DELIVERED BUNKERS
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="bg-surface-container-low p-3 rounded-xl border border-surface-container-high/50">
                <span className="text-on-surface-variant text-[10px] block">VLSFO 0.5% SULPHUR</span>
                <span className="text-xl font-bold text-primary">$612.00</span>
                <span className="text-on-surface-variant text-[10px] block">USD per Metric Ton</span>
              </div>
              <div className="bg-surface-container-low p-3 rounded-xl border border-surface-container-high/50">
                <span className="text-on-surface-variant text-[10px] block">HSFO 380 CST (HIGH SULPHUR)</span>
                <span className="text-xl font-bold text-secondary">$465.00</span>
                <span className="text-on-surface-variant text-[10px] block">USD per Metric Ton</span>
              </div>
            </div>

            {/* Hi-5 Spread */}
            <div className="bg-surface-container-low p-3 rounded-xl border border-primary/30 flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-primary block">
                  Hi-5 Fuel Spread (VLSFO - HSFO)
                </span>
                <span className="text-[11px] text-on-surface-variant">
                  Scrubber fitted vessel gross economic advantage
                </span>
              </div>
              <span className="text-lg font-mono font-bold text-tertiary">
                +$147 / MT
              </span>
            </div>
          </div>
        </div>
      )}

      {activeSubTab === 'congestion' && (
        <div className="flex flex-col gap-3">
          <div className="bg-surface-container rounded-xl border border-surface-container-high p-4 flex flex-col gap-3 shadow-md">
            <h3 className="text-sm font-semibold text-on-surface">
              Global Bulk Port Waiting Barometer
            </h3>
            <div className="space-y-2 text-xs">
              {[
                { port: 'Haldia (IND)', wait: '4.2 Days', queue: '9 vessels', status: 'CRITICAL', color: 'text-error bg-error/15' },
                { port: 'Richards Bay (ZAF)', wait: '4.8 Days', queue: '14 vessels', status: 'ELEVATED', color: 'text-error bg-error/15' },
                { port: 'Newcastle (AUS)', wait: '3.5 Days', queue: '11 vessels', status: 'MODERATE', color: 'text-amber-400 bg-amber-400/15' },
                { port: 'Qingdao (CHN)', wait: '2.4 Days', queue: '8 vessels', status: 'NORMAL', color: 'text-secondary bg-secondary/15' },
                { port: 'Paradip (IND)', wait: '1.1 Days', queue: '2 vessels', status: 'RAPID', color: 'text-tertiary bg-tertiary/15' },
                { port: 'Singapore (SGP)', wait: '0.6 Days', queue: '1 vessel', status: 'CLEAR', color: 'text-tertiary bg-tertiary/15' },
              ].map((p) => (
                <div key={p.port} className="flex items-center justify-between p-2.5 rounded-lg bg-surface-container-low border border-surface-container-high/40">
                  <div className="flex items-center gap-2">
                    <Anchor className="w-3.5 h-3.5 text-primary" />
                    <span className="font-semibold text-on-surface">{p.port}</span>
                  </div>
                  <div className="flex items-center gap-3 font-mono">
                    <span className="text-on-surface-variant">{p.queue}</span>
                    <span className="font-bold text-on-surface">{p.wait}</span>
                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${p.color}`}>
                      {p.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
