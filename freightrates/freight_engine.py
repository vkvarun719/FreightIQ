"""
freight_engine.py - Core Decision Support Engine for Intelligent Freight Rate Forecasting & Chartering Optimization (2026 Edition).
"""

import os
import json
import math
from datetime import datetime, timedelta
import numpy as np

import baltic_data
import forecasting_models
import maritime_data

CURRENT_DATE = datetime(2026, 9, 8) # September 2026 latest trading baseline

def get_calibrated_forecasts(horizon_days=90, base_filepath='Baltic Dry Index Historical Data.csv'):
    """
    Loads historical index with 2026 dates and generates ensemble forecasts.
    """
    records = baltic_data.load_baltic_raw(base_filepath)
    enriched, _ = baltic_data.calculate_technical_indicators(records)
    X, y_prices, y_returns, _ = baltic_data.extract_feature_matrix(enriched)
    
    ensemble = forecasting_models.MetaEnsembleForecaster().fit(X[:-1], y_returns[:-1], [r['price'] for r in records])
    
    raw_forecasts = ensemble.forecast_multistep(records, steps=horizon_days, start_date=records[-1]['date'])
    return raw_forecasts, records, enriched, ensemble

# -------------------------------------------------------------
# REQUIREMENT A: Optimal Market Entry Timing
# -------------------------------------------------------------
def analyze_optimal_timing(forecast_list, vessel_type='Capesize', contract_duration='Spot (1 Month)'):
    rates = [f['predicted_price'] for f in forecast_list]
    dates = [f['date'] for f in forecast_list]
    
    current_rate = rates[0]
    min_rate = min(rates)
    min_idx = rates.index(min_rate)
    optimal_date = dates[min_idx]
    
    delta_vs_prompt = current_rate - min_rate
    savings_pct = (delta_vs_prompt / current_rate) * 100.0 if current_rate > 0 else 0.0
    
    if min_idx <= 2:
        timing_action = "IMMEDIATE ENTRY (PROMPT FIXTURE)"
        reasoning = f"Market is currently near a local support floor (${current_rate:,.2f} BDI). Secure prompt vessel commitments before projected upward rebound."
    elif min_idx > 2 and savings_pct >= 3.0:
        timing_action = "DEFERRED ENTRY (STRATEGIC BUYING WINDOW)"
        reasoning = f"Forecast model identifies a rate trough toward ${min_rate:,.2f} BDI around {optimal_date} (Step {min_idx + 1}). Deferring charter fixing to this window delivers an estimated {savings_pct:.1f}% freight savings (${delta_vs_prompt:,.2f} BDI delta)."
    else:
        timing_action = "STAGGERED / INDEX-LINKED ENTRY"
        reasoning = f"Freight rates remain bounded within a tight channel (${min_rate:,.2f} - ${max(rates):,.2f} BDI). Fix 50% on index-linked terms with a bunker collar adjustment."

    contract_recommendation = ""
    if 'Spot' in contract_duration:
        contract_recommendation = "Spot Voyage Charter recommended to capitalize on immediate rate cycle dips."
    elif '3 Month' in contract_duration:
        contract_recommendation = "Short-Term Time Charter (3 Months) with floating bunker adjustment clause."
    elif '6 Month' in contract_duration:
        contract_recommendation = "Mid-Term Period Charter (6 Months) with early renewal option in Q4 2026."
    else:
        contract_recommendation = "Annual Contract of Affreightment (COA 12-Month) with quarterly index recalculation."

    return {
        'vessel_type': vessel_type,
        'timing_action': timing_action,
        'optimal_window_date': optimal_date,
        'optimal_day_step': min_idx + 1,
        'current_rate': current_rate,
        'optimal_rate': min_rate,
        'potential_savings_pct': round(savings_pct, 2),
        'potential_savings_delta': round(delta_vs_prompt, 2),
        'reasoning': reasoning,
        'contract_recommendation': contract_recommendation,
        'horizon_analyzed_days': len(forecast_list)
    }

