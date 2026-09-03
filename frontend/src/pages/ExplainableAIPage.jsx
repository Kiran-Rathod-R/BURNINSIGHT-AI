import React from 'react';
import { Brain, Sparkles, CheckCircle2 } from 'lucide-react';

export default function ExplainableAIPage() {
  const globalFeatures = [
    { feature: 'Lot Z-Score (0h)', weight: '34.2%', description: 'Deviations from manufacturing lot mean' },
    { feature: '0h-96h Leakage Drift', weight: '26.8%', description: 'Temporal degradation velocity' },
    { feature: 'Isolation Forest Score', weight: '21.5%', description: 'Lot-aware anomaly score' },
    { feature: 'Degradation Acceleration', weight: '11.4%', description: 'Change in rate of change' },
    { feature: 'Baseline Leakage (0h)', weight: '6.1%', description: 'Absolute baseline current' },
  ];

  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
        <div className="flex items-center space-x-2 text-cyan-400 font-bold text-base">
          <Brain className="w-5 h-5" />
          <h2>Explainable AI (SHAP) & Model Transparency</h2>
        </div>
        <p className="text-xs text-slate-400">
          Global SHAP feature importance ranking showing how the AI model attributes prediction risk across features.
        </p>

        <div className="space-y-3">
          {globalFeatures.map((f, idx) => (
            <div key={idx} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 flex justify-between items-center text-xs">
              <div>
                <span className="font-bold text-white font-mono">{f.feature}</span>
                <span className="text-slate-400 block text-[11px] mt-0.5">{f.description}</span>
              </div>
              <span className="font-mono font-bold text-cyan-400 text-sm">{f.weight}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
