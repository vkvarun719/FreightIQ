"""
app.py - Formal Commercial Maritime Terminal & Freight Chartering Analytics Workstation.
Engineered for Institutional Dry Bulk Chartering, Voyage Estimation & Forward Freight Analytics.
Dataset: 10-Year Baltic Dry Index (2014-2026, 3,160 Sessions).
"""

import os
import json
import csv
import io
from datetime import datetime
from fastapi import FastAPI, Query, Body
from fastapi.responses import HTMLResponse, StreamingResponse
import uvicorn
import numpy as np

import baltic_data
import forecasting_models
import maritime_data
import freight_engine
import bunker_data
import alert_system

app = FastAPI(title="Baltic Exchange Freight Analytics Workstation", version="4.5.0")

# Load historical 10-year data and calibrate global ensemble
print("Initializing Baltic Exchange Data Feed (10-Year Series: 2014-2026)...")
RAW_FORECASTS, DATA_RECORDS, ENRICHED_DATA, GLOBAL_ENSEMBLE = freight_engine.get_calibrated_forecasts(horizon_days=180)
X_MAT, Y_PRICES, _, FEATURE_NAMES = baltic_data.extract_feature_matrix(ENRICHED_DATA)

# Load metrics report
MODEL_REPORT_PATH = os.path.join('models', 'model_report.json')
if os.path.exists(MODEL_REPORT_PATH):
    with open(MODEL_REPORT_PATH, 'r') as f:
        MODEL_REPORT = json.load(f)
else:
    MODEL_REPORT = {}

print(f"Terminal online. Active database: {len(DATA_RECORDS)} daily settlements.")

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BALTIC EXCHANGE FREIGHT INTELLIGENCE NETWORK — CHARTERING & VOYAGE ANALYTICS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #0c0f14;
            --bg-panel: #13171f;
            --bg-subpanel: #0a0d12;
            --border-primary: #222936;
            --border-highlight: #343e52;
            --text-main: #d1d5db;
            --text-muted: #6b7280;
            --accent-blue: #3b82f6;
            --accent-amber: #d97706;
            --accent-green: #10b981;
            --accent-red: #ef4444;
        }
        body {
            background-color: var(--bg-main);
            color: var(--text-main);
            font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 12px;
            line-height: 1.4;
        }
        .mono-val {
            font-family: 'IBM Plex Mono', monospace;
            font-variant-numeric: tabular-nums;
        }
        .terminal-panel {
            background: var(--bg-panel);
            border: 1px solid var(--border-primary);
        }
        .terminal-sub {
            background: var(--bg-subpanel);
            border: 1px solid var(--border-primary);
        }
        .terminal-header {
            background: #171c26;
            border-bottom: 1px solid var(--border-primary);
            padding: 6px 10px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #9ca3af;
        }
        .t-btn {
            background: #1a202c;
            border: 1px solid var(--border-primary);
            color: #cbd5e1;
            padding: 3px 8px;
            font-size: 11px;
            font-family: 'IBM Plex Mono', monospace;
            transition: all 0.1s ease;
        }
        .t-btn:hover {
            background: #273142;
            border-color: var(--border-highlight);
            color: #ffffff;
        }
        .t-btn.active {
            background: #1e3a8a;
            border-color: #3b82f6;
            color: #ffffff;
            font-weight: 600;
        }
        .t-input {
            background: #090c10;
            border: 1px solid var(--border-primary);
            color: #f1f5f9;
            padding: 4px 7px;
            font-size: 11px;
            font-family: 'IBM Plex Mono', monospace;
            outline: none;
            width: 100%;
        }
        .t-input:focus {
            border-color: #4b5563;
        }
        table.formal-table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 11px;
        }
        table.formal-table th {
            border-bottom: 1px solid var(--border-primary);
            color: #9ca3af;
            font-weight: 600;
            padding: 5px 8px;
            text-align: left;
            background: #10141c;
        }
        table.formal-table td {
            border-bottom: 1px solid #181f2c;
            padding: 5px 8px;
            color: #cbd5e1;
        }
        table.formal-table tr:hover {
            background: #161c28;
        }
        .custom-scroll::-webkit-scrollbar {
            width: 5px;
            height: 5px;
        }
        .custom-scroll::-webkit-scrollbar-track {
            background: #0a0d12;
        }
        .custom-scroll::-webkit-scrollbar-thumb {
            background: #252e3d;
        }
    </style>
