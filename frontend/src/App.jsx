import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';

import OverviewPage from './pages/OverviewPage';
import UploadPage from './pages/UploadPage';
import ComponentDetailPage from './pages/ComponentDetailPage';
import LotAnalysisPage from './pages/LotAnalysisPage';
import AnomalyDetectionPage from './pages/AnomalyDetectionPage';
import PredictionPage from './pages/PredictionPage';
import RiskAnalysisPage from './pages/RiskAnalysisPage';
import ExplainableAIPage from './pages/ExplainableAIPage';
import ModelPerformancePage from './pages/ModelPerformancePage';
import SettingsPage from './pages/SettingsPage';

import { fetchDashboardSummary } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [summaryData, setSummaryData] = useState(null);
  const [selectedCompId, setSelectedCompId] = useState('');
  const [isDemoLoading, setIsDemoLoading] = useState(false);

  const loadSummary = async () => {
    try {
      const data = await fetchDashboardSummary();
      setSummaryData(data);
    } catch (err) {
      console.error('Failed to load dashboard summary:', err);
    }
  };

  useEffect(() => {
    loadSummary();
  }, []);

  const handleSelectComponent = (compId) => {
    setSelectedCompId(compId);
    setActiveTab('component');
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col font-sans">
      <Header
        onRefresh={loadSummary}
        isDemoLoading={isDemoLoading}
        setIsDemoLoading={setIsDemoLoading}
      />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        <main className="flex-1 p-6 overflow-y-auto max-h-[calc(100vh-4rem)]">
          {activeTab === 'overview' && (
            <OverviewPage
              summaryData={summaryData}
              onSelectComponent={handleSelectComponent}
            />
          )}

          {activeTab === 'upload' && (
            <UploadPage onRefresh={loadSummary} />
          )}

          {activeTab === 'component' && (
            <ComponentDetailPage initialComponentId={selectedCompId} />
          )}

          {activeTab === 'lot' && (
            <LotAnalysisPage />
          )}

          {activeTab === 'anomaly' && (
            <AnomalyDetectionPage />
          )}

          {activeTab === 'prediction' && (
            <PredictionPage />
          )}

          {activeTab === 'risk' && (
            <RiskAnalysisPage />
          )}

          {activeTab === 'xai' && (
            <ExplainableAIPage />
          )}

          {activeTab === 'performance' && (
            <ModelPerformancePage />
          )}

          {activeTab === 'settings' && (
            <SettingsPage onRefresh={loadSummary} />
          )}
        </main>
      </div>
    </div>
  );
}