# -------------------------------------------------------------
# REQUIREMENT B: Vessel Type & Port Infrastructure Optimization
# -------------------------------------------------------------
def optimize_vessel_for_port(cargo_mt, commodity, origin_port_name, dest_port_name, prompt_cape_rate):
    dest_port = maritime_data.INDIA_EAST_COAST_PORTS.get(dest_port_name, maritime_data.INDIA_EAST_COAST_PORTS['Visakhapatnam'])
    origin_port = maritime_data.ORIGIN_PORTS.get(origin_port_name, {
        'avg_distance_nm': 3500,
        'typical_load_rate_tpd': 45000,
        'monsoon_impact': 'Moderate'
    })

    distance_nm = origin_port['avg_distance_nm']
    load_rate = origin_port['typical_load_rate_tpd']
    disch_rate = dest_port['discharge_rate_tpd']

    evaluations = {}
    best_vessel = None
    min_cost_per_mt = float('inf')

    for v_name, v_spec in maritime_data.VESSEL_SPECS.items():
        is_allowed = True
        violation_reasons = []
        warning_notes = []

        # 1. Draft check
        if v_spec['draft_m'] > dest_port['max_draft_m']:
            is_allowed = False
            violation_reasons.append(
                f"Draft ({v_spec['draft_m']}m) exceeds {dest_port_name} max permissible draft ({dest_port['max_draft_m']}m)."
            )

        # 2. LOA check
        if v_spec['loa_m'] > dest_port['max_loa_m']:
            is_allowed = False
            violation_reasons.append(
                f"LOA ({v_spec['loa_m']}m) exceeds {dest_port_name} max length ({dest_port['max_loa_m']}m)."
            )

        # 3. Port-specific constraints
        if dest_port_name == 'Haldia' and v_name in ['Capesize', 'Panamax']:
            is_allowed = False
            violation_reasons.append("Haldia Hooghly river draft (8.5m) prohibits Capesize and laden Panamax.")

        if dest_port_name == 'Visakhapatnam' and v_name == 'Capesize':
            warning_notes.append("Capesize restricted to VPA Outer Harbour only (max 16.5m draft).")

        if dest_port_name == 'Paradip' and v_name == 'Capesize':
            warning_notes.append("Capesize requires high-tide pilotage window.")

        # Voyage Calculations
        effective_capacity = min(cargo_mt, v_spec['capacity_mt'])
        num_trips_needed = math.ceil(cargo_mt / v_spec['capacity_mt'])
        
        speed = v_spec['speed_knots']
        sea_days = distance_nm / (speed * 24.0)
        round_trip_sea = sea_days * 2.0
        
        load_days = effective_capacity / load_rate + 1.0
        disch_days = effective_capacity / disch_rate + 1.0
        waiting_days = 2.0 if 'Low' in dest_port['congestion_index'] else (4.0 if 'Moderate' in dest_port['congestion_index'] else 6.5)
        total_port_days = load_days + disch_days + waiting_days
        total_voyage_days = sea_days + total_port_days

        # Daily hire calculation
        v_multiplier = v_spec['base_multiplier']
        daily_hire = prompt_cape_rate * 10.5 * v_multiplier
        bunker_cost = (round_trip_sea * v_spec['fuel_sea_mt_day'] + total_port_days * v_spec['fuel_port_mt_day']) * 610.0
        port_dues = 45000 if v_name == 'Capesize' else (32000 if v_name == 'Panamax' else 22000)
        
        total_freight_cost = (total_voyage_days * daily_hire + bunker_cost + port_dues) * num_trips_needed
        freight_per_mt = total_freight_cost / cargo_mt

        demurrage_risk = "Low" if waiting_days <= 2.5 else ("Moderate" if waiting_days <= 4.5 else "High")
        demurrage_rate = daily_hire * 1.25

        eval_data = {
            'vessel_name': v_name,
            'is_allowed': is_allowed,
            'violation_reasons': violation_reasons,
            'warning_notes': warning_notes,
            'effective_capacity_mt': effective_capacity,
            'trips_required': num_trips_needed,
            'sea_days_one_way': round(sea_days, 1),
            'total_port_turnaround_days': round(total_port_days, 1),
            'total_voyage_days': round(total_voyage_days, 1),
            'daily_hire_usd': round(daily_hire, 2),
            'total_freight_cost_usd': round(total_freight_cost, 2),
            'freight_cost_per_mt_usd': round(freight_per_mt, 2),
            'demurrage_risk': demurrage_risk,
            'demurrage_daily_exposure_usd': round(demurrage_rate, 2)
        }
        evaluations[v_name] = eval_data

        if is_allowed and freight_per_mt < min_cost_per_mt:
            min_cost_per_mt = freight_per_mt
            best_vessel = v_name

    if not best_vessel:
        best_vessel = 'Handysize'

    return {
        'origin_port': origin_port_name,
        'dest_port': dest_port_name,
        'cargo_volume_mt': cargo_mt,
        'commodity': commodity,
        'recommended_vessel': best_vessel,
        'recommended_cost_per_mt': evaluations[best_vessel]['freight_cost_per_mt_usd'],
        'total_turnaround_days': evaluations[best_vessel]['total_port_turnaround_days'],
        'port_draft_limit_m': dest_port['max_draft_m'],
        'port_loa_limit_m': dest_port['max_loa_m'],
        'port_handling_profile': f"{dest_port['discharge_rate_tpd']:,} TPD ({dest_port['state']})",
        'all_vessel_evaluations': evaluations
    }