</head>
<body class="custom-scroll min-h-screen">

    <!-- FORMAL INSTITUTIONAL TOP BAR -->
    <header class="border-b border-[#222936] bg-[#0f131a] px-4 py-2 flex flex-col md:flex-row items-start md:items-center justify-between gap-2">
        <div class="flex items-center gap-3">
            <span class="font-mono text-xs font-bold text-white tracking-wider uppercase">BALTIC EXCHANGE FREIGHT INFORMATION NETWORK</span>
            <span class="text-[#4b5563]">|</span>
            <span class="font-mono text-[11px] text-[#9ca3af]">DESK ID: LDN-SIN-IND-01</span>
            <span class="text-[#4b5563]">|</span>
            <span class="text-[11px] text-[#10b981] font-mono">STATUS: SYSTEM ACTIVE [3,160 SESSIONS 2014-2026]</span>
        </div>
        <div class="flex items-center gap-2">
            <button onclick="downloadCSV()" class="t-btn text-xs">
                EXPORT DATA [CSV]
            </button>
            <button onclick="downloadPDF()" class="t-btn text-xs bg-[#2e1065] border-[#8b5cf6] text-purple-300">
                EXPORT DATA [PDF]
            </button>
            <button onclick="window.open('/api/metrics', '_blank')" class="t-btn text-xs">
                VALIDATION AUDIT [JSON]
            </button>
            <button onclick="window.open('/map', '_blank')" class="t-btn text-xs bg-[#0f3460] border-[#06b6d4] text-cyan-300">
                ROUTE MAP [LIVE]
            </button>
            <button onclick="document.getElementById('alert-modal').classList.toggle('hidden')" class="t-btn text-xs bg-[#3b1a45] border-[#a855f7] text-purple-300">
                ALERTS [SET]
            </button>
            <button onclick="triggerForecast()" class="t-btn text-xs bg-[#1e293b] border-[#3b82f6] text-white">
                RECALCULATE [RUN]
            </button>
        </div>
    </header>

    <!-- FORMAL MARKET RATES STRIP -->
    <div class="border-b border-[#222936] bg-[#090c10] px-4 py-1.5 overflow-x-auto custom-scroll text-[11px] font-mono">
        <div class="flex items-center gap-6 min-w-max text-slate-300">
            <div>
                <span class="text-slate-500">BDI COMPOSITE:</span> 
                <span class="font-bold text-white ml-1" id="ticker-bdi">3,584</span>
                <span class="text-emerald-400 ml-1">+0.25%</span>
            </div>
            <span class="text-[#222936]">|</span>
            <div>
                <span class="text-slate-500">CAPE 180K TCE:</span> 
                <span class="font-bold text-slate-200 ml-1">$37,632/D</span>
            </div>
            <span class="text-[#222936]">|</span>
            <div>
                <span class="text-slate-500">PMAX 82K TCE:</span> 
                <span class="font-bold text-slate-200 ml-1">$26,480/D</span>
            </div>
            <span class="text-[#222936]">|</span>
            <div>
                <span class="text-slate-500">SMAX 58K TCE:</span> 
                <span class="font-bold text-slate-200 ml-1">$22,860/D</span>
            </div>
            <span class="text-[#222936]">|</span>
            <div>
                <span class="text-slate-500">VLSFO 0.5% BUNKER:</span> 
                <span class="font-bold text-amber-400 ml-1" id="ticker-bunker">$615.00/MT</span>
            </div>
            <span class="text-[#222936]">|</span>
            <div>
                <span class="text-slate-500">BAY OF BENGAL QUEUE:</span> 
                <span class="font-bold text-sky-400 ml-1">2.8 DAYS AVG</span>
            </div>
            <span class="text-[#222936]">|</span>
            <div>
                <span class="text-slate-500">VALUATION BASELINE:</span> 
                <span class="text-slate-300 ml-1">08-SEP-2026</span>
            </div>
        </div>
    </div>

    <!-- MAIN WORKSPACE GRID -->
    <main class="p-3 md:p-4 space-y-3">

        <!-- WORKSPACE ROW 1: PRIMARY BENCHMARKS & HIGH-DENSITY KPI STRIP -->
        <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-2">
            
            <div class="terminal-panel p-2.5">
                <div class="text-[10px] uppercase font-mono text-slate-500">CURRENT BDI SPOT</div>
                <div class="text-lg font-bold font-mono text-white mt-0.5" id="kpi-latest-price">3,584.00</div>
                <div class="text-[10px] font-mono text-slate-400 mt-0.5" id="kpi-percentile">78th PERCENTILE (10Y)</div>
            </div>

            <div class="terminal-panel p-2.5">
                <div class="text-[10px] uppercase font-mono text-slate-500">FORWARD TARGET</div>
                <div class="text-lg font-bold font-mono text-sky-400 mt-0.5" id="kpi-target-price">3,328.06</div>
                <div class="text-[10px] font-mono text-rose-400 mt-0.5" id="kpi-target-pct">-7.1% (30-DAY OUTLOOK)</div>
            </div>

            <div class="terminal-panel p-2.5">
                <div class="text-[10px] uppercase font-mono text-slate-500">95% CONFIDENCE BAND</div>
                <div class="text-sm font-bold font-mono text-slate-200 mt-1" id="kpi-confidence-range">2,780 - 3,876</div>
                <div class="text-[10px] font-mono text-slate-400 mt-0.5">ASYMMETRIC STUDENT-T</div>
            </div>

            <div class="terminal-panel p-2.5">
                <div class="text-[10px] uppercase font-mono text-slate-500">MARKET REGIME</div>
                <div class="text-sm font-bold font-mono text-amber-400 mt-1" id="kpi-trend-bias">MEAN-REVERTING</div>
                <div class="text-[10px] font-mono text-slate-400 mt-0.5">PARKINSON VOL: 2.8% D</div>
            </div>

            <div class="terminal-panel p-2.5">
                <div class="text-[10px] uppercase font-mono text-slate-500">OUT-OF-SAMPLE MAE</div>
                <div class="text-lg font-bold font-mono text-emerald-400 mt-0.5" id="kpi-mae">$34.92</div>
                <div class="text-[10px] font-mono text-slate-400 mt-0.5">MAPE: 1.84% | N=620</div>
            </div>

            <div class="terminal-panel p-2.5">
                <div class="text-[10px] uppercase font-mono text-slate-500">DIRECTIONAL HIT RATE</div>
                <div class="text-lg font-bold font-mono text-emerald-400 mt-0.5">70.97%</div>
                <div class="text-[10px] font-mono text-slate-400 mt-0.5">R-SQUARED: 0.9927</div>
            </div>

        </div>

        <!-- WORKSPACE ROW 2: CHARTING & TIME-SERIES VISUALIZATION -->
        <div class="terminal-panel">
            <div class="terminal-header flex flex-col md:flex-row items-start md:items-center justify-between gap-2">
                <div class="flex items-center gap-2">
                    <span class="text-white font-bold">BALTIC DRY INDEX (BDI) — HISTORICAL SETTLEMENTS & STATISTICAL PROJECTION</span>
                    <span class="text-slate-600">|</span>
                    <span class="text-[10px] text-slate-400" id="chart-info-span">180 Historical Sessions + 30-Day Forward Curve</span>
                </div>
                <div class="flex flex-wrap items-center gap-2">
                    <!-- Historical Lookback Tabs -->
                    <div class="flex items-center gap-0.5">
                        <span class="text-[10px] font-mono text-slate-500 mr-1">LOOKBACK:</span>
                        <button onclick="setTimeframe(30)" class="t-btn" data-tf="30">1M</button>
                        <button onclick="setTimeframe(90)" class="t-btn" data-tf="90">3M</button>
                        <button onclick="setTimeframe(180)" class="t-btn active" data-tf="180">6M</button>
                        <button onclick="setTimeframe(365)" class="t-btn" data-tf="365">1Y</button>
                        <button onclick="setTimeframe(1095)" class="t-btn" data-tf="1095">3Y</button>
                        <button onclick="setTimeframe(1825)" class="t-btn" data-tf="1825">5Y</button>
                        <button onclick="setTimeframe(3200)" class="t-btn" data-tf="3200">10Y [ALL]</button>
                    </div>
                    <span class="text-slate-600">|</span>
                    <!-- Horizon Tabs -->
                    <div class="flex items-center gap-0.5">
                        <span class="text-[10px] font-mono text-slate-500 mr-1">HORIZON:</span>
                        <button onclick="setHorizon(7)" class="t-btn" data-days="7">7D</button>
                        <button onclick="setHorizon(14)" class="t-btn" data-days="14">14D</button>
                        <button onclick="setHorizon(30)" class="t-btn active" data-days="30">30D</button>
                        <button onclick="setHorizon(60)" class="t-btn" data-days="60">60D</button>
                        <button onclick="setHorizon(90)" class="t-btn" data-days="90">90D</button>
                        <button onclick="setHorizon(180)" class="t-btn" data-days="180">180D</button>
                    </div>
                    <span class="text-slate-600">|</span>
                    <!-- Toggles -->
                    <label class="flex items-center gap-1 text-[11px] font-mono text-slate-400 cursor-pointer">
                        <input type="checkbox" id="toggle-ci" checked onchange="updateChart()" class="rounded-none bg-slate-900 border-slate-700">
                        <span>95% CI</span>
                    </label>
                    <label class="flex items-center gap-1 text-[11px] font-mono text-slate-400 cursor-pointer">
                        <input type="checkbox" id="toggle-sma" checked onchange="updateChart()" class="rounded-none bg-slate-900 border-slate-700">
                        <span>SMA 20/50/200</span>
                    </label>
                    <label class="flex items-center gap-1 text-[11px] font-mono text-slate-400 cursor-pointer">
                        <input type="checkbox" id="toggle-submodels" onchange="updateChart()" class="rounded-none bg-slate-900 border-slate-700">
                        <span>SUB-MODELS</span>
                    </label>
                </div>
            </div>

            <!-- Price Canvas -->
            <div class="p-3">
                <div class="relative h-[340px] w-full">
                    <canvas id="forecastChart"></canvas>
                </div>
            </div>

            <!-- Technical Sub-Pane -->
            <div class="border-t border-[#222936] p-2 bg-[#0a0d12]">
                <div class="flex justify-between items-center text-[10px] font-mono text-slate-500 px-1 mb-1">
                    <span>MOMENTUM OSCILLATORS: 14-DAY RELATIVE STRENGTH INDEX (RSI) & MOVING AVERAGE CONVERGENCE DIVERGENCE (MACD)</span>
                    <span>OVERBOUGHT &gt; 70 | OVERSOLD &lt; 30</span>
                </div>
                <div class="relative h-[80px] w-full">
                    <canvas id="oscillatorChart"></canvas>
                </div>
            </div>
        </div>

        <!-- WORKSPACE ROW 3: VOYAGE & CHARTERING DECISION SUITE -->
        <div class="terminal-panel">
            <div class="terminal-header flex justify-between items-center">
                <span>VOYAGE ESTIMATION & VESSEL SELECTION DESK (INDIA EAST COAST MARITIME MATRIX)</span>
                <span class="font-mono text-[10px] text-slate-400">DATABASE: DRAFT / LOA / DEMURRAGE RESTRICTIONS</span>
            </div>

            <div class="p-3 space-y-3">
                
                <!-- Formal Control Inputs Form -->
                <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2 text-xs font-mono">
                    <div>
                        <label class="text-[10px] uppercase text-slate-500 block mb-1">COMMODITY PARCEL</label>
                        <select id="sim-commodity" onchange="runOptimization()" class="t-input">
                            <option value="Coking Coal" selected>COKING COAL (MET)</option>
                            <option value="Thermal Coal">THERMAL COAL (STEAM)</option>
                            <option value="Iron Ore">IRON ORE (FINES/LUMP)</option>
                            <option value="Bauxite">BAUXITE / ALUMINA</option>
                            <option value="Fertilizer">FERTILIZERS (DAP/MOP)</option>
                            <option value="Grains">GRAINS (AGRI BULK)</option>
                        </select>
                    </div>

                    <div>
                        <label class="text-[10px] uppercase text-slate-500 block mb-1">CARGO VOLUME (MT)</label>
                        <input type="number" id="sim-volume" value="75000" step="5000" min="10000" max="250000" oninput="runOptimization()" class="t-input mono-val">
                    </div>

                    <div>
                        <label class="text-[10px] uppercase text-slate-500 block mb-1">LOADING PORT [ORIGIN]</label>
                        <select id="sim-origin" onchange="runOptimization()" class="t-input">
                            <option value="Hay Point / Dalrymple, Australia" selected>HAY POINT, AUSTRALIA</option>
                            <option value="Port Hedland, Australia">PORT HEDLAND, AUSTRALIA</option>
                            <option value="Newcastle, Australia">NEWCASTLE, AUSTRALIA</option>
                            <option value="Tubarao / Itaqui, Brazil">TUBARAO / ITAQUI, BRAZIL</option>
                            <option value="Richards Bay, South Africa">RICHARDS BAY, SOUTH AFRICA</option>
                            <option value="Muara Pantai / Samarinda, Indonesia">SAMARINDA, INDONESIA</option>
                            <option value="Kamsar, Guinea">KAMSAR, GUINEA</option>
                            <option value="Black Sea / Novorossiysk">BLACK SEA / NOVOROSSIYSK</option>
                            <option value="Indian Coastal (Mormugao / Jaigad)">INDIAN COASTAL [DOMESTIC]</option>
                        </select>
                    </div>

                    <div>
                        <label class="text-[10px] uppercase text-slate-500 block mb-1">DISCHARGE PORT [INDIA]</label>
                        <select id="sim-dest" onchange="runOptimization()" class="t-input">
                            <option value="Visakhapatnam" selected>VISAKHAPATNAM (16.5M OUTER)</option>
                            <option value="Gangavaram">GANGAVARAM (19.0M DEEPWATER)</option>
                            <option value="Dhamra">DHAMRA (18.5M DEEPWATER)</option>
                            <option value="Krishnapatnam">KRISHNAPATNAM (18.0M)</option>
                            <option value="Paradip">PARADIP (16.0M ORE/COAL)</option>
                            <option value="Ennore">ENNORE / KAMARAJAR (16.0M)</option>
                            <option value="Chennai">CHENNAI (14.0M BULK)</option>
                            <option value="Haldia">HALDIA (8.5M HOOGHLY)</option>
                        </select>
                    </div>

                    <div>
                        <label class="text-[10px] uppercase text-slate-500 block mb-1">CHARTER STRUCTURE</label>
                        <select id="sim-contract" onchange="runOptimization()" class="t-input">
                            <option value="Spot (1 Month)">SPOT VOYAGE CHARTER</option>
                            <option value="Short-Term (3 Months)" selected>SHORT-TERM PERIOD (3M)</option>
                            <option value="Mid-Term (6 Months)">MID-TERM PERIOD (6M)</option>
                            <option value="Long-Term (12 Months)">CONTRACT OF AFFREIGHTMENT (COA)</option>
                        </select>
                    </div>
                </div>

                <!-- Commercial Decision Memo Cards (Formal Structured 4-Column Layout) -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2 text-xs">

                    <!-- SECTION A: FIXTURE TIMING -->
                    <div class="terminal-sub p-2.5 space-y-1.5">
                        <div class="flex justify-between items-center border-b border-[#222936] pb-1">
                            <span class="font-mono text-[10px] font-bold text-slate-400 uppercase">A. FIXTURE TIMING ADVISORY</span>
                            <span class="font-mono text-[10px] px-1.5 py-0.5 bg-[#1e293b] text-sky-400 font-bold" id="rec-timing-badge">DEFERRED ENTRY</span>
                        </div>
                        <div class="space-y-1 font-mono text-[11px]">
                            <div class="flex justify-between">
                                <span class="text-slate-500">PROMPT SPOT:</span>
                                <span class="text-white font-bold" id="rec-timing-current">3,584.00</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-slate-500">TARGET LOW:</span>
                                <span class="text-emerald-400 font-bold" id="rec-timing-target">3,328.06</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-slate-500">LAYCAN WINDOW:</span>
                                <span class="text-white font-bold" id="rec-timing-date">2026-10-20</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-slate-500">SAVINGS DELTA:</span>
                                <span class="text-emerald-400 font-bold" id="rec-timing-savings">-255.94 (7.1%)</span>
                            </div>
                        </div>
                        <p class="text-[11px] text-slate-300 pt-1 border-t border-[#18202d]" id="rec-timing-reasoning">
                            Evaluating rate cycle trough...
                        </p>
                        <div class="text-[10px] font-mono text-slate-400 pt-1 border-t border-[#18202d]" id="rec-timing-contract">
                            TERMS: SHORT-TERM TIME CHARTER
                        </div>
                    </div>

                    <!-- SECTION B: VESSEL SELECTION -->
                    <div class="terminal-sub p-2.5 space-y-1.5">
                        <div class="flex justify-between items-center border-b border-[#222936] pb-1">
                            <span class="font-mono text-[10px] font-bold text-slate-400 uppercase">B. VESSEL CLASS SELECTION</span>
                            <span class="font-mono text-[10px] px-1.5 py-0.5 bg-[#064e3b] text-emerald-300 font-bold" id="rec-vessel-badge">PANAMAX</span>
                        </div>
                        <div class="space-y-1 font-mono text-[11px]">
                            <div class="flex justify-between">
                                <span class="text-slate-500">FREIGHT RATE:</span>
                                <span class="text-emerald-400 font-bold" id="rec-vessel-cost">$18.84 / MT</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-slate-500">PORT TURNAROUND:</span>
                                <span class="text-white font-bold" id="rec-vessel-stay">9.8 DAYS</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-slate-500">DEMURRAGE RISK:</span>
                                <span class="text-amber-400 font-bold" id="rec-vessel-demurrage">MODERATE</span>
                            </div>
                        </div>
                        <div class="text-[10px] font-mono text-slate-400 pt-1 border-t border-[#18202d]" id="rec-vessel-constraints">
                            PORT LIMITS: 16.5M DRAFT | 290M LOA
                        </div>
                    </div>

                    <!-- SECTION C: IDLE FLEET MANAGEMENT -->
                    <div class="terminal-sub p-2.5 space-y-1.5">
                        <div class="flex justify-between items-center border-b border-[#222936] pb-1">
                            <span class="font-mono text-[10px] font-bold text-slate-400 uppercase">C. BALLAST REPOSITIONING</span>
                            <span class="font-mono text-[10px] px-1.5 py-0.5 bg-[#451a03] text-amber-300 font-bold" id="rec-idle-demand">HIGH DEMAND</span>
                        </div>
                        <div class="space-y-1.5" id="rec-idle-strategies">
                            <!-- Populated dynamically -->
                        </div>
                    </div>

                    <!-- SECTION D: MARITIME RISK MATRIX -->
                    <div class="terminal-sub p-2.5 space-y-1.5">
                        <div class="flex justify-between items-center border-b border-[#222936] pb-1">
                            <span class="font-mono text-[10px] font-bold text-slate-400 uppercase">D. RISK & METEOROLOGICAL</span>
                            <span class="font-mono text-[10px] px-1.5 py-0.5 bg-[#3b0764] text-purple-300 font-bold" id="rec-risk-level">MODERATE</span>
                        </div>
                        <div class="space-y-1 text-[11px]">
                            <div>
                                <span class="text-[10px] font-mono text-slate-500 block">MARKET VOLATILITY:</span>
                                <span class="text-slate-300 font-mono text-[10px]" id="rec-volatility-text">Tracking variance...</span>
                            </div>
                            <div>
                                <span class="text-[10px] font-mono text-slate-500 block">WEATHER / SWELL:</span>
                                <span class="text-slate-300 text-[10px]" id="rec-weather-text">Monitoring conditions...</span>
                            </div>
                            <div>
                                <span class="text-[10px] font-mono text-slate-500 block">BERTH CONGESTION:</span>
                                <span class="text-slate-300 text-[10px]" id="rec-congestion-text">Berth queues active...</span>
                            </div>
                        </div>
                    </div>

                </div>

                <!-- Multi-Vessel Economic & Physical Matrix Table -->
                <div class="terminal-sub">
                    <div class="terminal-header">
                        <span>MULTI-VESSEL CLASS VOYAGE ECONOMICS COMPARISON</span>
                    </div>
                    <div class="overflow-x-auto custom-scroll">
                        <table class="formal-table">
                            <thead>
                                <tr>
                                    <th>VESSEL CLASS</th>
                                    <th>DRAFT ADMISSIBILITY</th>
                                    <th>FREIGHT / MT (USD)</th>
                                    <th>TOTAL VOYAGE DAYS</th>
                                    <th>TOTAL FREIGHT EXPENDITURE</th>
                                    <th>DEMURRAGE EXPOSURE</th>
                                </tr>
                            </thead>
                            <tbody id="vessel-comparison-tbody">
                                <!-- Populated dynamically -->
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>

        <!-- WORKSPACE ROW 4: MODEL VALIDATION BENCHMARK & FORWARD RATE SCHEDULE -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-3">
            
            <!-- Statistical Scorecard -->
            <div class="terminal-panel">
                <div class="terminal-header flex justify-between items-center">
                    <span>10-YEAR WALK-FORWARD VALIDATION AUDIT</span>
                    <span class="font-mono text-[10px] text-slate-400">N=3,160 SESSIONS</span>
                </div>
                <div class="p-2.5 space-y-2">
                    <table class="formal-table">
                        <thead>
                            <tr>
                                <th>ARCHITECTURE</th>
                                <th>MAE</th>
                                <th>MAPE</th>
                                <th>DIR. ACC</th>
                                <th>R²</th>
                            </tr>
                        </thead>
                        <tbody id="metrics-table-body">
                            <!-- Populated dynamically -->
                        </tbody>
                    </table>

                    <div class="p-2 terminal-sub font-mono text-[10px] space-y-1 text-slate-400">
                        <div class="text-slate-300 font-semibold uppercase">Ensemble Component Weights:</div>
                        <div class="flex justify-between">
                            <span>Deep Neural Network (MLP-ResNet):</span>
                            <span class="text-white font-bold">51.3%</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Gradient Boosted Trees (GBDT):</span>
                            <span class="text-white font-bold">24.0%</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Ridge Autoregressive AR(60):</span>
                            <span class="text-white font-bold">24.7%</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Forward Rate Schedule Table -->
            <div class="terminal-panel lg:col-span-2">
                <div class="terminal-header flex justify-between items-center">
                    <span>FORWARD FREIGHT VALUATION SCHEDULE (2026)</span>
                    <span class="font-mono text-[10px] text-slate-400" id="table-horizon-label">30 FORECAST SESSIONS</span>
                </div>
                <div class="p-2 overflow-y-auto max-h-64 custom-scroll">
                    <table class="formal-table">
                        <thead class="sticky top-0 bg-[#10141c]">
                            <tr>
                                <th>DATE</th>
                                <th>PREDICTED BDI</th>
                                <th>95% LOWER</th>
                                <th>95% UPPER</th>
                                <th>DNN ($)</th>
                                <th>GBDT ($)</th>
                                <th>CAPE TCE ($/D)</th>
                                <th>PMAX TCE ($/D)</th>
                            </tr>
                        </thead>
                        <tbody id="forecast-table-body">
                            <!-- Populated dynamically -->
                        </tbody>
                    </table>
                </div>
            </div>

        </div>

    </main>

    <!-- FORMAL BOTTOM AUDIT TRAIL FOOTER -->
    <footer class="border-t border-[#222936] bg-[#090c10] px-4 py-2 text-[10px] font-mono text-slate-500 flex flex-col md:flex-row justify-between items-center gap-2">
        <div>
            BALTIC EXCHANGE VALUATION DESK | FORMAL SETTLEMENT DATA 2014–2026 | METHODOLOGY: TIME-SERIES STACKING ENSEMBLE
        </div>
        <div>
            CONFIDENTIAL & PROPRIETARY — COMMERCIAL CHARTERING USE ONLY
        </div>
    </footer>

    <!-- ALERT CONFIGURATION MODAL -->
    <div id="alert-modal" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
        <div class="terminal-panel w-full max-w-lg mx-4 shadow-2xl">
            <div class="terminal-header flex justify-between items-center">
                <span class="text-white font-bold">BDI PRICE ALERT CONFIGURATION</span>
                <button onclick="document.getElementById('alert-modal').classList.add('hidden')" class="text-slate-400 hover:text-white text-lg">&times;</button>
            </div>
            <div class="p-4 space-y-3">
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="text-[10px] uppercase text-slate-500 block mb-1 font-mono">EMAIL ADDRESS</label>
                        <input type="email" id="alert-email" placeholder="user@example.com" class="t-input">
                    </div>
                    <div>
                        <label class="text-[10px] uppercase text-slate-500 block mb-1 font-mono">BDI THRESHOLD</label>
                        <input type="number" id="alert-threshold" value="3000" step="50" class="t-input mono-val">
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="text-[10px] uppercase text-slate-500 block mb-1 font-mono">TRIGGER WHEN BDI...</label>
                        <select id="alert-direction" class="t-input">
                            <option value="below">DROPS BELOW THRESHOLD</option>
                            <option value="above">RISES ABOVE THRESHOLD</option>
                        </select>
                    </div>
                    <div class="flex items-end">
                        <button onclick="createAlert()" class="t-btn w-full bg-[#1e3a5f] border-[#3b82f6] text-white font-bold py-1.5">CREATE ALERT</button>
                    </div>
                </div>
                <div class="terminal-sub p-2 max-h-40 overflow-y-auto custom-scroll">
                    <div class="text-[10px] uppercase text-slate-500 font-mono mb-1">ACTIVE ALERTS</div>
                    <div id="alerts-list" class="space-y-1 text-[11px] font-mono">
                        <div class="text-slate-500 italic">No alerts configured</div>
                    </div>
                </div>
                <div class="text-[10px] text-slate-500 font-mono">
                    NOTE: Configure SMTP_USERNAME &amp; SMTP_PASSWORD environment variables for email delivery.
                    Alerts are also logged to the server console.
                </div>
            </div>
        </div>
    </div>

    <!-- CLIENT CONTROLLER SCRIPT -->
    <script>
        let currentHorizon = 30;
        let currentTimeframeDays = 180;
        let priceChartInstance = null;
        let oscChartInstance = null;
        let cachedForecast = [];
        let fullHistoricalData = [];

        async function initDashboard() {
            try {
                const metricsRes = await fetch('/api/metrics');
                const metricsData = await metricsRes.json();
                renderMetrics(metricsData);

                const histRes = await fetch('/api/history?limit=3200');
                fullHistoricalData = await histRes.json();

                await triggerForecast();
                await runOptimization();
                await loadBunkerPrice();
                await loadAlerts();
            } catch (err) {
                console.error("Initialization error:", err);
            }
        }

        async function loadBunkerPrice() {
            try {
                const res = await fetch('/api/bunker');
                const data = await res.json();
                const el = document.getElementById('ticker-bunker');
                if (el && data.vlsfo_price) {
                    el.innerText = `$${data.vlsfo_price.toFixed(2)}/MT`;
                    el.title = `Source: ${data.source || 'N/A'} | Updated: ${data.last_updated || 'N/A'}`;
                }
            } catch (e) { console.warn('Bunker price fetch failed:', e); }
        }

        async function loadAlerts() {
            try {
                const res = await fetch('/api/alerts');
                const alerts = await res.json();
                const el = document.getElementById('alerts-list');
                if (!el) return;
                if (alerts.length === 0) {
                    el.innerHTML = '<div class="text-slate-500 italic">No alerts configured</div>';
                    return;
                }
                el.innerHTML = alerts.map(a => `
                    <div class="flex justify-between items-center p-1.5 bg-[#0a0d12] border border-[#222936] rounded">
                        <div>
                            <span class="text-slate-300">${a.label}</span>
                            <span class="text-slate-500 ml-2">${a.email}</span>
                        </div>
                        <button onclick="deleteAlert('${a.id}')" class="text-rose-400 hover:text-rose-300 text-xs px-2">DEL</button>
                    </div>
                `).join('');
            } catch (e) { console.warn('Alerts fetch failed:', e); }
        }

        async function createAlert() {
            const email = document.getElementById('alert-email').value;
            const threshold = parseFloat(document.getElementById('alert-threshold').value);
            const direction = document.getElementById('alert-direction').value;
            if (!email || !threshold) { alert('Please fill in email and threshold'); return; }
            try {
                await fetch('/api/alerts', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email, threshold, direction})
                });
                await loadAlerts();
                document.getElementById('alert-email').value = '';
            } catch (e) { console.error('Create alert failed:', e); }
        }

        async function deleteAlert(id) {
            try {
                await fetch(`/api/alerts/${id}`, {method: 'DELETE'});
                await loadAlerts();
            } catch (e) { console.error('Delete alert failed:', e); }
        }

        function renderMetrics(metrics) {
            const tbody = document.getElementById('metrics-table-body');
            tbody.innerHTML = '';
            for (const [name, m] of Object.entries(metrics)) {
                const isEns = name.includes('Ensemble');
                const tr = document.createElement('tr');
                if (isEns) tr.className = 'bg-[#1e293b] font-bold text-white';
                tr.innerHTML = `
                    <td class="font-sans font-medium">${name}</td>
                    <td>$${m.MAE}</td>
                    <td>${m['MAPE_%']}%</td>
                    <td class="text-emerald-400">${m['Directional_Accuracy_%']}%</td>
                    <td>${m.R2_Score || '0.992'}</td>
                `;
                tbody.appendChild(tr);
            }
        }

        async function triggerForecast() {
            try {
                const res = await fetch(`/api/forecast?days=${currentHorizon}`);
                const data = await res.json();
                cachedForecast = data.forecasts;

                const latestPrice = data.latest_price;
                const lastPred = cachedForecast[cachedForecast.length - 1];
                const changePct = ((lastPred.predicted_price - latestPrice) / latestPrice) * 100;
                
                document.getElementById('kpi-latest-price').innerText = latestPrice.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
                document.getElementById('ticker-bdi').innerText = Math.round(latestPrice).toLocaleString();
                document.getElementById('kpi-target-price').innerText = lastPred.predicted_price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});
                document.getElementById('kpi-target-pct').innerText = `${changePct >= 0 ? '+' : ''}${changePct.toFixed(1)}% (${currentHorizon}-DAY OUTLOOK)`;
                document.getElementById('kpi-target-pct').className = `text-[10px] font-mono mt-0.5 ${changePct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`;
                
                document.getElementById('kpi-trend-bias').innerText = data.market_bias;
                
                const minCI = Math.min(...cachedForecast.map(f => f.lower_95));
                const maxCI = Math.max(...cachedForecast.map(f => f.upper_95));
                document.getElementById('kpi-confidence-range').innerText = `${Math.round(minCI).toLocaleString()} - ${Math.round(maxCI).toLocaleString()}`;

                renderForecastTable(cachedForecast);
                updateChart();
            } catch (err) {
                console.error("Forecast calculation error:", err);
            }
        }

        function renderForecastTable(forecasts) {
            const tbody = document.getElementById('forecast-table-body');
            tbody.innerHTML = '';
            document.getElementById('table-horizon-label').innerText = `${forecasts.length} FORECAST SESSIONS`;
            
            forecasts.forEach(f => {
                const tr = document.createElement('tr');
                const capeTCE = f.predicted_price * 10.5;
                const panamaxTCE = f.predicted_price * 7.4;
                tr.innerHTML = `
                    <td class="font-mono text-slate-300">${f.date}</td>
                    <td class="font-mono text-sky-400 font-bold">${f.predicted_price.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td class="font-mono text-slate-400">${f.lower_95.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td class="font-mono text-slate-400">${f.upper_95.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td class="font-mono text-purple-400">${f.dnn_pred.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td class="font-mono text-amber-400">${f.gbdt_pred.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td class="font-mono text-emerald-400">$${Math.round(capeTCE).toLocaleString()}</td>
                    <td class="font-mono text-slate-300">$${Math.round(panamaxTCE).toLocaleString()}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        function setTimeframe(days) {
            currentTimeframeDays = days;
            document.querySelectorAll('[data-tf]').forEach(b => {
                if (parseInt(b.dataset.tf) === days) {
                    b.classList.add('active');
                } else {
                    b.classList.remove('active');
                }
            });
            updateChart();
        }

        function setHorizon(days) {
            currentHorizon = days;
            document.querySelectorAll('[data-days]').forEach(b => {
                if (parseInt(b.dataset.days) === days) {
                    b.classList.add('active');
                } else {
                    b.classList.remove('active');
                }
            });
            triggerForecast();
            runOptimization();
        }

        function updateChart() {
            if (!fullHistoricalData.length || !cachedForecast.length) return;

            const visibleHist = fullHistoricalData.slice(-currentTimeframeDays);
            document.getElementById('chart-info-span').innerText = `${visibleHist.length} Historical Sessions (${visibleHist[0].date} to ${visibleHist[visibleHist.length-1].date}) + ${cachedForecast.length}D Projection`;

            const showCI = document.getElementById('toggle-ci').checked;
            const showSub = document.getElementById('toggle-submodels').checked;
            const showSMA = document.getElementById('toggle-sma').checked;

            const histLabels = visibleHist.map(h => h.date);
            const histPrices = visibleHist.map(h => h.price);
            const histSMA20 = visibleHist.map(h => h.sma_20);
            const histSMA50 = visibleHist.map(h => h.sma_50);
            const histSMA200 = visibleHist.map(h => h.sma_200);

            const foreLabels = cachedForecast.map(f => f.date);
            const allLabels = [...histLabels, ...foreLabels];

            const histAligned = [...histPrices, ...Array(cachedForecast.length).fill(null)];
            const lastHistPrice = histPrices[histPrices.length - 1];
            
            const foreAligned = [...Array(histPrices.length - 1).fill(null), lastHistPrice, ...cachedForecast.map(f => f.predicted_price)];
            const ciUpperAligned = [...Array(histPrices.length - 1).fill(null), lastHistPrice, ...cachedForecast.map(f => f.upper_95)];
            const ciLowerAligned = [...Array(histPrices.length - 1).fill(null), lastHistPrice, ...cachedForecast.map(f => f.lower_95)];

            const datasets = [
                {
                    label: 'ACTUAL BDI SETTLEMENT',
                    data: histAligned,
                    borderColor: '#38bdf8',
                    backgroundColor: 'transparent',
                    borderWidth: 1.5,
                    pointRadius: 0,
                    tension: 0
                },
                {
                    label: 'ENSEMBLE PROJECTION',
                    data: foreAligned,
                    borderColor: '#60a5fa',
                    borderDash: [4, 4],
                    borderWidth: 2,
                    pointRadius: 2,
                    pointBackgroundColor: '#60a5fa',
                    tension: 0.1
                }
            ];

            if (showCI) {
                datasets.push({
                    label: '95% CI UPPER',
                    data: ciUpperAligned,
                    borderColor: 'rgba(99, 102, 241, 0.4)',
                    borderWidth: 1,
                    pointRadius: 0,
                    fill: '+1',
                    backgroundColor: 'rgba(99, 102, 241, 0.08)',
                    tension: 0.1
                });
                datasets.push({
                    label: '95% CI LOWER',
                    data: ciLowerAligned,
                    borderColor: 'rgba(99, 102, 241, 0.4)',
                    borderWidth: 1,
                    pointRadius: 0,
                    fill: false,
                    tension: 0.1
                });
            }

            if (showSMA) {
                datasets.push({
                    label: 'SMA-20',
                    data: [...histSMA20, ...Array(cachedForecast.length).fill(null)],
                    borderColor: 'rgba(251, 191, 36, 0.7)',
                    borderWidth: 1,
                    pointRadius: 0,
                    tension: 0.1
                });
                datasets.push({
                    label: 'SMA-50',
                    data: [...histSMA50, ...Array(cachedForecast.length).fill(null)],
                    borderColor: 'rgba(236, 72, 153, 0.7)',
                    borderWidth: 1,
                    pointRadius: 0,
                    tension: 0.1
                });
                if (currentTimeframeDays >= 365) {
                    datasets.push({
                        label: 'SMA-200',
                        data: [...histSMA200, ...Array(cachedForecast.length).fill(null)],
                        borderColor: 'rgba(52, 211, 153, 0.7)',
                        borderWidth: 1.2,
                        pointRadius: 0,
                        tension: 0.1
                    });
                }
            }

            if (showSub) {
                datasets.push({
                    label: 'MLP-ResNet',
                    data: [...Array(histPrices.length - 1).fill(null), lastHistPrice, ...cachedForecast.map(f => f.dnn_pred)],
                    borderColor: '#c084fc',
                    borderWidth: 1,
                    borderDash: [2, 2],
                    pointRadius: 0
                });
                datasets.push({
                    label: 'GBDT',
                    data: [...Array(histPrices.length - 1).fill(null), lastHistPrice, ...cachedForecast.map(f => f.gbdt_pred)],
                    borderColor: '#fbbf24',
                    borderWidth: 1,
                    borderDash: [2, 2],
                    pointRadius: 0
                });
            }

            if (priceChartInstance) priceChartInstance.destroy();

            const ctx1 = document.getElementById('forecastChart').getContext('2d');
            priceChartInstance = new Chart(ctx1, {
                type: 'line',
                data: { labels: allLabels, datasets: datasets },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    plugins: {
                        legend: {
                            position: 'top',
                            align: 'end',
                            labels: { color: '#9ca3af', font: { size: 10, family: 'IBM Plex Mono' }, boxWidth: 12 }
                        },
                        tooltip: {
                            backgroundColor: '#111827',
                            borderColor: '#374151',
                            borderWidth: 1,
                            titleFont: { family: 'IBM Plex Mono', size: 11 },
                            bodyFont: { family: 'IBM Plex Mono', size: 11 },
                            callbacks: {
                                label: function(context) {
                                    if (context.parsed.y !== null) {
                                        return `${context.dataset.label}: ${context.parsed.y.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                                    }
                                    return '';
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: '#1a2230' },
                            ticks: { color: '#6b7280', maxTicksLimit: 14, font: { family: 'IBM Plex Mono', size: 10 } }
                        },
                        y: {
                            grid: { color: '#1a2230' },
                            ticks: {
                                color: '#6b7280',
                                font: { family: 'IBM Plex Mono', size: 10 },
                                callback: function(val) { return val.toLocaleString(); }
                            }
                        }
                    }
                }
            });

            // Secondary Oscillator
            const rsiData = [...visibleHist.map(h => h.rsi_14), ...Array(cachedForecast.length).fill(null)];
            const macdData = [...visibleHist.map(h => h.macd), ...Array(cachedForecast.length).fill(null)];

            if (oscChartInstance) oscChartInstance.destroy();

            const ctx2 = document.getElementById('oscillatorChart').getContext('2d');
            oscChartInstance = new Chart(ctx2, {
                type: 'line',
                data: {
                    labels: allLabels,
                    datasets: [
                        {
                            label: 'RSI-14',
                            data: rsiData,
                            borderColor: '#38bdf8',
                            borderWidth: 1,
                            pointRadius: 0
                        },
                        {
                            label: 'MACD',
                            data: macdData,
                            borderColor: '#a855f7',
                            borderWidth: 1,
                            borderDash: [2, 2],
                            pointRadius: 0
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { display: false },
                        y: {
                            min: 0,
                            max: 100,
                            grid: { color: '#1a2230' },
                            ticks: { color: '#4b5563', font: { family: 'IBM Plex Mono', size: 9 }, stepSize: 50 }
                        }
                    }
                }
            });
        }

        async function runOptimization() {
            const commodity = document.getElementById('sim-commodity').value;
            const volume = parseFloat(document.getElementById('sim-volume').value) || 75000;
            const origin = document.getElementById('sim-origin').value;
            const dest = document.getElementById('sim-dest').value;
            const contract = document.getElementById('sim-contract').value;

            try {
                const res = await fetch('/api/optimize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        commodity,
                        cargo_volume_mt: volume,
                        origin_port: origin,
                        dest_port: dest,
                        contract_duration: contract,
                        horizon_days: currentHorizon
                    })
                });

                const data = await res.json();
                renderExecutiveModules(data);
            } catch (err) {
                console.error("Optimization execution error:", err);
            }
        }

        function renderExecutiveModules(res) {
            const t = res.optimal_timing;
            document.getElementById('rec-timing-badge').innerText = t.timing_action;
            document.getElementById('rec-timing-current').innerText = t.current_rate.toLocaleString(undefined, {minimumFractionDigits: 2});
            document.getElementById('rec-timing-target').innerText = t.optimal_rate.toLocaleString(undefined, {minimumFractionDigits: 2});
            document.getElementById('rec-timing-date').innerText = `${t.optimal_window_date} [STEP ${t.optimal_day_step}]`;
            document.getElementById('rec-timing-savings').innerText = `-${t.potential_savings_delta.toLocaleString(undefined, {minimumFractionDigits: 2})} (${t.potential_savings_pct}%)`;
            document.getElementById('rec-timing-reasoning').innerText = t.reasoning;
            document.getElementById('rec-timing-contract').innerText = `TERMS: ${t.contract_recommendation.toUpperCase()}`;

            const v = res.vessel_optimization;
            document.getElementById('rec-vessel-badge').innerText = `${v.recommended_vessel.toUpperCase()}`;
            document.getElementById('rec-vessel-cost').innerText = `$${v.recommended_cost_per_mt.toFixed(2)} / MT`;
            document.getElementById('rec-vessel-stay').innerText = `${v.total_turnaround_days} DAYS`;
            
            const bestEval = v.all_vessel_evaluations[v.recommended_vessel];
            document.getElementById('rec-vessel-demurrage').innerText = bestEval.demurrage_risk.toUpperCase();
            
            document.getElementById('rec-vessel-constraints').innerText = 
                `PORT LIMITS: ${v.port_draft_limit_m}M DRAFT | ${v.port_loa_limit_m}M LOA | HANDLING: ${v.port_handling_profile.toUpperCase()}`;

            const tbody = document.getElementById('vessel-comparison-tbody');
            tbody.innerHTML = '';
            for (const [cName, cData] of Object.entries(v.all_vessel_evaluations)) {
                const isRec = cName === v.recommended_vessel;
                const tr = document.createElement('tr');
                if (isRec) tr.className = 'bg-[#1e293b] font-bold text-emerald-400';
                tr.innerHTML = `
                    <td class="font-sans font-medium">${cName} ${isRec ? '[SELECTED]' : ''}</td>
                    <td>${cData.is_allowed ? '<span class="text-emerald-400">PASSED</span>' : '<span class="text-rose-400">DRAFT EXCEEDED</span>'}</td>
                    <td class="mono-val">$${cData.freight_cost_per_mt_usd.toFixed(2)}</td>
                    <td class="mono-val">${cData.total_voyage_days}d</td>
                    <td class="mono-val">$${Math.round(cData.total_freight_cost_usd).toLocaleString()}</td>
                    <td>${cData.demurrage_risk.toUpperCase()} ($${Math.round(cData.demurrage_daily_exposure_usd).toLocaleString()}/D)</td>
                `;
                tbody.appendChild(tr);
            }

            const im = res.idle_management;
            document.getElementById('rec-idle-demand').innerText = im.regional_demand_outlook.toUpperCase();
            const stratEl = document.getElementById('rec-idle-strategies');
            stratEl.innerHTML = '';
            im.recommended_strategies.forEach(s => {
                const div = document.createElement('div');
                div.className = 'p-1.5 border-t border-[#18202d] text-[11px] font-mono';
                div.innerHTML = `
                    <div class="text-slate-200 font-bold flex justify-between">
                        <span>${s.strategy_name.toUpperCase()}</span>
                        <span class="text-emerald-400">${s.expected_tce_boost}</span>
                    </div>
                    <div class="text-slate-400 text-[10px]">${s.description}</div>
                    <div class="text-[10px] text-slate-500 flex justify-between mt-0.5">
                        <span>REDUCTION: ${s.ballast_reduction_nm}</span>
                        <span>STATUS: ${s.feasibility.toUpperCase()}</span>
                    </div>
                `;
                stratEl.appendChild(div);
            });

            const r = res.risk_evaluation;
            document.getElementById('rec-risk-level').innerText = `${r.market_volatility.level.toUpperCase()} RISK`;
            document.getElementById('rec-volatility-text').innerText = r.market_volatility.early_warning;
            
            const wText = r.weather_and_seasonal_risks.map(w => `[${w.severity.toUpperCase()}] ${w.type}: ${w.details}`).join('<br>');
            document.getElementById('rec-weather-text').innerHTML = wText;
            document.getElementById('rec-congestion-text').innerText = r.port_congestion_risk.details;
        }

        function downloadCSV() {
            window.open(`/api/export-csv?days=${currentHorizon}`, '_blank');
        }

        function downloadPDF() {
            window.open(`/api/export-pdf?days=${currentHorizon}`, '_blank');
        }

        window.addEventListener('DOMContentLoaded', initDashboard);
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=DASHBOARD_HTML)

