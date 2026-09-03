import React from 'react';
import {
  LayoutDashboard, Upload, Search, Building2, AlertTriangle,
  TrendingUp, Target, Brain, Cpu, Settings
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview Dashboard', icon: LayoutDashboard },
  { id: 'upload', label: 'Dataset Upload', icon: Upload },
  { id: 'component', label: 'Component Analysis', icon: Search },
  { id: 'lot', label: 'Lot Analysis', icon: Building2 },
  { id: 'anomaly', label: 'Anomaly Detection', icon: AlertTriangle },
  { id: 'prediction', label: '168h Prediction', icon: TrendingUp },
  { id: 'risk', label: 'Risk Analysis', icon: Target },
  { id: 'xai', label: 'Explainable AI (SHAP)', icon: Brain },
  { id: 'performance', label: 'Model Performance', icon: Cpu },
  { id: 'settings', label: 'Settings & Config', icon: Settings },
];

export default function Sidebar({ activeTab, setActiveTab }) {
  return (
    <aside className="w-64 border-r border-slate-800 bg-[#0F172A] p-4 flex flex-col justify-between shrink-0 min-h-[calc(100vh-4rem)]">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[10px] font-semibold text-slate-500 uppercase tracking-wider font-mono">
          System Modules
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-150 cursor-pointer ${
                isActive
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px] text-slate-400 space-y-1">
        <div className="flex justify-between items-center text-slate-300 font-medium">
          <span>Engine</span>
          <span className="text-cyan-400 font-mono font-bold">BURNINSIGHT AI</span>
        </div>
        <div className="text-[10px] text-slate-500">AI Anomaly Detection & 168h Prediction Engine</div>
      </div>

    </aside>
  );
}
