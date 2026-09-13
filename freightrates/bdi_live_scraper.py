"""
bdi_live_scraper.py - Automated Live Baltic Dry Index (BDI) Settlement Scraper & Model Retraining Engine.
Engineered for Institutional Freight Analytics & Daily Forward Model Refresh (2014-2026).
"""

import os
import sys
import re
import csv
import json
import time
import argparse
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

# Standard paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

DEFAULT_CSV_PATHS = [
    os.path.join(SCRIPT_DIR, 'Baltic Dry Index Historical Data.csv'),
    os.path.join(PROJECT_ROOT, 'Baltic Dry Index Historical Data.csv')
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
    'Cache-Control': 'no-cache',
    'Sec-Ch-Ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"'
}

def clean_float(val):
    """Sanitizes numerical string."""
    if val is None:
        return None
    val_str = str(val).replace(',', '').replace('%', '').strip(' "')
    try:
        return float(val_str)
    except ValueError:
        return None

def parse_month_day(date_str, default_year=None):
    """
    Parses 'Sep/11', 'Sep 11', '09/11', '11/09/2026' into a datetime object.
    """
    if default_year is None:
        default_year = datetime.now().year

    date_str = str(date_str).strip()
    
    # Try full formats first
    for fmt in ('%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d', '%d-%b-%Y', '%b %d, %Y'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass

    # Try 'Sep/11' or 'Sep 11'
    m_match = re.match(r'([A-Za-z]{3})[/\s]+(\d{1,2})', date_str)
    if m_match:
        month_name, day = m_match.groups()
        try:
            dt = datetime.strptime(f"{month_name} {day} {default_year}", "%b %d %Y")
            return dt
        except ValueError:
            pass

    # Fallback to current date
    return datetime.now()

# ---------------------------------------------------------------------------
# SCRAPING SOURCE 1: TradingEconomics (Fast, accurate, verified active)
# ---------------------------------------------------------------------------
def scrape_trading_economics():
    """
    Scrapes live Baltic Dry Index settlements from TradingEconomics.
    """
    url = 'https://tradingeconomics.com/commodity/baltic'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 1. Look for Baltic Dry in table
        table = soup.find('table')
        price = None
        change = 0.0
        change_pct = 0.0
        date_str = None
        
        if table:
            for tr in table.find_all('tr'):
                tds = [td.get_text(strip=True) for td in tr.find_all(['th', 'td'])]
                if any('baltic' in td.lower() for td in tds):
                    # Filter non-empty
                    parts = [p for p in tds if p]
                    if len(parts) >= 2:
                        price = clean_float(parts[1])
                    if len(parts) >= 3:
                        change = clean_float(parts[2])
                    if len(parts) >= 4:
                        change_pct = clean_float(parts[3])
                    if len(parts) >= 7:
                        date_str = parts[-1]
                    break

        # Fallback to direct element if table not matched
        if price is None:
            price_elem = soup.find('span', {'id': 'market_last'}) or soup.find('span', {'id': 'last'})
            if price_elem:
                price = clean_float(price_elem.text)

        if price is None or price <= 0:
            return None

        dt = parse_month_day(date_str) if date_str else datetime.now()
        
        # Determine high/low from table or estimates
        prev_close = price - change if change is not None else price
        high_p = max(price, prev_close)
        low_p = min(price, prev_close)

        return {
            'source': 'TradingEconomics',
            'date': dt,
            'date_str_iso': dt.strftime('%Y-%m-%d'),
            'date_str_csv': dt.strftime('%m/%d/%Y'),
            'price': price,
            'open': price,
            'high': high_p,
            'low': low_p,
            'change': change if change is not None else 0.0,
            'change_pct': change_pct if change_pct is not None else 0.0
        }
    except Exception as e:
        print(f"[bdi_live_scraper] TradingEconomics scrape warning: {e}")
        return None

# ---------------------------------------------------------------------------
# SCRAPING SOURCE 2: Hellenic Shipping News (Official Dry Bulk Market Reports)
# ---------------------------------------------------------------------------
def scrape_hellenic_shipping():
    """
    Parses Hellenic Shipping News freight reports for Baltic Dry Index settlement.
    """
    url = 'https://www.hellenicshippingnews.com/category/freight-news/'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, 'html.parser')
        article_url = None
        for a in soup.find_all('a', href=True):
            txt = a.get_text(strip=True).lower()
            if 'baltic dry' in txt or 'bulk freight index' in txt:
                article_url = a['href']
                break

        if not article_url:
            return None

        art_resp = requests.get(article_url, headers=HEADERS, timeout=10)
        if art_resp.status_code != 200:
            return None

        art_soup = BeautifulSoup(art_resp.text, 'html.parser')
        text = art_soup.get_text(' ')

        # Pattern: declined/rose X points, or Y%, to Z
        match = re.search(r'(declined|dropped|fell|rose|gained|climbed)\s+([\d\.]+)\s+points?,?\s+or\s+([\d\.]+)%?,?\s+to\s+([\d,]+)', text, re.IGNORECASE)
        if not match:
            match = re.search(r'Baltic\s+(?:Dry\s+)?index[^\.\n]+?(declined|dropped|fell|rose|gained|climbed)\s+([\d\.]+)[^\.\n]+?to\s+([\d,]+)', text, re.IGNORECASE)
            
        if match:
            direction = match.group(1).lower()
            pts = float(match.group(2))
            pct_val = 0.0
            if len(match.groups()) >= 4 and match.group(3):
                pct_val = float(match.group(3))
            price_val = clean_float(match.groups()[-1])
            
            is_down = any(w in direction for w in ('declined', 'dropped', 'fell'))
            change_pts = -pts if is_down else pts
            change_pct = -pct_val if is_down else pct_val
            
            # Find date in article (e.g. 12/09/2026)
            date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
            dt = datetime.strptime(date_match.group(1), '%d/%m/%Y') if date_match else datetime.now()

            return {
                'source': 'Hellenic Shipping News',
                'date': dt,
                'date_str_iso': dt.strftime('%Y-%m-%d'),
                'date_str_csv': dt.strftime('%m/%d/%Y'),
                'price': price_val,
                'open': price_val,
                'high': price_val,
                'low': price_val,
                'change': change_pts,
                'change_pct': change_pct
            }
        return None
    except Exception as e:
        print(f"[bdi_live_scraper] Hellenic Shipping scrape warning: {e}")
        return None