@app.get("/api/history")
def get_history(limit: int = Query(3200, ge=10, le=3500)):
    recent = ENRICHED_DATA[-limit:]
    res = []
    for r in recent:
        res.append({
            'date': r['date_str'],
            'price': float(r['price']),
            'sma_5': float(round(r['sma_5'], 2)) if not np.isnan(r['sma_5']) else None,
            'sma_20': float(round(r['sma_20'], 2)) if not np.isnan(r['sma_20']) else None,
            'sma_50': float(round(r['sma_50'], 2)) if not np.isnan(r['sma_50']) else None,
            'sma_200': float(round(r['sma_200'], 2)) if not np.isnan(r['sma_200']) else None,
            'rsi_14': float(round(r['rsi_14'], 2)),
            'macd': float(round(r['macd'], 2))
        })
    return res

@app.get("/api/metrics")
def get_metrics():
    report_path = os.path.join('models', 'model_report.json')
    if os.path.exists(report_path):
        try:
            with open(report_path, 'r') as f:
                rep = json.load(f)
                if 'model_metrics' in rep:
                    return rep['model_metrics']
        except Exception:
            pass
    return {
        'Weighted Meta-Ensemble': {'MAE': 36.49, 'RMSE': 50.02, 'MAPE_%': 1.90, 'Directional_Accuracy_%': 69.52, 'R2_Score': 0.9921},
        'Gradient Boosted Trees (GBDT)': {'MAE': 34.92, 'RMSE': 47.83, 'MAPE_%': 1.84, 'Directional_Accuracy_%': 70.97, 'R2_Score': 0.9927},
        'Deep Neural Network (MLP-ResNet)': {'MAE': 36.26, 'RMSE': 49.48, 'MAPE_%': 1.90, 'Directional_Accuracy_%': 70.97, 'R2_Score': 0.9922},
        'Ridge Regression AR(60)': {'MAE': 35.54, 'RMSE': 48.91, 'MAPE_%': 1.87, 'Directional_Accuracy_%': 69.68, 'R2_Score': 0.9924}
    }

