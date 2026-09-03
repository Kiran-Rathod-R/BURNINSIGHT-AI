import React, { useState, useEffect } from 'react';
import { Settings, Save, CheckCircle2 } from 'lucide-react';
import { fetchSettings, updateSettings } from '../services/api';

export default function SettingsPage({ onRefresh }) {
  const [threshold, setThreshold] = useState(30.0);
  const [contamination, setContamination] = useState(0.08);
  const [savedMsg, setSavedMsg] = useState('');

  useEffect(() => {
    fetchSettings().then((res) => {
      if (res.safety_drift_threshold) setThreshold(res.safety_drift_threshold);
      if (res.anomaly_contamination) setContamination(res.anomaly_contamination);
    });
  }, []);

  const handleSave = async () => {
    try {
      await updateSettings({
        safety_drift_threshold: parseFloat(threshold),
        anomaly_contamination: parseFloat(contamination)
      });
      setSavedMsg('Settings updated successfully!');
      if (onRefresh) onRefresh();
      setTimeout(() => setSavedMsg(''), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-6">
        <div className="flex items-center space-x-2 text-cyan-400 font-bold text-base">
          <Settings className="w-5 h-5" />
          <h2>Configurable Thresholds & Parameters</h2>
        </div>

        <div className="space-y-4 text-xs font-mono">
          <div>
            <label className="block text-slate-300 font-bold mb-1">
              Safety Drift Threshold (&micro;A): <span className="text-cyan-400">{threshold} &micro;A</span>
            </label>
            <input
              type="range"
              min="5.0"
              max="100.0"
              step="1.0"
              value={threshold}
              onChange={(e) => setThreshold(e.target.value)}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
            <span className="text-[10px] text-slate-500 block mt-1">Predicted 168h values above this limit trigger UNSAFE drift status.</span>
          </div>

          <div>
            <label className="block text-slate-300 font-bold mb-1">
              Isolation Forest Contamination: <span className="text-cyan-400">{(contamination * 100).toFixed(0)}%</span>
            </label>
            <input
              type="range"
              min="0.01"
              max="0.25"
              step="0.01"
              value={contamination}
              onChange={(e) => setContamination(e.target.value)}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
            <span className="text-[10px] text-slate-500 block mt-1">Sensitivity parameter estimating baseline proportion of outliers.</span>
          </div>
        </div>

        {savedMsg && (
          <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            <span>{savedMsg}</span>
          </div>
        )}

        <button
          onClick={handleSave}
          className="w-full py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs flex items-center justify-center gap-2 cursor-pointer shadow-lg shadow-cyan-500/20"
        >
          <Save className="w-4 h-4" />
          <span>Save System Configurations</span>
        </button>
      </div>
    </div>
  );
}
