import React, { useState } from 'react';
import { SAMPLE_FLEET } from '../data/maritimeData';
import { FleetVessel } from '../types';
import { 
  Compass, 
  Ship, 
  Radio, 
  Navigation, 
  Wind, 
  AlertCircle, 
  CheckCircle, 
  Search, 
  SlidersHorizontal,
  ExternalLink,
  Anchor,
  X,
  MapPin
} from 'lucide-react';

export const RadarScreen: React.FC = () => {
  const [selectedVessel, setSelectedVessel] = useState<FleetVessel | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filteredVessels = SAMPLE_FLEET.filter((v) => {
    const matchesStatus = statusFilter === 'All' || v.status === statusFilter;
    const matchesQuery = 
      v.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      v.origin.toLowerCase().includes(searchQuery.toLowerCase()) ||
      v.destination.toLowerCase().includes(searchQuery.toLowerCase()) ||
      v.cargo.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesQuery;
  });

  return (
    <div className="flex flex-col w-full max-w-3xl mx-auto px-4 sm:px-6 py-4 pb-28 gap-4">
      {/* Screen Header */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Radio className="w-5 h-5 text-primary animate-pulse" />
            <h1 className="text-xl sm:text-2xl font-bold text-on-surface">
              Global AIS Fleet Radar
            </h1>
          </div>
          <span className="text-[11px] font-mono bg-tertiary/15 text-tertiary border border-tertiary/30 px-2 py-0.5 rounded font-bold">
            AIS STREAM LIVE
          </span>
        </div>
        <p className="text-xs text-on-surface-variant">
          Real-time dry bulk vessel telemetry, draft surveillance, and oceanic waypoint ETA tracking
        </p>
      </div>

      {/* Tactical Radar Map Canvas Simulation */}
      <div className="relative w-full h-64 sm:h-72 bg-surface-container-lowest rounded-2xl border border-surface-container-high overflow-hidden shadow-lg p-2 select-none">
        {/* Radar Circles & Coordinate Grid */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-30">
          <div className="w-96 h-96 rounded-full border border-primary/40 flex items-center justify-center">
            <div className="w-64 h-64 rounded-full border border-primary/40 flex items-center justify-center">
              <div className="w-36 h-36 rounded-full border border-primary/40" />
            </div>
          </div>
          {/* Crosshairs */}
          <div className="absolute w-full h-px bg-primary/20" />
          <div className="absolute h-full w-px bg-primary/20" />
        </div>

        {/* Sweep radar beam animation */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden flex items-center justify-center">
          <div 
            className="w-full h-full origin-center animate-[spin_8s_linear_infinite]"
            style={{
              background: 'conic-gradient(from 0deg at 50% 50%, rgba(76, 215, 246, 0.15) 0deg, transparent 60deg, transparent 360deg)'
            }}
          />
        </div>

        {/* Tactical Legend HUD */}
        <div className="absolute top-3 left-3 z-10 flex flex-col gap-1 bg-surface/80 backdrop-blur-md px-2.5 py-1.5 rounded-lg border border-surface-container-high text-[10px] font-mono">
          <div className="flex items-center gap-1.5 text-on-surface">
            <Compass className="w-3 h-3 text-primary" />
            <span>SECTOR: INDO-PACIFIC BASIN</span>
          </div>
          <span className="text-on-surface-variant">AIS COVERAGE: SATELLITE S-BAND</span>
        </div>

        <div className="absolute top-3 right-3 z-10 bg-surface/80 backdrop-blur-md px-2.5 py-1.5 rounded-lg border border-surface-container-high text-[10px] font-mono text-tertiary">
          <span>ACTIVE TARGETS: {SAMPLE_FLEET.length} VESSELS</span>
        </div>

        {/* Interactive Vessel Blips on Simulated Oceanic Grid */}
        <div className="absolute inset-0 p-6 flex items-center justify-center">
          {SAMPLE_FLEET.map((v, idx) => {
            // Pseudo layout coordinate positions
            const positions = [
              { top: '35%', left: '55%' },
              { top: '48%', left: '42%' },
              { top: '70%', left: '72%' },
              { top: '25%', left: '38%' },
              { top: '58%', left: '22%' },
            ];
            const pos = positions[idx % positions.length];
            const isSelected = selectedVessel?.imo === v.imo;

            return (
              <button
                key={v.imo}
                onClick={() => setSelectedVessel(v)}
                style={{ top: pos.top, left: pos.left }}
                className={`absolute -translate-x-1/2 -translate-y-1/2 group p-1 flex flex-col items-center transition-all duration-200 z-20 ${
                  isSelected ? 'scale-125 z-30' : 'hover:scale-110'
                }`}
              >
                <div className={`relative flex items-center justify-center w-7 h-7 rounded-full border shadow-md transition-all ${
                  isSelected
                    ? 'bg-primary text-on-primary border-white ring-4 ring-primary/30'
                    : 'bg-surface-container-high/90 text-primary border-primary/50'
                }`}>
                  <Navigation 
                    className="w-3.5 h-3.5"
                    style={{ transform: `rotate(${v.headingDeg}deg)` }}
                  />
                  {v.status === 'Underway' && (
                    <span className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-tertiary animate-ping" />
                  )}
                </div>
                <span className="text-[9px] font-mono font-bold bg-surface-container-lowest/90 px-1 rounded text-on-surface shadow mt-0.5 whitespace-nowrap">
                  {v.name.replace('MV ', '')}
                </span>
              </button>
            );
          })}
        </div>

        {/* Bottom Coordinates Readout */}
        <div className="absolute bottom-2 left-3 right-3 flex items-center justify-between text-[10px] font-mono text-on-surface-variant bg-surface/70 px-2 py-1 rounded">
          <span>LAT 08°24.12'N | LNG 085°07.30'E</span>
          <span>SWELL: 1.8M MODERATE | WIND: NE 14 KTS</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-2">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter by vessel name, port, or cargo..."
            className="w-full bg-surface-container border border-surface-container-high rounded-xl py-2 pl-9 pr-3 text-xs sm:text-sm text-on-surface placeholder:text-on-surface-variant/60 focus:outline-none focus:border-primary"
          />
        </div>

        <div className="flex items-center gap-1 overflow-x-auto no-scrollbar">
          {['All', 'Underway', 'Anchored', 'Bunkering'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-3 py-1.5 rounded-xl text-xs font-mono font-semibold transition-all shrink-0 ${
                statusFilter === status
                  ? 'bg-primary text-on-primary shadow-sm'
                  : 'bg-surface-container border border-surface-container-high text-on-surface-variant hover:text-on-surface'
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {/* Vessel List */}
      <div className="flex flex-col gap-3">
        {filteredVessels.map((vessel) => {
          const isSelected = selectedVessel?.imo === vessel.imo;
          return (
            <div
              key={vessel.imo}
              onClick={() => setSelectedVessel(vessel)}
              className={`bg-surface-container rounded-xl border p-4 cursor-pointer transition-all duration-200 shadow-sm hover:border-primary/50 flex flex-col gap-2.5 ${
                isSelected ? 'border-primary ring-1 ring-primary/40 bg-surface-container-high/40' : 'border-surface-container-high'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex flex-col">
                  <div className="flex items-center gap-2">
                    <Ship className="w-4 h-4 text-primary" />
                    <span className="font-bold text-sm sm:text-base text-on-surface">
                      {vessel.name}
                    </span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-surface-container-highest text-secondary border border-surface-container-highest">
                      {vessel.class}
                    </span>
                  </div>
                  <span className="text-xs font-mono text-on-surface-variant">
                    {vessel.imo} • {vessel.dwt.toLocaleString()} DWT • Draught: {vessel.draftMeters}m
                  </span>
                </div>

                <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold uppercase border ${
                  vessel.status === 'Underway'
                    ? 'bg-tertiary/15 text-tertiary border-tertiary/30'
                    : 'bg-amber-500/15 text-amber-400 border-amber-500/30'
                }`}>
                  {vessel.status}
                </span>
              </div>

              {/* Route & ETA */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 bg-surface-container-low p-2.5 rounded-lg text-xs font-mono border border-surface-container-high/40">
                <div className="flex items-center gap-1.5 text-on-surface truncate">
                  <MapPin className="w-3.5 h-3.5 text-tertiary shrink-0" />
                  <span>{vessel.origin}</span>
                  <span className="text-on-surface-variant">→</span>
                  <span>{vessel.destination}</span>
                </div>

                <div className="flex items-center justify-between sm:justify-end gap-3 text-on-surface-variant">
                  <span>SPEED: <strong className="text-on-surface">{vessel.speedKnots} kts</strong></span>
                  <span>CII: <strong className="text-tertiary">{vessel.ciiRating}</strong></span>
                </div>
              </div>

              {vessel.congestionWarning && (
                <div className="flex items-center gap-1.5 text-xs text-error bg-error-container/20 border border-error/30 px-2.5 py-1.5 rounded-md">
                  <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                  <span className="truncate">{vessel.congestionWarning}</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Detailed Vessel Modal */}
      {selectedVessel && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface-container border border-surface-container-high rounded-2xl max-w-lg w-full p-5 max-h-[90vh] overflow-y-auto flex flex-col gap-4 shadow-2xl animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-surface-container-high pb-3">
              <div className="flex items-center gap-2">
                <Ship className="w-5 h-5 text-primary" />
                <div>
                  <h3 className="text-base font-bold text-on-surface">
                    {selectedVessel.name}
                  </h3>
                  <span className="text-xs font-mono text-on-surface-variant">
                    {selectedVessel.imo} • Class {selectedVessel.class}
                  </span>
                </div>
              </div>
              <button
                onClick={() => setSelectedVessel(null)}
                className="w-8 h-8 rounded-lg hover:bg-surface-container-high flex items-center justify-center text-on-surface-variant hover:text-on-surface"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs font-mono bg-surface-container-lowest p-3 rounded-xl border border-surface-container-high/60">
              <div>
                <span className="text-on-surface-variant block text-[10px]">CURRENT STATUS</span>
                <span className="text-tertiary font-bold">{selectedVessel.status}</span>
              </div>
              <div>
                <span className="text-on-surface-variant block text-[10px]">SPEED &amp; HEADING</span>
                <span className="text-on-surface font-semibold">{selectedVessel.speedKnots} kts / {selectedVessel.headingDeg}°</span>
              </div>
              <div>
                <span className="text-on-surface-variant block text-[10px]">CURRENT DRAUGHT</span>
                <span className="text-on-surface font-semibold">{selectedVessel.draftMeters} meters</span>
              </div>
              <div>
                <span className="text-on-surface-variant block text-[10px]">DEADWEIGHT (DWT)</span>
                <span className="text-on-surface font-semibold">{selectedVessel.dwt.toLocaleString()} MT</span>
              </div>
              <div>
                <span className="text-on-surface-variant block text-[10px]">CARGO MANIFEST</span>
                <span className="text-primary font-semibold">{selectedVessel.cargoVolume.toLocaleString()} MT {selectedVessel.cargo}</span>
              </div>
              <div>
                <span className="text-on-surface-variant block text-[10px]">CHARTERER</span>
                <span className="text-on-surface font-semibold truncate">{selectedVessel.charterer}</span>
              </div>
            </div>

            <div className="bg-surface-container-low p-3 rounded-xl border border-surface-container-high/50 flex flex-col gap-1 text-xs">
              <span className="text-[10px] font-mono text-secondary font-bold uppercase">
                ESTIMATED TIME OF ARRIVAL (ETA)
              </span>
              <span className="text-on-surface font-mono font-semibold">
                {selectedVessel.eta}
              </span>
              <span className="text-on-surface-variant text-[11px] mt-1">
                Route: {selectedVessel.origin} to {selectedVessel.destination}
              </span>
            </div>

            <button
              onClick={() => setSelectedVessel(null)}
              className="w-full py-2.5 rounded-xl bg-primary text-on-primary font-semibold text-xs shadow-md hover:brightness-110 transition-all"
            >
              Close Vessel Telemetry
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
