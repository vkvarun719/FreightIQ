export type Commodity = 'Coal' | 'Iron Ore' | 'Grain' | 'Bauxite';

export interface PortOption {
  code: string;
  name: string;
  country: string;
  region: string;
  maxDraft: number; // in meters
  typicalCongestionDays: number;
  type: 'export' | 'discharge' | 'bunker';
}

export interface VoyageParameters {
  commodity: Commodity;
  cargoVolume: number; // 30,000 to 180,000 MT
  originPort: string;
  destinationPort: string;
  laycanStart: string;
  laycanEnd: string;
}

export interface VesselRecommendation {
  className: string;
  vesselName: string;
  dwt: number;
  ciiRating: 'A' | 'B' | 'C' | 'D';
  ecoSpeedKnots: number;
  ecoConsumptionTonsDay: number;
  standardSpeedKnots: number;
  fuelSavedUsd: number;
  fuelSavedTons: number;
  ballastWaterCompliance: string;
}

export interface PortRestrictionAlert {
  portCode: string;
  portName: string;
  maxDraft: number;
  severity: 'critical' | 'optimal' | 'moderate';
  statusTag: string;
  description: string;
  tacticalMitigation: string;
  waitingDays: number;
  queueCount: number;
}

export interface LegalRiskGuard {
  standardForm: string;
  projectedBerthWaitingDays: number;
  queueVessels: number;
  demurrageExposureDaily: number;
  clausesProtected: string[];
  wibonProtection: boolean;
  wiponProtection: boolean;
  charterRiskScore: number;
}

export interface FleetVessel {
  imo: string;
  name: string;
  class: 'Capesize' | 'Panamax' | 'Supramax' | 'Handymax';
  dwt: number;
  status: 'Underway' | 'Anchored' | 'Discharging' | 'Loading' | 'Bunkering';
  origin: string;
  destination: string;
  speedKnots: number;
  headingDeg: number;
  coordinates: [number, number]; // [lat, lng]
  cargo: string;
  cargoVolume: number;
  eta: string;
  ciiRating: 'A' | 'B' | 'C';
  draftMeters: number;
  charterer: string;
  congestionWarning?: string;
}

export interface CharterFixture {
  fixtureId: string;
  charterer: string;
  shipowner: string;
  vesselName: string;
  vesselClass: string;
  cargo: string;
  cargoQuantity: string;
  laycanWindow: string;
  loadingPort: string;
  dischargingPort: string;
  freightRate: string;
  demurrageRate: string;
  despatchRate: string;
  governingLaw: string;
  specialClauses: {
    wibon: boolean;
    wipon: boolean;
    wifpon: boolean;
    bunkersPriceIndexation: boolean;
    sanctionsClause: boolean;
    ciiClause: boolean;
  };
}

export interface BusinessInfo {
  companyName: string;
  tradingName: string;
  tagline: string;
  imoCompanyNumber: string;
  headquarters: {
    addressLine1: string;
    city: string;
    state: string;
    country: string;
    postalCode: string;
  };
  contactChannels: {
    commercialCharteringEmail: string;
    operationsDemurrageEmail: string;
    generalInquiriesEmail: string;
    primaryPhone: string;
    emergency247OpsPhone: string;
    satelliteVhfCallsign: string;
  };
  operatingHours: string;
  globalDesks: Array<{
    hub: string;
    location: string;
    dutyOfficer: string;
    timezone: string;
    activeStatus: string;
  }>;
}

export interface ContactFormData {
  fullName: string;
  corporateEmail: string;
  companyName: string;
  phoneNumber: string;
  inquiryType: string;
  cargoParcelClass: string;
  urgency: string;
  message: string;
}

export interface ContactValidationErrors {
  fullName?: string;
  corporateEmail?: string;
  companyName?: string;
  phoneNumber?: string;
  inquiryType?: string;
  cargoParcelClass?: string;
  urgency?: string;
  message?: string;
}

export interface BDIPoint {
  date: string;
  price: number;
  open?: number;
  high?: number;
  low?: number;
  change_pct?: number;
  sma_5?: number;
  sma_20?: number;
}

export interface BDIForecastItem {
  step: number;
  date: string;
  predicted_price: number;
  lower_95: number;
  upper_95: number;
  ridge_pred?: number;
  gbdt_pred?: number;
  dnn_pred?: number;
  volatility_std?: number;
}

export interface BDIForecastResponse {
  latest_date: string;
  latest_price: number;
  horizon_days: number;
  market_bias: string;
  forecasts: BDIForecastItem[];
}

export interface OptimizationResult {
  timestamp: string;
  optimal_timing: {
    recommended_action: string;
    optimal_date: string;
    prompt_rate: number;
    target_rate: number;
    cost_delta_pct: number;
    reasoning: string;
    horizon_summary?: string;
  };
  vessel_optimization: {
    cargo_volume_mt: number;
    recommended_vessel: string;
    optimal_freight_per_mt: number;
    total_voyage_days: number;
    port_stay_days: number;
    sea_transit_days: number;
    evaluations: Array<{
      vessel_type: string;
      draft_compatible: boolean;
      freight_per_mt: number;
      total_voyage_cost_usd: number;
      transit_days: number;
      demurrage_exposure_risk: string;
      fuel_consumed_tons: number;
    }>;
  };
  idle_management: {
    arrival_port: string;
    arrival_date: string;
    strategies: Array<{
      title: string;
      action: string;
      ballast_reduction_nm: string;
      tce_impact: string;
      feasibility: string;
    }>;
  };
  risk_evaluation: {
    market_volatility: {
      level: string;
      early_warning: string;
      hedging_recommendation: string;
    };
    weather_and_seasonal_risks: Array<{
      type: string;
      severity: string;
      details: string;
    }>;
    port_congestion_risk: {
      waiting_days_est: string;
      details: string;
      protective_clauses: string[];
    };
  };
}

