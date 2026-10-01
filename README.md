# FreightIQ (Baltic Capesize Predictive AI) 🚢

An end-to-end machine learning suite built to forecast Baltic Capesize freight rates using historical market data. 

## 🌟 Project Overview
This project is a comprehensive time-series forecasting platform designed to predict maritime freight rates. It features a robust data pipeline that engineers technical indicators and feeds them into a custom Weighted Meta-Ensemble model to achieve high-accuracy predictions.

## 🚀 Key Features
* **Advanced Feature Engineering:** Automatically computes technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, Volatility) and seasonality encodings.
* **Custom ML Architectures:** Includes implementations of Ridge Regression, Gradient Boosted Trees (GBDT), Deep Neural Networks (MLP), and Holt-Winters Exponential Smoothing.
* **Weighted Meta-Ensemble:** Combines base models to achieve robust out-of-sample forecasting with a directional accuracy of ~62.6%.
* **Interactive Web Dashboard:** A FastAPI backend serving a live web interface with interactive chart visualizations.
* **CLI Integration:** Dedicated scripts for walk-forward validation model training and customizable future rate predictions (exportable to CSV/JSON).

## 💻 Tech Stack
* **Python** (FastAPI, Uvicorn)
* **Machine Learning** (Scikit-Learn, Numpy, Pandas)
* **Frontend** (HTML/JS/Chart.js)

## ⚙️ How to Run Locally


```bash
pip install fastapi uvicorn pandas numpy scikit-learn
Start the Backend Server:
python app.py
View the Dashboard: Open your browser and navigate to http://localhost:8000
