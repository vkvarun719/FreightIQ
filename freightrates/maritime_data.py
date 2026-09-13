"""
maritime_data.py - Maritime intelligence database containing:
1. Multi-vessel dry bulk specifications (Capesize, Panamax, Supramax, Handysize)
2. India's East Coast port restrictions (Max draft, LOA, beam, handling rates, constraints)
3. Major dry bulk trade routes and distance matrices (Nautical miles)
4. Commodity parcel profiles
"""

import numpy as np

# -------------------------------------------------------------
# 1. Vessel Class Specifications
# -------------------------------------------------------------
VESSEL_SPECS = {
    'Capesize': {
        'name': 'Capesize',
        'dwt_range': '150,000 - 210,000 DWT',
        'typical_dwt': 180000,
        'capacity_mt': 170000,
        'draft_m': 18.2,       # Typical laden draft (meters)
        'loa_m': 292.0,        # Length overall
        'beam_m': 45.0,
        'speed_knots': 12.5,
        'fuel_sea_mt_day': 38.0,
        'fuel_port_mt_day': 3.5,
        'typical_commodities': ['Iron Ore', 'Coking Coal', 'Bauxite'],
        'base_multiplier': 1.35, # Multiplier vs Baltic Dry Index composite
        'avg_daily_operating_cost': 7800, # USD/day OPEX
    },
    'Panamax': {
        'name': 'Panamax / Kamsarmax',
        'dwt_range': '65,000 - 85,000 DWT',
        'typical_dwt': 82000,
        'capacity_mt': 75000,
        'draft_m': 14.5,
        'loa_m': 229.0,
        'beam_m': 32.26,
        'speed_knots': 13.0,
        'fuel_sea_mt_day': 26.0,
        'fuel_port_mt_day': 2.8,
        'typical_commodities': ['Thermal Coal', 'Coking Coal', 'Grains', 'Bauxite', 'Fertilizers'],
        'base_multiplier': 0.95, # Multiplier vs Baltic Dry Index composite
        'avg_daily_operating_cost': 6400,
    },
    'Supramax': {
        'name': 'Supramax / Ultramax',
        'dwt_range': '50,000 - 64,000 DWT',
        'typical_dwt': 60000,
        'capacity_mt': 56000,
        'draft_m': 13.0,
        'loa_m': 199.9,
        'beam_m': 32.2,
        'speed_knots': 13.5,
        'fuel_sea_mt_day': 22.0,
        'fuel_port_mt_day': 4.5, # Geared with cranes/grabs
        'typical_commodities': ['Thermal Coal', 'Fertilizers', 'Petcoke', 'Minerals', 'Steel', 'Grains'],
        'base_multiplier': 0.82, # Multiplier vs Baltic Dry Index composite
        'avg_daily_operating_cost': 5600,
        'geared': True,
    },
    'Handysize': {
        'name': 'Handysize',
        'dwt_range': '25,000 - 40,000 DWT',
        'typical_dwt': 35000,
        'capacity_mt': 33000,
        'draft_m': 10.5,
        'loa_m': 180.0,
        'beam_m': 28.0,
        'speed_knots': 12.0,
        'fuel_sea_mt_day': 16.0,
        'fuel_port_mt_day': 3.5,
        'typical_commodities': ['Fertilizers', 'Grains', 'Steel Products', 'Sugar', 'Salt', 'Alumina'],
        'base_multiplier': 0.65, # Multiplier vs Baltic Dry Index composite
        'avg_daily_operating_cost': 4900,
        'geared': True,
    }
}

