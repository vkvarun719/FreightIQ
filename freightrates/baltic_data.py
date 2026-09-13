"""
baltic_data.py - High-Performance Data Ingestion and Multi-Decade Feature Engineering
for Baltic Dry Index (BDI) Freight Rate Analytics & Forecasting (2014-2026).
"""

import csv
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import numpy as np
import os

def decode_excel_date(val_str):
    """Parses various date formats from CSV / Excel into datetime."""
    if not val_str:
        return None
    val_str = str(val_str).strip(' "')
    
    # Try numeric Excel serial date
    try:
        serial = float(val_str)
        dt_excel = datetime(1899, 12, 30) + timedelta(days=serial)
        return dt_excel
    except ValueError:
        pass
    
    # Try common date string formats
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y', '%b %d, %Y', '%d-%b-%y', '%d-%m-%Y'):
        try:
            return datetime.strptime(val_str, fmt)
        except ValueError:
            continue
    return None

def clean_float(val_str):
    """Sanitizes numerical strings by removing commas, percentage signs, and whitespace."""
    if val_str is None:
        return None
    val_str = str(val_str).replace(',', '').replace('%', '').strip(' "')
    try:
        return float(val_str)
    except ValueError:
        return None

def load_baltic_raw(filepath='Baltic Dry Index Historical Data.csv'):
    """
    Extracts raw historical records from CSV or Excel (.xlsx) file.
    Searches local directory, parent directory, and workspace root automatically.
    """
    candidate_paths = [
        filepath,
        os.path.join(os.path.dirname(__file__), filepath),
        os.path.join(os.path.dirname(__file__), '..', filepath),
        os.path.join(os.path.dirname(__file__), 'Baltic Dry Index Historical Data.csv'),
        'Baltic Dry Index Historical Data.csv',
        '../Baltic Dry Index Historical Data.csv',
        'Book1.csv',
        'Book1.xlsx'
    ]
    
    target_path = None
    for p in candidate_paths:
        if p and os.path.exists(p):
            target_path = p
            break
            
    if not target_path:
        raise FileNotFoundError(f"Baltic Dry Index data file '{filepath}' not found in candidate paths: {candidate_paths}")

    records = []

    if target_path.lower().endswith('.csv'):
        with open(target_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for r in reader:
                if not r or len(r) < 2:
                    continue
                date_raw = r[0].strip(' "')
                price_raw = r[1]
                open_raw = r[2] if len(r) > 2 and r[2].strip() else price_raw
                high_raw = r[3] if len(r) > 3 and r[3].strip() else price_raw
                low_raw = r[4] if len(r) > 4 and r[4].strip() else price_raw
                vol_raw = r[5] if len(r) > 5 else ''
                change_raw = r[6] if len(r) > 6 else '0'

                dt = decode_excel_date(date_raw)
                price = clean_float(price_raw)
                open_p = clean_float(open_raw)
                high_p = clean_float(high_raw)
                low_p = clean_float(low_raw)
                vol = clean_float(vol_raw)
                change = clean_float(change_raw)

                if dt is not None and price is not None:
                    records.append({
                        'date': dt,
                        'date_str': dt.strftime('%Y-%m-%d'),
                        'price': price,
                        'open': open_p if open_p is not None else price,
                        'high': high_p if high_p is not None else price,
                        'low': low_p if low_p is not None else price,
                        'vol': vol if vol is not None else 0.0,
                        'change_pct': change if change is not None else 0.0
                    })
    else:
        with zipfile.ZipFile(target_path, 'r') as z:
            shared_strings = []
            if 'xl/sharedStrings.xml' in z.namelist():
                tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
                ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                for si in tree.findall('main:si', ns):
                    t = si.find('main:t', ns)
                    if t is not None:
                        shared_strings.append(t.text)
                    else:
                        r_texts = [r.find('main:t', ns).text for r in si.findall('main:r', ns) if r.find('main:t', ns) is not None and r.find('main:t', ns).text]
                        shared_strings.append("".join(r_texts))

            sheet_tree = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
            ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            rows = sheet_tree.findall('main:sheetData/main:row', ns)
            
            parsed_rows = []
            for row in rows:
                row_dict = {}
                for c in row.findall('main:c', ns):
                    col_ref = ''.join([ch for ch in c.attrib.get('r', '') if ch.isalpha()])
                    val_elem = c.find('main:v', ns)
                    val = val_elem.text if val_elem is not None else None
                    t = c.attrib.get('t')
                    if t == 's' and val is not None:
                        val = shared_strings[int(val)]
                    row_dict[col_ref] = val
                parsed_rows.append(row_dict)

        for r in parsed_rows[1:]:
            date_raw = r.get('A')
            price_raw = r.get('B')
            open_raw = r.get('C')
            high_raw = r.get('D')
            low_raw = r.get('E')
            vol_raw = r.get('F')
            change_raw = r.get('G')
            
            dt = decode_excel_date(date_raw)
            price = clean_float(price_raw)
            open_p = clean_float(open_raw)
            high_p = clean_float(high_raw)
            low_p = clean_float(low_raw)
            vol = clean_float(vol_raw)
            change = clean_float(change_raw)
            
            if dt is not None and price is not None:
                records.append({
                    'date': dt,
                    'date_str': dt.strftime('%Y-%m-%d'),
                    'price': price,
                    'open': open_p if open_p is not None else price,
                    'high': high_p if high_p is not None else price,
                    'low': low_p if low_p is not None else price,
                    'vol': vol if vol is not None else 0.0,
                    'change_pct': change if change is not None else 0.0
                })
            
    # Sort chronologically (oldest to newest)
    records.sort(key=lambda x: x['date'])
    
    # Remove duplicates by date if any
    unique_records = []
    seen_dates = set()
    for r in records:
        d_key = r['date_str']
        if d_key not in seen_dates:
            seen_dates.add(d_key)
            unique_records.append(r)
            
    return unique_records

def calculate_technical_indicators(records):
    """
    Computes comprehensive time-series feature matrix across 10-year historical dataset:
    - Multi-period Moving Averages (SMA 5, 10, 20, 50, 100, 200)
    - Exponential Moving Averages (EMA 12, 26) & MACD / Signal / Histogram
    - Multi-scale Momentum (RSI 14, ROC 5, ROC 20, ROC 60)
    - Volatility & Bandwidths (Rolling Std 5, 20, 60, Parkinson Volatility, Bollinger Bands)
    - Multi-Frequency Cyclical Fourier Harmonics (Annual, Semi-Annual, Quarterly)
    - Multi-Scale Lags & Return Structures (Lags 1, 2, 3, 5, 10, 20, 30, 60)
    - Moving Average Trend Ratios & Golden Cross Index
    """
    n = len(records)
    prices = np.array([r['price'] for r in records], dtype=np.float64)
    highs = np.array([max(r['high'], r['price']) for r in records], dtype=np.float64)
    lows = np.array([min(r['low'], r['price']) for r in records], dtype=np.float64)
    dates = [r['date'] for r in records]
    
    # 1. Moving Averages
    def sma(series, window):
        res = np.empty(len(series))
        res[:] = np.nan
        for i in range(window - 1, len(series)):
            res[i] = np.mean(series[i - window + 1:i + 1])
        return res

    def ema(series, span):
        alpha = 2.0 / (span + 1.0)
        res = np.empty(len(series))
        res[0] = series[0]
        for i in range(1, len(series)):
            res[i] = alpha * series[i] + (1.0 - alpha) * res[i - 1]
        return res

    sma_5 = sma(prices, 5)
    sma_10 = sma(prices, 10)
    sma_20 = sma(prices, 20)
    sma_50 = sma(prices, 50)
    sma_100 = sma(prices, 100)
    sma_200 = sma(prices, 200)

    ema_12 = ema(prices, 12)
    ema_26 = ema(prices, 26)
    macd_line = ema_12 - ema_26
    macd_signal = ema(macd_line, 9)
    macd_hist = macd_line - macd_signal

    # 2. Volatilities and Bollinger Bands
    rolling_std_5 = np.empty(n)
    rolling_std_20 = np.empty(n)
    rolling_std_60 = np.empty(n)
    parkinson_vol = np.empty(n)
    
    rolling_std_5[:] = np.nan
    rolling_std_20[:] = np.nan
    rolling_std_60[:] = np.nan
    parkinson_vol[:] = np.nan

    for i in range(4, n):
        rolling_std_5[i] = np.std(prices[i - 4:i + 1])
    for i in range(19, n):
        rolling_std_20[i] = np.std(prices[i - 19:i + 1])
    for i in range(59, n):
        rolling_std_60[i] = np.std(prices[i - 59:i + 1])

    # Parkinson Volatility Estimator (using High / Low ratios)
    for i in range(n):
        h = max(highs[i], 1.0)
        l = max(lows[i], 0.1)
        parkinson_vol[i] = np.sqrt((np.log(h / l) ** 2) / (4.0 * np.log(2.0)))

    bb_upper = sma_20 + 2.0 * rolling_std_20
    bb_lower = sma_20 - 2.0 * rolling_std_20
    bb_bandwidth = (bb_upper - bb_lower) / np.maximum(sma_20, 1.0)
    bb_pct_b = (prices - bb_lower) / np.maximum(bb_upper - bb_lower, 1e-6)

    # 3. Relative Strength Index (RSI 14)
    rsi_14 = np.empty(n)
    rsi_14[:] = np.nan
    diffs = np.diff(prices)
    gains = np.where(diffs > 0, diffs, 0.0)
    losses = np.where(diffs < 0, -diffs, 0.0)
    
    if n > 14:
        avg_gain = np.mean(gains[:14])
        avg_loss = np.mean(losses[:14])
        rs = avg_gain / max(avg_loss, 1e-6)
        rsi_14[14] = 100.0 - (100.0 / (1.0 + rs))
        for i in range(15, n):
            avg_gain = (avg_gain * 13.0 + gains[i - 1]) / 14.0
            avg_loss = (avg_loss * 13.0 + losses[i - 1]) / 14.0
            rs = avg_gain / max(avg_loss, 1e-6)
            rsi_14[i] = 100.0 - (100.0 / (1.0 + rs))

    # 4. Assemble enriched feature matrix
    enriched = []
    min_warmup = 60 # Ensure 60 days of history for warm-up
    for i in range(min_warmup, n):
        curr_price = prices[i]
        curr_dt = dates[i]
        
        # Lags
        p_lag1 = prices[i - 1]
        p_lag2 = prices[i - 2]
        p_lag3 = prices[i - 3]
        p_lag5 = prices[i - 5]
        p_lag10 = prices[i - 10]
        p_lag20 = prices[i - 20]
        p_lag30 = prices[i - 30]
        p_lag60 = prices[i - 60]
        
        ret_1 = (curr_price - p_lag1) / p_lag1
        ret_2 = (curr_price - p_lag2) / p_lag2
        ret_3 = (curr_price - p_lag3) / p_lag3
        ret_5 = (curr_price - p_lag5) / p_lag5
        ret_10 = (curr_price - p_lag10) / p_lag10
        ret_20 = (curr_price - p_lag20) / p_lag20
        ret_30 = (curr_price - p_lag30) / p_lag30
        ret_60 = (curr_price - p_lag60) / p_lag60

        # Ratios vs Moving Averages
        s5 = sma_5[i] if not np.isnan(sma_5[i]) else curr_price
        s10 = sma_10[i] if not np.isnan(sma_10[i]) else curr_price
        s20 = sma_20[i] if not np.isnan(sma_20[i]) else curr_price
        s50 = sma_50[i] if not np.isnan(sma_50[i]) else curr_price
        s100 = sma_100[i] if not np.isnan(sma_100[i]) else curr_price
        s200 = sma_200[i] if not np.isnan(sma_200[i]) else curr_price

        ratio_sma5 = curr_price / max(s5, 1.0)
        ratio_sma10 = curr_price / max(s10, 1.0)
        ratio_sma20 = curr_price / max(s20, 1.0)
        ratio_sma50 = curr_price / max(s50, 1.0)
        ratio_sma100 = curr_price / max(s100, 1.0)
        ratio_sma200 = curr_price / max(s200, 1.0)
        golden_cross = (s50 - s200) / max(s200, 1.0)

        # Calendar / Multi-Harmonic Seasonality
        month = curr_dt.month
        quarter = (month - 1) // 3 + 1
        day_of_week = curr_dt.weekday()
        day_of_year = curr_dt.timetuple().tm_yday
        
        # Multi-frequency Fourier cycles
        sin_annual = np.sin(2.0 * np.pi * day_of_year / 365.25)
        cos_annual = np.cos(2.0 * np.pi * day_of_year / 365.25)
        sin_semiannual = np.sin(4.0 * np.pi * day_of_year / 365.25)
        cos_semiannual = np.cos(4.0 * np.pi * day_of_year / 365.25)
        sin_quarterly = np.sin(8.0 * np.pi * day_of_year / 365.25)
        cos_quarterly = np.cos(8.0 * np.pi * day_of_year / 365.25)

        feature_dict = {
            'date': curr_dt,
            'date_str': curr_dt.strftime('%Y-%m-%d'),
            'price': curr_price,
            'log_price': np.log(max(curr_price, 1.0)),
            # Multi-scale Returns
            'ret_1': ret_1,
            'ret_2': ret_2,
            'ret_3': ret_3,
            'ret_5': ret_5,
            'ret_10': ret_10,
            'ret_20': ret_20,
            'ret_30': ret_30,
            'ret_60': ret_60,
            # Moving Average Ratios
            'ratio_sma5': ratio_sma5,
            'ratio_sma10': ratio_sma10,
            'ratio_sma20': ratio_sma20,
            'ratio_sma50': ratio_sma50,
            'ratio_sma100': ratio_sma100,
            'ratio_sma200': ratio_sma200,
            'golden_cross': golden_cross,
            # Raw Averages for visualization
            'sma_5': s5,
            'sma_20': s20,
            'sma_50': s50,
            'sma_100': s100,
            'sma_200': s200,
            # Momentum & Oscillators
            'macd': macd_line[i],
            'macd_signal': macd_signal[i],
            'macd_hist': macd_hist[i],
            'rsi_14': rsi_14[i] if not np.isnan(rsi_14[i]) else 50.0,
            # Multi-scale Volatility
            'vol_5': rolling_std_5[i] / max(curr_price, 1.0) if not np.isnan(rolling_std_5[i]) else 0.02,
            'vol_20': rolling_std_20[i] / max(curr_price, 1.0) if not np.isnan(rolling_std_20[i]) else 0.03,
            'vol_60': rolling_std_60[i] / max(curr_price, 1.0) if not np.isnan(rolling_std_60[i]) else 0.04,
            'parkinson_vol': parkinson_vol[i],
            'bb_pct_b': bb_pct_b[i] if not np.isnan(bb_pct_b[i]) else 0.5,
            'bb_bandwidth': bb_bandwidth[i] if not np.isnan(bb_bandwidth[i]) else 0.1,
            # Fourier Seasonality
            'sin_annual': sin_annual,
            'cos_annual': cos_annual,
            'sin_semiannual': sin_semiannual,
            'cos_semiannual': cos_semiannual,
            'sin_quarterly': sin_quarterly,
            'cos_quarterly': cos_quarterly,
            'month': month,
            'quarter': quarter,
            'day_of_week': day_of_week,
        }
        enriched.append(feature_dict)

    return enriched, records

FEATURE_NAMES = [
    'ret_1', 'ret_2', 'ret_3', 'ret_5', 'ret_10', 'ret_20', 'ret_30', 'ret_60',
    'ratio_sma5', 'ratio_sma10', 'ratio_sma20', 'ratio_sma50', 'ratio_sma100', 'ratio_sma200', 'golden_cross',
    'macd', 'macd_signal', 'macd_hist', 'rsi_14',
    'vol_5', 'vol_20', 'vol_60', 'parkinson_vol', 'bb_pct_b', 'bb_bandwidth',
    'sin_annual', 'cos_annual', 'sin_semiannual', 'cos_semiannual', 'sin_quarterly', 'cos_quarterly',
    'month', 'quarter', 'day_of_week'
]

def extract_feature_matrix(enriched_records, feature_names=FEATURE_NAMES):
    """Generates numpy feature matrix X, price targets, and next-step returns."""
    n = len(enriched_records)
    X = np.zeros((n, len(feature_names)), dtype=np.float64)
    y_prices = np.zeros(n, dtype=np.float64)
    y_returns = np.zeros(n, dtype=np.float64)
    
    for i, r in enumerate(enriched_records):
        curr_p = r['price']
        y_prices[i] = curr_p
        if i < n - 1:
            next_p = enriched_records[i + 1]['price']
            y_returns[i] = (next_p - curr_p) / max(curr_p, 1.0)
        else:
            y_returns[i] = 0.0
            
        for j, fname in enumerate(feature_names):
            X[i, j] = float(r.get(fname, 0.0))
            
    return X, y_prices, y_returns, feature_names

