import { Commodity, PortOption, PortRestrictionAlert, VesselRecommendation, FleetVessel } from '../types';

export const COMMODITIES: Commodity[] = ['Coal', 'Iron Ore', 'Grain', 'Bauxite'];

// Indian Ports as Origins (User requirement: Add Indian ports in origin section)
export const ORIGIN_PORTS: PortOption[] = [
  { code: 'IND-VTZ', name: 'Visakhapatnam (IND)', country: 'India', region: 'East Coast (Andhra Pradesh)', maxDraft: 16.5, typicalCongestionDays: 3.2, type: 'export' },
  { code: 'IND-PAR', name: 'Paradip (IND)', country: 'India', region: 'East Coast (Odisha)', maxDraft: 16.0, typicalCongestionDays: 4.1, type: 'export' },
  { code: 'IND-DHM', name: 'Dhamra (IND)', country: 'India', region: 'East Coast (Odisha)', maxDraft: 18.5, typicalCongestionDays: 1.8, type: 'export' },
  { code: 'IND-GGV', name: 'Gangavaram (IND)', country: 'India', region: 'East Coast (Andhra Pradesh)', maxDraft: 19.0, typicalCongestionDays: 1.5, type: 'export' },
  { code: 'IND-HAL', name: 'Haldia (IND)', country: 'India', region: 'East Coast (West Bengal)', maxDraft: 8.5, typicalCongestionDays: 5.5, type: 'export' },
  { code: 'IND-ENR', name: 'Kamarajar / Ennore (IND)', country: 'India', region: 'East Coast (Tamil Nadu)', maxDraft: 16.0, typicalCongestionDays: 2.4, type: 'export' },
  { code: 'IND-MAA', name: 'Chennai (IND)', country: 'India', region: 'East Coast (Tamil Nadu)', maxDraft: 14.0, typicalCongestionDays: 2.8, type: 'export' },
  { code: 'IND-KRI', name: 'Krishnapatnam (IND)', country: 'India', region: 'East Coast (Andhra Pradesh)', maxDraft: 18.0, typicalCongestionDays: 2.1, type: 'export' },
  { code: 'IND-MRM', name: 'Mormugao (IND)', country: 'India', region: 'West Coast (Goa)', maxDraft: 14.5, typicalCongestionDays: 3.0, type: 'export' },
  { code: 'IND-BOM', name: 'Mumbai / JNPT (IND)', country: 'India', region: 'West Coast (Maharashtra)', maxDraft: 15.0, typicalCongestionDays: 2.2, type: 'export' },
];

// Foreign Ports as Destinations (User requirement: Foreign ports in destination section)
export const DESTINATION_PORTS: PortOption[] = [
  { code: 'CHN-QIN', name: 'Qingdao (CHN)', country: 'China', region: 'East Asia', maxDraft: 21.0, typicalCongestionDays: 2.4, type: 'discharge' },
  { code: 'NLD-ROT', name: 'Rotterdam (NLD)', country: 'Netherlands', region: 'North Sea (Europe)', maxDraft: 23.5, typicalCongestionDays: 1.2, type: 'discharge' },
  { code: 'SGP-SGP', name: 'Singapore (SGP)', country: 'Singapore', region: 'Straits of Malacca', maxDraft: 20.5, typicalCongestionDays: 0.6, type: 'bunker' },
  { code: 'JPN-TYO', name: 'Tokyo / Chiba (JPN)', country: 'Japan', region: 'East Asia', maxDraft: 17.5, typicalCongestionDays: 1.8, type: 'discharge' },
  { code: 'CHN-FAN', name: 'Fangcheng / Guangzhou (CHN)', country: 'China', region: 'South China', maxDraft: 16.2, typicalCongestionDays: 3.1, type: 'discharge' },
  { code: 'KOR-PUS', name: 'Busan (KOR)', country: 'South Korea', region: 'East Asia', maxDraft: 18.0, typicalCongestionDays: 1.6, type: 'discharge' },
  { code: 'BGD-CGP', name: 'Chittagong (BGD)', country: 'Bangladesh', region: 'Bay of Bengal', maxDraft: 9.5, typicalCongestionDays: 4.8, type: 'discharge' },
  { code: 'ARE-DXB', name: 'Jebel Ali / Dubai (ARE)', country: 'UAE', region: 'Persian Gulf', maxDraft: 16.0, typicalCongestionDays: 1.4, type: 'discharge' },
  { code: 'GBR-TAL', name: 'Port Talbot / Dunkirk (GBR/FRA)', country: 'UK / France', region: 'Atlantic / Channel', maxDraft: 17.8, typicalCongestionDays: 2.0, type: 'discharge' },
];

