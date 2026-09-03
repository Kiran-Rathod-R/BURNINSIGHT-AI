import React, { useState, useEffect } from 'react';
import { Building2, Layers, ShieldCheck, AlertTriangle, XCircle } from 'lucide-react';
import { fetchLots, fetchLotDetail } from '../services/api';

export default function LotAnalysisPage() {
  const [lots, setLots] = useState([]);
  const [selectedLotId, setSelectedLotId] = useState('');
  const [lotDetail, setLotDetail] = useState(null);

  useEffect(() => {
    fetchLots().then((res) => {
      if (res.lots && res.lots.length > 0) {
        setLots(res.lots);
        setSelectedLotId(res.lots[0].lot_id);
      }
    });
  }, []);

  useEffect(() => {
    if (selectedLotId) {
      fetchLotDetail(selectedLotId).then((res) => setLotDetail(res));
    }
  }, [selectedLotId]);

  if (!lotDetail) {
    return <div className="p-8 text-center text-slate-400">Loading lot statistics...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header Dropdown */}
      <div className="flex justify-between items-center p-4 rounded-2xl glass-panel border border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Batch Lot-Level Statistical Analysis</h2>
            <p className="text-xs text-slate-400">Relative statistical deviation checks within manufacturing batches</p>
          </div>
        </div>

        <select
          value={selectedLotId}
          onChange={(e) => setSelectedLotId(e.target.value)}
          className="bg-slate-900 border border-slate-700 text-cyan-400 font-mono text-xs rounded-lg px-4 py-2"
        >
          {lots.map((l) => (
            <option key={l.lot_id} value={l.lot_id}>
              {l.lot_id} ({l.total_components} comps - Health {l.lot_health_score}%)
            </option>
          ))}
        </select>
      </div>

      {/* Lot Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl glass-panel border border-cyan-500/30 bg-cyan-500/5">
          <div className="text-xs font-semibold text-slate-400">Lot Health Index</div>
          <div className="text-3xl font-extrabold text-cyan-400 mt-1 font-mono">
            {lotDetail.lot_health_score}%
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Overall batch reliability</div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-slate-800">
          <div className="text-xs font-semibold text-slate-400">Total Components</div>
          <div className="text-2xl font-extrabold text-white mt-1 font-mono">{lotDetail.total_components}</div>
          <div className="text-[10px] text-slate-500 mt-1">Batch count</div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-slate-800">
          <div className="text-xs font-semibold text-slate-400">Baseline Mean (&mu;)</div>
          <div className="text-2xl font-extrabold text-slate-200 mt-1 font-mono">{lotDetail.mean_leakage_0h} &micro;A</div>
          <div className="text-[10px] text-slate-500 mt-1">Standard deviation (&sigma;): {lotDetail.std_leakage_0h} &micro;A</div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-slate-800 flex items-center justify-around text-center text-xs font-mono">
          <div>
            <span className="text-emerald-400 font-bold text-lg">{lotDetail.healthy_count}</span>
            <span className="block text-[10px] text-slate-400">Pass</span>
          </div>
          <div>
            <span className="text-amber-400 font-bold text-lg">{lotDetail.watch_count}</span>
            <span className="block text-[10px] text-slate-400">Watch</span>
          </div>
          <div>
            <span className="text-rose-400 font-bold text-lg">{lotDetail.early_reject_count}</span>
            <span className="block text-[10px] text-slate-400">Reject</span>
          </div>
        </div>
      </div>

      {/* Top Suspicious Components Table */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800">
        <h3 className="text-sm font-semibold text-white mb-4">Lot Outlier Component Summary ({selectedLotId})</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-2">Component ID</th>
                <th className="pb-2">Status</th>
                <th className="pb-2">Risk Score</th>
                <th className="pb-2">Anomaly Score</th>
                <th className="pb-2">Lot Z-Score</th>
                <th className="pb-2">Pred 168h</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {lotDetail.top_suspicious_components?.map((c) => (
                <tr key={c.component_id} className="hover:bg-slate-800/50">
                  <td className="py-2.5 font-bold text-cyan-400">{c.component_id}</td>
                  <td className="py-2.5">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      c.decision === 'EARLY REJECT' ? 'bg-rose-500/20 text-rose-400' : 'bg-amber-500/20 text-amber-400'
                    }`}>
                      {c.decision}
                    </span>
                  </td>
                  <td className="py-2.5 text-rose-400 font-bold">{c.risk_score}</td>
                  <td className="py-2.5 text-amber-400">{c.anomaly_score}</td>
                  <td className="py-2.5 text-cyan-400">+{c.lot_z_score_0h?.toFixed(2)}&sigma;</td>
                  <td className="py-2.5 text-slate-200">{c.predicted_168h?.toFixed(1)} &micro;A</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
