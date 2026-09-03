import React from 'react';
import { ShieldCheck, Play, Download, Activity, Cpu } from 'lucide-react';
import { triggerDemoMode, getExportURL } from '../services/api';

export default function Header({ onRefresh, isDemoLoading, setIsDemoLoading }) {
  const handleDemoTrigger = async () => {
    try {
      setIsDemoLoading(true);
      await triggerDemoMode();
      if (onRefresh) onRefresh();
    } catch (err) {
      console.error('Demo trigger failed:', err);
    } finally {
      setIsDemoLoading(false);
    }
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-[#0F172A]/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center space-x-3">
        <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
          <Cpu className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
            BURNINSIGHT AI
            <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-mono border border-cyan-500/30">
              Component Burn-In Screening
            </span>
          </h1>
          <p className="text-xs text-slate-400">Lot-Aware Anomaly Detection & 168h Predictive Analytics</p>
        </div>

      </div>

      <div className="flex items-center space-x-4">
        {/* System Health Badge */}
        <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium">
          <Activity className="w-3.5 h-3.5 animate-spin" />
          <span>AI Pipeline Active</span>
        </div>

        {/* 1-Click Demo Mode Button */}
        <button
          onClick={handleDemoTrigger}
          disabled={isDemoLoading}
          className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-cyan-500/20 transition-all duration-200 disabled:opacity-50 cursor-pointer"
        >
          <Play className="w-4 h-4 fill-white" />
          <span>{isDemoLoading ? 'Running AI Engine...' : '1-Click SIH Demo Mode'}</span>
        </button>

        {/* Export CSV Button */}
        <a
          href={getExportURL()}
          download
          className="flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
        >
          <Download className="w-4 h-4" />
          <span>Export Results</span>
        </a>
      </div>
    </header>
  );
}
