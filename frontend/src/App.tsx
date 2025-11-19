import React, { useState, useEffect } from 'react';
import ConfigPanel from './components/ConfigPanel';
import ChatInterface from './components/ChatInterface';
import ObservabilityDashboard from './components/ObservabilityDashboard';
import type { ObservabilityData, DatasetInfo, ConfigResponse } from './types';
import { getConfig, getDatasets } from './services/api';

const App: React.FC = () => {
  const [observability, setObservability] = useState<ObservabilityData | null>(null);
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [config, setConfig] = useState<ConfigResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [configData, datasetsData] = await Promise.all([
        getConfig(),
        getDatasets(),
      ]);
      setConfig(configData);
      setDatasets(datasetsData.datasets);
    } catch (error) {
      console.error('Error loading initial data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleObservabilityUpdate = (data: ObservabilityData) => {
    setObservability(data);
  };

  const handleDatasetsUpdate = () => {
    getDatasets().then((data) => setDatasets(data.datasets));
  };

  const handleConfigUpdate = () => {
    getConfig().then((data) => setConfig(data));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#EDE4CC]">
        <div className="text-black text-xl">Loading RAG Prototype...</div>
      </div>
    );
  }

  return (
    <div className="h-screen overflow-hidden bg-[#EDE4CC]">
      {/* Header */}
      <div className="bg-[#59A6CC] text-white px-6 py-4 shadow-lg">
        <h1 className="text-3xl font-bold tracking-wide">RAG Learning Prototype</h1>
        <p className="text-sm mt-1">
          Explore how Retrieval-Augmented Generation works with interactive controls and full observability
        </p>
      </div>

      {/* Three Panel Layout */}
      <div className="flex gap-4 p-4" style={{ height: 'calc(100vh - 92px)' }}>
        {/* Left Panel - Configuration */}
        <div className="w-[28%] min-w-[338px] bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden flex flex-col">
          <ConfigPanel
            datasets={datasets}
            config={config}
            onDatasetsUpdate={handleDatasetsUpdate}
            onConfigUpdate={handleConfigUpdate}
          />
        </div>

        {/* Center Panel - Chat */}
        <div className="w-[44%] min-w-[452px] bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden flex flex-col">
          <ChatInterface
            datasets={datasets}
            config={config}
            onObservabilityUpdate={handleObservabilityUpdate}
          />
        </div>

        {/* Right Panel - Observability */}
        <div className="w-[28%] min-w-[338px] bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden flex flex-col">
          <ObservabilityDashboard observability={observability} />
        </div>
      </div>
    </div>
  );
};

export default App;
