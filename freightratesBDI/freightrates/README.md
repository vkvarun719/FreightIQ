# FreightIQ 2026: Intelligent Freight Rate Forecasting & Chartering Optimization

An enterprise AI decision support platform designed for dry bulk logistics managers, charterers, and supply chain directors. Powered by the **Baltic Dry Index (BDI)** historical market dataset (`Baltic Dry Index Historical Data.csv`), it transforms daily reactive chartering into a proactive, data-driven predictive strategy.

---

## 1. Executive Capabilities (All 4 Core Requirements)

### a. Optimal Market Entry Timing
* Predicts freight rate trajectories across **Capesize, Panamax, Supramax, and Handysize** classes derived from the Baltic Dry Index composite benchmark.
* Identifies optimal chartering windows over short-term (1-3 months) and mid-term (6-12 months) horizons.
* Quantifies cost savings deltas between prompt spot execution and strategic deferred entry.

### b. Vessel Type & Port Infrastructure Optimization (India East Coast)
* Models comprehensive navigational restrictions across all major East Coast ports:
  * **Dhamra Port (DPCL)** (Max draft: 18.5m | LOA: 320m)
  * **Gangavaram Port** (Max draft: 19.0m | LOA: 310m)
  * **Krishnapatnam Port (KPCT)** (Max draft: 18.0m | LOA: 300m)
  * **Visakhapatnam Port (VPA)** (Outer Harbour: 16.5m draft | Inner: 11.5m)
  * **Paradip Port (PPT)** (Max draft: 16.0m | LOA: 285m)
  * **Kamarajar / Ennore Port** (Max draft: 16.0m | LOA: 270m)
  * **Chennai Port (ChPA)** (Max draft: 14.0m | LOA: 250m)
  * **Haldia Dock Complex (KOPT)** (Severe Hooghly riverine draft limit: 8.5m)
* Evaluates cargo parcel volumes against vessel capacity, voyage transit days, berth handling discharge rates (TPD), total turnaround stay, and demurrage exposure to recommend the lowest **Freight Cost per Metric Ton ($/MT)**.

### c. Idle Scenario Management & Deadheading Elimination
* Projects seasonal low-demand windows (e.g. post-CNY lull, monsoon port slowdowns).
* Proposes actionable triangulation and backhaul employments:
  * **Domestic Coastal Coal Cabotage** (East-to-South Coast power utilities)
  * **Southeast Asia Agricultural / Bauxite Backhaul**
  * **Indian Ocean Triangulation** (e.g. Richards Bay or Western Australia positioning)
* Quantifies ballast nautical miles eliminated and net Time Charter Equivalent (TCE) boost.

### d. Risk Mitigation & Early Warning System
* **Market Volatility Index**: Early warning alerts for standard deviation spikes and FFA hedging triggers.
* **Bay of Bengal Meteorological Alerts**: Tracks South-West Monsoon swell and North-East post-monsoon cyclone windows (Oct-Dec) to prevent port clearance suspensions.
* **Port Congestion Risk**: Predicts waiting queues and recommends protective charter party clauses (e.g., WIBON - Whether In Berth Or Not).

---

## 2. Quick Start & Usage

### Launch Interactive Web Dashboard
```bash
python app.py
```
Open **`http://127.0.0.1:8000`** in your browser to access the live interactive simulator.

### Run via Command Line (CLI)
Forecast a 75,000 MT Coking Coal shipment from Hay Point Australia to Visakhapatnam:
```bash
python predict.py --commodity "Coking Coal" --volume 75000 --origin "Hay Point / Dalrymple, Australia" --dest "Visakhapatnam" --days 60
```
Export multi-vessel forecasts to CSV:
```bash
python predict.py --days 90 --output forecast_2026.csv
```
