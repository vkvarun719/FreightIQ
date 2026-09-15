"""
bdi_live_scraper.py - Institutional Baltic Dry Index (BDI) Live Settlement Scraper & Automated Model Retraining Engine.
Includes strict sanity validation gates, dynamic HTML/JSON parsing, multi-source failover, and deterministic path resolution.
"""

import os
import sys
import re
import csv
import json
import time
import argparse
from datetime import datetime, date, timedelta
import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# DETERMINISTIC CANONICAL PATH RESOLUTION
# ---------------------------------------------------------------------------
CURRENT_FILE = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_FILE)

if os.path.basename(CURRENT_DIR) == 'freightrates':
    FREIGHTRATES_DIR = CURRENT_DIR
    WORKSPACE_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..'))
else:
    WORKSPACE_ROOT = CURRENT_DIR
    FREIGHTRATES_DIR = os.path.join(CURRENT_DIR, 'freightrates')

# The canonical CSV read by app.py, train.py, and freight_engine.py:
CANONICAL_CSV = os.path.join(FREIGHTRATES_DIR, 'Baltic Dry Index Historical Data.csv')
ROOT_CSV = os.path.join(WORKSPACE_ROOT, 'Baltic Dry Index Historical Data.csv')

# Ensure we always update CANONICAL_CSV, plus ROOT_CSV if separate
TARGET_CSV_PATHS = [CANONICAL_CSV]
if os.path.exists(ROOT_CSV) and os.path.abspath(ROOT_CSV) != os.path.abspath(CANONICAL_CSV):
    TARGET_CSV_PATHS.append(ROOT_CSV)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
    'Cache-Control': 'no-cache'
}

def clean_float(val):
    """Sanitizes numerical string into clean float."""
    if val is None:
        return None
    val_str = str(val).replace(',', '').replace('%', '').strip(' "')
    try:
        return float(val_str)
    except ValueError:
        return None

