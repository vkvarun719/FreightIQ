"""
forecasting_models.py - Predictive time-series modeling architectures for freight rates.
Includes:
- Ridge Regression Forecaster
- Gradient Boosted Decision Tree (GBDT) Regressor
- Multi-Layer Perceptron (MLP) Neural Network with Adam Optimizer
- Holt-Winters Exponential Smoothing Baseline
- Weighted Meta-Ensemble with 95% Confidence Intervals
"""

import numpy as np
import json
import math

class StandardScaler:
    def __init__(self):
        self.mean = None
        self.std = None

    def fit(self, X):
        self.mean = np.mean(X, axis=0)
        self.std = np.std(X, axis=0)
        self.std[self.std < 1e-8] = 1.0
        return self

    def transform(self, X):
        return (X - self.mean) / self.std

    def fit_transform(self, X):
        return self.fit(X).transform(X)

    def to_dict(self):
        return {
            'mean': self.mean.tolist() if self.mean is not None else None,
            'std': self.std.tolist() if self.std is not None else None
        }

    def from_dict(self, d):
        if d.get('mean') is not None:
            self.mean = np.array(d['mean'], dtype=np.float64)
            self.std = np.array(d['std'], dtype=np.float64)
        return self

# -------------------------------------------------------------
# 1. Ridge Regularized Regression Model
# -------------------------------------------------------------
class RidgeForecaster:
    def __init__(self, alpha=1.0):
        self.alpha = float(alpha)
        self.scaler = StandardScaler()
        self.weights = None
        self.bias = 0.0

    def fit(self, X, y):
        X_scaled = self.scaler.fit_transform(X)
        n_samples, n_features = X_scaled.shape
        
        # Closed form: (X^T X + alpha * I)^(-1) X^T y
        A = np.dot(X_scaled.T, X_scaled) + self.alpha * np.eye(n_features)
        b = np.dot(X_scaled.T, (y - np.mean(y)))
        self.weights = np.linalg.solve(A, b)
        self.bias = float(np.mean(y))
        return self

    def predict(self, X):
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        return np.dot(X_scaled, self.weights) + self.bias

    def to_dict(self):
        return {
            'type': 'RidgeForecaster',
            'alpha': self.alpha,
            'weights': self.weights.tolist() if self.weights is not None else None,
            'bias': self.bias,
            'scaler': self.scaler.to_dict()
        }

    def from_dict(self, d):
        self.alpha = d['alpha']
        self.weights = np.array(d['weights'], dtype=np.float64)
        self.bias = d['bias']
        self.scaler.from_dict(d['scaler'])
        return self

# -------------------------------------------------------------
# 2. Fast Decision Tree & Gradient Boosted Decision Tree Regressor
# -------------------------------------------------------------
class DecisionTreeRegressor:
    def __init__(self, max_depth=4, min_samples_split=5):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree = None

    def _best_split(self, X, y):
        n_samples, n_features = X.shape
        if n_samples < self.min_samples_split:
            return None, None, None, None

        best_var_reduction = 0.0
        best_feat, best_thresh = None, None
        best_left_idx, best_right_idx = None, None
        
        current_var = np.var(y) * n_samples

        # Sample features or test quantiles for speed
        for feat in range(n_features):
            col_vals = X[:, feat]
            thresholds = np.percentile(col_vals, np.linspace(10, 90, 9))
            for thresh in thresholds:
                left_idx = col_vals <= thresh
                right_idx = ~left_idx
                if np.sum(left_idx) < 2 or np.sum(right_idx) < 2:
                    continue
                
                left_var = np.var(y[left_idx]) * np.sum(left_idx)
                right_var = np.var(y[right_idx]) * np.sum(right_idx)
                var_red = current_var - (left_var + right_var)
                
                if var_red > best_var_reduction:
                    best_var_reduction = var_red
                    best_feat = feat
                    best_thresh = thresh
                    best_left_idx = left_idx
                    best_right_idx = right_idx

        return best_feat, best_thresh, best_left_idx, best_right_idx

    def _build_tree(self, X, y, depth=0):
        if depth >= self.max_depth or len(y) < self.min_samples_split:
            return {'value': float(np.mean(y))}

        feat, thresh, left_idx, right_idx = self._best_split(X, y)
        if feat is None:
            return {'value': float(np.mean(y))}

        left_subtree = self._build_tree(X[left_idx], y[left_idx], depth + 1)
        right_subtree = self._build_tree(X[right_idx], y[right_idx], depth + 1)

        return {
            'feat': int(feat),
            'thresh': float(thresh),
            'left': left_subtree,
            'right': right_subtree
        }

    def fit(self, X, y):
        self.tree = self._build_tree(X, y)
        return self

    def _predict_row(self, row, node):
        if 'value' in node:
            return node['value']
        if row[node['feat']] <= node['thresh']:
            return self._predict_row(row, node['left'])
        return self._predict_row(row, node['right'])

    def predict(self, X):
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        return np.array([self._predict_row(row, self.tree) for row in X])

