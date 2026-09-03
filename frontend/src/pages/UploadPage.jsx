import React, { useState } from 'react';
import { UploadCloud, CheckCircle, AlertCircle, FileText, Sparkles } from 'lucide-react';
import { uploadCSVFile, triggerDemoMode } from '../services/api';

export default function UploadPage({ onRefresh }) {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    try {
      setIsUploading(true);
      setError(null);
      const res = await uploadCSVFile(file);
      setReport(res.preprocessing_report);
      if (onRefresh) onRefresh();
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please verify CSV format.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDemo = async () => {
    try {
      setIsUploading(true);
      setError(null);
      const res = await triggerDemoMode();
      setReport(res.preprocessing_report);
      if (onRefresh) onRefresh();
    } catch (err) {
      setError('Demo dataset generation failed.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Upload Zone Card */}
      <div className="p-8 rounded-2xl glass-panel border border-slate-800 text-center space-y-4">
        <div className="w-16 h-16 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 flex items-center justify-center mx-auto">
          <UploadCloud className="w-8 h-8" />
        </div>
        <div>
          <h2 className="text-lg font-bold text-white">Upload Component Burn-In Screening Dataset</h2>
          <p className="text-xs text-slate-400 mt-1">
            Supports CSV files containing fields: <code className="text-cyan-400">component_id, lot_id, measurement_time_hours (0,24,96,168), leakage_current, voltage, current</code>
          </p>
        </div>

        <div className="border-2 border-dashed border-slate-700 hover:border-cyan-500/50 rounded-xl p-6 bg-slate-900/40 transition-colors">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="hidden"
            id="csv-upload-input"
          />
          <label htmlFor="csv-upload-input" className="cursor-pointer space-y-2 block">
            <FileText className="w-8 h-8 text-slate-500 mx-auto" />
            <span className="text-xs text-slate-300 block">
              {file ? file.name : 'Click to select CSV file or drag and drop'}
            </span>
          </label>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center justify-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="flex justify-center gap-4 pt-2">
          <button
            onClick={handleUpload}
            disabled={!file || isUploading}
            className="px-6 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-cyan-500/20 cursor-pointer"
          >
            {isUploading ? 'Processing AI Pipeline...' : 'Run Pipeline Analysis'}
          </button>
          <button
            onClick={handleDemo}
            disabled={isUploading}
            className="px-6 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-semibold border border-cyan-500/30 flex items-center gap-2 cursor-pointer"
          >
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span>Load Demo Dataset</span>
          </button>
        </div>
      </div>

      {/* Preprocessing Report */}
      {report && (
        <div className="p-6 rounded-2xl glass-panel border border-cyan-500/30 bg-cyan-500/5 space-y-4">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-emerald-400" />
              Data Preprocessing & Validation Report
            </h3>
            <span className="text-xs font-mono px-3 py-1 rounded bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30">
              Data Quality: {report.data_quality_score}%
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
            <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
              <div className="text-slate-400 text-[10px]">Total Rows</div>
              <div className="text-lg font-bold text-white">{report.total_rows}</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
              <div className="text-slate-400 text-[10px]">Missing Imputed</div>
              <div className="text-lg font-bold text-amber-400">{report.missing_values_count}</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
              <div className="text-slate-400 text-[10px]">Duplicates Filtered</div>
              <div className="text-lg font-bold text-cyan-400">{report.duplicates_removed}</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800">
              <div className="text-slate-400 text-[10px]">Outliers Detected</div>
              <div className="text-lg font-bold text-rose-400">{report.outliers_detected}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