// Distance matrix (Nautical Miles from Indian Origins to Destinations)
export const ROUTE_DISTANCES: Record<string, Record<string, number>> = {
  'IND-VTZ': { 'CHN-QIN': 4250, 'NLD-ROT': 7800, 'SGP-SGP': 1580, 'JPN-TYO': 4600, 'CHN-FAN': 2450, 'KOR-PUS': 4400, 'BGD-CGP': 620, 'ARE-DXB': 2250, 'GBR-TAL': 7700 },
  'IND-PAR': { 'CHN-QIN': 4180, 'NLD-ROT': 7950, 'SGP-SGP': 1650, 'JPN-TYO': 4550, 'CHN-FAN': 2520, 'KOR-PUS': 4350, 'BGD-CGP': 420, 'ARE-DXB': 2400, 'GBR-TAL': 7850 },
  'IND-DHM': { 'CHN-QIN': 4150, 'NLD-ROT': 8000, 'SGP-SGP': 1680, 'JPN-TYO': 4520, 'CHN-FAN': 2550, 'KOR-PUS': 4320, 'BGD-CGP': 380, 'ARE-DXB': 2450, 'GBR-TAL': 7900 },
  'IND-GGV': { 'CHN-QIN': 4260, 'NLD-ROT': 7780, 'SGP-SGP': 1570, 'JPN-TYO': 4610, 'CHN-FAN': 2440, 'KOR-PUS': 4410, 'BGD-CGP': 630, 'ARE-DXB': 2240, 'GBR-TAL': 7680 },
  'IND-HAL': { 'CHN-QIN': 4100, 'NLD-ROT': 8050, 'SGP-SGP': 1720, 'JPN-TYO': 4480, 'CHN-FAN': 2590, 'KOR-PUS': 4280, 'BGD-CGP': 310, 'ARE-DXB': 2500, 'GBR-TAL': 7950 },
  'IND-ENR': { 'CHN-QIN': 4450, 'NLD-ROT': 7450, 'SGP-SGP': 1420, 'JPN-TYO': 4780, 'CHN-FAN': 2290, 'KOR-PUS': 4580, 'BGD-CGP': 910, 'ARE-DXB': 1950, 'GBR-TAL': 7350 },
  'IND-MAA': { 'CHN-QIN': 4460, 'NLD-ROT': 7440, 'SGP-SGP': 1410, 'JPN-TYO': 4790, 'CHN-FAN': 2280, 'KOR-PUS': 4590, 'BGD-CGP': 920, 'ARE-DXB': 1940, 'GBR-TAL': 7340 },
  'IND-KRI': { 'CHN-QIN': 4380, 'NLD-ROT': 7550, 'SGP-SGP': 1470, 'JPN-TYO': 4720, 'CHN-FAN': 2340, 'KOR-PUS': 4520, 'BGD-CGP': 820, 'ARE-DXB': 2040, 'GBR-TAL': 7450 },
  'IND-MRM': { 'CHN-QIN': 5100, 'NLD-ROT': 6450, 'SGP-SGP': 2080, 'JPN-TYO': 5450, 'CHN-FAN': 2950, 'KOR-PUS': 5250, 'BGD-CGP': 1850, 'ARE-DXB': 1180, 'GBR-TAL': 6350 },
  'IND-BOM': { 'CHN-QIN': 5250, 'NLD-ROT': 6200, 'SGP-SGP': 2220, 'JPN-TYO': 5600, 'CHN-FAN': 3100, 'KOR-PUS': 5400, 'BGD-CGP': 2010, 'ARE-DXB': 950, 'GBR-TAL': 6100 },
};

