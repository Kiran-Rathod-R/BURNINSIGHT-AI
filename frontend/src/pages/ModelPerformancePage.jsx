import React, { useState, useEffect } from 'react';
import { Cpu, CheckCircle } from 'lucide-react';
import { fetchModelPerformance } from '../services/api';

export default function ModelPerformancePage() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchModelPerformance().then((res) => setData(res));
  }, []);

  if (!data) return <div className="p-8 text-center text-slate-400">Loading model performance details...</div>;

  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <Cpu className="w-5 h-5 text-cyan-400" />
          Model Architecture & Validation Performance
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
            <div className="text-slate-400 text-[10px]">Anomaly Detector</div>
            <div className="text-sm font-bold text-cyan-400 mt-1">{data.anomaly_algorithm}</div>
            <div className="text-[10px] text-slate-500 mt-1">Contamination Rate: {(data.anomaly_contamination * 100).toFixed(0)}%</div>
          </div>
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
            <div className="text-slate-400 text-[10px]">Selected Champion 168h Regressor</div>
            <div className="text-sm font-bold text-emerald-400 mt-1">{data.best_prediction_model}</div>
            <div className="text-[10px] text-slate-500 mt-1">80/20 Train-Test Validation Split</div>
          </div>
        </div>
      </div>
    </div>
  );
}