# -------------------------------------------------------------
# REQUIREMENT C: Idle Scenario Management (Dynamic Port-Specific)
# -------------------------------------------------------------
PORT_IDLE_STRATEGIES = {
    'Visakhapatnam': [
        {
            'strategy_name': 'Coastal Coal Run to Ennore / Tuticorin',
            'description': 'Load domestic coal at Vizag / Gangavaram for TANGEDCO/NTPC power utilities on Tamil Nadu coast.',
            'ballast_reduction_nm': '1,250 NM saved vs returning empty to Australia/Indonesia',
            'expected_tce_boost': '+$2,400 / day net TCE boost',
            'feasibility': 'Immediate (High domestic coastal utility demand in Q3-Q4 2026)'
        },
        {
            'strategy_name': 'Kakinada Agri Grains & Bauxite Backhaul',
            'description': 'Reposition 35 NM south to Kakinada Deepwater to lift 45,000-65,000 MT rice/wheat for delivery to Chittagong / SE Asia.',
            'ballast_reduction_nm': '1,950 NM revenue miles generated',
            'expected_tce_boost': '+$1,850 / day net revenue',
            'feasibility': 'Optimal for Panamax and Supramax classes'
        }
    ],
    'Paradip': [
        {
            'strategy_name': 'Paradip-to-South Coast Coastal Coal Shuttle',
            'description': 'Engage in captive coastal coal movement from Paradip to Kamarajar (Ennore) or Krishnapatnam thermal stations.',
            'ballast_reduction_nm': '1,650 NM empty deadhead avoided',
            'expected_tce_boost': '+$2,800 / day net TCE boost',
            'feasibility': 'High volume corridor with dedicated mechanized loading'
        },
        {
            'strategy_name': 'Iron Ore Pellets to China / Vietnam',
            'description': 'Load export pellets from Paradip pellet plants for delivery to Southeast Asian / Chinese blast furnaces.',
            'ballast_reduction_nm': '2,400 NM laden revenue voyage',
            'expected_tce_boost': '+$2,100 / day net revenue',
            'feasibility': 'Active export licenses available in 2026'
        }
    ],
    'Dhamra': [
        {
            'strategy_name': 'Tata Steel / SAIL Triangular Supply Loop',
            'description': 'After coking coal discharge, ballast to UAE/Oman to lift limestone/gypsum back to Dhamra.',
            'ballast_reduction_nm': '2,200 NM unballasted repositioning saved',
            'expected_tce_boost': '+$3,100 / day net TCE',
            'feasibility': 'Ideal for Capesize and Panamax bulkers'
        },
        {
            'strategy_name': 'Paradip Coastal Coal Triangulation',
            'description': 'Short 40 NM repositioning to Paradip for coastal coal shipment to Krishnapatnam / Tuticorin.',
            'ballast_reduction_nm': '1,500 NM deadhead eliminated',
            'expected_tce_boost': '+$2,600 / day',
            'feasibility': 'Immediate availability'
        }
    ],
    'Gangavaram': [
        {
            'strategy_name': 'Rashtriya Ispat Nigam (RINL) Industrial Loop',
            'description': 'Engage in dedicated raw material supply cycle, picking up coastal bauxite or limestone from Gujarat/West Coast.',
            'ballast_reduction_nm': '1,800 NM deadhead reduction',
            'expected_tce_boost': '+$2,700 / day net TCE',
            'feasibility': 'Supported by deepwater 19.0m draft berths'
        },
        {
            'strategy_name': 'East Africa / South Africa Triangulation',
            'description': 'Ballast directly across Indian Ocean to Richards Bay (RBCT) for guaranteed thermal coal fixtures.',
            'ballast_reduction_nm': '3,200 NM avoided ballast to South America',
            'expected_tce_boost': 'Preserves 89% vessel operational utilization',
            'feasibility': 'Commercial standard for Capesize/Panamax'
        }
    ],
    'Krishnapatnam': [
        {
            'strategy_name': 'Granite & Agricultural Backhaul to Far East',
            'description': 'Load granite blocks and bagged agricultural goods from Krishnapatnam hinterland for Singapore / China delivery.',
            'ballast_reduction_nm': '2,100 NM revenue miles generated',
            'expected_tce_boost': '+$1,950 / day net revenue',
            'feasibility': 'Optimal for Supramax / Handysize with ship cranes'
        },
        {
            'strategy_name': 'APGENCO Coastal Power Triangle',
            'description': 'Short ballast north to Paradip/Vizag to pick up domestic coal for return to Krishnapatnam.',
            'ballast_reduction_nm': '1,400 NM saved vs foreign ballast',
            'expected_tce_boost': '+$2,300 / day net TCE',
            'feasibility': 'High recurring utility demand'
        }
    ],
    'Ennore': [
        {
            'strategy_name': 'Northbound Coastal Ballast Shuttle (Ennore -> Paradip)',
            'description': 'After discharging coal for TANGEDCO power plants, execute fast 500 NM ballast back to Paradip for immediate reload.',
            'ballast_reduction_nm': 'Reduces round-trip ballast time by 60% compared to international repositioning',
            'expected_tce_boost': '+$3,200 / day continuous TCE on round-voyage basis',
            'feasibility': 'Dedicated power utility coastal contract loop'
        },
        {
            'strategy_name': 'Tuticorin Salt & Mineral Sands Backhaul',
            'description': 'Reposition south to Tuticorin / VOC Port to load industrial salt and ilmenite sand for SE Asia.',
            'ballast_reduction_nm': '1,600 NM revenue generation',
            'expected_tce_boost': '+$1,700 / day',
            'feasibility': 'Optimal for Handysize/Supramax'
        }
    ],
    'Chennai': [
        {
            'strategy_name': 'Automotive / Steel & Fertilizer Transshipment',
            'description': 'Lift steel coils and manufactured goods from Chennai industrial corridor for Middle East / SE Asia.',
            'ballast_reduction_nm': '1,750 NM laden revenue voyage',
            'expected_tce_boost': '+$2,100 / day',
            'feasibility': 'Ideal for geared Handysize and Supramax'
        },
        {
            'strategy_name': 'Short Ballast to Krishnapatnam / Ennore',
            'description': 'Reposition 60 NM north to Krishnapatnam for bulk mineral or agricultural export cargoes.',
            'ballast_reduction_nm': 'Eliminates international deadheading',
            'expected_tce_boost': '+$1,800 / day',
            'feasibility': 'Immediate availability'
        }
    ],
    'Haldia': [
        {
            'strategy_name': 'Hooghly River & Sandheads Transshipment Shuttling',
            'description': 'Deploy geared Handysize as feeder/transshipment vessel lightering Panamax/Capesize at Sandheads for Haldia discharge.',
            'ballast_reduction_nm': 'High-frequency domestic shuttle generating 100% laden utilization',
            'expected_tce_boost': '+$3,500 / day transshipment premium',
            'feasibility': 'Essential service due to Haldia 8.5m draft restriction'
        },
        {
            'strategy_name': 'Kolkata-Chittagong Coastal Cabotage',
            'description': 'Pick up fly ash, cement clinker, and industrial minerals for short-sea delivery into Bangladesh.',
            'ballast_reduction_nm': '950 NM continuous revenue loop',
            'expected_tce_boost': '+$1,900 / day net TCE',
            'feasibility': 'High demand bilateral trade corridor'
        }
    ]
}

