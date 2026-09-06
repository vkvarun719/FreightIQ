"""
predict.py - Multi-Vessel Freight Rate Predictor & Chartering Optimization CLI (2026 Edition).
Usage:
    python predict.py --days 30
    python predict.py --commodity "Coking Coal" --volume 75000 --origin "Hay Point / Dalrymple, Australia" --dest "Visakhapatnam"
    python predict.py --days 60 --output forecast_2026.csv
"""

import argparse
import json
import csv
import os
import freight_engine
import maritime_data

def run_cli_forecast(days=30, commodity="Thermal Coal", volume=75000, origin="Hay Point / Dalrymple, Australia", dest="Visakhapatnam", contract="Short-Term (3 Months)", output_file=None):
    print("=" * 80)
    print("  FREIGHTIQ 2026: INTELLIGENT FREIGHT FORECASTING & CHARTERING OPTIMIZER")
    print("=" * 80)
    
    forecasts, _, _, _ = freight_engine.get_calibrated_forecasts(horizon_days=days)
    prompt_entry = forecasts[0]
    prompt_bdi = prompt_entry['predicted_price']
    
    print(f"\n[1] Baltic Dry Index (BDI) & Multi-Vessel Baseline (September 2026):")
    print(f"    - Baseline BDI Benchmark: {prompt_bdi:,.2f} pts")
    for v_name, v_spec in maritime_data.VESSEL_SPECS.items():
        v_rate = prompt_bdi * v_spec['base_multiplier']
        v_tce = v_rate * 10.5
        print(f"    - {v_name:<10} ({v_spec['typical_dwt']//1000}k DWT): {v_rate:,.2f} pts | Est. TCE: ${v_tce:,.2f}/day")
    
    # Requirement A: Timing
    timing_res = freight_engine.analyze_optimal_timing(
        forecasts, 
        vessel_type='Panamax' if volume <= 90000 else 'Capesize',
        contract_duration=contract
    )
    print("\n" + "-" * 80)
    print("  [A] OPTIMAL MARKET ENTRY TIMING")
    print("-" * 80)
    print(f"  Timing Action      : {timing_res['timing_action']}")
    print(f"  Target Entry Date  : {timing_res['optimal_window_date']} (Step {timing_res['optimal_day_step']})")
    print(f"  Current Rate       : {timing_res['current_rate']:,.2f} BDI")
    print(f"  Target Rate        : {timing_res['optimal_rate']:,.2f} BDI")
    print(f"  Projected Savings  : {timing_res['potential_savings_delta']:,.2f} BDI ({timing_res['potential_savings_pct']}%)")
    print(f"  Reasoning          : {timing_res['reasoning']}")

    # Requirement B: Vessel & Port Optimization
    vessel_res = freight_engine.optimize_vessel_for_port(
        cargo_mt=volume,
        commodity=commodity,
        origin_port_name=origin,
        dest_port_name=dest,
        prompt_cape_rate=prompt_bdi
    )
    print("\n" + "-" * 80)
    print(f"  [B] VESSEL TYPE & PORT OPTIMIZATION ({dest.upper()} DISCHARGE)")
    print("-" * 80)
    print(f"  Cargo Input        : {volume:,.0f} MT of {commodity} from {origin}")
    print(f"  Discharge Port     : {dest} (Max Draft: {vessel_res['port_draft_limit_m']}m | Max LOA: {vessel_res['port_loa_limit_m']}m)")
    print(f"  Recommended Vessel : {vessel_res['recommended_vessel'].upper()}")
    print(f"  Lowest Freight/MT  : ${vessel_res['recommended_cost_per_mt']:.2f} / MT")
    print(f"  Port Stay Duration : {vessel_res['total_turnaround_days']} days")
    
    print("\n  Vessel Class Evaluation Table:")
    print(f"  {'Class':<12} | {'Draft OK?':<10} | {'Freight/MT':<12} | {'Total Days':<12} | {'Demurrage Risk':<14}")
    print("  " + "-" * 70)
    for cName, cData in vessel_res['all_vessel_evaluations'].items():
        ok_str = "YES" if cData['is_allowed'] else "NO (Draft)"
        rec_mark = " (*)" if cName == vessel_res['recommended_vessel'] else ""
        print(f"  {cName + rec_mark:<14} | {ok_str:<10} | ${cData['freight_cost_per_mt_usd']:>9.2f}  | {cData['total_voyage_days']:>9.1f}d | {cData['demurrage_risk']:<14}")

    # Requirement C: Idle Management
    idle_res = freight_engine.generate_idle_management_strategy(
        dest_port_name=dest,
        arrival_date_str=forecasts[min(14, len(forecasts)-1)]['date'],
        vessel_type=vessel_res['recommended_vessel']
    )
    print("\n" + "-" * 80)
    print("  [C] IDLE SCENARIO MANAGEMENT & DEADHEADING REDUCTION")
    print("-" * 80)
    print(f"  Regional Demand    : {idle_res['regional_demand_outlook']}")
    for s in idle_res['recommended_strategies']:
        print(f"  * Strategy: {s['strategy_name']}")
        print(f"    - Action : {s['description']}")
        print(f"    - Benefit: {s['ballast_reduction_nm']} | TCE Impact: {s['expected_tce_boost']}")

    # Requirement D: Risk Mitigation
    risk_res = freight_engine.evaluate_risk_and_early_warnings(
        dest_port_name=dest,
        origin_port_name=origin,
        forecast_list=forecasts
    )
    print("\n" + "-" * 80)
    print("  [D] RISK MITIGATION & EARLY WARNING SYSTEM")
    print("-" * 80)
    print(f"  Market Volatility  : [{risk_res['market_volatility']['level']}] {risk_res['market_volatility']['early_warning']}")
    for w in risk_res['weather_and_seasonal_risks']:
        print(f"  Weather Alert      : [{w['severity']}] {w['details']}")
    print(f"  Port Congestion    : [{risk_res['port_congestion_risk']['level']}] {risk_res['port_congestion_risk']['details']}")
    print("-" * 80)

    # Export if requested
    if output_file:
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Step', 'Date', 'Predicted_BDI', 'Lower_95', 'Upper_95', 'DNN_Pred', 'GBDT_Pred', 'Ridge_Pred'])
            for fc in forecasts:
                writer.writerow([fc['step'], fc['date'], fc['predicted_price'], fc['lower_95'], fc['upper_95'], fc['dnn_pred'], fc['gbdt_pred'], fc['ridge_pred']])
        print(f"\nSaved Baltic Dry Index forecast schedule to '{output_file}'.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="FreightIQ 2026 CLI Optimizer")
    parser.add_argument('--days', type=int, default=30, help="Forecast horizon days")
    parser.add_argument('--commodity', type=str, default="Thermal Coal")
    parser.add_argument('--volume', type=float, default=75000)
    parser.add_argument('--origin', type=str, default="Hay Point / Dalrymple, Australia")
    parser.add_argument('--dest', type=str, default="Visakhapatnam")
    parser.add_argument('--contract', type=str, default="Short-Term (3 Months)")
    parser.add_argument('--output', type=str, default=None)
    args = parser.parse_args()
    
    run_cli_forecast(
        days=args.days,
        commodity=args.commodity,
        volume=args.volume,
        origin=args.origin,
        dest=args.dest,
        contract=args.contract,
        output_file=args.output
    )