# -------------------------------------------------------------
# 2. India's East Coast Ports Infrastructure Database
# -------------------------------------------------------------
INDIA_EAST_COAST_PORTS = {
    'Dhamra': {
        'name': 'Dhamra Port (DPCL)',
        'state': 'Odisha',
        'lat': 20.78, 'lon': 86.95,
        'max_draft_m': 18.5,
        'max_loa_m': 320.0,
        'max_beam_m': 50.0,
        'max_dwt': 200000,
        'allowed_vessels': ['Capesize', 'Panamax', 'Supramax', 'Handysize'],
        'discharge_rate_tpd': 45000, # Mechanical conveyor systems
        'loading_rate_tpd': 40000,
        'tidal_restriction': 'Minimal (All-weather deep draft deepwater port)',
        'congestion_index': 'Low (1.5 - 2.5 days avg waiting)',
        'notes': 'Deepwater port capable of handling fully laden Capesize vessels directly without lighterage.'
    },
    'Gangavaram': {
        'name': 'Gangavaram Port',
        'state': 'Andhra Pradesh',
        'lat': 17.62, 'lon': 83.24,
        'max_draft_m': 19.0,
        'max_loa_m': 310.0,
        'max_beam_m': 50.0,
        'max_dwt': 200000,
        'allowed_vessels': ['Capesize', 'Panamax', 'Supramax', 'Handysize'],
        'discharge_rate_tpd': 50000,
        'loading_rate_tpd': 42000,
        'tidal_restriction': 'None (Deep draft all-weather port)',
        'congestion_index': 'Low-Moderate (1 - 3 days)',
        'notes': 'Deepest port on East Coast; optimal for large Capesize coking coal and iron ore discharges.'
    },
    'Krishnapatnam': {
        'name': 'Krishnapatnam Port (KPCT)',
        'state': 'Andhra Pradesh',
        'lat': 14.25, 'lon': 80.13,
        'max_draft_m': 18.0,
        'max_loa_m': 300.0,
        'max_beam_m': 48.0,
        'max_dwt': 180000,
        'allowed_vessels': ['Capesize', 'Panamax', 'Supramax', 'Handysize'],
        'discharge_rate_tpd': 40000,
        'loading_rate_tpd': 35000,
        'tidal_restriction': 'Minimal',
        'congestion_index': 'Low-Moderate (2 - 3.5 days)',
        'notes': 'Excellent deepwater coal & fertilizer hub with automated rakes.'
    },
    'Visakhapatnam': {
        'name': 'Visakhapatnam Port (VPA)',
        'state': 'Andhra Pradesh',
        'lat': 17.69, 'lon': 83.29,
        'max_draft_m': 16.5, # Outer Harbour (Inner is 11.5m)
        'max_loa_m': 290.0,
        'max_beam_m': 45.0,
        'max_dwt': 150000, # Baby-Cape or Part-laden Capesize / Full Panamax
        'allowed_vessels': ['Panamax', 'Supramax', 'Handysize', 'Capesize (Part-laden Outer Berth)'],
        'discharge_rate_tpd': 30000,
        'loading_rate_tpd': 35000,
        'tidal_restriction': 'Outer Harbour deep draft; Inner Harbour restricted to 11.5m draft / Handysize/Supramax.',
        'congestion_index': 'Moderate (3 - 5 days waiting)',
        'notes': 'Outer harbour handles Capesize up to 16.5m draft. Inner berths restricted to Panamax/Supramax.'
    },
    'Paradip': {
        'name': 'Paradip Port Trust (PPT)',
        'state': 'Odisha',
        'lat': 20.26, 'lon': 86.61,
        'max_draft_m': 16.0, # Deep Draft Coal Berth
        'max_loa_m': 285.0,
        'max_beam_m': 45.0,
        'max_dwt': 130000,
        'allowed_vessels': ['Panamax', 'Supramax', 'Handysize', 'Capesize (Part-laden only)'],
        'discharge_rate_tpd': 35000,
        'loading_rate_tpd': 40000,
        'tidal_restriction': 'Subject to swell and seasonal monsoons; draft variations apply.',
        'congestion_index': 'Moderate-High (4 - 7 days during peak coal/iron ore runs)',
        'notes': 'Major coal & pellet terminal. Capesize requires lightened draft.'
    },
    'Ennore': {
        'name': 'Kamarajar Port (Ennore)',
        'state': 'Tamil Nadu',
        'lat': 13.22, 'lon': 80.32,
        'max_draft_m': 16.0,
        'max_loa_m': 270.0,
        'max_beam_m': 43.0,
        'max_dwt': 120000,
        'allowed_vessels': ['Panamax', 'Supramax', 'Handysize'],
        'discharge_rate_tpd': 30000,
        'loading_rate_tpd': 25000,
        'tidal_restriction': 'Moderate',
        'congestion_index': 'Moderate (2.5 - 4 days)',
        'notes': 'Key thermal coal discharge terminal serving Tamil Nadu power plants.'
    },
    'Chennai': {
        'name': 'Chennai Port (ChPA)',
        'state': 'Tamil Nadu',
        'lat': 13.10, 'lon': 80.30,
        'max_draft_m': 14.0,
        'max_loa_m': 250.0,
        'max_beam_m': 38.0,
        'max_dwt': 80000,
        'allowed_vessels': ['Panamax', 'Supramax', 'Handysize'],
        'discharge_rate_tpd': 20000,
        'loading_rate_tpd': 18000,
        'tidal_restriction': 'Moderate',
        'congestion_index': 'Moderate (2 - 4 days)',
        'notes': 'Mainly fertilizer, clean cargo, and coastal bulk. Dusty coal restricted to Ennore.'
    },
    'Haldia': {
        'name': 'Haldia Dock Complex (KOPT)',
        'state': 'West Bengal',
        'lat': 22.03, 'lon': 88.06,
        'max_draft_m': 8.5, # Critical riverine Hooghly draft restriction
        'max_loa_m': 195.0,
        'max_beam_m': 32.2,
        'max_dwt': 45000,
        'allowed_vessels': ['Handysize', 'Supramax (Part-laden only)'],
        'discharge_rate_tpd': 15000,
        'loading_rate_tpd': 12000,
        'tidal_restriction': 'Severe riverine tidal draft restriction (governed by daily tidal windows).',
        'congestion_index': 'High (5 - 8 days waiting due to lock gates & tidal pilotage)',
        'notes': 'Severe draft restriction (~8.0 - 8.5m). Capesize & full Panamax STRICTLY PROHIBITED. Requires coastal transshipment at Sandheads or lightened Handysize.'
    }
}

