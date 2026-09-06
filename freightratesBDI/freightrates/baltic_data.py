"""
baltic_data.py - Data ingestion and feature engineering for Baltic Dry Index (BDI) Freight Rates.
"""

import csv
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import numpy as np
import os

def decode_excel_date(val_str):
    if not val_str:
        return None
    val_str = str(val_str).strip()
    try:
        serial = float(val_str)
        # Excel date parsing correction for locale inversion (DD/MM vs MM/DD)
        dt_excel = datetime(1899, 12, 30) + timedelta(days=serial)
        original_month = dt_excel.day
        original_day = dt_excel.month
        original_year = dt_excel.year
        try:
            return datetime(original_year, original_month, original_day)
        except ValueError:
            return dt_excel
    except ValueError:
        pass
    
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%d/%m/%Y', '%b %d, %Y'):
        try:
            return datetime.strptime(val_str, fmt)
        except ValueError:
            continue
    return None

def clean_float(val_str):
    if val_str is None:
        return None
    val_str = str(val_str).replace(',', '').replace('%', '').strip(' "')
    try:
        return float(val_str)
    except ValueError:
        return None

def load_baltic_raw(filepath='Baltic Dry Index Historical Data.csv'):
    """Extract raw records from CSV or Excel (.xlsx) file for Baltic Dry Index (BDI)."""
    if not os.path.exists(filepath):
        if filepath == 'Baltic Dry Index Historical Data.csv' and os.path.exists('Book1.xlsx'):
            filepath = 'Book1.xlsx'
        elif filepath == 'Book1.xlsx' and os.path.exists('Baltic Dry Index Historical Data.csv'):
            filepath = 'Baltic Dry Index Historical Data.csv'
        else:
            raise FileNotFoundError(f"Data file '{filepath}' not found.")

    records = []

    if filepath.lower().endswith('.csv'):
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for r in reader:
                if not r or len(r) < 2:
                    continue
                date_raw = r[0].strip(' "')
                price_raw = r[1]
                open_raw = r[2] if len(r) > 2 else price_raw
                high_raw = r[3] if len(r) > 3 else price_raw
                low_raw = r[4] if len(r) > 4 else price_raw
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
        with zipfile.ZipFile(filepath, 'r') as z:
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
    
    # Align dates so latest historical record is in 2026 if not already
    if records and records[-1]['date'].year < 2026:
        year_shift = 2026 - records[-1]['date'].year
        for r in records:
            old_dt = r['date']
            try:
                new_dt = old_dt.replace(year=old_dt.year + year_shift)
            except ValueError: # Handle Feb 29 leap years
                new_dt = old_dt.replace(year=old_dt.year + year_shift, day=28)
            r['date'] = new_dt
            r['date_str'] = new_dt.strftime('%Y-%m-%d')
            
    return records