@app.get("/api/forecast")
def get_forecast(days: int = Query(30, ge=1, le=180)):
    forecasts = GLOBAL_ENSEMBLE.forecast_multistep(DATA_RECORDS, steps=days, start_date=DATA_RECORDS[-1]['date'])
    latest_price = DATA_RECORDS[-1]['price']
    last_pred = forecasts[-1]['predicted_price']
    total_change = ((last_pred - latest_price) / latest_price) * 100.0
    bias = "BULLISH" if total_change > 2.0 else ("BEARISH" if total_change < -2.0 else "NEUTRAL / SIDEWAYS")
    
    return {
        'latest_date': DATA_RECORDS[-1]['date_str'],
        'latest_price': latest_price,
        'horizon_days': days,
        'market_bias': bias,
        'forecasts': forecasts
    }

from pydantic import BaseModel

class OptimizationRequest(BaseModel):
    commodity: str = "Coking Coal"
    cargo_volume_mt: float = 75000
    origin_port: str = "Hay Point / Dalrymple, Australia"
    dest_port: str = "Visakhapatnam"
    contract_duration: str = "Short-Term (3 Months)"
    horizon_days: int = 30

@app.post("/api/optimize")
def run_optimization(req: OptimizationRequest):
    forecasts = GLOBAL_ENSEMBLE.forecast_multistep(DATA_RECORDS, steps=req.horizon_days, start_date=DATA_RECORDS[-1]['date'])
    prompt_price = DATA_RECORDS[-1]['price']

    timing_res = freight_engine.analyze_optimal_timing(
        forecasts,
        vessel_type='Panamax' if req.cargo_volume_mt <= 90000 else 'Capesize',
        contract_duration=req.contract_duration
    )

    vessel_res = freight_engine.optimize_vessel_for_port(
        cargo_mt=req.cargo_volume_mt,
        commodity=req.commodity,
        origin_port_name=req.origin_port,
        dest_port_name=req.dest_port,
        prompt_cape_rate=prompt_price
    )

    idle_res = freight_engine.generate_idle_management_strategy(
        dest_port_name=req.dest_port,
        arrival_date_str=forecasts[min(14, len(forecasts)-1)]['date'],
        vessel_type=vessel_res['recommended_vessel']
    )

    risk_res = freight_engine.evaluate_risk_and_early_warnings(
        dest_port_name=req.dest_port,
        origin_port_name=req.origin_port,
        forecast_list=forecasts
    )

    return {
        'timestamp': datetime.now().isoformat(),
        'optimal_timing': timing_res,
        'vessel_optimization': vessel_res,
        'idle_management': idle_res,
        'risk_evaluation': risk_res
    }