export function getRouteDistanceNm(originCode: string, destCode: string): number {
  if (ROUTE_DISTANCES[originCode] && ROUTE_DISTANCES[originCode][destCode]) {
    return ROUTE_DISTANCES[originCode][destCode];
  }
  return 3800; // default average nautical miles
}

export function computeVesselRecommendation(cargoVolume: number): VesselRecommendation {
  if (cargoVolume < 60000) {
    const fuelVal = Math.round((cargoVolume / 75000) * 32400);
    const fuelTons = Math.round((cargoVolume / 75000) * 52);
    return {
      className: 'Supramax Class',
      vesselName: 'MV Nordic Horizon • 58,200 DWT',
      dwt: 58200,
      ciiRating: 'A',
      ecoSpeedKnots: 11.2,
      ecoConsumptionTonsDay: 19.5,
      standardSpeedKnots: 13.0,
      fuelSavedUsd: fuelVal,
      fuelSavedTons: fuelTons,
      ballastWaterCompliance: 'USCG & D-2 Type Approved',
    };
  } else if (cargoVolume <= 95000) {
    const fuelVal = Math.round((cargoVolume / 75000) * 42800);
    const fuelTons = Math.round((cargoVolume / 75000) * 68);
    return {
      className: 'Panamax Class',
      vesselName: 'MV Pacific Mariner • 76,500 DWT',
      dwt: 76500,
      ciiRating: 'A',
      ecoSpeedKnots: 11.5,
      ecoConsumptionTonsDay: 22.0,
      standardSpeedKnots: 13.5,
      fuelSavedUsd: fuelVal,
      fuelSavedTons: fuelTons,
      ballastWaterCompliance: 'D-2 Compliant (Alfa Laval PureBallast)',
    };
  } else {
    const fuelVal = Math.round((cargoVolume / 75000) * 86000);
    const fuelTons = Math.round((cargoVolume / 75000) * 138);
    return {
      className: 'Capesize Class',
      vesselName: 'MV Stella Ocean • 178,000 DWT',
      dwt: 178000,
      ciiRating: 'B',
      ecoSpeedKnots: 10.8,
      ecoConsumptionTonsDay: 38.0,
      standardSpeedKnots: 14.0,
      fuelSavedUsd: fuelVal,
      fuelSavedTons: fuelTons,
      ballastWaterCompliance: 'BWTS Commissioned & IMO Tier III',
    };
  }
}

