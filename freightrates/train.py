"""
train.py - Train and evaluate Baltic Dry Index (BDI) freight rate models with walk-forward validation.
"""

import os
import json
import numpy as np
import baltic_data
import forecasting_models

def calculate_metrics(y_true, y_pred, prev_prices=None):
    y_true = np.asarray(y_true, dtype=np.float64)
    y_pred = np.asarray(y_pred, dtype=np.float64)
    
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    mape = float(np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1e-6)))) * 100.0
    
    # R-squared
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    ss_res = np.sum((y_true - y_pred) ** 2)
    r2 = float(1.0 - (ss_res / max(ss_tot, 1e-6)))

    # Directional Accuracy (predicting market movement up/down correctly)
    if prev_prices is not None:
        actual_dir = np.sign(y_true - prev_prices)
        pred_dir = np.sign(y_pred - prev_prices)
        correct_dir = np.sum(actual_dir == pred_dir)
        dir_acc = float(correct_dir / len(y_true)) * 100.0
    else:
        dir_acc = None

    return {
        'MAE': round(mae, 2),
        'RMSE': round(rmse, 2),
        'MAPE_%': round(mape, 2),
        'R2_Score': round(r2, 4),
        'Directional_Accuracy_%': round(dir_acc, 2) if dir_acc is not None else None
    }

def train_and_evaluate(filepath='Baltic Dry Index Historical Data.csv', test_ratio=0.20):
    print("=" * 70)
    print("  BALTIC DRY INDEX (BDI) FREIGHT RATE PREDICTIVE MODEL TRAINING")
    print("=" * 70)
    
    # 1. Load Data
    print(f"\n[1/5] Loading historical data from '{filepath}'...")
    records = baltic_data.load_baltic_raw(filepath)
    print(f"      Loaded {len(records)} daily records from {records[0]['date_str']} to {records[-1]['date_str']}.")

    # 2. Compute Features
    print("\n[2/5] Calculating technical indicators, momentum, volatility & seasonality...")
    enriched, raw_records = baltic_data.calculate_technical_indicators(records)
    X, y_prices, y_returns, feature_names = baltic_data.extract_feature_matrix(enriched)
    print(f"      Feature matrix: {X.shape[0]} samples x {X.shape[1]} features.")
    
    # Exclude last row since forward return is unknown for future
    X_samples = X[:-1]
    y_ret_samples = y_returns[:-1]
    prev_prices = y_prices[:-1]
    actual_next_prices = y_prices[1:]
    
    # 3. Time-Series Train/Test Split (Walk-Forward Out-Of-Sample)
    split_idx = int(len(X_samples) * (1.0 - test_ratio))
    X_train, X_test = X_samples[:split_idx], X_samples[split_idx:]
    y_train, y_test = y_ret_samples[:split_idx], y_ret_samples[split_idx:]
    test_prev = prev_prices[split_idx:]
    test_actual = actual_next_prices[split_idx:]
    
    train_dates = (enriched[0]['date_str'], enriched[split_idx - 1]['date_str'])
    test_dates = (enriched[split_idx]['date_str'], enriched[-2]['date_str'])
    print(f"\n[3/5] Time-series Split:")
    print(f"      Train Set: {len(X_train)} trading days ({train_dates[0]} to {train_dates[1]})")
    print(f"      Test Set : {len(X_test)} trading days ({test_dates[0]} to {test_dates[1]})")

    # 4. Train Individual Models & Evaluate Out-of-Sample
    print("\n[4/5] Training predictive models on Train Set and testing out-of-sample...")
    
    models = {
        'Ridge Regression': forecasting_models.RidgeForecaster(alpha=25.0).fit(X_train, y_train),
        'Gradient Boosted Trees (GBDT)': forecasting_models.GBDTForecaster(n_estimators=45, learning_rate=0.04, max_depth=3).fit(X_train, y_train),
        'Deep Neural Network (MLP)': forecasting_models.DeepNeuralNetForecaster(hidden_dims=(32, 16), lr=0.008, epochs=250).fit(X_train, y_train),
    }

    metrics_summary = {}
    test_predictions = {}

    for name, model in models.items():
        ret_preds = np.clip(model.predict(X_test), -0.05, 0.05)
        price_preds = test_prev * (1.0 + ret_preds)
        test_predictions[name] = price_preds
        m = calculate_metrics(test_actual, price_preds, test_prev)
        metrics_summary[name] = m
        print(f"\n   -> {name}:")
        print(f"      MAE: ${m['MAE']:.2f} | RMSE: ${m['RMSE']:.2f} | MAPE: {m['MAPE_%']:.2f}% | Directional Acc: {m['Directional_Accuracy_%']:.2f}% | R2: {m['R2_Score']:.4f}")

    # Meta Ensemble
    ensemble = forecasting_models.MetaEnsembleForecaster().fit(X_train, y_train, [r['price'] for r in records[:split_idx]])
    ens_test_preds = np.zeros(len(X_test))
    for i in range(len(X_test)):
        step_res = ensemble.predict_step(X_test[i:i+1])
        ens_test_preds[i] = test_prev[i] * (1.0 + step_res['ensemble'])
    
    ens_metrics = calculate_metrics(test_actual, ens_test_preds, test_prev)
    metrics_summary['Weighted Meta-Ensemble'] = ens_metrics
    print(f"\n   -> Weighted Meta-Ensemble:")
    print(f"      MAE: ${ens_metrics['MAE']:.2f} | RMSE: ${ens_metrics['RMSE']:.2f} | MAPE: {ens_metrics['MAPE_%']:.2f}% | Directional Acc: {ens_metrics['Directional_Accuracy_%']:.2f}% | R2: {ens_metrics['R2_Score']:.4f}")
    print(f"      Ensemble Model Weights: {json.dumps({k: round(v, 3) for k, v in ensemble.weights.items()})}")

    # 5. Fit Full Ensemble on 100% Data for Future Production Forecasting
    print("\n[5/5] Fitting final Production Meta-Ensemble on complete Baltic Dry Index dataset...")
    full_ensemble = forecasting_models.MetaEnsembleForecaster().fit(X_samples, y_ret_samples, [r['price'] for r in records])

    # Sample 30-day future forecast
    sample_forecast = full_ensemble.forecast_multistep(records, steps=30)
    print(f"      Generated 30-day sample forecast from {sample_forecast[0]['date']} (${sample_forecast[0]['predicted_price']}) to {sample_forecast[-1]['date']} (${sample_forecast[-1]['predicted_price']})")
    
    # Save Report
    os.makedirs('models', exist_ok=True)
    report = {
        'total_historical_records': len(records),
        'date_range': {'start': records[0]['date_str'], 'end': records[-1]['date_str']},
        'features_used': feature_names,
        'train_split': {'count': len(X_train), 'start': train_dates[0], 'end': train_dates[1]},
        'test_split': {'count': len(X_test), 'start': test_dates[0], 'end': test_dates[1]},
        'model_metrics': metrics_summary,
        'ensemble_weights': ensemble.weights,
        'latest_rate': records[-1]['price'],
        'latest_date': records[-1]['date_str'],
        'sample_30d_forecast': sample_forecast
    }

    report_path = os.path.join('models', 'model_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\nSaved trained model evaluation report to: '{report_path}'")

    return full_ensemble, records, report

if __name__ == '__main__':
    train_and_evaluate('Baltic Dry Index Historical Data.csv')