# ---------------------------------------------------------------------------
# SCRAPING SOURCE 3: Investing.com (With anti-bot bypass headers)
# ---------------------------------------------------------------------------
def scrape_investing_com():
    """
    Attempts to pull Baltic Dry Index settlement from Investing.com.
    """
    url = 'https://www.investing.com/indices/baltic-dry'
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        resp = session.get(url, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            price_elem = (soup.find('div', {'data-test': 'instrument-price-last'}) or
                          soup.find('span', {'data-test': 'instrument-price-last'}) or
                          soup.find('span', id='last_last'))
            if price_elem:
                price = clean_float(price_elem.text)
                if price and price > 0:
                    dt = datetime.now()
                    return {
                        'source': 'Investing.com',
                        'date': dt,
                        'date_str_iso': dt.strftime('%Y-%m-%d'),
                        'date_str_csv': dt.strftime('%m/%d/%Y'),
                        'price': price,
                        'open': price,
                        'high': price,
                        'low': price,
                        'change': 0.0,
                        'change_pct': 0.0
                    }
        return None
    except Exception as e:
        print(f"[bdi_live_scraper] Investing.com scrape warning: {e}")
        return None

# ---------------------------------------------------------------------------
# UNIFIED LIVE SETTLEMENT SCRAPER
# ---------------------------------------------------------------------------
def fetch_live_bdi_settlement():
    """
    Queries data sources in order of resilience and returns validated settlement.
    """
    print("[1/4] Querying live maritime market feeds for Baltic Dry Index settlement...")
    
    sources = [
        ('TradingEconomics', scrape_trading_economics),
        ('Hellenic Shipping News', scrape_hellenic_shipping),
        ('Investing.com', scrape_investing_com)
    ]
    
    for name, scraper_fn in sources:
        print(f"      Attempting source: {name}...")
        res = scraper_fn()
        if res and res.get('price'):
            print(f"      [OK] Successfully retrieved live BDI settlement from {res['source']}:")
            print(f"           Settlement Date : {res['date_str_csv']} ({res['date_str_iso']})")
            print(f"           BDI Price       : {res['price']:,.2f} pts")
            print(f"           Daily Change    : {res['change']:+,.2f} pts ({res['change_pct']:+.2f}%)")
            return res
        else:
            print(f"      [-] Source {name} returned no data, falling back...")

    raise RuntimeError("Unable to pull live BDI settlement from any configured web source.")

# ---------------------------------------------------------------------------
# CSV SYNCHRONIZATION & DEDUPLICATION
# ---------------------------------------------------------------------------
def sync_bdi_csv(settlement, target_csv_paths=None, force=False):
    """
    Appends newly scraped BDI settlement to the historical CSV files without duplicates.
    Maintains exact institutional format: "Date","Price","Open","High","Low","Vol.","Change %"
    """
    if target_csv_paths is None:
        target_csv_paths = DEFAULT_CSV_PATHS

    target_date_csv = settlement['date_str_csv']
    target_dt = settlement['date']
    results = []

    new_row_str = (
        f'"{target_date_csv}",'
        f'"{settlement["price"]:,.2f}",'
        f'"{settlement["open"]:,.2f}",'
        f'"{settlement["high"]:,.2f}",'
        f'"{settlement["low"]:,.2f}",'
        f'"",'
        f'"{settlement["change_pct"]:+.2f}%"\n'
    )

    print(f"\n[2/4] Synchronizing historical datasets with settlement {target_date_csv}...")

    for path in target_csv_paths:
        if not os.path.exists(path):
            print(f"      [-] Skipping non-existent path: {path}")
            continue

        with open(path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        if not lines:
            print(f"      [!] Empty CSV file at: {path}")
            continue

        header = lines[0]
        data_lines = lines[1:]

        # Check existing dates
        existing_dates = set()
        for line in data_lines[:20]: # Check recent 20 lines
            parts = [p.strip(' "\n\r') for p in line.split(',')]
            if parts:
                existing_dates.add(parts[0])

        if target_date_csv in existing_dates and not force:
            print(f"      [i] Record for {target_date_csv} already present in {os.path.basename(path)}. No update needed.")
            results.append({'path': path, 'updated': False, 'reason': 'Already present'})
            continue

        # If forcing update, remove any line with the same date
        if force:
            data_lines = [l for l in data_lines if not l.startswith(f'"{target_date_csv}"')]

        # Insert at index 0 (immediately after header, descending order)
        updated_lines = [header, new_row_str] + data_lines

        # Atomic write
        temp_path = path + '.tmp'
        with open(temp_path, 'w', encoding='utf-8-sig', newline='') as f:
            f.writelines(updated_lines)
        os.replace(temp_path, path)

        print(f"      [+] Added settlement {target_date_csv} (${settlement['price']:,.2f}) to: {path}")
        results.append({'path': path, 'updated': True, 'count': len(updated_lines) - 1})

    return results

# ---------------------------------------------------------------------------
# AUTOMATED MODEL RETRAINING PIPELINE
# ---------------------------------------------------------------------------
def retrain_models():
    """
    Executes walk-forward cross validation and model ensemble retraining.
    """
    print("\n[3/4] Triggering automated model retraining on updated Baltic dataset...")
    
    # Add script dir and candidate freightrates dir to path so imports work cleanly
    candidate_dirs = [
        SCRIPT_DIR,
        os.path.join(SCRIPT_DIR, 'freightrates'),
        PROJECT_ROOT,
        os.path.join(PROJECT_ROOT, 'freightrates')
    ]
    for d in candidate_dirs:
        if os.path.exists(d) and d not in sys.path:
            sys.path.insert(0, d)
    
    import train
    
    # Locate valid CSV file
    csv_path = None
    for p in DEFAULT_CSV_PATHS:
        if os.path.exists(p):
            csv_path = p
            break
    if not csv_path:
        csv_path = 'Baltic Dry Index Historical Data.csv'

    full_ensemble, records, report = train.train_and_evaluate(csv_path)
    
    print("\n[4/4] Automated Model Retraining Complete.")
    print(f"      Latest Benchmark Session: {report['latest_date']} -> ${report['latest_rate']:,.2f} BDI")
    print(f"      Updated Total Sessions  : {report['total_historical_records']}")
    print(f"      Meta-Ensemble MAE       : ${report['model_metrics']['Weighted Meta-Ensemble']['MAE']:.2f}")
    print(f"      Meta-Ensemble R^2       : {report['model_metrics']['Weighted Meta-Ensemble']['R2_Score']:.4f}")
    print(f"      Directional Accuracy    : {report['model_metrics']['Weighted Meta-Ensemble']['Directional_Accuracy_%']:.2f}%")
    return report

# ---------------------------------------------------------------------------
# MASTER UPDATE RUNNER
# ---------------------------------------------------------------------------
def run_live_update(force=False, retrain_if_no_change=False):
    """
    Orchestrates the complete live scraper, CSV synchronizer, and model retrainer.
    """
    start_time = time.time()
    print("=" * 80)
    print(f"  BALTIC DRY INDEX (BDI) LIVE DATA AUTO-UPDATE PIPELINE")
    print(f"  Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Step 1: Scrape
    settlement = fetch_live_bdi_settlement()

    # Step 2: Update CSV
    sync_results = sync_bdi_csv(settlement, force=force)
    any_updated = any(r.get('updated') for r in sync_results)

    # Step 3: Retrain models if new data or forced
    report = None
    if any_updated or force or retrain_if_no_change:
        report = retrain_models()
    else:
        print("\n[3/4] Datasets already up-to-date. Skipping model retraining (use --force-retrain to override).")

    duration = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"  PIPELINE EXECUTION FINISHED IN {duration:.2f}s")
    print("=" * 80)

    return {
        'status': 'success',
        'settlement': settlement,
        'sync_results': sync_results,
        'retrained': any_updated or force or retrain_if_no_change,
        'report': report,
        'duration_seconds': duration
    }

# ---------------------------------------------------------------------------
# SCHEDULING DAEMON
# ---------------------------------------------------------------------------
def run_scheduler(schedule_time_str="18:30", interval_hours=None):
    """
    Runs continuous scheduler daemon for automated daily scraping and retraining.
    """
    print(f"[*] Starting BDI Auto-Update Scheduler Daemon...")
    if interval_hours:
        print(f"[*] Mode: Periodic interval every {interval_hours} hour(s).")
    else:
        print(f"[*] Mode: Daily settlement schedule at {schedule_time_str} local time.")

    while True:
        now = datetime.now()
        should_run = False

        if interval_hours:
            wait_secs = interval_hours * 3600
            print(f"[{now.strftime('%H:%M:%S')}] Waiting {interval_hours} hour(s) until next run...")
            time.sleep(wait_secs)
            should_run = True
        else:
            # Parse target time e.g. "18:30"
            try:
                target_hour, target_min = map(int, schedule_time_str.split(':'))
            except ValueError:
                target_hour, target_min = 18, 30

            target_today = now.replace(hour=target_hour, minute=target_min, second=0, microsecond=0)
            if now >= target_today:
                # Next run is tomorrow
                next_run = target_today + timedelta(days=1)
            else:
                next_run = target_today

            wait_secs = (next_run - now).total_seconds()
            print(f"[{now.strftime('%H:%M:%S')}] Next scheduled run at: {next_run.strftime('%Y-%m-%d %H:%M:%S')} (in {wait_secs/3600:.2f} hours)")
            time.sleep(min(wait_secs, 3600)) # Sleep in intervals
            if datetime.now() >= next_run - timedelta(seconds=10):
                should_run = True

        if should_run:
            try:
                run_live_update()
            except Exception as ex:
                print(f"[ERROR in scheduled pipeline]: {ex}")

# ---------------------------------------------------------------------------
# CLI ENTRYPOINT
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Live Baltic Dry Index (BDI) Auto-Scraper and Model Retrainer")
    parser.add_argument('--run-now', action='store_true', help="Execute scraping, CSV sync, and model retraining immediately")
    parser.add_argument('--test-scrape', action='store_true', help="Only test live scraping without modifying CSVs or retraining")
    parser.add_argument('--force', action='store_true', help="Force update CSV and retrain even if settlement date already exists")
    parser.add_argument('--force-retrain', action='store_true', help="Retrain models even if dataset has no new dates")
    parser.add_argument('--schedule', type=str, metavar="HH:MM", help="Run as daily daemon at HH:MM local time (e.g. 18:30)")
    parser.add_argument('--interval', type=float, metavar="HOURS", help="Run periodically every N hours")

    args = parser.parse_args()

    if args.test_scrape:
        res = fetch_live_bdi_settlement()
        print("\nTest Scrape Succeeded! Data structure:")
        print(json.dumps({k: str(v) for k, v in res.items()}, indent=2))
    elif args.schedule or args.interval:
        run_scheduler(schedule_time_str=args.schedule or "18:30", interval_hours=args.interval)
    else:
        # Default behavior: run now
        run_live_update(force=args.force, retrain_if_no_change=args.force_retrain)