export function computePortAlert(destPortCode: string, cargoVolume: number, originPortCode?: string): PortRestrictionAlert {
  // Check Origin constraints first (e.g. Haldia river draft)
  if (originPortCode === 'IND-HAL') {
    const isExceeded = cargoVolume > 40000;
    return {
      portCode: 'IND-HAL',
      portName: 'Haldia Dock Complex (IND)',
      maxDraft: 8.5,
      severity: isExceeded ? 'critical' : 'moderate',
      statusTag: isExceeded ? 'CRITICAL LOADING RESTRICTION' : 'TIDAL LOCK WINDOW',
      description: `Origin Port: Haldia has strict Hooghly river draft limit of 8.5m. A ${cargoVolume.toLocaleString()} MT parcel exceeds safe departure draft.`,
      tacticalMitigation: 'Short-load vessel to 38,000 MT at Haldia and top-up at Sandheads or Paradip anchorage via lighterage barge.',
      waitingDays: 5.5,
      queueCount: 11,
    };
  }

  // Check Destination restrictions
  if (destPortCode === 'BGD-CGP') {
    const isExceeded = cargoVolume > 45000;
    return {
      portCode: 'BGD-CGP',
      portName: 'Chittagong (BGD)',
      maxDraft: 9.5,
      severity: isExceeded ? 'critical' : 'moderate',
      statusTag: isExceeded ? 'SHALLOW BARRIER RESTRICTION' : 'RIVERINE APPROACH',
      description: `Discharge Port: Chittagong outer bar limits draft to 9.5m. Heavy parcel requires outer anchorage transshipment.`,
      tacticalMitigation: 'Engage Kutubdia anchorage lighterage tankers/barges or deploy geared Supramax vessels under 45,000 MT.',
      waitingDays: 4.8,
      queueCount: 14,
    };
  } else if (destPortCode === 'CHN-QIN') {
    return {
      portCode: 'CHN-QIN',
      portName: 'Qingdao (CHN)',
      maxDraft: 21.0,
      severity: 'optimal',
      statusTag: 'DEEPWATER ORE TERMINAL',
      description: 'Dongjiakou port area accommodates 400,000 DWT Valemax ore carriers. 21.0m draft available.',
      tacticalMitigation: 'Direct mechanized conveyor discharge to stockyard or inland rail link.',
      waitingDays: 2.4,
      queueCount: 5,
    };
  } else if (destPortCode === 'NLD-ROT') {
    return {
      portCode: 'NLD-ROT',
      portName: 'Rotterdam (NLD)',
      maxDraft: 23.5,
      severity: 'optimal',
      statusTag: 'DEEPWATER GATEWAY',
      description: 'Europort and Maasvlakte terminals offer unrestricted 23.5m tidal basin depth.',
      tacticalMitigation: 'Rhine river hinterland barges and direct automated grab discharge ready upon arrival.',
      waitingDays: 1.2,
      queueCount: 3,
    };
  } else if (destPortCode === 'SGP-SGP') {
    return {
      portCode: 'SGP-SGP',
      portName: 'Singapore (SGP)',
      maxDraft: 20.5,
      severity: 'optimal',
      statusTag: 'TRANSIT & BUNKER HUB',
      description: 'Unrestricted deepwater anchorage. Optimal for VLSFO replenishment and transshipment fixing.',
      tacticalMitigation: 'Barge bunker delivery pre-cleared with Maritime and Port Authority of Singapore (MPA).',
      waitingDays: 0.6,
      queueCount: 1,
    };
  } else if (destPortCode === 'JPN-TYO') {
    return {
      portCode: 'JPN-TYO',
      portName: 'Tokyo / Chiba (JPN)',
      maxDraft: 17.5,
      severity: 'optimal',
      statusTag: 'INDUSTRIAL BULK TERMINAL',
      description: 'Permissible draft 17.5m at Chiba Tokyo Bay deep berths. Fully handles Panamax and Baby-Cape.',
      tacticalMitigation: 'Guaranteed rapid pneumatic and continuous unloader discharge.',
      waitingDays: 1.8,
      queueCount: 4,
    };
  } else if (destPortCode === 'CHN-FAN') {
    return {
      portCode: 'CHN-FAN',
      portName: 'Fangcheng / Guangzhou (CHN)',
      maxDraft: 16.2,
      severity: 'moderate',
      statusTag: 'SOUTH CHINA CONGESTION',
      description: 'Permissible draft 16.2m. High berth occupancy during southern steel mill replenishment cycles.',
      tacticalMitigation: 'Ensure WIBON (Whether In Berth Or Not) clause is active to protect against 3.5-day demurrage.',
      waitingDays: 3.1,
      queueCount: 8,
    };
  } else if (destPortCode === 'KOR-PUS') {
    return {
      portCode: 'KOR-PUS',
      portName: 'Busan (KOR)',
      maxDraft: 18.0,
      severity: 'optimal',
      statusTag: 'NORTHEAST ASIA HUB',
      description: 'Draft 18.0m available at modern industrial outer bulk piers.',
      tacticalMitigation: 'Automated turn-around operations guaranteed within 36 hours.',
      waitingDays: 1.6,
      queueCount: 3,
    };
  } else {
    return {
      portCode: 'ARE-DXB',
      portName: 'Jebel Ali / Dubai (ARE)',
      maxDraft: 16.0,
      severity: 'optimal',
      statusTag: 'PERSIAN GULF TERMINAL',
      description: 'Permissible draft 16.0m. Sheltered basin with high-speed gantry cranes.',
      tacticalMitigation: 'Direct road and feeder connectivity across Gulf Cooperation Council (GCC).',
      waitingDays: 1.4,
      queueCount: 2,
    };
  }
}