def parse_settlement_date(date_str, reference_year=None):
    """
    Strict date parser. Returns datetime.date object.
    Never defaults to today's date if parsing fails.
    """
    if not date_str:
        return None
    if reference_year is None:
        reference_year = datetime.now().year

    date_str = str(date_str).strip(' "\'')

    # Try standard full date formats
    for fmt in ('%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d', '%d-%b-%Y', '%b %d, %Y', '%b %d %Y'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            pass

    # Try 'Sep/15' or 'Sep 15'
    m_match = re.match(r'^([A-Za-z]{3})[/\s]+(\d{1,2})$', date_str)
    if m_match:
        month_name, day = m_match.groups()
        try:
            dt = datetime.strptime(f"{month_name} {day} {reference_year}", "%b %d %Y")
            return dt.date()
        except ValueError:
            pass

    return None

def get_latest_csv_record(csv_path=CANONICAL_CSV):
    """Reads the top historical session from the CSV."""
    if not os.path.exists(csv_path):
        return None
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        first_row = next(reader, None)
        if first_row and len(first_row) >= 2:
            dt = parse_settlement_date(first_row[0])
            price = clean_float(first_row[1])
            return {
                'date': dt,
                'date_str_csv': first_row[0],
                'price': price
            }
    return None

# ---------------------------------------------------------------------------
# INSTITUTIONAL VALIDATION GATE (Circuit Breakers & Sanity Checks)
# ---------------------------------------------------------------------------
def validate_settlement(candidate, prior_record=None):
    """
    Strict validation gate:
    1. Positive and reasonable price (200 - 25,000)
    2. Date is not a weekend (Mon-Fri only)
    3. Date is not older than the latest CSV record
    4. 15% daily circuit-breaker vs prior close (rejects column shifts)
    5. Internal consistency (change matches price difference)
    """
    if candidate is None:
        return False, "Candidate settlement is None"

    price = candidate.get('price')
    dt = candidate.get('date')
    change = candidate.get('change')
    change_pct = candidate.get('change_pct')

    if price is None or price < 200.0 or price > 25000.0:
        return False, f"Price ${price} out of institutional bounds [200, 25000]"

    if dt is None:
        return False, "Settlement date is missing or failed to parse"

    # Weekend check (0=Mon, 4=Fri, 5=Sat, 6=Sun)
    if dt.weekday() >= 5:
        return False, f"Settlement date {dt} falls on a weekend ({dt.strftime('%A')})"

    if prior_record and prior_record.get('price'):
        prior_price = prior_record['price']
        prior_date = prior_record.get('date')

        # Check circuit-breaker: Baltic rarely moves > 10% in a session, 15% is strict upper bound
        pct_move = abs(price - prior_price) / prior_price
        if pct_move > 0.15:
            return False, f"Circuit-breaker triggered: {pct_move*100:.1f}% daily move exceeds 15% limit (${prior_price} -> ${price})"

        # Chronology check: new settlement cannot be older than latest recorded date
        if prior_date and dt < prior_date:
            return False, f"Settlement date {dt} is older than latest recorded session {prior_date}"

        # Internal consistency check if change is provided
        if change is not None and abs(change) > 0.01:
            calculated_diff = price - prior_price
            # If the candidate date is strictly newer than prior date, change should align
            if prior_date and dt > prior_date:
                if abs(calculated_diff - change) > 5.0:
                    print(f"[validation warning] Scraped change {change:+} differs from price delta {calculated_diff:+} by >5 pts")

    return True, "Passed institutional validation"

# ---------------------------------------------------------------------------
# SOURCE 1: TradingEconomics (Dual JSON Script + Dynamic Column Table Parser)
# ---------------------------------------------------------------------------
def scrape_trading_economics(prior_record=None):
    """
    Scrapes TradingEconomics with dual-mode parser:
    1. Direct JSON extraction from TEChartsMeta (immune to HTML shifts)
    2. Dynamic column header mapping from market table
    """
    url = 'https://tradingeconomics.com/commodity/baltic'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None

        price = None
        change = 0.0
        change_pct = 0.0
        date_obj = None

        # Mode A: Parse TEChartsMeta JSON block
        meta_match = re.search(r'TEChartsMeta\s*=\s*(\[\{.*?\}\]);', resp.text, re.DOTALL)
        if meta_match:
            try:
                meta_json = json.loads(meta_match.group(1))
                if meta_json and isinstance(meta_json, list):
                    item = meta_json[0]
                    if 'last' in item and item['last'] is not None:
                        price = float(item['last'])
            except Exception as e:
                print(f"[TE Parser] TEChartsMeta JSON error: {e}")

        # Mode B: Dynamic Column Mapping from HTML Table
        soup = BeautifulSoup(resp.text, 'html.parser')
        table = soup.find('table')
        if table:
            # Map column names from <th>
            headers_list = [th.get_text(strip=True).lower() for th in table.find_all('th')]
            
            for tr in table.find_all('tr'):
                cells = [td.get_text(strip=True) for td in tr.find_all(['th', 'td'])]
                if any('baltic' in c.lower() for c in cells):
                    # Check column indices
                    for idx, cell_val in enumerate(cells):
                        if idx < len(headers_list):
                            h_name = headers_list[idx]
                            if 'price' in h_name and price is None:
                                price = clean_float(cell_val)
                            elif 'date' in h_name:
                                date_obj = parse_settlement_date(cell_val)
                            elif 'day' in h_name and '%' in cell_val:
                                change_pct = clean_float(cell_val)
                    
                    # Also look for explicit point change in row (e.g. '-85.00')
                    for cell_val in cells:
                        if re.match(r'^[+-]?\d{1,4}\.\d{2}$', cell_val) and not cell_val.endswith('%'):
                            val = clean_float(cell_val)
                            if val != price:
                                change = val
                    
                    # If date was not found via header, scan cells for 'Mon/DD' or 'Sep/15'
                    if date_obj is None:
                        for cell_val in cells:
                            d = parse_settlement_date(cell_val)
                            if d:
                                date_obj = d
                                break
                    break

        # Fallback price from span
        if price is None:
            span = soup.find('span', {'id': 'market_last'})
            if span:
                price = clean_float(span.text)

        if price is None or date_obj is None:
            return None

        # Calculate implied change pct if change given
        if prior_record and prior_record.get('price') and (change_pct == 0.0 or change_pct is None):
            change_pct = ((price - prior_record['price']) / prior_record['price']) * 100.0

        candidate = {
            'source': 'TradingEconomics',
            'date': date_obj,
            'date_str_iso': date_obj.strftime('%Y-%m-%d'),
            'date_str_csv': date_obj.strftime('%m/%d/%Y'),
            'price': price,
            'open': price,
            'high': price,
            'low': price,
            'change': change if change != 0.0 else (price - prior_record['price'] if prior_record else 0.0),
            'change_pct': round(change_pct, 2)
        }

        valid, msg = validate_settlement(candidate, prior_record)
        if valid:
            return candidate
        else:
            print(f"[TradingEconomics] Settlement rejected by validation gate: {msg}")
            return None
    except Exception as e:
        print(f"[TradingEconomics] Scraper error: {e}")
        return None

# ---------------------------------------------------------------------------
# SOURCE 2: Seaandjob (Direct Maritime News Wire Settlement Reports)
# ---------------------------------------------------------------------------
def scrape_seaandjob(prior_record=None):
    """
    Parses Seaandjob news reports for official Baltic Dry Index settlements.
    Example: "The Baltic dry index fell 1.8% to 3445 on Monday"
    """
    url = 'https://www.seaandjob.com/?s=Baltic+dry+index'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, 'html.parser')
        article_url = None
        for a in soup.find_all('a', href=True):
            txt = a.get_text(strip=True).lower()
            if 'baltic dry' in txt:
                article_url = a['href']
                break

        if not article_url:
            return None

        art_resp = requests.get(article_url, headers=HEADERS, timeout=10)
        if art_resp.status_code != 200:
            return None

        art_soup = BeautifulSoup(art_resp.text, 'html.parser')
        body = art_soup.get_text(' ')

        # Pattern: "Baltic dry index (fell|rose|declined|gained) X% to Y on (Day)"
        m = re.search(r'Baltic\s+(?:dry\s+)?index\s+(fell|rose|declined|gained|dropped)\s+([\d\.]+)%\s+to\s+([\d,]+)\s+on\s+(\w+)', body, re.IGNORECASE)
        if not m:
            # Pattern: "Baltic dry bulk freight index ... to Y"
            m = re.search(r'Baltic\s+(?:dry\s+)?index\s+[^\.\n]+?(fell|rose|declined|gained|dropped)\s+([\d\.]+)%?[^\.\n]+?to\s+([\d,]+)', body, re.IGNORECASE)

        if m:
            direction = m.group(1).lower()
            pct_val = float(m.group(2))
            price_val = clean_float(m.group(3))
            is_down = any(w in direction for w in ('fell', 'declined', 'dropped'))
            change_pct = -pct_val if is_down else pct_val

            # Extract date from post metadata or text
            date_match = re.search(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}', body)
            if date_match:
                date_obj = parse_settlement_date(date_match.group(0))
            else:
                date_obj = None

            if price_val and date_obj:
                prior_p = prior_record['price'] if prior_record else price_val
                change_pts = price_val - prior_p

                candidate = {
                    'source': 'Seaandjob',
                    'date': date_obj,
                    'date_str_iso': date_obj.strftime('%Y-%m-%d'),
                    'date_str_csv': date_obj.strftime('%m/%d/%Y'),
                    'price': price_val,
                    'open': price_val,
                    'high': price_val,
                    'low': price_val,
                    'change': change_pts,
                    'change_pct': round(change_pct, 2)
                }

                valid, msg = validate_settlement(candidate, prior_record)
                if valid:
                    return candidate
                else:
                    print(f"[Seaandjob] Settlement rejected by validation gate: {msg}")
        return None
    except Exception as e:
        print(f"[Seaandjob] Scraper error: {e}")
        return None