def generate_idle_management_strategy(dest_port_name, arrival_date_str, vessel_type='Panamax'):
    strategies = PORT_IDLE_STRATEGIES.get(dest_port_name, PORT_IDLE_STRATEGIES['Visakhapatnam'])
    return {
        'arrival_date': arrival_date_str,
        'dest_port': dest_port_name,
        'regional_demand_outlook': 'High (Active Q3-Q4 2026 Shipping Season)',
        'recommended_strategies': strategies
    }

# -------------------------------------------------------------
# REQUIREMENT D: Risk Mitigation & Early Warnings (Port & Origin Specific)
# -------------------------------------------------------------
PORT_CONGESTION_DATA = {
    'Dhamra': {'level': 'LOW', 'details': 'Dhamra Port (DPCL): 1.5 - 2.5 days avg waiting. Deepwater automated berths; minimal delay risk.'},
    'Gangavaram': {'level': 'LOW', 'details': 'Gangavaram Port: 1 - 3 days avg waiting. Deepest draft on East Coast (19.0m); rapid turnaround.'},
    'Krishnapatnam': {'level': 'MODERATE', 'details': 'Krishnapatnam Port (KPCT): 2 - 3.5 days waiting. Automated rakes; minor berth allocation queues.'},
    'Visakhapatnam': {'level': 'MODERATE', 'details': 'Visakhapatnam Port (VPA): 3 - 5 days waiting. Outer harbour fast for Capesize; inner berths subject to tidal lock.'},
    'Paradip': {'level': 'HIGH', 'details': 'Paradip Port Trust (PPT): 4 - 7 days waiting. Heavy thermal coal and iron ore traffic; enforce WIBON demurrage clause.'},
    'Ennore': {'level': 'MODERATE', 'details': 'Kamarajar Port (Ennore): 2.5 - 4 days waiting. Thermal coal discharge queue for Tamil Nadu power utilities.'},
    'Chennai': {'level': 'MODERATE', 'details': 'Chennai Port (ChPA): 2 - 4 days waiting. General cargo & fertilizer berths require advance stem reservation.'},
    'Haldia': {'level': 'HIGH', 'details': 'Haldia Dock Complex (KOPT): 5 - 8 days waiting. Lock-gate transit and severe Hooghly tidal pilotage constraints.'}
}

