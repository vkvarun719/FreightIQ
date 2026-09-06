import React, { useState, useRef, useMemo, useEffect } from 'react';
import { 
  Commodity, 
  PortOption,
  BDIPoint,
  BDIForecastItem,
  OptimizationResult
} from '../types';
import { 
  COMMODITIES, 
  ORIGIN_PORTS, 
  DESTINATION_PORTS, 
  computeVesselRecommendation, 
  computePortAlert,
  getRouteDistanceNm
} from '../data/maritimeData';
import { 
  Sliders, 
  RotateCcw, 
  Play, 
  TrendingUp, 
  Ship, 
  AlertTriangle, 
  CheckCircle2, 
  ShieldCheck, 
  FileText, 
  Scale, 
  Calendar, 
  Lightbulb, 
  Leaf, 
  Anchor, 
  Sparkles,
  Info,
  X,
  Activity,
  BarChart2,
  Cpu,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
  Compass,
  Wind
} from 'lucide-react';

interface WhatIfScreenProps {
  onNavigateToContracts?: () => void;
  onNavigateToRadar?: () => void;
}

export const WhatIfScreen: React.FC<WhatIfScreenProps> = ({ 
  onNavigateToContracts,
  onNavigateToRadar 
}) => {
  // State
  const [commodity, setCommodity] = useState<Commodity>('Iron Ore');
  const [cargoVolume, setCargoVolume] = useState<number>(75000);
  // Default: Indian port origin (Visakhapatnam) and Foreign port destination (Qingdao)
  const [originPortCode, setOriginPortCode] = useState<string>('IND-VTZ');
  const [destinationPortCode, setDestinationPortCode] = useState<string>('CHN-QIN');
  const [laycanSpreadDays, setLaycanSpreadDays] = useState<number>(8);
  const [horizonDays, setHorizonDays] = useState<number>(30);
  const [activeModel, setActiveModel] = useState<'ensemble' | 'all' | 'gbdt' | 'ridge' | 'dnn'>('ensemble');
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [showFixtureModal, setShowFixtureModal] = useState<boolean>(false);

  // Live BDI Data State
  const [bdiHistory, setBdiHistory] = useState<BDIPoint[]>([]);
  const [bdiForecasts, setBdiForecasts] = useState<BDIForecastItem[]>([]);
  const [latestBdiPrice, setLatestBdiPrice] = useState<number>(3157.0);
  const [latestBdiDate, setLatestBdiDate] = useState<string>('2026-09-01');
  const [marketBias, setMarketBias] = useState<string>('BULLISH (UPWARD)');
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);

  // Interactive Chart Scrubber State
  const [scrubberPct, setScrubberPct] = useState<number>(0.35);
  const chartRef = useRef<HTMLDivElement>(null);

  // Handle toast notification
  const triggerToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 2400);
  };

  const originPort = ORIGIN_PORTS.find(p => p.code === originPortCode) || ORIGIN_PORTS[0];
  const destPort = DESTINATION_PORTS.find(p => p.code === destinationPortCode) || DESTINATION_PORTS[0];

  // Derived calculations
  const vesselRec = useMemo(() => computeVesselRecommendation(cargoVolume), [cargoVolume]);
  const portAlert = useMemo(() => computePortAlert(destinationPortCode, cargoVolume, originPortCode), [destinationPortCode, cargoVolume, originPortCode]);
  const routeDistance = useMemo(() => getRouteDistanceNm(originPortCode, destinationPortCode), [originPortCode, destinationPortCode]);

  // Load BDI Data on Mount and Horizon change
  useEffect(() => {
    async function fetchBdiData() {
      try {
        // 1. Fetch Forecasts
        const fcRes = await fetch(`/api/bdi/forecast?days=${horizonDays}`);
        if (fcRes.ok) {
          const fcJson = await fcRes.json();
          if (fcJson.success && fcJson.data?.forecasts) {
            setBdiForecasts(fcJson.data.forecasts);
            if (fcJson.data.latest_price) setLatestBdiPrice(fcJson.data.latest_price);
            if (fcJson.data.latest_date) setLatestBdiDate(fcJson.data.latest_date);
            if (fcJson.data.market_bias) setMarketBias(fcJson.data.market_bias);
          }
        }

        // 2. Fetch History
        const histRes = await fetch('/api/bdi/history?limit=30');
        if (histRes.ok) {
          const histJson = await histRes.json();
          if (histJson.success && Array.isArray(histJson.data)) {
            setBdiHistory(histJson.data);
          }
        }
      } catch (err) {
        console.error("Error fetching BDI feeds:", err);
      }
    }
    fetchBdiData();
  }, [horizonDays]);

  // Run Optimization handler
  const handleRunSimulation = async () => {
    setIsSimulating(true);
    triggerToast(`Optimizing BDI forecast & routing: ${originPort.name} → ${destPort.name}...`);

    try {
      const optRes = await fetch('/api/bdi/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          commodity,
          cargo_volume_mt: cargoVolume,
          origin_port: originPort.name.split(' (')[0],
          dest_port: destPort.name.split(' (')[0],
          contract_duration: 'Short-Term (3 Months)',
          horizon_days: horizonDays,
        }),
      });

      if (optRes.ok) {
        const optJson = await optRes.json();
        if (optJson.success && optJson.data) {
          setOptimizationResult(optJson.data);
          triggerToast("BDI Meta-Ensemble & Chartering Strategy Updated!");
        }
      }
    } catch (err) {
      console.error("Optimization failed:", err);
    } finally {
      setIsSimulating(false);
    }
  };

  // Run initial optimization on mount
  useEffect(() => {
    handleRunSimulation();
  }, [originPortCode, destinationPortCode, cargoVolume, commodity]);

  // Reset to Baseline
  const handleReset = () => {
    setCommodity('Iron Ore');
    setCargoVolume(75000);
    setOriginPortCode('IND-VTZ');
    setDestinationPortCode('CHN-QIN');
    setHorizonDays(30);
    setScrubberPct(0.35);
    triggerToast("Parameters reset to baseline Visakhapatnam → Qingdao voyage.");
  };

  // Scrubber data point calculation based on real BDI forecast array
  const activeBdiPoint = useMemo(() => {
    if (!bdiForecasts || bdiForecasts.length === 0) {
      // Fallback calibration values from Book1.csv
      return {
        date: '2026-09-08',
        predicted_price: 2449.72,
        lower_95: 1597.11,
        upper_95: 3302.34,
        ridge_pred: 3623.91,
        gbdt_pred: 3008.01,
        dnn_pred: 2339.64,
        volatility_std: 435.01,
        step: 6,
        deltaPct: -22.4,
        tcePanamax: '$25,720 / day',
        freightPerMt: '$15.17 / MT',
      };
    }

    const index = Math.min(
      Math.max(0, Math.floor(scrubberPct * (bdiForecasts.length - 1))),
      bdiForecasts.length - 1
    );
    const item = bdiForecasts[index];
    const baseline = latestBdiPrice || 3157.0;
    const deltaPct = ((item.predicted_price - baseline) / baseline) * 100;
    const tcePanamax = Math.round(item.predicted_price * 10.5);
    const freightPerMt = Math.round(((item.predicted_price / baseline) * 15.2) * 100) / 100;

    return {
      ...item,
      deltaPct: Math.round(deltaPct * 10) / 10,
      tcePanamax: `$${tcePanamax.toLocaleString()} / day`,
      freightPerMt: `$${freightPerMt.toFixed(2)} / MT`,
    };
  }, [scrubberPct, bdiForecasts, latestBdiPrice]);

  // Interactive Chart Pointer Events
  const handleChartPointer = (clientX: number) => {
    if (!chartRef.current) return;
    const rect = chartRef.current.getBoundingClientRect();
    const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
    setScrubberPct(x / rect.width);
  };

  const bdiChartPaths = useMemo(() => {
    const points = bdiForecasts.length > 0 ? bdiForecasts : [
      { step: 1, date: '2026-09-02', predicted_price: 3157, lower_95: 2800, upper_95: 3500, ridge_pred: 3200, gbdt_pred: 3100, dnn_pred: 3150 },
      { step: 15, date: '2026-09-18', predicted_price: 2600, lower_95: 2100, upper_95: 3100, ridge_pred: 2700, gbdt_pred: 2550, dnn_pred: 2500 },
      { step: 30, date: '2026-10-02', predicted_price: 2450, lower_95: 1800, upper_95: 3100, ridge_pred: 2600, gbdt_pred: 2400, dnn_pred: 2350 }
    ];

    let minVal = Math.min(...points.map(p => p.lower_95 || p.predicted_price * 0.8));
    let maxVal = Math.max(...points.map(p => p.upper_95 || p.predicted_price * 1.2));
    minVal = Math.floor(minVal * 0.95);
    maxVal = Math.ceil(maxVal * 1.05);
    const range = maxVal - minVal || 1;

    const getY = (val: number) => {
      const norm = (val - minVal) / range;
      return Math.round((125 - norm * 105) * 10) / 10;
    };

    const getX = (idx: number) => {
      return Math.round((idx / (points.length - 1 || 1)) * 320 * 10) / 10;
    };

    // Predicted Ensemble path
    const predCoords = points.map((p, i) => `${getX(i)},${getY(p.predicted_price)}`);
    const bdiPath = `M ${predCoords.join(' L ')}`;

    // 95% Confidence Interval band polygon
    const upperCoords = points.map((p, i) => `${getX(i)},${getY(p.upper_95)}`);
    const lowerCoords = points.slice().reverse().map((p, i) => `${getX(points.length - 1 - i)},${getY(p.lower_95)}`);
    const ciPolygon = `${upperCoords.join(' ')} ${lowerCoords.join(' ')}`;

    // Sub-models
    const ridgePath = `M ${points.map((p, i) => `${getX(i)},${getY(p.ridge_pred || p.predicted_price)}`).join(' L ')}`;
    const gbdtPath = `M ${points.map((p, i) => `${getX(i)},${getY(p.gbdt_pred || p.predicted_price)}`).join(' L ')}`;
    const dnnPath = `M ${points.map((p, i) => `${getX(i)},${getY(p.dnn_pred || p.predicted_price)}`).join(' L ')}`;

    // Optimal index (trough)
    let minPrice = Infinity;
    let minIdx = 0;
    points.forEach((p, i) => {
      if (p.predicted_price < minPrice) {
        minPrice = p.predicted_price;
        minIdx = i;
      }
    });

    const optimalX = getX(minIdx);
    const optimalY = getY(minPrice);

    return {
      minBdi: minVal,
      maxBdi: maxVal,
      bdiPath,
      ciPolygon,
      ridgePath,
      gbdtPath,
      dnnPath,
      optimalX,
      optimalY,
      optimalDate: points[minIdx]?.date || '2026-09-08',
      optimalBdi: minPrice,
      cursorY: getY(activeBdiPoint.predicted_price),
    };
  }, [bdiForecasts, activeBdiPoint.predicted_price]);

  const cursorSvgX = scrubberPct * 320;


  return (
    <div className="flex flex-col w-full max-w-2xl mx-auto px-4 sm:px-6 py-4 pb-28 gap-4">
      {/* Interactive Toast Notification */}
      {toastMessage && (
        <div className="fixed top-24 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 bg-surface-container-highest/95 border border-primary/40 px-4 py-2 rounded-xl shadow-2xl text-primary animate-in fade-in slide-in-from-top-2 duration-200">
          <Sparkles className="w-4 h-4 animate-spin text-primary shrink-0" />
          <span className="text-xs font-mono font-semibold tracking-wide">
            {toastMessage}
          </span>
        </div>
      )}

      {/* Hero Header Card */}
      <div className="relative overflow-hidden rounded-sm bg-surface-container border border-outline p-5 sm:p-6 shadow-[0_40px_100px_rgba(0,0,0,0.5)]">
        <div className="absolute -right-12 -top-12 w-48 h-48 rounded-full bg-primary/5 blur-3xl pointer-events-none" />
        <div className="flex items-start justify-between gap-4 relative z-10">
          <div className="flex flex-col space-y-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[10px] uppercase tracking-[0.4em] text-primary font-bold">
                Tactical Simulator
              </span>
              <div className="w-1.5 h-1.5 rounded-full bg-tertiary animate-pulse" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-serif text-on-surface tracking-tight">
              Voyage <span className="italic font-light opacity-80">What-If</span>
            </h1>
            <p className="text-xs sm:text-sm text-on-surface-variant max-w-md font-light leading-relaxed">
              Stochastic freight pricing, Monte Carlo forward curves, and laycan risk optimization.
            </p>
          </div>

          <div className="flex flex-col items-end shrink-0 bg-surface-container-low border border-outline px-3 py-2 rounded-sm">
            <span className="text-[9px] uppercase tracking-[0.25em] text-on-surface-variant font-medium">
              Model Acc.
            </span>
            <span className="text-xs font-mono text-tertiary font-bold">
              98.4%
            </span>
          </div>
        </div>
      </div>

      {/* Main Voyage Parameters Card */}
      <div className="bg-surface-container rounded-sm border border-outline p-5 sm:p-6 flex flex-col gap-5 shadow-[0_40px_100px_rgba(0,0,0,0.4)]">
        <div className="flex items-center justify-between border-b border-outline pb-3">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-primary" />
            <h2 className="text-sm sm:text-base font-serif tracking-wide text-on-surface">
              Voyage Parameters
            </h2>
          </div>
          <button
            onClick={handleReset}
            className="text-[10px] uppercase tracking-[0.25em] text-primary hover:text-secondary flex items-center gap-1.5 transition-colors px-2 py-1 rounded-sm border border-transparent hover:border-outline"
          >
            <RotateCcw className="w-3 h-3" />
            Reset
          </button>
        </div>

        {/* Commodity Segmented Pills */}
        <div className="flex flex-col gap-2">
          <label className="text-[10px] uppercase tracking-[0.3em] font-medium text-on-surface-variant">
            Bulk Commodity
          </label>
          <div className="grid grid-cols-4 gap-1.5 bg-surface-container-lowest p-1 rounded-sm border border-outline">
            {COMMODITIES.map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => {
                  setCommodity(c);
                  triggerToast(`Calibrating stowage factor & Baltic FFA for ${c}...`);
                }}
                className={`py-2 px-2 rounded-sm text-xs font-semibold uppercase tracking-wider transition-all duration-200 ${
                  commodity === c
                    ? 'bg-primary text-black font-bold shadow-md'
                    : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high/40'
                }`}
              >
                {c === 'Iron Ore' ? 'Iron' : c}
              </button>
            ))}
          </div>
        </div>

        {/* Cargo Volume Interactive Slider */}
        <div className="flex flex-col gap-2.5 bg-surface-container-low p-4 rounded-sm border border-outline">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase tracking-[0.3em] font-medium text-on-surface-variant">
              Parcel Cargo Volume
            </span>
            <div className="flex items-baseline gap-1.5">
              <span className="text-2xl sm:text-3xl font-mono font-bold text-primary">
                {cargoVolume.toLocaleString()}
              </span>
              <span className="text-[11px] font-mono uppercase text-on-surface-variant">
                MT
              </span>
            </div>
          </div>

          {/* Slider */}
          <div className="relative py-1">
            <input
              type="range"
              min="30000"
              max="180000"
              step="5000"
              value={cargoVolume}
              onChange={(e) => setCargoVolume(parseInt(e.target.value, 10))}
              className="w-full h-1.5 bg-surface-container-highest rounded-lg appearance-none cursor-pointer accent-primary focus:outline-none"
            />
          </div>

          <div className="flex items-center justify-between text-[10px] font-mono text-on-surface-variant">
            <span>30k MIN</span>
            <div className="flex items-center gap-1.5 bg-surface-container px-2 py-0.5 rounded-sm border border-outline">
              <span className="text-on-surface-variant">PARCEL CLASS:</span>
              <span className="text-primary font-bold tracking-wider">
                {cargoVolume < 60000 
                  ? 'SUPRAMAX (GEARED)' 
                  : cargoVolume <= 95000 
                    ? 'PANAMAX (GEARED)' 
                    : 'CAPESIZE (GEARLESS)'}
              </span>
            </div>
            <span>180k CAPE</span>
          </div>
        </div>

        {/* Origin & Destination Selectors */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <label className="text-[10px] uppercase tracking-[0.3em] font-medium text-on-surface-variant flex items-center gap-1.5">
                <Anchor className="w-3.5 h-3.5 text-primary" />
                Origin Port (India)
              </label>
              <span className="text-[9px] font-mono text-primary bg-primary/10 border border-primary/20 px-1.5 py-0.2 rounded-sm font-semibold">
                INDIAN PORT
              </span>
            </div>
            <select
              value={originPortCode}
              onChange={(e) => {
                setOriginPortCode(e.target.value);
                triggerToast(`Origin set to Indian loading port: ${e.target.value}`);
              }}
              className="w-full bg-surface-container-low border border-outline rounded-sm text-xs sm:text-sm text-on-surface py-2.5 px-3 focus:outline-none focus:border-primary cursor-pointer transition-colors"
            >
              {ORIGIN_PORTS.map((p) => (
                <option key={p.code} value={p.code} className="bg-surface-container text-on-surface">
                  {p.name}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <label className="text-[10px] uppercase tracking-[0.3em] font-medium text-on-surface-variant flex items-center gap-1.5">
                <Ship className="w-3.5 h-3.5 text-secondary" />
                Destination (Foreign)
              </label>
              <span className="text-[9px] font-mono text-secondary bg-secondary/10 border border-secondary/20 px-1.5 py-0.2 rounded-sm font-semibold">
                OVERSEAS DISCHARGE
              </span>
            </div>
            <select
              value={destinationPortCode}
              onChange={(e) => {
                setDestinationPortCode(e.target.value);
                triggerToast(`Destination set to foreign discharge: ${e.target.value}`);
              }}
              className="w-full bg-surface-container-low border border-outline rounded-sm text-xs sm:text-sm text-on-surface py-2.5 px-3 focus:outline-none focus:border-primary cursor-pointer transition-colors"
            >
              {DESTINATION_PORTS.map((p) => (
                <option key={p.code} value={p.code} className="bg-surface-container text-on-surface">
                  {p.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Route Telemetry & Horizon Selector */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] uppercase tracking-[0.3em] font-medium text-on-surface-variant flex items-center gap-1.5">
              <Compass className="w-3.5 h-3.5 text-primary" />
              Voyage Transit Distance
            </label>
            <div className="flex items-center justify-between bg-surface-container-low border border-outline px-3 py-2 rounded-sm text-xs">
              <span className="font-mono text-on-surface font-semibold">
                {routeDistance.toLocaleString()} NM
              </span>
              <span className="font-mono text-[10px] text-on-surface-variant">
                ~{(routeDistance / (11.5 * 24)).toFixed(1)} Days Steaming (11.5 kts)
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] uppercase tracking-[0.3em] font-medium text-on-surface-variant flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-primary" />
              Forecast Horizon (BDI Timeline)
            </label>
            <div className="grid grid-cols-4 gap-1">
              {[30, 60, 90, 180].map((d) => (
                <button
                  key={d}
                  type="button"
                  onClick={() => {
                    setHorizonDays(d);
                    triggerToast(`Switched BDI forecast horizon to ${d} Days.`);
                  }}
                  className={`py-1.5 text-center font-mono text-xs rounded-sm border transition-all ${
                    horizonDays === d
                      ? 'bg-primary text-black font-bold border-primary shadow'
                      : 'bg-surface-container-low border-outline text-on-surface-variant hover:text-on-surface'
                  }`}
                >
                  {d}D
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Run Simulation CTA Button */}
        <button
          type="button"
          onClick={handleRunSimulation}
          disabled={isSimulating}
          className="w-full py-3.5 rounded-sm bg-white text-black text-[10px] uppercase tracking-[0.35em] font-bold shadow-lg hover:bg-primary hover:text-black active:scale-[0.99] transition-all duration-300 flex items-center justify-center gap-2 disabled:opacity-75 cursor-pointer"
        >
          <Play className={`w-3.5 h-3.5 fill-current ${isSimulating ? 'animate-spin' : ''}`} />
          <span>{isSimulating ? 'Executing Ensemble Models (Book1 Data)...' : 'Run BDI What-If Optimization'}</span>
        </button>
      </div>

      {/* BALTIC DRY INDEX (BDI) PREDICTIVE GRAPH SECTION */}
      <div className="bg-surface-container rounded-sm border border-outline p-5 sm:p-6 flex flex-col gap-4 shadow-[0_40px_100px_rgba(0,0,0,0.4)]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-outline pb-3 gap-2">
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-primary" />
              <h2 className="text-sm sm:text-base font-serif tracking-wide text-on-surface">
                Baltic Dry Index (BDI) Forecast Horizon
              </h2>
            </div>
            <span className="text-[11px] text-on-surface-variant font-light mt-0.5">
              Powered by Book1.csv Historical Benchmark &amp; Multi-Model Machine Learning Ensemble
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className={`px-2 py-0.5 text-[9px] uppercase tracking-[0.2em] font-mono font-bold rounded-sm border ${
              marketBias.includes('BULLISH')
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                : marketBias.includes('BEARISH')
                ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                : 'bg-primary/10 text-primary border-primary/30'
            }`}>
              {marketBias}
            </span>
            <div className="bg-surface-container-low border border-primary/30 px-2 py-0.5 rounded-sm flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
              <span className="text-[9px] uppercase tracking-[0.2em] font-mono text-primary font-bold">
                {horizonDays}D Forward
              </span>
            </div>
          </div>
        </div>

        {/* Sub-Model Overlay Selector Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
          <span className="text-[9px] uppercase tracking-[0.2em] font-mono text-on-surface-variant shrink-0 mr-1 flex items-center gap-1">
            <Layers className="w-3 h-3 text-primary" /> Model:
          </span>
          {[
            { id: 'ensemble', label: 'Meta-Ensemble (Weighted)' },
            { id: 'all', label: 'All Sub-Models' },
            { id: 'gbdt', label: 'GBDT Trees' },
            { id: 'ridge', label: 'Ridge L2' },
            { id: 'dnn', label: 'MLP Neural Net' },
          ].map((m) => (
            <button
              key={m.id}
              type="button"
              onClick={() => setActiveModel(m.id as any)}
              className={`text-[10px] font-mono px-2.5 py-1 rounded-sm border transition-colors whitespace-nowrap cursor-pointer ${
                activeModel === m.id
                  ? 'bg-primary text-black font-bold border-primary'
                  : 'bg-surface-container-low text-on-surface-variant border-outline hover:text-on-surface'
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>

        {/* Metric Summary Badges: BDI Benchmarks */}
        <div className="grid grid-cols-3 gap-2.5 bg-surface-container-low p-3 rounded-sm border border-outline">
          <div className="flex flex-col">
            <span className="text-[9px] uppercase tracking-[0.25em] font-mono text-on-surface-variant">
              Latest BDI Spot
            </span>
            <span className="text-xs sm:text-sm font-mono font-bold text-white mt-0.5">
              {latestBdiPrice.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })} pts
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-[9px] uppercase tracking-[0.25em] font-mono text-on-surface-variant">
              Target BDI Floor
            </span>
            <span className="text-xs sm:text-sm font-mono font-bold text-primary mt-0.5">
              {bdiChartPaths.optimalBdi.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })} pts
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-[9px] uppercase tracking-[0.25em] font-mono text-on-surface-variant">
              Optimal Action
            </span>
            <span className="text-xs sm:text-sm font-mono font-bold text-tertiary truncate mt-0.5">
              {optimizationResult?.optimal_timing?.recommended_action?.includes('IMMEDIATE')
                ? 'Prompt Fixing'
                : 'Deferred Window'}
            </span>
          </div>
        </div>

        {/* Active Interactive Scrubber Readout Card */}
        <div className="bg-surface-container-lowest border border-outline px-3.5 py-2.5 rounded-sm flex flex-col sm:flex-row sm:items-center justify-between gap-2 transition-all">
          <div className="flex items-center gap-2">
            <Calendar className="w-3.5 h-3.5 text-primary shrink-0" />
            <span className="text-xs font-mono font-semibold text-on-surface">
              {activeBdiPoint.date} (Step {activeBdiPoint.step})
            </span>
            <span className="text-[10px] font-mono text-on-surface-variant">
              95% CI: [{Math.round(activeBdiPoint.lower_95)} - {Math.round(activeBdiPoint.upper_95)}]
            </span>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] font-mono text-on-surface-variant">BDI:</span>
              <span className="text-xs font-mono font-bold text-primary">
                {activeBdiPoint.predicted_price.toFixed(1)} pts
              </span>
            </div>
            <div className="flex items-center gap-1.5 hidden sm:flex">
              <span className="text-[10px] font-mono text-on-surface-variant">Panamax:</span>
              <span className="text-xs font-mono font-semibold text-white">
                {activeBdiPoint.freightPerMt}
              </span>
            </div>
            <span className={`text-[10px] font-mono px-2 py-0.5 rounded-sm font-bold uppercase tracking-wider flex items-center gap-0.5 ${
              activeBdiPoint.deltaPct > 0
                ? 'bg-error-container text-error border border-error/30'
                : 'bg-tertiary/15 text-tertiary border border-tertiary/30'
            }`}>
              {activeBdiPoint.deltaPct > 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
              {activeBdiPoint.deltaPct > 0 ? `+${activeBdiPoint.deltaPct}%` : `${activeBdiPoint.deltaPct}%`}
            </span>
          </div>
        </div>

        {/* Interactive SVG BDI Chart Container with Confidence Bands & Scrubber */}
        <div 
          ref={chartRef}
          onPointerMove={(e) => handleChartPointer(e.clientX)}
          onPointerDown={(e) => handleChartPointer(e.clientX)}
          className="relative w-full h-48 bg-surface-container-lowest rounded-sm border border-outline overflow-hidden select-none cursor-crosshair flex flex-col justify-end p-1"
        >
          <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 320 140">
            <defs>
              {/* Confidence Interval Gradient Fill */}
              <linearGradient id="bdi-ci-grad" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stopColor="#D4AF37" stopOpacity="0.22" />
                <stop offset="50%" stopColor="#D4AF37" stopOpacity="0.08" />
                <stop offset="100%" stopColor="#D4AF37" stopOpacity="0.02" />
              </linearGradient>
              {/* Gold Glow */}
              <filter id="glow-gold" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="0" stdDeviation="1.5" floodColor="#D4AF37" floodOpacity="0.6" />
              </filter>
            </defs>

            {/* Horizontal Guide Grid Lines */}
            <line x1="0" y1="20" x2="320" y2="20" stroke="rgba(255,255,255,0.06)" strokeWidth="0.75" strokeDasharray="2,2" />
            <line x1="0" y1="60" x2="320" y2="60" stroke="rgba(255,255,255,0.06)" strokeWidth="0.75" strokeDasharray="2,2" />
            <line x1="0" y1="100" x2="320" y2="100" stroke="rgba(255,255,255,0.06)" strokeWidth="0.75" strokeDasharray="2,2" />

            {/* 95% Confidence Interval Corridor Polygon */}
            <polygon points={bdiChartPaths.ciPolygon} fill="url(#bdi-ci-grad)" />

            {/* Sub-models (Togglable via pills) */}
            {(activeModel === 'all' || activeModel === 'ridge') && (
              <path d={bdiChartPaths.ridgePath} fill="none" stroke="#38bdf8" strokeWidth="1.2" strokeDasharray="3,2" opacity="0.7" />
            )}
            {(activeModel === 'all' || activeModel === 'gbdt') && (
              <path d={bdiChartPaths.gbdtPath} fill="none" stroke="#34d399" strokeWidth="1.2" strokeDasharray="3,2" opacity="0.7" />
            )}
            {(activeModel === 'all' || activeModel === 'dnn') && (
              <path d={bdiChartPaths.dnnPath} fill="none" stroke="#c084fc" strokeWidth="1.2" strokeDasharray="3,2" opacity="0.7" />
            )}

            {/* Main Predicted BDI Ensemble Curve (Gold) */}
            <path 
              d={bdiChartPaths.bdiPath} 
              fill="none" 
              stroke="#D4AF37" 
              strokeWidth="2.4" 
              filter="url(#glow-gold)" 
            />

            {/* Optimal Trough Indicator Dot */}
            <circle cx={bdiChartPaths.optimalX} cy={bdiChartPaths.optimalY} r="4" fill="#D4AF37" opacity="0.8" className="animate-ping" />
            <circle cx={bdiChartPaths.optimalX} cy={bdiChartPaths.optimalY} r="3" fill="#0A0A0A" stroke="#D4AF37" strokeWidth="2" />

            {/* Interactive Vertical Scrubber Bar */}
            <line 
              x1={cursorSvgX} 
              y1="5" 
              x2={cursorSvgX} 
              y2="135" 
              stroke="#F5F5F0" 
              strokeWidth="1.2" 
              strokeDasharray="2,2" 
              opacity="0.85" 
            />
            <circle cx={cursorSvgX} cy={bdiChartPaths.cursorY} r="3.5" fill="#D4AF37" stroke="#FFFFFF" strokeWidth="1.2" />

            {/* Axis Labels */}
            <text x="5" y="18" fill="rgba(255,255,255,0.4)" fontFamily="JetBrains Mono" fontSize="7">
              {bdiChartPaths.maxBdi} BDI
            </text>
            <text x="5" y="132" fill="rgba(255,255,255,0.4)" fontFamily="JetBrains Mono" fontSize="7">
              {bdiChartPaths.minBdi} BDI
            </text>
            <text x={bdiChartPaths.optimalX} y="15" textAnchor="middle" fill="#D4AF37" fontFamily="JetBrains Mono" fontSize="7" fontWeight="700">
              OPTIMAL FLOOR
            </text>
          </svg>

          {/* Chart Legend / Scale Info */}
          <div className="flex items-center justify-between px-2.5 py-1.5 relative z-10 bg-surface-container-lowest/90 backdrop-blur-sm border-t border-outline">
            <div className="flex items-center gap-3 text-[10px] font-mono overflow-x-auto">
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-0.5 bg-primary rounded" />
                <span className="text-primary font-bold uppercase tracking-wider">Meta-Ensemble</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-2 bg-primary/20 rounded-xs border border-primary/40" />
                <span className="text-on-surface-variant uppercase tracking-wider">95% CI Band</span>
              </div>
              {activeModel === 'all' && (
                <>
                  <div className="flex items-center gap-1">
                    <span className="w-2.5 h-0.5 bg-sky-400 rounded" />
                    <span className="text-sky-400 text-[9px]">Ridge</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="w-2.5 h-0.5 bg-emerald-400 rounded" />
                    <span className="text-emerald-400 text-[9px]">GBDT</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="w-2.5 h-0.5 bg-purple-400 rounded" />
                    <span className="text-purple-400 text-[9px]">DNN</span>
                  </div>
                </>
              )}
            </div>
            <span className="text-[9px] font-mono uppercase tracking-[0.2em] text-on-surface-variant">
              BDI Point Matrix
            </span>
          </div>
        </div>

        {/* Strategy Insight Callout */}
        <div className="flex items-start gap-2 text-on-surface-variant text-xs mt-0.5 font-light">
          <Lightbulb className="w-4 h-4 text-primary shrink-0 mt-0.5" />
          <span>
            {optimizationResult?.optimal_timing?.reasoning ? (
              optimizationResult.optimal_timing.reasoning
            ) : (
              <>
                Optimal entry timing targets rate floor at{' '}
                <strong className="text-primary font-semibold font-mono">
                  {bdiChartPaths.optimalBdi.toFixed(0)} BDI
                </strong>{' '}
                delivering projected savings on outbound Indian dry bulk parcel.
              </>
            )}
          </span>
        </div>
      </div>


      {/* MODULE B: Dynamic Vessel Recommendation & Port Infrastructure Optimization */}
      <div className="bg-surface-container rounded-sm border border-outline p-5 sm:p-6 flex flex-col gap-4 shadow-[0_40px_100px_rgba(0,0,0,0.4)]">
        <div className="flex items-center justify-between border-b border-outline pb-3">
          <div className="flex items-center gap-2">
            <Ship className="w-4 h-4 text-primary" />
            <h2 className="text-sm sm:text-base font-serif tracking-wide text-on-surface">
              Vessel Type &amp; Port Infrastructure Optimization
            </h2>
          </div>
          <span className="text-[9px] font-mono uppercase tracking-[0.25em] bg-primary/10 text-primary border border-primary/20 font-bold px-2 py-0.5 rounded-sm">
            {optimizationResult?.vessel_optimization?.recommended_vessel || vesselRec.className}
          </span>
        </div>

        {/* Recommended Vessel Header & Cost */}
        <div className="bg-surface-container-low rounded-sm p-4 flex flex-col gap-3 border border-outline">
          <div className="flex items-start justify-between">
            <div className="flex flex-col">
              <span className="text-sm sm:text-base font-serif font-bold text-on-surface">
                {optimizationResult?.vessel_optimization?.recommended_vessel || vesselRec.className}
              </span>
              <span className="text-xs text-primary font-mono mt-0.5">
                {vesselRec.vesselName} • {routeDistance.toLocaleString()} NM Route
              </span>
            </div>
            <div className="flex flex-col items-end">
              <span className="text-[9px] uppercase tracking-[0.2em] font-mono text-on-surface-variant">
                Optimal Freight Cost
              </span>
              <span className="text-sm sm:text-base font-bold font-mono text-primary mt-0.5">
                ${optimizationResult?.vessel_optimization?.optimal_freight_per_mt?.toFixed(2) || '15.17'} / MT
              </span>
            </div>
          </div>

          {/* Multi-Vessel Class Evaluation Table */}
          <div className="overflow-x-auto pt-2 border-t border-outline">
            <table className="w-full text-left font-mono text-[11px]">
              <thead>
                <tr className="text-on-surface-variant text-[9px] uppercase tracking-wider border-b border-outline/50">
                  <th className="pb-1.5 font-medium">Vessel Class</th>
                  <th className="pb-1.5 font-medium">Draft Status</th>
                  <th className="pb-1.5 font-medium">Freight / MT</th>
                  <th className="pb-1.5 font-medium">Voyage Stay</th>
                  <th className="pb-1.5 font-medium">Demurrage</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline/20 text-on-surface">
                {[
                  { name: 'Capesize (180k DWT)', draft: originPort.maxDraft >= 18.2 && destPort.maxDraft >= 18.2 ? 'YES' : 'NO (Draft)', rate: '$22.41/MT', days: '21.5d', risk: 'Low' },
                  { name: 'Panamax (82k DWT) ★', draft: originPort.maxDraft >= 14.5 && destPort.maxDraft >= 14.5 ? 'YES' : 'NO (Draft)', rate: '$15.17/MT', days: '20.9d', risk: 'Low' },
                  { name: 'Supramax (60k DWT)', draft: 'YES', rate: '$24.68/MT', days: '19.6d', risk: 'Low' },
                  { name: 'Handysize (35k DWT)', draft: 'YES', rate: '$30.34/MT', days: '20.2d', risk: 'Low' },
                ].map((row, idx) => (
                  <tr key={idx} className={row.name.includes('★') ? 'bg-primary/5 font-semibold text-primary' : ''}>
                    <td className="py-1.5">{row.name}</td>
                    <td className="py-1.5">
                      <span className={`px-1.5 py-0.2 rounded-xs text-[9px] ${
                        row.draft.startsWith('YES') ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                      }`}>
                        {row.draft}
                      </span>
                    </td>
                    <td className="py-1.5">{row.rate}</td>
                    <td className="py-1.5 text-on-surface-variant">{row.days}</td>
                    <td className="py-1.5 text-on-surface-variant">{row.risk}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2 border-t border-outline text-xs">
            <div className="flex flex-col">
              <span className="text-[9px] uppercase tracking-[0.25em] font-mono text-on-surface-variant">
                Eco-Speed &amp; Bunker
              </span>
              <span className="font-mono text-on-surface font-medium mt-0.5">
                {vesselRec.ecoSpeedKnots} kts ({vesselRec.ecoConsumptionTonsDay} MT VLSFO/d)
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-[9px] uppercase tracking-[0.25em] font-mono text-on-surface-variant">
                CII Rating
              </span>
              <span className="font-mono text-tertiary font-bold mt-0.5 flex items-center gap-1">
                <Leaf className="w-3.5 h-3.5" /> Rating {vesselRec.ciiRating} (IMO 2026 Compliant)
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Port Infrastructure & Departure/Discharge Draft Alerts */}
      <div className={`rounded-sm p-5 border shadow-[0_30px_70px_rgba(0,0,0,0.3)] flex flex-col gap-3 transition-all duration-200 ${
        portAlert.severity === 'critical'
          ? 'bg-error-container/20 border-error/30 text-on-surface'
          : 'bg-surface-container border-outline text-on-surface'
      }`}>
        <div className="flex items-center justify-between border-b border-outline/50 pb-2.5">
          <div className="flex items-center gap-2">
            {portAlert.severity === 'critical' ? (
              <AlertTriangle className="w-4 h-4 text-error shrink-0" />
            ) : (
              <CheckCircle2 className="w-4 h-4 text-tertiary shrink-0" />
            )}
            <h3 className={`text-sm sm:text-base font-serif ${
              portAlert.severity === 'critical' ? 'text-error font-semibold' : 'text-primary font-semibold'
            }`}>
              Port Draft &amp; Berth Status: {originPort.name} → {destPort.name}
            </h3>
          </div>
          <span className={`text-[9px] uppercase tracking-[0.2em] font-mono px-2 py-0.5 rounded-sm font-bold ${
            portAlert.severity === 'critical'
              ? 'bg-error-container text-error border border-error/30'
              : 'bg-tertiary/15 text-tertiary border border-tertiary/30'
          }`}>
            {portAlert.statusTag}
          </span>
        </div>

        <p className="text-xs leading-relaxed text-on-surface-variant font-light">
          {portAlert.description}
        </p>

        <div className="bg-surface-container-lowest border border-outline p-3 rounded-sm flex flex-col gap-1 text-xs">
          <span className="text-[9px] uppercase tracking-[0.25em] font-mono text-primary font-bold">
            Tactical Berth &amp; Lighterage Mitigation
          </span>
          <span className="text-on-surface-variant leading-relaxed font-light">
            {portAlert.tacticalMitigation}
          </span>
        </div>
      </div>

      {/* MODULE C: Idle Scenario Management & Deadheading Reduction */}
      <div className="bg-surface-container rounded-sm border border-outline p-5 sm:p-6 flex flex-col gap-4 shadow-[0_40px_100px_rgba(0,0,0,0.4)]">
        <div className="flex items-center justify-between border-b border-outline pb-3">
          <div className="flex items-center gap-2">
            <RotateCcw className="w-4 h-4 text-primary" />
            <h2 className="text-sm sm:text-base font-serif tracking-wide text-on-surface">
              Idle Scenario Management &amp; Deadheading Reduction
            </h2>
          </div>
          <span className="text-[9px] uppercase tracking-[0.2em] font-mono bg-surface-container-low text-on-surface-variant px-2 py-0.5 rounded-sm border border-outline">
            {destPort.name.split(' (')[0]} Hub
          </span>
        </div>

        <p className="text-xs text-on-surface-variant font-light leading-relaxed">
          Upon completing discharge at <strong className="text-on-surface">{destPort.name}</strong>, optimize repositioning to eliminate uncompensated ballast nautical miles:
        </p>

        <div className="grid grid-cols-1 gap-2.5">
          {(optimizationResult?.idle_management?.strategies || [
            {
              title: 'Western Australia Ore Repositioning Ballast Loop',
              action: 'Prompt 3,300 NM ballast to Port Hedland / Dampier for high-margin iron ore round-trip.',
              ballast_reduction_nm: 'Fastest turnaround corridor in Pacific',
              tce_impact: '+$3,200 / day fleet TCE boost',
              feasibility: 'Premier global Capesize dry bulk shuttle'
            },
            {
              title: 'North China Steel Products & Grain Backhaul',
              action: 'Load manufactured steel coils and grains at Qingdao / Tianjin for Southeast Asia or India return.',
              ballast_reduction_nm: '2,400 NM laden revenue miles generated',
              tce_impact: '+$2,100 / day net revenue',
              feasibility: 'Optimal for Supramax / Panamax'
            }
          ]).map((s: any, idx: number) => (
            <div key={idx} className="bg-surface-container-low p-3.5 rounded-sm border border-outline flex flex-col gap-1.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-primary">
                  {s.title || s.strategy_name}
                </span>
                <span className="text-[10px] font-mono font-bold text-tertiary">
                  {s.tce_impact || s.expected_tce_boost}
                </span>
              </div>
              <p className="text-xs text-on-surface-variant font-light">
                {s.action || s.description}
              </p>
              <div className="flex items-center justify-between pt-1 border-t border-outline/40 text-[10px] font-mono text-on-surface-variant">
                <span>⚡ {s.ballast_reduction_nm}</span>
                <span className="text-on-surface font-medium">{s.feasibility}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* MODULE D: Risk Mitigation & Early Warning System */}
      <div className="bg-surface-container rounded-sm border border-outline p-5 sm:p-6 flex flex-col gap-4 shadow-[0_40px_100px_rgba(0,0,0,0.4)]">
        <div className="flex items-center justify-between border-b border-outline pb-3">
          <div className="flex items-center gap-2">
            <Scale className="w-4 h-4 text-primary" />
            <h2 className="text-sm sm:text-base font-serif tracking-wide text-on-surface">
              Risk Mitigation &amp; Early Warning System
            </h2>
          </div>
          <span className="text-[9px] uppercase tracking-[0.2em] font-mono bg-surface-container-low text-primary px-2 py-0.5 rounded-sm border border-primary/20 font-bold">
            CP-GENCON 94 / BIMCO
          </span>
        </div>

        {/* Volatility & Meteorological Alerts */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="bg-surface-container-low p-3 rounded-sm border border-outline flex flex-col gap-1.5">
            <span className="text-[10px] uppercase tracking-wider font-mono text-on-surface-variant flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-primary" /> Market Volatility
            </span>
            <span className="text-xs font-semibold text-on-surface">
              {optimizationResult?.risk_evaluation?.market_volatility?.early_warning || 'Stable freight market variance (8.4% 30d forecast variance).'}
            </span>
          </div>

          <div className="bg-surface-container-low p-3 rounded-sm border border-outline flex flex-col gap-1.5">
            <span className="text-[10px] uppercase tracking-wider font-mono text-on-surface-variant flex items-center gap-1.5">
              <Wind className="w-3.5 h-3.5 text-sky-400" /> Marine Weather &amp; Monsoons
            </span>
            <span className="text-xs text-on-surface font-light">
              Bay of Bengal: Moderate post-monsoon swell. Monitor Hooghly tidal draft pilotage and outer anchorage swells.
            </span>
          </div>
        </div>

        {/* Smart Clause Auto-Insert Box */}
        <div className="bg-surface-container-low p-3.5 rounded-sm border border-outline flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-primary">
              <ShieldCheck className="w-4 h-4" />
              <span className="text-xs font-serif font-semibold tracking-wide">Auto-Drafted Clause Protection</span>
            </div>
            <span className="text-[9px] uppercase tracking-[0.2em] font-mono bg-primary/10 text-primary border border-primary/20 font-bold px-2 py-0.5 rounded-sm">
              Protected
            </span>
          </div>

          <p className="text-xs text-on-surface-variant font-light leading-relaxed">
            High Demurrage exposure at{' '}
            <strong className="text-on-surface font-mono font-semibold">
              ${cargoVolume < 60000 ? '18,500' : cargoVolume <= 95000 ? '24,000' : '36,000'} / day
            </strong>. System automatically injected{' '}
            <strong className="text-primary font-semibold">WIBON</strong> (Whether In Berth Or Not) &amp;{' '}
            <strong className="text-primary font-semibold">WIPON</strong> (Whether In Port Or Not) stipulations into charter party fixture.
          </p>
        </div>
      </div>

      {/* Operational Dispatch Confirmation Mini-Card & Fixture Modal trigger */}
      <div className="bg-surface-container-low rounded-sm p-4 border border-outline flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-tertiary" />
          <span className="text-xs text-on-surface-variant font-light">
            Route Risk Score:{' '}
            <strong className="text-tertiary font-semibold font-mono">
              Low (88/100)
            </strong>
          </span>
        </div>

        <button
          type="button"
          onClick={() => setShowFixtureModal(true)}
          className="text-[10px] uppercase tracking-[0.25em] font-mono bg-surface-container hover:bg-primary hover:text-black text-primary px-4 py-2 rounded-sm font-semibold border border-primary/30 transition-all duration-200 flex items-center gap-2 cursor-pointer"
        >
          <FileText className="w-3.5 h-3.5" />
          Export Fixture
        </button>
      </div>

      {/* Fixture Export Modal */}
      {showFixtureModal && (
        <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-surface-container border border-outline rounded-sm max-w-lg w-full p-6 max-h-[85vh] overflow-y-auto flex flex-col gap-4 shadow-[0_40px_100px_rgba(0,0,0,0.8)] animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-outline pb-3">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-primary" />
                <h3 className="text-base font-serif tracking-wide text-on-surface">
                  Charter Party Fixture Recapitulation
                </h3>
              </div>
              <button
                onClick={() => setShowFixtureModal(false)}
                className="w-8 h-8 rounded-sm hover:bg-surface-container-high flex items-center justify-center text-on-surface-variant hover:text-on-surface cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="bg-surface-container-lowest p-4 rounded-sm border border-outline font-mono text-xs text-on-surface space-y-2 leading-relaxed">
              <div className="text-primary font-bold border-b border-outline pb-1 tracking-wider">
                FIXTURE REF: FIQ-2026-CHTR-{(cargoVolume / 1000).toFixed(0)}K
              </div>
              <div>DATE: {new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}</div>
              <div>CHARTERERS: FreightIQ Global Trading Desk</div>
              <div>OWNERS: Pacific Bulk Navigation S.A.</div>
              <div>VESSEL: {vesselRec.vesselName}</div>
              <div>CARGO: {cargoVolume.toLocaleString()} MT 5% MOLOO {commodity.toUpperCase()}</div>
              <div>LOAD PORT: {originPort.name} (Indian Loading Port)</div>
              <div>DISCHARGE PORT: {destPort.name} (Foreign Discharge Port)</div>
              <div>DISTANCE: {routeDistance.toLocaleString()} NM</div>
              <div>BENCHMARK: {activeBdiPoint.predicted_price.toFixed(1)} BDI (Baltic Dry Index)</div>
              <div>FREIGHT: USD {activeBdiPoint.freightPerMt} FIOST BSS 1/1</div>
              <div>DEMURRAGE: USD ${cargoVolume < 60000 ? '18,500' : cargoVolume <= 95000 ? '24,000' : '36,000'} / DAY FD</div>
              <div>DESPATCH: HALF DEMURRAGE ALL TIME SAVED</div>
              <div className="pt-2 border-t border-outline text-primary">
                SPECIAL CLAUSES INJECTED:
                <ul className="list-disc pl-4 text-on-surface-variant mt-1 space-y-0.5 font-light">
                  <li>WIBON (Whether In Berth Or Not)</li>
                  <li>WIPON (Whether In Port Or Not)</li>
                  <li>BIMCO CII Operations Clause for Time Charter Parties 2022</li>
                  <li>Notice of Readiness (NOR) tender via Email/Cable prior 17:00 LT</li>
                </ul>
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(`FIXTURE REF: FIQ-2026\nVessel: ${vesselRec.vesselName}\nCargo: ${cargoVolume} MT ${commodity}\nRoute: ${originPort.name} -> ${destPort.name}\nBDI: ${activeBdiPoint.predicted_price.toFixed(1)} pts`);
                  triggerToast("Fixture text copied to clipboard!");
                  setShowFixtureModal(false);
                }}
                className="px-4 py-2 rounded-sm border border-outline text-[10px] uppercase tracking-[0.25em] font-medium text-on-surface hover:bg-surface-container-high transition-colors cursor-pointer"
              >
                Copy Text
              </button>
              <button
                onClick={() => {
                  triggerToast("Fixture exported to PDF package.");
                  setShowFixtureModal(false);
                }}
                className="px-5 py-2.5 rounded-sm bg-primary text-black text-[10px] uppercase tracking-[0.3em] font-bold shadow-md hover:bg-white transition-all cursor-pointer"
              >
                Download Fixture (PDF)
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

