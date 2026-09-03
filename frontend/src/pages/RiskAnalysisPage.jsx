import React from 'react';
import { Target, ShieldAlert } from 'lucide-react';

export default function RiskAnalysisPage() {
  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
        <div className="flex items-center space-x-2 text-rose-400 font-bold text-base">
          <Target className="w-5 h-5" />
          <h2>Transparent Risk Scoring Matrix (0 - 100)</h2>
        </div>
        <p className="text-xs text-slate-400">
          Composite risk scoring combines weighted components to avoid black-box decision making.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs font-mono">
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-1">
            <div className="text-cyan-400 font-bold">1. Lot Anomaly Score (30%)</div>
            <div className="text-slate-400 text-[11px]">Isolation Forest distance relative to lot baseline</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-1">
            <div className="text-amber-400 font-bold">2. Temporal Drift Rate (25%)</div>
            <div className="text-slate-400 text-[11px]">0h &rarr; 24h &rarr; 96h rate of change & acceleration</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-1">
            <div className="text-rose-400 font-bold">3. Safety Overflow Margin (25%)</div>
            <div className="text-slate-400 text-[11px]">Predicted 168h overflow percentage beyond safety limit</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-1">
            <div className="text-indigo-400 font-bold">4. Lot Z-Score Severity (20%)</div>
            <div className="text-slate-400 text-[11px]">Standard deviations from manufacturing lot mean</div>
          </div>
        </div>
      </div>
    </div>
  );
}
