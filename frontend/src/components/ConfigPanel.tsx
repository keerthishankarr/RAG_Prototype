import React, { useState } from 'react';
import type { DatasetInfo, ConfigResponse } from '../types';
import { updateDataset, deleteDataset, updateConfig } from '../services/api';
import DatasetManager from './DatasetManager';

interface ConfigPanelProps {
  datasets: DatasetInfo[];
  config: ConfigResponse | null;
  onDatasetsUpdate: () => void;
  onConfigUpdate: () => void;
}

const ConfigPanel: React.FC<ConfigPanelProps> = ({
  datasets,
  config,
  onDatasetsUpdate,
  onConfigUpdate,
}) => {
  const [showUpload, setShowUpload] = useState(false);
  const [localConfig, setLocalConfig] = useState(config);

  const totalChunks = datasets.reduce((sum, d) => sum + d.num_chunks, 0);
  const activeDatasets = datasets.filter(d => d.enabled).length;

  const handleToggleDataset = async (datasetId: string, enabled: boolean) => {
    try {
      await updateDataset(datasetId, { enabled: !enabled });
      onDatasetsUpdate();
    } catch (error) {
      console.error('Error toggling dataset:', error);
    }
  };

  const handleDeleteDataset = async (datasetId: string) => {
    if (!confirm('Are you sure you want to delete this dataset?')) return;
    try {
      await deleteDataset(datasetId);
      onDatasetsUpdate();
    } catch (error) {
      console.error('Error deleting dataset:', error);
    }
  };

  const handleConfigChange = async (key: string, value: any) => {
    const updated = { ...localConfig, [key]: value };
    setLocalConfig(updated as ConfigResponse);
    try {
      await updateConfig({ [key]: value });
      onConfigUpdate();
    } catch (error) {
      console.error('Error updating config:', error);
    }
  };

  return (
    <>
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3.5 bg-gray-50 border-b border-gray-200">
        <img src="/icons/settings-icon.svg" alt="Settings" className="w-5 h-5" />
        <h2 className="text-base font-normal text-[#0A0A0A]">Configuration</h2>
      </div>

      {/* Content */}
      <div className="overflow-y-auto" style={{ height: 'calc(100vh - 121px)' }}>
        {/* Dataset Management */}
        <div className="px-4 py-5">
          <h3 className="text-base font-normal text-[#0A0A0A] mb-4">Dataset Management</h3>

          {/* Stats Cards */}
          <div className="grid grid-cols-2 gap-2 mb-4">
            <div className="bg-[#EFF6FF] rounded p-2">
              <div className="text-xs text-[#4A5565] mb-1">Total Datasets</div>
              <div className="text-sm font-normal text-[#155DFC]">{datasets.length}</div>
            </div>
            <div className="bg-[#F0FDF4] rounded p-2">
              <div className="text-xs text-[#4A5565] mb-1">Active</div>
              <div className="text-sm font-normal text-[#00A63E]">{activeDatasets}</div>
            </div>
            <div className="bg-[#FAF5FF] rounded p-2 col-span-2">
              <div className="text-xs text-[#4A5565] mb-1">Total Chunks</div>
              <div className="text-sm font-normal text-[#9810FA]">{totalChunks.toLocaleString()}</div>
            </div>
          </div>

          {/* Dataset Cards */}
          <div className="space-y-2 mb-2">
            {datasets.map((dataset) => (
              <div
                key={dataset.id}
                className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[10px] p-3.5 shadow-[0px_8px_10px_-6px_rgba(0,0,0,0.1),0px_20px_25px_-5px_rgba(0,0,0,0.1)]"
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex items-start gap-2 flex-1">
                    <span className="text-xl leading-none">{dataset.name.includes('Aesop') ? '📚' : '📖'}</span>
                    <div className="flex-1">
                      <div className="text-base font-normal text-[#0A0A0A] leading-6">{dataset.name}</div>
                      <div className="text-xs text-[#6A7282] leading-4">
                        {dataset.num_chunks} chunks • {(dataset.file_size / 1024).toFixed(0)}KB
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="px-2 py-0.5 bg-[#DCFCE7] text-[#008236] text-xs rounded leading-4">
                      Active
                    </div>
                    <div className="text-xs text-[#99A1AF] leading-4">
                      {new Date(dataset.created_at).toISOString().split('T')[0]}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleToggleDataset(dataset.id, dataset.enabled)}
                    className={`relative w-8 h-[18.4px] rounded-full transition-colors ${
                      dataset.enabled ? 'bg-[#030213]' : 'bg-gray-300'
                    }`}
                  >
                    <div
                      className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                        dataset.enabled ? 'right-0.5' : 'left-0.5'
                      }`}
                    />
                  </button>
                  <button
                    onClick={() => handleDeleteDataset(dataset.id)}
                    className="w-8 h-8 flex items-center justify-center hover:bg-gray-100 rounded"
                  >
                    <img src="/icons/trash-icon.svg" alt="Delete" className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Add Dataset Button */}
          <button
            onClick={() => setShowUpload(true)}
            className="w-full py-2 px-3 bg-white border border-[rgba(0,0,0,0.1)] text-[#0A0A0A] rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
          >
            <img src="/icons/plus-icon.svg" alt="Add" className="w-4 h-4" />
            Add Dataset
          </button>
        </div>

        {/* Chunking Settings */}
        {localConfig && (
          <>
            <div className="px-4 py-4 border-t border-[rgba(0,0,0,0.1)]">
              <h3 className="text-base font-normal text-[#0A0A0A] mb-4">Chunking Settings</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-[#0A0A0A] mb-2 leading-none">
                    Chunk Size (characters)
                  </label>
                  <input
                    type="number"
                    min="300"
                    max="800"
                    value={localConfig.default_chunk_size}
                    onChange={(e) =>
                      handleConfigChange('default_chunk_size', parseInt(e.target.value))
                    }
                    className="w-full px-3 py-2 bg-[#F3F3F5] border border-[rgba(0,0,0,0)] rounded-lg text-sm text-[#0A0A0A] focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <p className="text-xs text-[#6A7282] mt-1.5 leading-4">Recommended: 300-800</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-[#0A0A0A] mb-2 leading-none">
                    Chunk Overlap (characters)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="200"
                    value={localConfig.default_chunk_overlap}
                    onChange={(e) =>
                      handleConfigChange('default_chunk_overlap', parseInt(e.target.value))
                    }
                    className="w-full px-3 py-2 bg-[#F3F3F5] border border-[rgba(0,0,0,0)] rounded-lg text-sm text-[#0A0A0A] focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <p className="text-xs text-[#6A7282] mt-1.5 leading-4">Overlap helps maintain context between chunks</p>
                </div>
                <button className="w-full py-2 px-3 bg-[#ECEEF2] text-[#030213] rounded-lg text-sm font-medium hover:bg-gray-300 transition-colors flex items-center justify-center gap-2">
                  <img src="/icons/refresh-icon.svg" alt="Refresh" className="w-4 h-4" />
                  Re-chunk & Re-index
                </button>
              </div>
            </div>

            {/* Retrieval Settings */}
            <div className="px-4 py-4 border-t border-[rgba(0,0,0,0.1)]">
              <h3 className="text-base font-normal text-[#0A0A0A] mb-4">Retrieval Settings</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="text-sm font-medium text-[#0A0A0A] leading-none">Top-K Chunks</label>
                    <div className="px-2 py-0.5 bg-[#EFF6FF] text-[#155DFC] text-sm font-normal rounded">
                      {localConfig.default_top_k}
                    </div>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="100"
                    value={localConfig.default_top_k}
                    onChange={(e) =>
                      handleConfigChange('default_top_k', parseInt(e.target.value))
                    }
                    className="w-full h-4 bg-[#E5E7EB] rounded-full appearance-none cursor-pointer slider"
                  />
                  <div className="flex justify-between text-xs text-[#6A7282] mt-1">
                    <span>1</span>
                    <span>50</span>
                    <span>100</span>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="text-sm font-medium text-[#0A0A0A] flex items-center gap-1 leading-none">
                      Similarity Threshold
                      <img src="/icons/info-icon.svg" alt="Info" className="w-3 h-3" />
                    </label>
                    <div className="px-2 py-0.5 text-[#00A63E] text-sm font-normal rounded">
                      {localConfig.default_min_score.toFixed(2)}
                    </div>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={localConfig.default_min_score}
                    onChange={(e) =>
                      handleConfigChange('default_min_score', parseFloat(e.target.value))
                    }
                    className="w-full h-4 bg-[#E5E7EB] rounded-full appearance-none cursor-pointer slider"
                  />
                  <div className="flex justify-between text-xs text-[#6A7282] mt-1">
                    <span>0.0</span>
                    <span>0.5</span>
                    <span>1.0</span>
                  </div>
                </div>
                <div className="bg-[#F9FAFB] rounded-lg p-3">
                  <div className="flex justify-between items-center mb-2">
                    <div className="text-sm text-[#4A5565]">Embedding Model</div>
                    <div className="px-2 py-0.5 bg-[#DCFCE7] text-[#008236] text-xs rounded leading-4">
                      Local/Free
                    </div>
                  </div>
                  <div className="text-sm text-[#0A0A0A] mb-1">all-MiniLM-L6-v2</div>
                  <div className="text-xs text-[#6A7282]">384 dimensions</div>
                </div>
              </div>
            </div>

            {/* System Prompt */}
            <div className="px-4 py-4 border-t border-[rgba(0,0,0,0.1)]">
              <h3 className="text-base font-normal text-[#0A0A0A] mb-4">System Prompt</h3>
              <div>
                <label className="block text-sm font-medium text-[#0A0A0A] mb-2 leading-none">
                  Prompt Template
                </label>
                <textarea
                  value={localConfig.system_prompt}
                  onChange={(e) => handleConfigChange('system_prompt', e.target.value)}
                  className="w-full px-3 py-2 bg-[#F3F3F5] border border-[rgba(0,0,0,0)] rounded-lg text-sm text-[#0A0A0A] resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
                  rows={10}
                  placeholder="Enter your system prompt template..."
                />
                <p className="text-xs text-[#6A7282] mt-1.5 leading-4">
                  Use {'{retrieved_chunks}'} and {'{user_query}'} as placeholders
                </p>
              </div>
            </div>

            {/* LLM Settings */}
            <div className="px-4 py-4 border-t border-[rgba(0,0,0,0.1)]">
              <h3 className="text-base font-normal text-[#0A0A0A] mb-4">LLM Settings</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="text-sm font-medium text-[#0A0A0A] leading-none">Model</label>
                    <span className="text-sm">💰💰💰</span>
                  </div>
                  <select
                    value={localConfig.default_model}
                    onChange={(e) => handleConfigChange('default_model', e.target.value)}
                    className="w-full px-3 py-2 bg-[#F3F3F5] border border-[rgba(0,0,0,0)] rounded-lg text-sm text-[#0A0A0A] focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none"
                  >
                    <option value="gpt-4o">Claude Sonnet 4.5</option>
                    <option value="gpt-4o-mini">GPT-4o</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  </select>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="text-sm font-medium text-[#0A0A0A] flex items-center gap-1 leading-none">
                      Temperature
                      <img src="/icons/info-icon-2.svg" alt="Info" className="w-3 h-3" />
                    </label>
                    <div className="px-2 py-0.5 bg-[#FAF5FF] text-[#9810FA] text-sm font-normal rounded">
                      {localConfig.default_temperature}
                    </div>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    value={localConfig.default_temperature}
                    onChange={(e) =>
                      handleConfigChange('default_temperature', parseFloat(e.target.value))
                    }
                    className="w-full h-4 bg-[#E5E7EB] rounded-full appearance-none cursor-pointer slider"
                  />
                  <div className="flex justify-between text-xs text-[#6A7282] mt-1">
                    <span>Focused</span>
                    <span>Balanced</span>
                    <span>Creative</span>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className="text-sm font-medium text-[#0A0A0A] leading-none">Max Tokens</label>
                    <span className="text-xs text-[#6A7282]">~{Math.round(localConfig.default_max_tokens / 4)} words</span>
                  </div>
                  <input
                    type="number"
                    min="50"
                    max="4000"
                    value={localConfig.default_max_tokens}
                    onChange={(e) =>
                      handleConfigChange('default_max_tokens', parseInt(e.target.value))
                    }
                    className="w-full px-3 py-2 bg-[#F3F3F5] border border-[rgba(0,0,0,0)] rounded-lg text-sm text-[#0A0A0A] focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
                  />
                  <input
                    type="range"
                    min="50"
                    max="4000"
                    step="50"
                    value={localConfig.default_max_tokens}
                    onChange={(e) =>
                      handleConfigChange('default_max_tokens', parseInt(e.target.value))
                    }
                    className="w-full h-4 bg-[#E5E7EB] rounded-full appearance-none cursor-pointer slider"
                  />
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      {showUpload && (
        <DatasetManager onClose={() => setShowUpload(false)} onSuccess={onDatasetsUpdate} />
      )}

      <style>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: white;
          border: 1px solid #030213;
          cursor: pointer;
          box-shadow: 0 1px 2px -1px rgba(0, 0, 0, 0.1), 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        }
        .slider::-moz-range-thumb {
          width: 16px;
          height: 16px;
          border-radius: 50%;
          background: white;
          border: 1px solid #030213;
          cursor: pointer;
          box-shadow: 0 1px 2px -1px rgba(0, 0, 0, 0.1), 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        }
      `}</style>
    </>
  );
};

export default ConfigPanel;