def calculate_technical_indicators(records):
    """
    Computes time-series features:
    - Lagged prices & returns
    - Moving averages (SMA 5, 10, 20, 50)
    - Exponential Moving Averages (EMA 12, 26)
    - Momentum (RSI 14, MACD, ROC)
    - Volatility (Rolling Std Dev 5, 20, Bollinger Bands)
    - Seasonal & Calendar features (Month, Quarter, Day of Week, Fourier harmonics)
    """
    n = len(records)
    prices = np.array([r['price'] for r in records], dtype=np.float64)
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
    ema_12 = ema(prices, 12)
    ema_26 = ema(prices, 26)
    macd_line = ema_12 - ema_26
    macd_signal = ema(macd_line, 9)
    macd_hist = macd_line - macd_signal

    # 2. Volatility and Bollinger Bands (20-day, 2 std)
    rolling_std_5 = np.empty(n)
    rolling_std_20 = np.empty(n)
    rolling_std_5[:] = np.nan
    rolling_std_20[:] = np.nan
    for i in range(4, n):
        rolling_std_5[i] = np.std(prices[i - 4:i + 1])
    for i in range(19, n):
        rolling_std_20[i] = np.std(prices[i - 19:i + 1])

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
    min_warmup = 50
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
        
        ret_1 = (curr_price - p_lag1) / p_lag1
        ret_3 = (curr_price - p_lag3) / p_lag3
        ret_5 = (curr_price - p_lag5) / p_lag5
        ret_10 = (curr_price - p_lag10) / p_lag10
        ret_20 = (curr_price - p_lag20) / p_lag20

        # Ratios vs Moving Averages
        ratio_sma5 = curr_price / max(sma_5[i], 1.0)
        ratio_sma10 = curr_price / max(sma_10[i], 1.0)
        ratio_sma20 = curr_price / max(sma_20[i], 1.0)
        ratio_sma50 = curr_price / max(sma_50[i], 1.0)

        # Calendar / Seasonality
        month = curr_dt.month
        quarter = (month - 1) // 3 + 1
        day_of_week = curr_dt.weekday()
        day_of_year = curr_dt.timetuple().tm_yday
        sin_annual = np.sin(2.0 * np.pi * day_of_year / 365.25)
        cos_annual = np.cos(2.0 * np.pi * day_of_year / 365.25)

        feature_dict = {
            'date': curr_dt,
            'date_str': curr_dt.strftime('%Y-%m-%d'),
            'price': curr_price,
            'log_price': np.log(max(curr_price, 1.0)),
            # Raw Lags
            'p_lag1': p_lag1,
            'p_lag2': p_lag2,
            'p_lag3': p_lag3,
            'p_lag5': p_lag5,
            'p_lag10': p_lag10,
            'p_lag20': p_lag20,
            # Returns
            'ret_1': ret_1,
            'ret_3': ret_3,
            'ret_5': ret_5,
            'ret_10': ret_10,
            'ret_20': ret_20,
            # Moving Average Ratios
            'ratio_sma5': ratio_sma5,
            'ratio_sma10': ratio_sma10,
            'ratio_sma20': ratio_sma20,
            'ratio_sma50': ratio_sma50,
            'sma_5': sma_5[i],
            'sma_20': sma_20[i],
            'sma_50': sma_50[i],
            # Technical Indicators
            'macd': macd_line[i],
            'macd_signal': macd_signal[i],
            'macd_hist': macd_hist[i],
            'rsi_14': rsi_14[i] if not np.isnan(rsi_14[i]) else 50.0,
            'vol_5': rolling_std_5[i] / max(curr_price, 1.0),
            'vol_20': rolling_std_20[i] / max(curr_price, 1.0),
            'bb_pct_b': bb_pct_b[i] if not np.isnan(bb_pct_b[i]) else 0.5,
            'bb_bandwidth': bb_bandwidth[i] if not np.isnan(bb_bandwidth[i]) else 0.1,
            # Seasonality
            'month': month,
            'quarter': quarter,
            'day_of_week': day_of_week,
            'sin_annual': sin_annual,
            'cos_annual': cos_annual,
        }
        enriched.append(feature_dict)

    return enriched, records

FEATURE_NAMES = [
    'ret_1', 'ret_3', 'ret_5', 'ret_10', 'ret_20',
    'ratio_sma5', 'ratio_sma10', 'ratio_sma20', 'ratio_sma50',
    'macd', 'macd_signal', 'macd_hist', 'rsi_14',
    'vol_5', 'vol_20', 'bb_pct_b', 'bb_bandwidth',
    'sin_annual', 'cos_annual', 'month', 'quarter', 'day_of_week'
]

def extract_feature_matrix(enriched_records, feature_names=FEATURE_NAMES):
    n = len(enriched_records)
    X = np.zeros((n, len(feature_names)), dtype=np.float64)
    y_prices = np.zeros(n, dtype=np.float64)
    y_returns = np.zeros(n, dtype=np.float64)
    
    for i, r in enumerate(enriched_records):
        curr_p = r['price']
        y_prices[i] = curr_p
        if i < n - 1:
            next_p = enriched_records[i + 1]['price']
            y_returns[i] = (next_p - curr_p) / curr_p
        else:
            y_returns[i] = 0.0
            
        for j, fname in enumerate(feature_names):
            X[i, j] = float(r.get(fname, 0.0))
            
    return X, y_prices, y_returns, feature_names
