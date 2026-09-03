import React, { useState, useEffect } from 'react';
import { TrendingUp, Cpu, Award } from 'lucide-react';
import { fetchModelPerformance } from '../services/api';

export default function PredictionPage() {
  const [modelPerf, setModelPerf] = useState(null);

  useEffect(() => {
    fetchModelPerformance().then((res) => setModelPerf(res));
  }, []);

  if (!modelPerf) {
    return <div className="p-8 text-center text-slate-400">Loading model performance metrics...</div>;
  }

  const evaluated = modelPerf.models_evaluated || {};

  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl glass-panel border border-slate-800">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-cyan-400" />
              168-Hour Measurement Prediction Models
            </h2>
            <p className="text-xs text-slate-400">Evaluated on validation dataset using earlier test points (&le;96h)</p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold font-mono">
            <Award className="w-4 h-4" /> Champion Model: {modelPerf.best_prediction_model}
          </div>
        </div>

        {/* Model Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Object.entries(evaluated).map(([name, m]) => {
            const isChampion = name === modelPerf.best_prediction_model;
            return (
              <div
                key={name}
                className={`p-5 rounded-xl glass-panel border transition-all ${
                  isChampion ? 'border-cyan-500/50 bg-cyan-500/10 shadow-lg shadow-cyan-500/10' : 'border-slate-800'
                }`}
              >
                <div className="flex justify-between items-center mb-3">
                  <h3 className="font-bold text-sm text-white flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-cyan-400" /> {name}
                  </h3>
                  {isChampion && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/40">
                      WINNER
                    </span>
                  )}
                </div>

                <div className="space-y-2 font-mono text-xs">
                  <div className="flex justify-between border-b border-slate-800 pb-1">
                    <span className="text-slate-400">Mean Absolute Error (MAE):</span>
                    <span className="font-bold text-cyan-400">{m.mae} &micro;A</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800 pb-1">
                    <span className="text-slate-400">Root Mean Squared (RMSE):</span>
                    <span className="font-bold text-slate-200">{m.rmse}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">R&sup2; Variance Explained:</span>
                    <span className="font-bold text-emerald-400">{(m.r2 * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
