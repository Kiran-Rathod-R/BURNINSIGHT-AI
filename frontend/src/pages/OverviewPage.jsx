import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, ShieldAlert, Layers, Database } from 'lucide-react';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';

const COLORS = {
  PASS: '#10B981',        // Emerald
  WATCH: '#F59E0B',       // Amber
  'EARLY REJECT': '#EF4444' // Rose
};

export default function OverviewPage({ summaryData, onSelectComponent }) {
  if (!summaryData || summaryData.status === 'NO_DATA_LOADED') {
    return (
      <div className="p-12 text-center glass-panel rounded-2xl border border-slate-800 space-y-4">
        <Database className="w-12 h-12 text-cyan-500 mx-auto animate-bounce" />
        <h2 className="text-xl font-bold text-white">No Burn-In Dataset Loaded</h2>
        <p className="text-sm text-slate-400 max-w-md mx-auto">
          Please upload a component CSV file or click <strong className="text-cyan-400">1-Click SIH Demo Mode</strong> in the header bar to generate and analyze synthetic burn-in screening data.
        </p>
      </div>
    );
  }

  const pieData = Object.entries(summaryData.decision_distribution || {}).map(([key, val]) => ({
    name: key,
    value: val
  }));

  return (
    <div className="space-y-6">
      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="p-4 rounded-xl glass-panel border border-slate-800">
          <div className="text-xs font-medium text-slate-400">Total Components</div>
          <div className="text-2xl font-extrabold text-white mt-1 font-mono">
            {summaryData.total_components.toLocaleString()}
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Screened across 4 test points</div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-emerald-500/20 bg-emerald-500/5">
          <div className="text-xs font-medium text-emerald-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4" /> PASS
          </div>
          <div className="text-2xl font-extrabold text-white mt-1 font-mono">
            {summaryData.pass_count.toLocaleString()}
          </div>
          <div className="text-[10px] text-emerald-500/80 mt-1">Normal electrical drift</div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-amber-500/20 bg-amber-500/5">
          <div className="text-xs font-medium text-amber-400 flex items-center gap-1.5">
            <AlertTriangle className="w-4 h-4" /> WATCH
          </div>
          <div className="text-2xl font-extrabold text-white mt-1 font-mono">
            {summaryData.watch_count.toLocaleString()}
          </div>
          <div className="text-[10px] text-amber-500/80 mt-1">Moderate deviation</div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-rose-500/20 bg-rose-500/5">
          <div className="text-xs font-medium text-rose-400 flex items-center gap-1.5">
            <XCircle className="w-4 h-4" /> EARLY REJECT
          </div>
          <div className="text-2xl font-extrabold text-white mt-1 font-mono">
            {summaryData.early_reject_count.toLocaleString()}
          </div>
          <div className="text-[10px] text-rose-500/80 mt-1">High lot / drift anomaly</div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-slate-800">
          <div className="text-xs font-medium text-slate-400 flex items-center gap-1.5">
            <ShieldAlert className="w-4 h-4 text-rose-400" /> High Risk (&ge;70)
          </div>
          <div className="text-2xl font-extrabold text-rose-400 mt-1 font-mono">
            {summaryData.high_risk_count.toLocaleString()}
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Action required</div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-slate-800">
          <div className="text-xs font-medium text-slate-400 flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-cyan-400" /> Lots Analyzed
          </div>
          <div className="text-2xl font-extrabold text-cyan-400 mt-1 font-mono">
            {summaryData.total_lots}
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Batch screening lots</div>
        </div>
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Donut Chart: Decision Distribution */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">AI Screening Decisions</h3>
            <p className="text-xs text-slate-400">Distribution across PASS / WATCH / EARLY REJECT</p>
          </div>
          <div className="h-56 my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#6366F1'} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center space-x-4 text-xs font-medium">
            {pieData.map((d) => (
              <div key={d.name} className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[d.name] }}></span>
                <span className="text-slate-300">{d.name}: {d.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Anomalies Table */}
        <div className="lg:col-span-2 p-5 rounded-2xl glass-panel border border-slate-800">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Top Anomalous Components Flagged</h3>
              <p className="text-xs text-slate-400">Components with high lot Z-score or predicted drift violation</p>
            </div>
            <span className="text-xs text-cyan-400 font-mono">Lot-Relative Outliers</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-mono">
                  <th className="pb-2">Component ID</th>
                  <th className="pb-2">Lot ID</th>
                  <th className="pb-2">Type</th>
                  <th className="pb-2">Decision</th>
                  <th className="pb-2">Risk Score</th>
                  <th className="pb-2">Lot Z-Score</th>
                  <th className="pb-2">Pred 168h</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {summaryData.top_anomalous_components?.map((c) => (
                  <tr
                    key={c.component_id}
                    onClick={() => onSelectComponent && onSelectComponent(c.component_id)}
                    className="hover:bg-slate-800/50 transition-colors cursor-pointer"
                  >
                    <td className="py-2.5 font-semibold text-cyan-400 font-mono">{c.component_id}</td>
                    <td className="py-2.5 text-slate-300 font-mono">{c.lot_id}</td>
                    <td className="py-2.5 text-slate-400">{c.component_type}</td>
                    <td className="py-2.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        c.decision === 'EARLY REJECT' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                        c.decision === 'WATCH' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                        'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      }`}>
                        {c.decision}
                      </span>
                    </td>
                    <td className="py-2.5 font-bold font-mono text-rose-400">{c.risk_score}/100</td>
                    <td className="py-2.5 font-mono text-amber-400">+{c.lot_z_score_0h?.toFixed(1)}&sigma;</td>
                    <td className="py-2.5 font-mono text-slate-200">{c.predicted_168h?.toFixed(1)} &micro;A</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
