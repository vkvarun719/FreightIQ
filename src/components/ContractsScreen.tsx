import React, { useState } from 'react';
import { 
  FileText, 
  ShieldCheck, 
  Calculator, 
  Scale, 
  Check, 
  Copy, 
  Download, 
  AlertTriangle, 
  Sparkles,
  HelpCircle
} from 'lucide-react';

export const ContractsScreen: React.FC = () => {
  const [standardForm, setStandardForm] = useState<string>('GENCON 94');
  const [wibonActive, setWibonActive] = useState<boolean>(true);
  const [wiponActive, setWiponActive] = useState<boolean>(true);
  const [wifponActive, setWifponActive] = useState<boolean>(true);
  const [ciiClauseActive, setCiiClauseActive] = useState<boolean>(true);
  const [bunkerEscalationActive, setBunkerEscalationActive] = useState<boolean>(true);

  // Demurrage Calculator State
  const [dailyDemurrage, setDailyDemurrage] = useState<number>(24000);
  const [waitingDays, setWaitingDays] = useState<number>(4.2);
  const [laytimeAllowedDays, setLaytimeAllowedDays] = useState<number>(3);
  const [shincMode, setShincMode] = useState<boolean>(true); // SHINC vs SHEX
  const [copiedNotification, setCopiedNotification] = useState<boolean>(false);

  // Calculations
  const excessDays = Math.max(0, waitingDays - laytimeAllowedDays);
  const calculatedDemurrageLiability = Math.round(excessDays * dailyDemurrage);
  const savedByWibon = Math.round(waitingDays * (wibonActive ? dailyDemurrage : 0));

  const copyFixtureToClipboard = () => {
    const fixtureText = `========================================================
FREIGHTIQ 2026 CHARTER PARTY CLAUSE ADDENDUM
Standard Proforma: ${standardForm}
Generated: ${new Date().toISOString()}
========================================================
1. NOTICE OF READINESS & LAYTIME COMMENCEMENT:
   Laytime for loading and discharging shall commence 12 hours 
   after Notice of Readiness (NOR) is tendered by Master or Agents.
   ${wibonActive ? '- STIPULATION: WIBON (Whether In Berth Or Not) STRICTLY APPLIES.' : ''}
   ${wiponActive ? '- STIPULATION: WIPON (Whether In Port Or Not) STRICTLY APPLIES.' : ''}
   ${wifponActive ? '- STIPULATION: WIFPON (Whether In Free Pratique Or Not) APPLIES.' : ''}

2. DEMURRAGE & DESPATCH:
   Demurrage at load and discharge ports shall be payable at 
   USD $${dailyDemurrage.toLocaleString()} per running day or pro-rata.
   Terms: ${shincMode ? 'SHINC (Sundays and Holidays Included)' : 'SHEX (Sundays and Holidays Excluded)'}.
   Despatch on all working time saved at 50% of Demurrage rate.

3. ENVIRONMENTAL EFFICIENCY & CII COOPERATION:
   ${ciiClauseActive ? 'BIMCO CII Operations Clause for Time/Voyage Charter Parties 2022 incorporated.' : 'Standard speed warranties apply.'}

4. JURISDICTION & GOVERNING LAW:
   This Contract shall be governed by and construed in accordance 
   with English Law and Singapore Maritime Arbitration Centre (SCMA).
========================================================`;
    navigator.clipboard.writeText(fixtureText);
    setCopiedNotification(true);
    setTimeout(() => setCopiedNotification(false), 2000);
  };

  return (
    <div className="flex flex-col w-full max-w-3xl mx-auto px-4 sm:px-6 py-4 pb-28 gap-4">
      {/* Header */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Scale className="w-5 h-5 text-secondary" />
            <h1 className="text-xl sm:text-2xl font-bold text-on-surface">
              Contracts &amp; Legal Guard
            </h1>
          </div>
          <span className="text-[11px] font-mono bg-primary/15 text-primary border border-primary/30 px-2 py-0.5 rounded font-bold">
            BIMCO COMPLIANT
          </span>
        </div>
        <p className="text-xs text-on-surface-variant">
          Automated fixture clause injection, demurrage exposure hedging, and charter party risk mitigation
        </p>
      </div>

      {/* Proforma Selection */}
      <div className="bg-surface-container rounded-xl border border-surface-container-high p-4 flex flex-col gap-3 shadow-md">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-on-surface">
            Charter Party Base Form
          </span>
          <span className="text-[10px] font-mono text-on-surface-variant">
            EDITION 2026
          </span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {['GENCON 94', 'NYPE 93', 'AMWELSH', 'BALTIME'].map((form) => (
            <button
              key={form}
              onClick={() => setStandardForm(form)}
              className={`py-2 px-3 rounded-lg text-xs font-mono font-semibold transition-all border ${
                standardForm === form
                  ? 'bg-primary text-on-primary border-primary shadow-sm'
                  : 'bg-surface-container-low border-surface-container-high text-on-surface-variant hover:text-on-surface'
              }`}
            >
              {form}
            </button>
          ))}
        </div>
      </div>

      {/* Legal Clause Protections Toggles */}
      <div className="bg-surface-container rounded-xl border border-surface-container-high p-4 flex flex-col gap-3 shadow-md">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-tertiary" />
            <h2 className="text-sm sm:text-base font-semibold text-on-surface">
              Protective Clause Injection Engine
            </h2>
          </div>
          <span className="text-[10px] font-mono text-tertiary font-bold bg-tertiary/10 px-2 py-0.5 rounded border border-tertiary/20">
            AUTO-GUARD ON
          </span>
        </div>

        <div className="flex flex-col gap-2.5">
          {/* WIBON */}
          <div className="flex items-center justify-between bg-surface-container-low p-3 rounded-xl border border-surface-container-high/50">
            <div className="flex flex-col pr-2">
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-xs font-bold text-primary">WIBON</span>
                <span className="text-xs font-medium text-on-surface">Whether In Berth Or Not</span>
              </div>
              <span className="text-[11px] text-on-surface-variant mt-0.5">
                Allows Notice of Readiness (NOR) tender even if berth is occupied, triggering laytime at anchorage.
              </span>
            </div>
            <button
              onClick={() => setWibonActive(!wibonActive)}
              className={`w-12 h-6 rounded-full transition-colors relative shrink-0 ${
                wibonActive ? 'bg-primary' : 'bg-surface-container-highest'
              }`}
            >
              <span className={`w-4 h-4 rounded-full bg-white transition-transform block absolute top-1 ${
                wibonActive ? 'left-7' : 'left-1'
              }`} />
            </button>
          </div>

          {/* WIPON */}
          <div className="flex items-center justify-between bg-surface-container-low p-3 rounded-xl border border-surface-container-high/50">
            <div className="flex flex-col pr-2">
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-xs font-bold text-primary">WIPON</span>
                <span className="text-xs font-medium text-on-surface">Whether In Port Or Not</span>
              </div>
              <span className="text-[11px] text-on-surface-variant mt-0.5">
                Validates NOR when congested roadstead or outer anchorage lies technically beyond port limits.
              </span>
            </div>
            <button
              onClick={() => setWiponActive(!wiponActive)}
              className={`w-12 h-6 rounded-full transition-colors relative shrink-0 ${
                wiponActive ? 'bg-primary' : 'bg-surface-container-highest'
              }`}
            >
              <span className={`w-4 h-4 rounded-full bg-white transition-transform block absolute top-1 ${
                wiponActive ? 'left-7' : 'left-1'
              }`} />
            </button>
          </div>

          {/* WIFPON */}
          <div className="flex items-center justify-between bg-surface-container-low p-3 rounded-xl border border-surface-container-high/50">
            <div className="flex flex-col pr-2">
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-xs font-bold text-secondary">WIFPON</span>
                <span className="text-xs font-medium text-on-surface">Whether In Free Pratique Or Not</span>
              </div>
              <span className="text-[11px] text-on-surface-variant mt-0.5">
                Shields laytime clock from port health quarantine delays when medical clearance is pending.
              </span>
            </div>
            <button
              onClick={() => setWifponActive(!wifponActive)}
              className={`w-12 h-6 rounded-full transition-colors relative shrink-0 ${
                wifponActive ? 'bg-primary' : 'bg-surface-container-highest'
              }`}
            >
              <span className={`w-4 h-4 rounded-full bg-white transition-transform block absolute top-1 ${
                wifponActive ? 'left-7' : 'left-1'
              }`} />
            </button>
          </div>

          {/* BIMCO CII */}
          <div className="flex items-center justify-between bg-surface-container-low p-3 rounded-xl border border-surface-container-high/50">
            <div className="flex flex-col pr-2">
              <div className="flex items-center gap-1.5">
                <span className="font-mono text-xs font-bold text-tertiary">BIMCO CII 2022</span>
                <span className="text-xs font-medium text-on-surface">Carbon Intensity Factor</span>
              </div>
              <span className="text-[11px] text-on-surface-variant mt-0.5">
                Mandates charterer speed adjustments to avoid vessel carbon rating degradation under IMO MARPOL Annex VI.
              </span>
            </div>
            <button
              onClick={() => setCiiClauseActive(!ciiClauseActive)}
              className={`w-12 h-6 rounded-full transition-colors relative shrink-0 ${
                ciiClauseActive ? 'bg-tertiary' : 'bg-surface-container-highest'
              }`}
            >
              <span className={`w-4 h-4 rounded-full bg-white transition-transform block absolute top-1 ${
                ciiClauseActive ? 'left-7' : 'left-1'
              }`} />
            </button>
          </div>
        </div>
      </div>

      {/* Demurrage Exposure Financial Simulator */}
      <div className="bg-surface-container rounded-xl border border-surface-container-high p-4 flex flex-col gap-3 shadow-md">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Calculator className="w-4 h-4 text-primary" />
            <h2 className="text-sm sm:text-base font-semibold text-on-surface">
              Demurrage &amp; Despatch Calculator
            </h2>
          </div>
          <span className="text-xs font-mono font-bold text-error">
            ${calculatedDemurrageLiability.toLocaleString()} LIABILITY
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-surface-container-low p-3.5 rounded-xl border border-surface-container-high/50 text-xs">
          {/* Daily Demurrage Slider */}
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <span className="text-on-surface-variant">Agreed Demurrage Rate</span>
              <span className="font-mono font-bold text-primary">
                ${dailyDemurrage.toLocaleString()} / day
              </span>
            </div>
            <input
              type="range"
              min="10000"
              max="45000"
              step="1000"
              value={dailyDemurrage}
              onChange={(e) => setDailyDemurrage(parseInt(e.target.value, 10))}
              className="w-full h-1.5 bg-surface-container-highest rounded appearance-none cursor-pointer accent-primary"
            />
          </div>

          {/* Waiting Days Slider */}
          <div className="flex flex-col gap-1.5">
            <div className="flex items-center justify-between">
              <span className="text-on-surface-variant">Projected Berth Congestion</span>
              <span className="font-mono font-bold text-error">
                {waitingDays} Days
              </span>
            </div>
            <input
              type="range"
              min="0.5"
              max="14.0"
              step="0.1"
              value={waitingDays}
              onChange={(e) => setWaitingDays(parseFloat(e.target.value))}
              className="w-full h-1.5 bg-surface-container-highest rounded appearance-none cursor-pointer accent-error"
            />
          </div>
        </div>

        {/* Laytime Configuration */}
        <div className="flex items-center justify-between text-xs bg-surface-container-low p-3 rounded-xl border border-surface-container-high/50">
          <div className="flex items-center gap-2">
            <span className="text-on-surface-variant">Laytime Basis:</span>
            <button
              onClick={() => setShincMode(!shincMode)}
              className="px-2 py-1 rounded bg-surface-container-high font-mono text-[11px] font-bold text-primary border border-surface-container-highest"
            >
              {shincMode ? 'SHINC (Sundays/Holidays Included)' : 'SHEX (Excluded)'}
            </button>
          </div>

          <div className="text-right">
            <span className="text-on-surface-variant block text-[10px]">WIBON VALUE CAPTURED</span>
            <span className="font-mono font-bold text-tertiary">
              +${savedByWibon.toLocaleString()} USD
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-2 pt-1">
          <button
            onClick={copyFixtureToClipboard}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-surface-container-high border border-surface-container-highest text-xs font-semibold text-on-surface hover:text-primary transition-all"
          >
            {copiedNotification ? (
              <>
                <Check className="w-3.5 h-3.5 text-tertiary" />
                <span>Copied to Clipboard!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy Clauses</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
