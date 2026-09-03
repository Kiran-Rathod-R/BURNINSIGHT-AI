import React, { useState, useEffect } from 'react';
import { Search, AlertTriangle, ShieldCheck, XCircle, Brain, TrendingUp, Info } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, BarChart, Bar, Cell } from 'recharts';
import { fetchComponents, fetchComponentDetail } from '../services/api';

export default function ComponentDetailPage({ initialComponentId }) {
  const [componentsList, setComponentsList] = useState([]);
  const [selectedCompId, setSelectedCompId] = useState(initialComponentId || '');
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchComponents({ limit: 100 }).then((res) => {
      if (res.components && res.components.length > 0) {
        setComponentsList(res.components);
        if (!selectedCompId) {
          // Default to first EARLY REJECT or top component
          const rejectComp = res.components.find((c) => c.current_status === 'EARLY REJECT');
          setSelectedCompId(rejectComp ? rejectComp.component_id : res.components[0].component_id);
        }
      }
    });
  }, []);

  useEffect(() => {
    if (selectedCompId) {
      setLoading(true);
      fetchComponentDetail(selectedCompId)
        .then((res) => setDetail(res))
        .catch((err) => console.error(err))
        .finally(() => setLoading(false));
    }
  }, [selectedCompId]);

  if (!detail) {
    return (
      <div className="p-8 text-center text-slate-400">
        Loading component analysis details...
      </div>
    );
  }

  // Format Recharts Time-Series data
  const timeSeriesData = [
    { hour: '0h', leakage: detail.measurements['0h'] },
    { hour: '24h', leakage: detail.measurements['24h'] },
    { hour: '96h', leakage: detail.measurements['96h'] },
    { hour: '168h (Pred)', leakage: detail.measurements['168h_predicted'], isPredicted: true },
  ];

  if (detail.measurements['168h_actual']) {
    timeSeriesData.push({ hour: '168h (Actual)', leakage: detail.measurements['168h_actual'], isActual: true });
  }

  const sihExp = detail.sih_explanation || {};

  return (
    <div className="space-y-6">
      {/* Component Selector Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 p-4 rounded-2xl glass-panel border border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Search className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              Component Deep-Dive Analysis
              <span className="font-mono text-cyan-400 text-sm">{detail.component_id}</span>
            </h2>
            <p className="text-xs text-slate-400">Lot ID: <span className="font-mono text-slate-200">{detail.lot_id}</span> | Type: {detail.component_type}</p>
          </div>
        </div>

        {/* Dropdown Search */}
        <select
          value={selectedCompId}
          onChange={(e) => setSelectedCompId(e.target.value)}
          className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-4 py-2 focus:ring-2 focus:ring-cyan-500 font-mono"
        >
          {componentsList.map((c) => (
            <option key={c.component_id} value={c.component_id}>
              {c.component_id} ({c.current_status} - Risk {c.risk_score})
            </option>
          ))}
        </select>
      </div>

      {/* Status Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Decision Badge Card */}
        <div className={`p-4 rounded-xl glass-panel border ${
          detail.current_status === 'EARLY REJECT' ? 'border-rose-500/40 bg-rose-500/10' :
          detail.current_status === 'WATCH' ? 'border-amber-500/40 bg-amber-500/10' :
          'border-emerald-500/40 bg-emerald-500/10'
        }`}>
          <div className="text-xs font-semibold text-slate-400">Final Decision</div>
          <div className={`text-xl font-extrabold mt-1 font-mono ${
            detail.current_status === 'EARLY REJECT' ? 'text-rose-400' :
            detail.current_status === 'WATCH' ? 'text-amber-400' : 'text-emerald-400'
          }`}>
            {detail.current_status}
          </div>
          <div className="text-[10px] text-slate-400 mt-1">Confidence: {(detail.confidence * 100).toFixed(0)}%</div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-slate-800">
          <div className="text-xs font-semibold text-slate-400">Risk Score</div>
          <div className="text-2xl font-extrabold text-rose-400 mt-1 font-mono">
            {detail.risk_score} <span className="text-xs font-normal text-slate-500">/ 100</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Weighted composite score</div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-slate-800">
          <div className="text-xs font-semibold text-slate-400">Lot Z-Score</div>
          <div className="text-2xl font-extrabold text-amber-400 mt-1 font-mono">
            +{detail.lot_z_score_0h?.toFixed(2)}&sigma;
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Deviations from lot mean</div>
        </div>

        <div className="p-4 rounded-xl glass-panel border border-slate-800">
          <div className="text-xs font-semibold text-slate-400">Pred 168h Leakage</div>
          <div className="text-2xl font-extrabold text-cyan-400 mt-1 font-mono">
            {detail.measurements['168h_predicted']?.toFixed(2)} &micro;A
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Safety Limit: {detail.configured_safety_limit} &micro;A</div>
        </div>
      </div>

      {/* 4-Part SIH Decision Explanation Card (Judge Feature!) */}
      <div className="p-6 rounded-2xl glass-panel border border-cyan-500/40 bg-gradient-to-br from-cyan-950/20 via-slate-900 to-indigo-950/20 space-y-4">
        <div className="flex items-center space-x-2 text-cyan-400 font-bold text-sm">
          <Brain className="w-5 h-5 animate-pulse" />
          <span>AI Decision Explanation (SIH Key Innovation)</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-1">
            <span className="font-bold text-amber-400 uppercase tracking-wider text-[10px]">WHY FLAGGED?</span>
            {sihExp.why?.map((w, idx) => (
              <p key={idx} className="text-slate-300 leading-relaxed font-sans">{w}</p>
            ))}
          </div>

          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-1">
            <span className="font-bold text-cyan-400 uppercase tracking-wider text-[10px]">WHAT CHANGED?</span>
            {sihExp.what_changed?.map((wc, idx) => (
              <p key={idx} className="text-slate-300 leading-relaxed font-sans">{wc}</p>
            ))}
          </div>

          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-1">
            <span className="font-bold text-indigo-400 uppercase tracking-wider text-[10px]">WHAT WILL HAPPEN?</span>
            <p className="text-slate-300 leading-relaxed font-sans">{sihExp.what_will_happen}</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-1">
            <span className="font-bold text-rose-400 uppercase tracking-wider text-[10px]">WHY UNSAFE?</span>
            <p className="text-slate-300 leading-relaxed font-sans">{sihExp.why_unsafe}</p>
          </div>
        </div>
      </div>

      {/* Main Graph: Measured vs Predicted + Safety Threshold */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Temporal Parameter Drift & 168h Projection</h3>
            <p className="text-xs text-slate-400">Leakage current trajectory across 0h, 24h, 96h + 168h AI model prediction</p>
          </div>
          <div className="flex items-center space-x-4 text-xs">
            <span className="flex items-center gap-1 text-cyan-400">
              <span className="w-3 h-0.5 bg-cyan-400"></span> Measured / Predicted
            </span>
            <span className="flex items-center gap-1 text-rose-400">
              <span className="w-3 h-0.5 bg-rose-500 border border-dashed"></span> Safety Threshold ({detail.configured_safety_limit} &micro;A)
            </span>
          </div>
        </div>

        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
              <XAxis dataKey="hour" stroke="#64748B" />
              <YAxis stroke="#64748B" unit=" µA" />
              <Tooltip
                contentStyle={{ backgroundColor: '#0F172A', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
              />
              <ReferenceLine
                y={detail.configured_safety_limit}
                stroke="#EF4444"
                strokeDasharray="5 5"
                label={{ value: 'Safety Limit', fill: '#EF4444', fontSize: 11 }}
              />
              <Line
                type="monotone"
                dataKey="leakage"
                stroke="#06B6D4"
                strokeWidth={3}
                dot={{ r: 6, fill: '#06B6D4' }}
                activeDot={{ r: 8 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