# -------------------------------------------------------------
# 3. Global Origins & Nautical Distance Matrix (to India East Coast)
# -------------------------------------------------------------
ORIGIN_PORTS = {
    'Port Hedland, Australia': {
        'commodity': ['Iron Ore'],
        'lat': -20.31, 'lon': 118.58,
        'avg_distance_nm': 3350,
        'typical_load_rate_tpd': 85000,
        'origin_region': 'Western Australia',
        'monsoon_impact': 'Tropical cyclone season Dec-April'
    },
    'Hay Point / Dalrymple, Australia': {
        'commodity': ['Coking Coal', 'Thermal Coal'],
        'lat': -21.27, 'lon': 149.30,
        'avg_distance_nm': 4650,
        'typical_load_rate_tpd': 60000,
        'origin_region': 'Eastern Australia',
        'monsoon_impact': 'Moderate'
    },
    'Newcastle, Australia': {
        'commodity': ['Thermal Coal', 'Coking Coal'],
        'lat': -32.93, 'lon': 151.78,
        'avg_distance_nm': 5100,
        'typical_load_rate_tpd': 55000,
        'origin_region': 'Eastern Australia',
        'monsoon_impact': 'Low'
    },
    'Tubarao / Itaqui, Brazil': {
        'commodity': ['Iron Ore', 'Bauxite', 'Grains'],
        'lat': -20.28, 'lon': -40.25,
        'avg_distance_nm': 8800,
        'typical_load_rate_tpd': 90000,
        'origin_region': 'Atlantic / South America',
        'monsoon_impact': 'Rainy season Dec-March in Brazil'
    },
    'Richards Bay, South Africa': {
        'commodity': ['Thermal Coal', 'Titanium Minerals'],
        'lat': -28.80, 'lon': 32.08,
        'avg_distance_nm': 4150,
        'typical_load_rate_tpd': 65000,
        'origin_region': 'South Africa',
        'monsoon_impact': 'Moderate winter swells'
    },
    'Muara Pantai / Samarinda, Indonesia': {
        'commodity': ['Thermal Coal'],
        'lat': -0.50, 'lon': 117.15,
        'avg_distance_nm': 2100,
        'typical_load_rate_tpd': 25000, # Anchorage transshipment
        'origin_region': 'Southeast Asia',
        'monsoon_impact': 'High rainfall during NW monsoon'
    },
    'Kamsar, Guinea': {
        'commodity': ['Bauxite'],
        'lat': 10.65, 'lon': -14.60,
        'avg_distance_nm': 7900,
        'typical_load_rate_tpd': 45000,
        'origin_region': 'West Africa',
        'monsoon_impact': 'Heavy rains June-Oct'
    },
    'Black Sea / Novorossiysk': {
        'commodity': ['Grains', 'Fertilizers', 'Coal'],
        'lat': 44.72, 'lon': 37.77,
        'avg_distance_nm': 4900,
        'typical_load_rate_tpd': 20000,
        'origin_region': 'Black Sea / Med',
        'monsoon_impact': 'Geopolitical / Bosphorus transit'
    },
    'Indian Coastal (Mormugao / Jaigad)': {
        'commodity': ['Thermal Coal', 'Iron Ore Pellets', 'Bauxite'],
        'lat': 15.41, 'lon': 73.80,
        'avg_distance_nm': 1100,
        'typical_load_rate_tpd': 28000,
        'origin_region': 'India West Coast (Domestic Coastal)',
        'monsoon_impact': 'Severe SW Monsoon June-August'
    }
}
