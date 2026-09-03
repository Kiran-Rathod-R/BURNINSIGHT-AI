import React, { useState, useEffect } from 'react';
import { AlertTriangle, ShieldCheck } from 'lucide-react';
import { fetchAnomalies } from '../services/api';

export default function AnomalyDetectionPage() {
  const [anomalyData, setAnomalyData] = useState(null);

  useEffect(() => {
    fetchAnomalies().then((res) => setAnomalyData(res));
  }, []);

  if (!anomalyData) {
    return <div className="p-8 text-center text-slate-400">Loading Isolation Forest anomaly analysis...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl glass-panel border border-slate-800">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              Isolation Forest Lot-Aware Anomaly Engine
            </h2>
            <p className="text-xs text-slate-400">Detects subtle outliers relative to manufacturing lot baseline</p>
          </div>
          <div className="text-right font-mono text-xs text-slate-300">
            <div>Anomalous Flagged: <span className="text-rose-400 font-bold">{anomalyData.anomalous_count}</span> / {anomalyData.total_components}</div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-2">Component ID</th>
                <th className="pb-2">Lot ID</th>
                <th className="pb-2">Type</th>
                <th className="pb-2">Anomaly Score (0-100)</th>
                <th className="pb-2">Status</th>
                <th className="pb-2">Rank in Lot</th>
                <th className="pb-2">Lot Z-Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {anomalyData.components?.map((c) => (
                <tr key={c.component_id} className="hover:bg-slate-800/50">
                  <td className="py-2.5 font-bold text-cyan-400">{c.component_id}</td>
                  <td className="py-2.5 text-slate-300">{c.lot_id}</td>
                  <td className="py-2.5 text-slate-400">{c.component_type}</td>
                  <td className="py-2.5 font-bold text-rose-400">{c.anomaly_score}</td>
                  <td className="py-2.5">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400">
                      {c.anomaly_status}
                    </span>
                  </td>
                  <td className="py-2.5 text-cyan-400">#{c.rank_in_lot}</td>
                  <td className="py-2.5 text-slate-200">+{c.lot_z_score_0h?.toFixed(1)}&sigma;</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