ORIGIN_WEATHER_DATA = {
    'Port Hedland, Australia': 'Western Australia cyclone season watch (Nov-April). Current conditions favorable.',
    'Hay Point / Dalrymple, Australia': 'Queensland trade route: Normal operating conditions.',
    'Newcastle, Australia': 'NSW Coast: Normal swell conditions.',
    'Tubarao / Itaqui, Brazil': 'Atlantic route: Minor winter swell; monitor Cape of Good Hope rounding.',
    'Richards Bay, South Africa': 'Indian Ocean passage: Moderate swell around Madagascar passage.',
    'Muara Pantai / Samarinda, Indonesia': 'Indonesia equatorial passage: Frequent squalls and anchorage barging delays.',
    'Kamsar, Guinea': 'West Africa Atlantic transit: Tropical rain season monitoring.',
    'Black Sea / Novorossiysk': 'Bosphorus transit queue and geopolitical insurance surcharges apply.',
    'Indian Coastal (Mormugao / Jaigad)': 'West Coast India: SW Monsoon tapering off; normal coastal navigation.'
}

def evaluate_risk_and_early_warnings(dest_port_name, origin_port_name, forecast_list):
    dest_risk = PORT_CONGESTION_DATA.get(dest_port_name, PORT_CONGESTION_DATA['Visakhapatnam'])
    origin_weather = ORIGIN_WEATHER_DATA.get(origin_port_name, 'Normal oceanic passage conditions.')
    
    rates = [f['predicted_price'] for f in forecast_list[:30]]
    vol_pct = (np.std(rates) / np.mean(rates)) * 100.0
    vol_level = "HIGH" if vol_pct > 12.0 else ("MODERATE" if vol_pct > 6.0 else "LOW")
    vol_msg = f"Elevated market volatility detected ({vol_pct:.1f}% 30-day forecast variance). Implement strict FFA bunker hedging." if vol_level == "HIGH" else f"Stable market conditions ({vol_pct:.1f}% variance)."

    return {
        'market_volatility': {
            'level': vol_level,
            'variance_pct': round(vol_pct, 2),
            'early_warning': vol_msg
        },
        'weather_and_seasonal_risks': [
            {
                'type': 'Origin & Transit Weather',
                'severity': 'MODERATE' if 'squalls' in origin_weather or 'cyclone' in origin_weather else 'LOW',
                'details': origin_weather
            },
            {
                'type': 'Bay of Bengal Regional Alert',
                'severity': 'MODERATE',
                'details': 'South-West Monsoon active across Bay of Bengal. Expect outer-anchorage swell delays and Hooghly/Haldia tidal draft fluctuations.'
            }
        ],
        'port_congestion_risk': {
            'port': dest_port_name,
            'level': dest_risk['level'],
            'details': f"{dest_risk['details']} Ensure charter party includes robust 'Whether In Berth Or Not' (WIBON) terms."
        }
    }