# ---------------------------------------------------------------------------
# SOURCE 3: Hellenic Shipping News (Official Freight Indices Reports)
# ---------------------------------------------------------------------------
def scrape_hellenic_shipping(prior_record=None):
    """
    Parses Hellenic Shipping News freight reports for Baltic settlement.
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

        match = re.search(r'(declined|dropped|fell|rose|gained|climbed)\s+([\d\.]+)\s+points?,?\s+or\s+([\d\.]+)%?,?\s+to\s+([\d,]+)', text, re.IGNORECASE)
        if match:
            direction = match.group(1).lower()
            pts = float(match.group(2))
            pct_val = float(match.group(3))
            price_val = clean_float(match.group(4))
            is_down = any(w in direction for w in ('declined', 'dropped', 'fell'))
            change_pts = -pts if is_down else pts
            change_pct = -pct_val if is_down else pct_val

            date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
            date_obj = parse_settlement_date(date_match.group(1)) if date_match else None

            if price_val and date_obj:
                candidate = {
                    'source': 'Hellenic Shipping News',
                    'date': date_obj,
                    'date_str_iso': date_obj.strftime('%Y-%m-%d'),
                    'date_str_csv': date_obj.strftime('%m/%d/%Y'),
                    'price': price_val,
                    'open': price_val,
                    'high': price_val,
                    'low': price_val,
                    'change': change_pts,
                    'change_pct': round(change_pct, 2)
                }
                valid, msg = validate_settlement(candidate, prior_record)
                if valid:
                    return candidate
                else:
                    print(f"[Hellenic] Settlement rejected by validation gate: {msg}")
        return None
    except Exception as e:
        print(f"[Hellenic] Scraper error: {e}")
        return None

# ---------------------------------------------------------------------------
# UNIFIED LIVE SETTLEMENT SCRAPER
# ---------------------------------------------------------------------------
def fetch_live_bdi_settlement():
    """
    Queries maritime market sources in order of resilience and runs through validation gate.
    """
    prior_record = get_latest_csv_record(CANONICAL_CSV)
    if prior_record:
        print(f"[Anchor] Latest recorded CSV settlement: {prior_record['date_str_csv']} at ${prior_record['price']:,.2f} BDI")

    print("[1/4] Querying live maritime market feeds for Baltic Dry Index settlement...")
    sources = [
        ('TradingEconomics', scrape_trading_economics),
        ('Seaandjob', scrape_seaandjob),
        ('Hellenic Shipping News', scrape_hellenic_shipping)
    ]

    for name, scraper_fn in sources:
        print(f"      Attempting source: {name}...")
        res = scraper_fn(prior_record=prior_record)
        if res and res.get('price'):
            print(f"      [OK] Verified valid settlement from {res['source']}:")
            print(f"           Settlement Date : {res['date_str_csv']} ({res['date_str_iso']})")
            print(f"           BDI Price       : {res['price']:,.2f} pts")
            print(f"           Daily Change    : {res['change']:+,.2f} pts ({res['change_pct']:+.2f}%)")
            return res
        else:
            print(f"      [-] Source {name} returned no valid settlement, checking next...")

    raise RuntimeError("Unable to pull validated live BDI settlement from any configured web source.")

# ---------------------------------------------------------------------------
# CSV SYNCHRONIZATION & ORDERED DEDUPLICATION
# ---------------------------------------------------------------------------
def sync_bdi_csv(settlement, target_csv_paths=None, force=False):
    """
    Synchronizes newly scraped settlement to CSV files:
    - Maintains exact institutional format: "Date","Price","Open","High","Low","Vol.","Change %"
    - Single settlement standard: Open = High = Low = Price
    - Strictly sorted in reverse chronological order
    - Automatically updates CANONICAL_CSV in freightrates/ and workspace root
    """
    if target_csv_paths is None:
        target_csv_paths = TARGET_CSV_PATHS

    target_date_csv = settlement['date_str_csv']
    target_dt = settlement['date']
    results = []

    # Format row strictly matching institutional dataset convention
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
            print(f"      [-] Target path does not exist: {path}")
            continue

        with open(path, 'r', encoding='utf-8-sig') as f:
            lines = [l for l in f if l.strip()]

        if not lines:
            continue

        header = lines[0].strip() + '\n'
        data_lines = lines[1:]

        # Parse all dates to avoid duplicates and ensure strict chronological ordering
        existing_records = []
        date_already_exists = False

        for line in data_lines:
            parts = [p.strip(' "\n\r') for p in line.split(',')]
            if parts:
                row_date = parse_settlement_date(parts[0])
                if row_date:
                    if row_date == target_dt:
                        date_already_exists = True
                        if force:
                            continue # Replace existing
                    existing_records.append((row_date, line if line.endswith('\n') else line + '\n'))

        if date_already_exists and not force:
            print(f"      [i] Settlement for {target_date_csv} is already present in {os.path.basename(path)}. No update needed.")
            results.append({'path': path, 'updated': False, 'reason': 'Already present'})
            continue

        # Insert new settlement and sort descending by date
        existing_records.append((target_dt, new_row_str))
        existing_records.sort(key=lambda x: x[0], reverse=True)

        updated_lines = [header] + [rec[1] for rec in existing_records]

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

    if FREIGHTRATES_DIR not in sys.path:
        sys.path.insert(0, FREIGHTRATES_DIR)

    import train

    full_ensemble, records, report = train.train_and_evaluate(CANONICAL_CSV)

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
    Master orchestrator: pulls live settlement, syncs CSVs, and retrains models.
    """
    start_time = time.time()
    print("=" * 80)
    print(f"  BALTIC DRY INDEX (BDI) LIVE DATA AUTO-UPDATE PIPELINE")
    print(f"  Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Canonical CSV : {CANONICAL_CSV}")
    print("=" * 80)

    # Step 1: Scrape & Validate
    settlement = fetch_live_bdi_settlement()

    # Step 2: Update CSVs
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
# SCHEDULER DAEMON
# ---------------------------------------------------------------------------
def run_scheduler(schedule_time_str="18:30", interval_hours=None):
    """
    Continuous scheduler daemon.
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
            try:
                target_hour, target_min = map(int, schedule_time_str.split(':'))
            except ValueError:
                target_hour, target_min = 18, 30

            target_today = now.replace(hour=target_hour, minute=target_min, second=0, microsecond=0)
            if now >= target_today:
                next_run = target_today + timedelta(days=1)
            else:
                next_run = target_today

            wait_secs = (next_run - now).total_seconds()
            print(f"[{now.strftime('%H:%M:%S')}] Next scheduled run at: {next_run.strftime('%Y-%m-%d %H:%M:%S')} (in {wait_secs/3600:.2f} hours)")
            time.sleep(min(wait_secs, 3600))
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
        run_live_update(force=args.force, retrain_if_no_change=args.force_retrain)