export const SAMPLE_FLEET: FleetVessel[] = [
  {
    imo: 'IMO 9748201',
    name: 'MV Pacific Mariner',
    class: 'Panamax',
    dwt: 76500,
    status: 'Underway',
    origin: 'Visakhapatnam (IND)',
    destination: 'Qingdao (CHN)',
    speedKnots: 11.5,
    headingDeg: 78,
    coordinates: [14.25, 87.80], // Bay of Bengal heading to Malacca
    cargo: 'Iron Ore Pellets',
    cargoVolume: 74000,
    eta: '18 Apr 2026 14:00 UTC',
    ciiRating: 'A',
    draftMeters: 14.1,
    charterer: 'Tata Steel Global Logistics',
    congestionWarning: 'Approaching Malacca Strait transit lane',
  },
  {
    imo: 'IMO 9631184',
    name: 'MV Nordic Horizon',
    class: 'Supramax',
    dwt: 58200,
    status: 'Underway',
    origin: 'Paradip (IND)',
    destination: 'Chittagong (BGD)',
    speedKnots: 12.0,
    headingDeg: 42,
    coordinates: [20.95, 89.20], // North Bay of Bengal
    cargo: 'Thermal Coal',
    cargoVolume: 42000,
    eta: '14 Apr 2026 08:30 UTC',
    ciiRating: 'A',
    draftMeters: 9.3,
    charterer: 'Adani Global PTE',
  },
  {
    imo: 'IMO 9812902',
    name: 'MV Stella Ocean',
    class: 'Capesize',
    dwt: 178000,
    status: 'Underway',
    origin: 'Dhamra (IND)',
    destination: 'Rotterdam (NLD)',
    speedKnots: 11.2,
    headingDeg: 220,
    coordinates: [5.10, 79.80], // South of Sri Lanka / Indian Ocean
    cargo: 'Bauxite & Alumina',
    cargoVolume: 168000,
    eta: '02 May 2026 18:00 UTC',
    ciiRating: 'B',
    draftMeters: 18.1,
    charterer: 'Vedanta Resources / Rio Tinto',
  },
  {
    imo: 'IMO 9520119',
    name: 'MV Ocean Titan',
    class: 'Panamax',
    dwt: 82000,
    status: 'Loading',
    origin: 'Gangavaram (IND)',
    destination: 'Tokyo / Chiba (JPN)',
    speedKnots: 0.0,
    headingDeg: 180,
    coordinates: [17.63, 83.23], // Gangavaram Berth #2
    cargo: 'Granulated Slag & Minerals',
    cargoVolume: 78000,
    eta: 'At Berth (Departure ETD: 15 APR)',
    ciiRating: 'A',
    draftMeters: 14.3,
    charterer: 'Jindal Steel & Power',
  },
  {
    imo: 'IMO 9690184',
    name: 'MV Atlantic Osprey',
    class: 'Capesize',
    dwt: 181000,
    status: 'Underway',
    origin: 'Mormugao (IND)',
    destination: 'Fangcheng / Guangzhou (CHN)',
    speedKnots: 10.8,
    headingDeg: 115,
    coordinates: [7.85, 76.50], // Off Cape Comorin
    cargo: 'Iron Ore Fines',
    cargoVolume: 172000,
    eta: '25 Apr 2026 06:00 UTC',
    ciiRating: 'B',
    draftMeters: 17.9,
    charterer: 'Essar Shipping / Vale',
  },
];