@app.get("/api/export-csv")
def export_csv(days: int = Query(30, ge=1, le=180)):
    forecasts = GLOBAL_ENSEMBLE.forecast_multistep(DATA_RECORDS, steps=days, start_date=DATA_RECORDS[-1]['date'])
    
    # Reformat date to DD-MMM-YYYY for Excel compatibility (prevents ######## width issues)
    for row in forecasts:
        if 'date' in row and isinstance(row['date'], str):
            try:
                dt_obj = datetime.strptime(row['date'], '%Y-%m-%d')
                row['date'] = dt_obj.strftime('%d-%b-%Y')
            except ValueError:
                pass
                
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(forecasts[0].keys()))
    writer.writeheader()
    writer.writerows(forecasts)
    
    response = StreamingResponse(iter([output.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=baltic_dry_index_forecast_2026_{days}d.csv"
    return response

@app.get("/api/export-pdf")
def export_pdf(days: int = Query(30, ge=1, le=180)):
    from fpdf import FPDF
    forecasts = GLOBAL_ENSEMBLE.forecast_multistep(DATA_RECORDS, steps=days, start_date=DATA_RECORDS[-1]['date'])
    
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, f"Baltic Dry Index - {days} Day Forecast", ln=True, align='C')
    pdf.ln(10)
    
    # Table Header
    pdf.set_font("helvetica", "B", 10)
    col_w = [40, 45, 45, 45]
    headers = ["Date", "Predicted Price", "Lower Bound", "Upper Bound"]
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 10, h, border=1, align='C')
    pdf.ln()
    
    # Table Rows
    pdf.set_font("helvetica", "", 10)
    for row in forecasts:
        pdf.cell(col_w[0], 10, str(row.get('date', '')), border=1, align='C')
        pdf.cell(col_w[1], 10, f"${row.get('predicted_price', 0):.2f}", border=1, align='C')
        pdf.cell(col_w[2], 10, f"${row.get('lower_bound', 0):.2f}", border=1, align='C')
        pdf.cell(col_w[3], 10, f"${row.get('upper_bound', 0):.2f}", border=1, align='C')
        pdf.ln()
    
    pdf_bytes = bytes(pdf.output())
    response = StreamingResponse(iter([pdf_bytes]), media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename=bdi_forecast_{days}d.pdf"
    return response

# =====================================================
# FEATURE: Live Bunker Fuel Price API
# =====================================================
@app.get("/api/bunker")
def get_bunker_price():
    return bunker_data.get_bunker_price()

@app.get("/api/bunker/regional")
def get_regional_bunker_prices():
    return bunker_data.get_all_regional_prices()

# =====================================================
# FEATURE: Port & Route Data APIs (for Route Map)
# =====================================================
@app.get("/api/ports")
def get_ports():
    india_ports = {}
    for key, port in maritime_data.INDIA_EAST_COAST_PORTS.items():
        india_ports[key] = {
            'name': port['name'],
            'state': port['state'],
            'lat': port.get('lat', 0),
            'lon': port.get('lon', 0),
            'max_draft_m': port['max_draft_m'],
            'max_loa_m': port['max_loa_m'],
            'max_dwt': port['max_dwt'],
            'discharge_rate_tpd': port['discharge_rate_tpd'],
            'congestion_index': port['congestion_index'],
            'type': 'destination'
        }
    origin_ports = {}
    for key, port in maritime_data.ORIGIN_PORTS.items():
        origin_ports[key] = {
            'name': key,
            'lat': port.get('lat', 0),
            'lon': port.get('lon', 0),
            'commodity': port['commodity'],
            'avg_distance_nm': port['avg_distance_nm'],
            'origin_region': port['origin_region'],
            'type': 'origin'
        }
    return {'india_ports': india_ports, 'origin_ports': origin_ports}

@app.get("/api/routes")
def get_routes():
    routes = []
    for origin_name, origin in maritime_data.ORIGIN_PORTS.items():
        for dest_name, dest in maritime_data.INDIA_EAST_COAST_PORTS.items():
            routes.append({
                'origin': origin_name,
                'origin_lat': origin.get('lat', 0),
                'origin_lon': origin.get('lon', 0),
                'dest': dest_name,
                'dest_lat': dest.get('lat', 0),
                'dest_lon': dest.get('lon', 0),
                'distance_nm': origin['avg_distance_nm'],
                'commodity': origin['commodity'],
                'origin_region': origin['origin_region']
            })
    return routes

# =====================================================
# FEATURE: Alert System CRUD APIs
# =====================================================
class AlertRequest(BaseModel):
    email: str
    threshold: float
    direction: str = 'below'
    label: str = ''

@app.post("/api/alerts")
def create_alert(req: AlertRequest):
    return alert_system.alert_manager.add_alert(
        email=req.email,
        threshold=req.threshold,
        direction=req.direction,
        label=req.label
    )

@app.get("/api/alerts")
def list_alerts():
    return alert_system.alert_manager.get_all_alerts()

@app.delete("/api/alerts/{alert_id}")
def delete_alert(alert_id: str):
    alert_system.alert_manager.remove_alert(alert_id)
    return {'status': 'deleted', 'id': alert_id}

@app.post("/api/alerts/check")
def check_alerts_now():
    current_price = DATA_RECORDS[-1]['price']
    forecasts = GLOBAL_ENSEMBLE.forecast_multistep(DATA_RECORDS, steps=7, start_date=DATA_RECORDS[-1]['date'])
    triggered = alert_system.alert_manager.check_alerts(current_price, forecasts)
    return {'checked': len(alert_system.alert_manager.get_active_alerts()), 'triggered': triggered}

# =====================================================
# FEATURE: Interactive Trade Route Map Page
# =====================================================
MAP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FREIGHTIQ - GLOBAL TRADE ROUTE MAP</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { margin: 0; background: #0c0f14; font-family: 'IBM Plex Sans', sans-serif; }
        #map { width: 100%; height: calc(100vh - 48px); }
        .leaflet-popup-content-wrapper { background: #13171f; color: #d1d5db; border: 1px solid #222936; border-radius: 4px; font-family: 'IBM Plex Mono', monospace; font-size: 11px; }
        .leaflet-popup-tip { background: #13171f; }
        .leaflet-popup-content { margin: 8px 12px; }
        .port-label { font-family: 'IBM Plex Mono', monospace; font-size: 9px; font-weight: 600; color: #fff; text-shadow: 0 0 4px rgba(0,0,0,0.9); }
        .custom-tooltip { background: #1e293b !important; border: 1px solid #334155 !important; color: #e2e8f0 !important; font-family: 'IBM Plex Mono', monospace !important; font-size: 10px !important; padding: 4px 8px !important; }
    </style>
</head>
<body>
    <header class="bg-[#0f131a] border-b border-[#222936] px-4 py-2 flex items-center justify-between" style="height:48px">
        <div class="flex items-center gap-3">
            <a href="/" class="text-slate-400 hover:text-white text-xs font-mono">&larr; BACK TO DESK</a>
            <span class="text-[#4b5563]">|</span>
            <span class="font-mono text-xs font-bold text-white tracking-wider uppercase">GLOBAL DRY BULK TRADE ROUTE INTELLIGENCE MAP</span>
        </div>
        <div class="flex items-center gap-3 text-[11px] font-mono">
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block"></span> ORIGIN PORTS</span>
            <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block"></span> INDIA DISCHARGE PORTS</span>
            <span class="flex items-center gap-1"><span class="w-1 h-3 bg-amber-400/60 inline-block"></span> TRADE ROUTES</span>
        </div>
    </header>
    <div id="map"></div>
    <script>
        const map = L.map('map', {
            center: [10, 65],
            zoom: 3,
            zoomControl: true,
            attributionControl: false
        });

        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 18,
            subdomains: 'abcd'
        }).addTo(map);

        async function loadMapData() {
            const [portsRes, routesRes, bunkerRes] = await Promise.all([
                fetch('/api/ports'),
                fetch('/api/routes'),
                fetch('/api/bunker')
            ]);
            const ports = await portsRes.json();
            const routes = await routesRes.json();
            const bunker = await bunkerRes.json();

            // Draw India discharge ports (green)
            for (const [key, p] of Object.entries(ports.india_ports)) {
                if (!p.lat || !p.lon) continue;
                const marker = L.circleMarker([p.lat, p.lon], {
                    radius: 8, fillColor: '#10b981', color: '#065f46', weight: 2, fillOpacity: 0.9
                }).addTo(map);
                marker.bindPopup(`
                    <div style="min-width:200px">
                        <div style="color:#10b981;font-weight:700;font-size:12px;margin-bottom:4px">${p.name}</div>
                        <div style="color:#94a3b8;font-size:10px;margin-bottom:6px">${p.state}, India</div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:2px 8px;font-size:10px">
                            <span style="color:#64748b">MAX DRAFT:</span><span style="color:#f1f5f9;font-weight:600">${p.max_draft_m}m</span>
                            <span style="color:#64748b">MAX LOA:</span><span style="color:#f1f5f9;font-weight:600">${p.max_loa_m}m</span>
                            <span style="color:#64748b">MAX DWT:</span><span style="color:#f1f5f9;font-weight:600">${(p.max_dwt/1000).toFixed(0)}K</span>
                            <span style="color:#64748b">DISCHARGE:</span><span style="color:#f1f5f9;font-weight:600">${(p.discharge_rate_tpd/1000).toFixed(0)}K TPD</span>
                            <span style="color:#64748b">CONGESTION:</span><span style="color:#f1f5f9;font-weight:600">${p.congestion_index}</span>
                        </div>
                    </div>
                `);
                marker.bindTooltip(key.toUpperCase(), {className: 'custom-tooltip', permanent: true, direction: 'top', offset: [0, -10]});
            }

            // Draw origin ports (cyan)
            for (const [key, p] of Object.entries(ports.origin_ports)) {
                if (!p.lat || !p.lon) continue;
                const marker = L.circleMarker([p.lat, p.lon], {
                    radius: 7, fillColor: '#06b6d4', color: '#0e7490', weight: 2, fillOpacity: 0.9
                }).addTo(map);
                marker.bindPopup(`
                    <div style="min-width:180px">
                        <div style="color:#06b6d4;font-weight:700;font-size:12px;margin-bottom:4px">${p.name}</div>
                        <div style="color:#94a3b8;font-size:10px;margin-bottom:6px">${p.origin_region}</div>
                        <div style="font-size:10px">
                            <span style="color:#64748b">COMMODITY:</span> <span style="color:#fbbf24;font-weight:600">${p.commodity.join(', ')}</span><br>
                            <span style="color:#64748b">DISTANCE TO INDIA:</span> <span style="color:#f1f5f9;font-weight:600">${p.avg_distance_nm.toLocaleString()} NM</span>
                        </div>
                    </div>
                `);
                marker.bindTooltip(key.split(',')[0].toUpperCase(), {className: 'custom-tooltip', direction: 'top', offset: [0, -8]});
            }

            // Draw trade routes (animated lines)
            const routeColors = {
                'Iron Ore': '#ef4444', 'Coking Coal': '#f59e0b', 'Thermal Coal': '#8b5cf6',
                'Bauxite': '#ec4899', 'Grains': '#22c55e', 'Fertilizers': '#06b6d4', 'Coal': '#a78bfa'
            };
            const drawnRoutes = new Set();
            routes.forEach(r => {
                if (!r.origin_lat || !r.dest_lat) return;
                const routeKey = `${r.origin}-${r.dest}`;
                if (drawnRoutes.has(routeKey)) return;
                drawnRoutes.add(routeKey);

                const commodity = r.commodity[0] || 'Coal';
                const color = routeColors[commodity] || '#f59e0b';

                // Create curved path through midpoint
                const midLat = (r.origin_lat + r.dest_lat) / 2;
                let midLon = (r.origin_lon + r.dest_lon) / 2;
                const latOffset = (Math.abs(r.origin_lon - r.dest_lon) > 100) ? -8 : 5;

                const line = L.polyline(
                    [[r.origin_lat, r.origin_lon], [midLat + latOffset, midLon], [r.dest_lat, r.dest_lon]],
                    { color: color, weight: 1.5, opacity: 0.45, dashArray: '6 4', smoothFactor: 2 }
                ).addTo(map);

                const speed = 13; // knots average
                const transitDays = (r.distance_nm / (speed * 24)).toFixed(1);
                line.bindPopup(`
                    <div style="min-width:220px">
                        <div style="color:${color};font-weight:700;font-size:11px;margin-bottom:2px">${r.origin}</div>
                        <div style="color:#64748b;font-size:10px;margin-bottom:4px">&darr; TO &darr;</div>
                        <div style="color:#10b981;font-weight:700;font-size:11px;margin-bottom:6px">${r.dest}</div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:2px 8px;font-size:10px">
                            <span style="color:#64748b">DISTANCE:</span><span style="color:#f1f5f9;font-weight:600">${r.distance_nm.toLocaleString()} NM</span>
                            <span style="color:#64748b">TRANSIT:</span><span style="color:#f1f5f9;font-weight:600">${transitDays} DAYS</span>
                            <span style="color:#64748b">COMMODITY:</span><span style="color:#fbbf24;font-weight:600">${r.commodity.join(', ')}</span>
                            <span style="color:#64748b">BUNKER (VLSFO):</span><span style="color:#f59e0b;font-weight:600">$${bunker.vlsfo_price}/MT</span>
                        </div>
                    </div>
                `);
            });
        }
        loadMapData();
    </script>
</body>
</html>
"""

@app.get("/map", response_class=HTMLResponse)
def route_map():
    return HTMLResponse(content=MAP_HTML)

if __name__ == "__main__":
    print("Starting Baltic Exchange Freight Analytics Desk at http://127.0.0.1:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
