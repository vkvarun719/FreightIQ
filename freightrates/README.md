# Baltic Dry Index (BDI) Freight Intelligence & Chartering Optimization Desk (2014–2026)

An institutional-grade commercial freight intelligence and decision support platform for dry bulk charterers, vessel operators, commodity traders, and maritime supply chain directors. Powered by **10+ years of daily Baltic Dry Index (BDI) historical settlements** (3,160 trading sessions spanning 2014 through 2026).

---

## 1. Quantitative Model Architectures & 10-Year Walk-Forward Benchmark

The platform utilizes a **Super Learner Stacking Meta-Ensemble** trained and evaluated via walk-forward out-of-sample backtesting across full market cycles (commodity slump of 2016, pandemic disruptions of 2020–2022, Red Sea canal diversions, and 2024–2026 rate recoveries):

| Model Architecture | Out-of-Sample MAE | Out-of-Sample RMSE | MAPE (%) | Directional Accuracy (%) | $R^2$ Score |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Gradient Boosted Trees (GBDT)** | **$34.92** | **$47.83** | **1.84%** | **70.97%** | **0.9927** |
| **Deep Neural Network (MLP-ResNet)** | $36.26 | $49.48 | 1.90% | **70.97%** | 0.9922 |
| **Ridge Autoregressive AR(60)** | $35.54 | $48.91 | 1.87% | 69.68% | 0.9924 |
| **Super Learner Meta-Ensemble** | **$36.49** | **$50.02** | **1.90%** | **69.52%** | **0.9921** |

* **Feature Matrix (34 Dimensional)**: 
  - Multi-Scale Moving Averages (SMA 5, 10, 20, 50, 100, 200) & Golden/Death Cross indicator
  - Exponential Moving Averages (EMA 12, 26), MACD, Signal, Histogram
  - Relative Strength Index (RSI-14) & Momentum Rate of Change (ROC 5, 20, 60)
  - Multi-Scale Volatility (Rolling Std 5, 20, 60), Parkinson High-Low Volatility, Bollinger Bands
  - Multi-Frequency Fourier Harmonics (Annual 365.25d, Semi-Annual 182.6d, Quarterly 91.3d)
  - Autoregressive Return Lags (Lags 1, 2, 3, 5, 10, 20, 30, 60)

---

## 2. Institutional Desk Capabilities (Requirements A, B, C, D)

### a. Optimal Market Entry & Fixture Timing
- Projects cyclical rate troughs across **Capesize (180k DWT), Panamax (82k DWT), Supramax (60k DWT), and Handysize (35k DWT)**.
- Recommends actionable fixture windows (Immediate Prompt vs Deferred Strategic Window) with quantified dollar savings vs prompt entry.

### b. Vessel Class & Port Infrastructure Optimization (India East Coast)
- Evaluates physical navigation constraints across all major East Coast India bulk terminals:
  - **Dhamra Port (DPCL)** (Max draft: 18.5m | LOA: 320m)
  - **Gangavaram Port** (Max draft: 19.0m | LOA: 310m)
  - **Krishnapatnam Port (KPCT)** (Max draft: 18.0m | LOA: 300m)
  - **Visakhapatnam Port (VPA)** (Outer Harbour: 16.5m draft | Inner: 11.5m)
  - **Paradip Port (PPT)** (Max draft: 16.0m | LOA: 285m)
  - **Kamarajar / Ennore Port** (Max draft: 16.0m | LOA: 270m)
  - **Chennai Port (ChPA)** (Max draft: 14.0m | LOA: 250m)
  - **Haldia Dock Complex (KOPT)** (Restricted Hooghly draft: 8.5m)
- Calculates complete voyage economics: net freight cost per metric ton ($/MT), sea transit days, port turnaround stay (TPD), bunker consumption (VLSFO @ $615/MT), port dues, and demurrage exposure.

### c. Idle Fleet & Backhaul Triangulation Optimization
- Proposes actionable coastal triangulation routes post-discharge to eliminate empty deadhead ballasting (e.g. Paradip-to-South Coast domestic coal cabotage, Kakinada agricultural grains/bauxite export, Indian Ocean triangulation loops).

### d. Early Warning & Meteorological Risk Matrix
- **Market Volatility Index**: Early warning alerts for variance spikes and FFA hedging triggers.
- **Bay of Bengal Meteorological Alerts**: Tracks South-West Monsoon swell and North-East post-monsoon cyclone seasons (Oct–Dec).
- **Port Congestion & Queue Tracking**: Projects berth waiting times and enforces protective charter terms (WIBON / WIPON).

---

## 3. Quick Start & Usage

### Launch Interactive Workstation (Browser UI)
```bash
python app.py
```
Open **`http://127.0.0.1:8000`** in your browser.

### Run Model Training & Walk-Forward Cross-Validation
```bash
python train.py
```
Outputs comprehensive performance metrics to `models/model_report.json`.

### Run via Command Line Interface (CLI)
```bash
python predict.py --commodity "Coking Coal" --volume 75000 --origin "Hay Point / Dalrymple, Australia" --dest "Visakhapatnam" --days 30
```

---

## 4. Live BDI Data Auto-Update via Web Scraping & Daily Retraining

To prevent model stale-out, the platform includes an automated live scraping and retraining pipeline:

### Features:
- **Multi-Source Scraping**: Pulls live daily Baltic Dry Index settlements from TradingEconomics, Investing.com, and Hellenic Shipping News.
- **CSV Synchronization & Deduplication**: Inserts new settlement records (`"Date","Price","Open","High","Low","Vol.","Change %"`) into `Baltic Dry Index Historical Data.csv` without duplicate rows.
- **Automated Model Retraining**: Automatically runs walk-forward cross validation and recalibrates the Ridge AR, GBDT, Deep MLP, and Super Learner Meta-Ensemble models, updating `models/model_report.json` and 30/90-day forward forecasts.
- **In-App Web 1-Click Sync**: Click the **`[LIVE AUTO-SYNC]`** button in the header of `http://127.0.0.1:8000` to trigger on-demand scraping and hot-reload model forecasts.

### Command-Line Usage:
```bash
# Run scrape, CSV sync, and model retraining right now:
python bdi_live_scraper.py --run-now

# Test scraping connectivity without modifying datasets or retraining:
python bdi_live_scraper.py --test-scrape

# Force update and retraining even if current date is already present:
python bdi_live_scraper.py --force

# Run continuous background daemon scheduled daily at 18:30 local time:
python bdi_live_scraper.py --schedule 18:30

# Run periodic background daemon checking every 6 hours:
python bdi_live_scraper.py --interval 6
```

### Windows OS Task Scheduler Automation:
To run silent daily updates automatically without keeping a terminal open:
1. Double click or run **`setup_windows_task.bat`**.
2. It registers the Windows Scheduled Task `BDI_Freight_Daily_Update` to execute **`run_daily_update.bat`** daily at 18:30.
3. Execution logs are stored at **`logs/scraper.log`**.