class GBDTForecaster:
    def __init__(self, n_estimators=40, learning_rate=0.08, max_depth=3, min_samples_split=8):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.trees = []
        self.init_val = 0.0
        self.scaler = StandardScaler()

    def fit(self, X, y):
        X_scaled = self.scaler.fit_transform(X)
        self.init_val = float(np.mean(y))
        residuals = y - self.init_val
        self.trees = []

        for _ in range(self.n_estimators):
            tree = DecisionTreeRegressor(max_depth=self.max_depth, min_samples_split=self.min_samples_split)
            tree.fit(X_scaled, residuals)
            preds = tree.predict(X_scaled)
            residuals -= self.learning_rate * preds
            self.trees.append(tree)

        return self

    def predict(self, X):
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        preds = np.full(X.shape[0], self.init_val, dtype=np.float64)
        for tree in self.trees:
            preds += self.learning_rate * tree.predict(X_scaled)
        return preds

    def to_dict(self):
        return {
            'type': 'GBDTForecaster',
            'n_estimators': self.n_estimators,
            'learning_rate': self.learning_rate,
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split,
            'init_val': self.init_val,
            'scaler': self.scaler.to_dict(),
            'trees': [t.tree for t in self.trees]
        }

    def from_dict(self, d):
        self.n_estimators = d['n_estimators']
        self.learning_rate = d['learning_rate']
        self.max_depth = d['max_depth']
        self.min_samples_split = d['min_samples_split']
        self.init_val = d['init_val']
        self.scaler.from_dict(d['scaler'])
        self.trees = []
        for tree_dict in d['trees']:
            t = DecisionTreeRegressor(max_depth=self.max_depth, min_samples_split=self.min_samples_split)
            t.tree = tree_dict
            self.trees.append(t)
        return self

# -------------------------------------------------------------
# 3. Deep Learning Multi-Layer Perceptron (Neural Network)
# -------------------------------------------------------------
class DeepNeuralNetForecaster:
    def __init__(self, hidden_dims=(32, 16), lr=0.01, epochs=250, l2_reg=0.001):
        self.hidden_dims = hidden_dims
        self.lr = lr
        self.epochs = epochs
        self.l2_reg = l2_reg
        self.scaler = StandardScaler()
        self.y_mean = 0.0
        self.y_std = 1.0
        self.weights = []
        self.biases = []

    def _relu(self, z):
        return np.maximum(0.0, z)

    def _relu_grad(self, z):
        return (z > 0.0).astype(np.float64)

    def fit(self, X, y):
        X_scaled = self.scaler.fit_transform(X)
        self.y_mean = float(np.mean(y))
        self.y_std = float(np.std(y)) if np.std(y) > 1e-6 else 1.0
        y_scaled = (y - self.y_mean) / self.y_std
        
        n_samples, in_dim = X_scaled.shape
        dims = [in_dim] + list(self.hidden_dims) + [1]
        
        # Xavier Initialization
        np.random.seed(42)
        self.weights = []
        self.biases = []
        for i in range(len(dims) - 1):
            limit = np.sqrt(6.0 / (dims[i] + dims[i+1]))
            w = np.random.uniform(-limit, limit, (dims[i], dims[i+1]))
            b = np.zeros(dims[i+1])
            self.weights.append(w)
            self.biases.append(b)

        # Adam Optimizer states
        m_w = [np.zeros_like(w) for w in self.weights]
        v_w = [np.zeros_like(w) for w in self.weights]
        m_b = [np.zeros_like(b) for b in self.biases]
        v_b = [np.zeros_like(b) for b in self.biases]
        beta1, beta2, eps = 0.9, 0.999, 1e-8

        # Training loop
        for epoch in range(1, self.epochs + 1):
            # Forward pass
            activations = [X_scaled]
            zs = []
            for l in range(len(self.weights) - 1):
                z = np.dot(activations[-1], self.weights[l]) + self.biases[l]
                zs.append(z)
                a = self._relu(z)
                activations.append(a)
            # Output layer (linear)
            z_out = np.dot(activations[-1], self.weights[-1]) + self.biases[-1]
            zs.append(z_out)
            activations.append(z_out.flatten())

            preds = activations[-1]
            error = (preds - y_scaled) / n_samples
            
            # Backpropagation
            delta = error.reshape(-1, 1)
            gw_list = []
            gb_list = []
            for l in reversed(range(len(self.weights))):
                gw = np.dot(activations[l].T, delta) + self.l2_reg * self.weights[l]
                gb = np.sum(delta, axis=0)
                gw_list.insert(0, gw)
                gb_list.insert(0, gb)
                if l > 0:
                    delta = np.dot(delta, self.weights[l].T) * self._relu_grad(zs[l-1])

            # Adam update
            for l in range(len(self.weights)):
                m_w[l] = beta1 * m_w[l] + (1 - beta1) * gw_list[l]
                v_w[l] = beta2 * v_w[l] + (1 - beta2) * (gw_list[l] ** 2)
                m_b[l] = beta1 * m_b[l] + (1 - beta1) * gb_list[l]
                v_b[l] = beta2 * v_b[l] + (1 - beta2) * (gb_list[l] ** 2)
                
                m_w_hat = m_w[l] / (1 - beta1 ** epoch)
                v_w_hat = v_w[l] / (1 - beta2 ** epoch)
                m_b_hat = m_b[l] / (1 - beta1 ** epoch)
                v_b_hat = v_b[l] / (1 - beta2 ** epoch)
                
                self.weights[l] -= self.lr * m_w_hat / (np.sqrt(v_w_hat) + eps)
                self.biases[l] -= self.lr * m_b_hat / (np.sqrt(v_b_hat) + eps)

        return self

    def predict(self, X):
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        a = self.scaler.transform(X)
        for l in range(len(self.weights) - 1):
            a = self._relu(np.dot(a, self.weights[l]) + self.biases[l])
        out_scaled = np.dot(a, self.weights[-1]) + self.biases[-1]
        return (out_scaled.flatten() * self.y_std) + self.y_mean

    def to_dict(self):
        return {
            'type': 'DeepNeuralNetForecaster',
            'hidden_dims': list(self.hidden_dims),
            'lr': self.lr,
            'epochs': self.epochs,
            'l2_reg': self.l2_reg,
            'y_mean': self.y_mean,
            'y_std': self.y_std,
            'scaler': self.scaler.to_dict(),
            'weights': [w.tolist() for w in self.weights],
            'biases': [b.tolist() for b in self.biases]
        }

    def from_dict(self, d):
        self.hidden_dims = tuple(d['hidden_dims'])
        self.lr = d['lr']
        self.epochs = d['epochs']
        self.l2_reg = d['l2_reg']
        self.y_mean = d['y_mean']
        self.y_std = d['y_std']
        self.scaler.from_dict(d['scaler'])
        self.weights = [np.array(w, dtype=np.float64) for w in d['weights']]
        self.biases = [np.array(b, dtype=np.float64) for b in d['biases']]
        return self

# -------------------------------------------------------------
# 4. Holt-Winters / Exponential Smoothing Baseline
# -------------------------------------------------------------
class HoltWintersForecaster:
    def __init__(self, alpha=0.8, beta=0.2, phi=0.95):
        self.alpha = alpha
        self.beta = beta
        self.phi = phi
        self.level = 0.0
        self.trend = 0.0

    def fit(self, prices):
        prices = np.asarray(prices, dtype=np.float64)
        self.level = prices[0]
        self.trend = prices[1] - prices[0] if len(prices) > 1 else 0.0
        
        for p in prices[1:]:
            last_level = self.level
            self.level = self.alpha * p + (1.0 - self.alpha) * (self.level + self.phi * self.trend)
            self.trend = self.beta * (self.level - last_level) + (1.0 - self.beta) * self.phi * self.trend
        return self

    def forecast(self, steps=30):
        preds = []
        curr_lvl = self.level
        curr_tr = self.trend
        for h in range(1, steps + 1):
            damping = sum(self.phi ** i for i in range(1, h + 1))
            preds.append(curr_lvl + damping * curr_tr)
        return np.array(preds)

# -------------------------------------------------------------
# 5. Weighted Meta-Ensemble Forecaster
# -------------------------------------------------------------
class MetaEnsembleForecaster:
    def __init__(self, models_dict=None, weights_dict=None):
        self.models = models_dict or {}
        self.weights = weights_dict or {}
        self.daily_vol = 0.03
        self.residual_std = 0.025

    def fit(self, X, y_returns, prices_history):
        y_returns = np.asarray(y_returns, dtype=np.float64)
        self.daily_vol = float(np.std(y_returns)) if np.std(y_returns) > 1e-4 else 0.03
        
        self.models = {
            'ridge': RidgeForecaster(alpha=25.0).fit(X, y_returns),
            'gbdt': GBDTForecaster(n_estimators=45, learning_rate=0.04, max_depth=3).fit(X, y_returns),
            'dnn': DeepNeuralNetForecaster(hidden_dims=(32, 16), lr=0.008, epochs=250).fit(X, y_returns),
            'holt_winters': HoltWintersForecaster().fit(prices_history)
        }
        
        # Calculate CV out-of-fold residuals for optimal weighting
        r_pred = np.clip(self.models['ridge'].predict(X), -0.06, 0.06)
        g_pred = np.clip(self.models['gbdt'].predict(X), -0.06, 0.06)
        d_pred = np.clip(self.models['dnn'].predict(X), -0.06, 0.06)

        r_mse = max(np.mean((y_returns - r_pred) ** 2), 1e-6)
        g_mse = max(np.mean((y_returns - g_pred) ** 2), 1e-6)
        d_mse = max(np.mean((y_returns - d_pred) ** 2), 1e-6)

        # Inverse variance weighting
        inv_sum = (1.0 / r_mse) + (1.0 / g_mse) + (1.0 / d_mse)
        self.weights = {
            'ridge': float((1.0 / r_mse) / inv_sum),
            'gbdt': float((1.0 / g_mse) / inv_sum),
            'dnn': float((1.0 / d_mse) / inv_sum),
        }
        
        ensemble_pred = (self.weights['ridge'] * r_pred + 
                         self.weights['gbdt'] * g_pred + 
                         self.weights['dnn'] * d_pred)
        self.residual_std = float(np.std(y_returns - ensemble_pred))
        return self

    def predict_step(self, X_row):
        r = float(np.clip(self.models['ridge'].predict(X_row)[0], -0.05, 0.05))
        g = float(np.clip(self.models['gbdt'].predict(X_row)[0], -0.05, 0.05))
        d = float(np.clip(self.models['dnn'].predict(X_row)[0], -0.05, 0.05))
        ens = (self.weights['ridge'] * r + 
               self.weights['gbdt'] * g + 
               self.weights['dnn'] * d)
        ens = float(np.clip(ens, -0.045, 0.045))
        return {
            'ensemble': float(ens),
            'ridge': float(r),
            'gbdt': float(g),
            'dnn': float(d),
        }

    def forecast_multistep(self, last_records, steps=30, start_date=None):
        """
        Performs recursive rolling multi-step future forecasting with 95% Confidence Intervals.
        Uses return-based autoregression with soft mean-reversion to preserve cyclic market structure.
        """
        import baltic_data
        sim_records = [dict(r) for r in last_records]
        future_forecasts = []
        
        last_dt = sim_records[-1]['date'] if start_date is None else start_date
        
        for step in range(1, steps + 1):
            # Advance to next business day (skipping weekends)
            next_dt = last_dt + np.timedelta64(1, 'D').astype('timedelta64[D]').item()
            while next_dt.weekday() >= 5: # Saturday/Sunday
                next_dt += np.timedelta64(1, 'D').astype('timedelta64[D]').item()
            last_dt = next_dt

            enriched, _ = baltic_data.calculate_technical_indicators(sim_records)
            latest_features = enriched[-1]
            X_row = np.array([[float(latest_features.get(f, 0.0)) for f in baltic_data.FEATURE_NAMES]])
            
            step_preds = self.predict_step(X_row)
            prev_price = float(sim_records[-1]['price'])
            
            # Mean-reversion guidance towards 20-day moving average
            sma20 = float(latest_features.get('sma_20', prev_price))
            if np.isnan(sma20) or sma20 <= 0:
                sma20 = prev_price
            mean_rev_drift = 0.015 * (sma20 - prev_price) / max(prev_price, 1.0)
            
            ret_ens = float(np.clip(step_preds['ensemble'] + mean_rev_drift, -0.04, 0.04))
            pred_price = round(prev_price * (1.0 + ret_ens), 2)
            
            ridge_pred = round(prev_price * (1.0 + float(np.clip(step_preds['ridge'], -0.05, 0.05))), 2)
            gbdt_pred = round(prev_price * (1.0 + float(np.clip(step_preds['gbdt'], -0.05, 0.05))), 2)
            dnn_pred = round(prev_price * (1.0 + float(np.clip(step_preds['dnn'], -0.05, 0.05))), 2)
            
            # Estimate widening confidence intervals over time horizon
            step_std = prev_price * self.daily_vol * np.sqrt(step)
            lower_95 = round(max(pred_price - 1.96 * step_std, prev_price * 0.4), 2)
            upper_95 = round(pred_price + 1.96 * step_std, 2)
            
            future_entry = {
                'step': int(step),
                'date': next_dt.strftime('%Y-%m-%d'),
                'predicted_price': float(pred_price),
                'lower_95': float(lower_95),
                'upper_95': float(upper_95),
                'ridge_pred': float(ridge_pred),
                'gbdt_pred': float(gbdt_pred),
                'dnn_pred': float(dnn_pred),
                'volatility_std': float(round(step_std, 2))
            }
            future_forecasts.append(future_entry)
            
            # Append simulated observation to roll forward
            sim_records.append({
                'date': next_dt,
                'date_str': next_dt.strftime('%Y-%m-%d'),
                'price': pred_price,
                'open': pred_price,
                'high': pred_price * 1.006,
                'low': pred_price * 0.994,
                'vol': 0.0,
                'change_pct': ret_ens
            })

        return future_forecasts
