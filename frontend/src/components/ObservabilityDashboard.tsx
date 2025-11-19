import React, { useState } from 'react';
import type { ObservabilityData } from '../types';

interface ObservabilityDashboardProps {
  observability: ObservabilityData | null;
}

const ObservabilityDashboard: React.FC<ObservabilityDashboardProps> = ({ observability }) => {
  const [showPrompt, setShowPrompt] = useState(false);
  const [expandedSteps, setExpandedSteps] = useState<Record<string, boolean>>({});

  if (!observability) {
    return (
      <>
        <div className="flex items-center gap-2 px-4 py-3.5 bg-gray-50 border-b border-gray-200">
          <img src="/icons/chart-icon.svg" alt="Dashboard" className="w-5 h-5" />
          <h2 className="text-base font-normal text-[#0A0A0A]">Observability Dashboard</h2>
        </div>
        <div className="flex items-center justify-center h-full">
          <p className="text-sm text-[#99A1AF]">Send a query to see observability data...</p>
        </div>
      </>
    );
  }

  const { steps, total_latency_ms, full_prompt } = observability;

  const embeddingStep = steps.find((s) => s.name === 'embedding');
  const retrievalStep = steps.find((s) => s.name === 'retrieval');
  const llmStep = steps.find((s) => s.name === 'llm_generation');

  const chunks = retrievalStep?.details.chunks || [];

  return (
    <>
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3.5 bg-gray-50 border-b border-gray-200">
        <img src="/icons/chart-icon.svg" alt="Dashboard" className="w-5 h-5" />
        <h2 className="text-base font-normal text-[#0A0A0A]">Observability Dashboard</h2>
      </div>

      {/* Content */}
      <div className="overflow-y-auto p-4 space-y-6" style={{ height: 'calc(100vh - 121px)' }}>
        {/* Query Pipeline Timeline */}
        <div className="space-y-3">
          <h3 className="text-base font-normal text-[#0A0A0A]">Query Pipeline</h3>
          <div className="space-y-2">
            {steps.map((step, i) => (
              <div key={i} className="bg-white border border-[rgba(0,0,0,0.1)] rounded-lg p-3 shadow-sm">
                <div
                  className="flex items-start gap-3 cursor-pointer"
                  onClick={() => setExpandedSteps(prev => ({ ...prev, [step.name]: !prev[step.name] }))}
                >
                  <div className="w-6 h-6 rounded bg-[#EFF6FF] text-[#155DFC] flex items-center justify-center text-xs font-medium flex-shrink-0">
                    {i + 1}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-normal text-[#0A0A0A] capitalize">
                      {step.name === 'llm_generation' ? 'LLM Generation' : step.name.replace('_', ' ')}
                    </div>
                    <div className="text-xs text-[#6A7282] mt-0.5">
                      {step.latency_ms}ms
                      {step.name === 'retrieval' && step.details.chunks &&
                        ` • ${step.details.chunks.length} chunks retrieved`
                      }
                    </div>
                  </div>
                  <svg
                    className={`w-4 h-4 text-[#99A1AF] transition-transform ${expandedSteps[step.name] ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>

                {/* Request/Response Details */}
                {expandedSteps[step.name] && (
                  <div className="mt-3 space-y-2">
                    {step.details.request && (
                      <div className="bg-[#F9FAFB] rounded p-2">
                        <div className="text-xs font-medium text-[#4A5565] mb-1">📤 Request</div>
                        <pre className="text-xs text-[#6A7282] whitespace-pre-wrap overflow-x-auto">
                          {JSON.stringify(step.details.request, null, 2)}
                        </pre>
                      </div>
                    )}
                    {step.details.response && (
                      <div className="bg-[#F9FAFB] rounded p-2">
                        <div className="text-xs font-medium text-[#4A5565] mb-1">📥 Response</div>
                        {step.name === 'retrieval' && step.details.response.chunks_data ? (
                          <div className="space-y-1">
                            <div className="text-xs text-[#6A7282] mb-1">
                              {step.details.response.chunks_retrieved} chunks retrieved
                            </div>
                            {step.details.response.chunks_data.map((chunk: any, idx: number) => (
                              <div key={idx} className="bg-white border border-[rgba(0,0,0,0.1)] rounded p-2">
                                <div className="flex justify-between mb-1">
                                  <span className="text-xs font-medium text-[#155DFC]">Chunk {idx + 1}</span>
                                  <span className="text-xs bg-[#DCFCE7] text-[#008236] px-1.5 py-0.5 rounded">
                                    {chunk.score.toFixed(2)}
                                  </span>
                                </div>
                                <p className="text-xs text-[#6A7282] line-clamp-3">{chunk.text}</p>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <pre className="text-xs text-[#6A7282] whitespace-pre-wrap overflow-x-auto">
                            {JSON.stringify(step.details.response, null, 2)}
                          </pre>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Retrieved Chunks */}
        {chunks.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-base font-normal text-[#0A0A0A]">Retrieved Chunks</h3>
            <div className="space-y-2">
              {chunks.map((chunk: any, i: number) => (
                <div key={i} className="bg-white border border-[rgba(0,0,0,0.1)] rounded-lg p-3 shadow-sm text-xs">
                  <div className="flex justify-between items-center mb-2 pb-2 border-b border-[rgba(0,0,0,0.05)]">
                    <span className="font-medium text-[#155DFC] text-xs">
                      📚 {chunk.metadata.source_title || 'Document'}
                    </span>
                    <span className="bg-[#DCFCE7] text-[#008236] px-2 py-0.5 rounded text-[10px] font-medium">
                      {chunk.score.toFixed(2)}
                    </span>
                  </div>
                  <p className="text-[#6A7282] leading-relaxed line-clamp-3">{chunk.text}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* LLM Details */}
        {llmStep && (
          <div className="space-y-3">
            <h3 className="text-base font-normal text-[#0A0A0A]">LLM Details</h3>

            <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-lg p-3 shadow-sm">
              <div className="text-xs font-medium text-[#4A5565] mb-3">Token Usage</div>
              <div className="space-y-0">
                {[
                  { label: 'Prompt Tokens', value: llmStep.details.prompt_tokens },
                  { label: 'Completion Tokens', value: llmStep.details.completion_tokens },
                  { label: 'Total Tokens', value: llmStep.details.total_tokens },
                  { label: 'Est. Cost', value: `$${llmStep.details.cost.toFixed(6)}` }
                ].map((item, idx, arr) => (
                  <div key={idx} className={`flex justify-between py-2 text-xs ${idx !== arr.length - 1 ? 'border-b border-[rgba(0,0,0,0.05)]' : ''}`}>
                    <span className="text-[#6A7282]">{item.label}</span>
                    <span className="text-[#0A0A0A] font-normal">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-lg p-3 shadow-sm">
              <div className="text-xs font-medium text-[#4A5565] mb-3">Performance</div>
              <div className="space-y-0">
                {[
                  { label: 'Total Latency', value: `${total_latency_ms}ms` },
                  { label: 'Model', value: llmStep.details.model },
                  { label: 'Temperature', value: llmStep.details.temperature }
                ].map((item, idx, arr) => (
                  <div key={idx} className={`flex justify-between py-2 text-xs ${idx !== arr.length - 1 ? 'border-b border-[rgba(0,0,0,0.05)]' : ''}`}>
                    <span className="text-[#6A7282]">{item.label}</span>
                    <span className="text-[#0A0A0A] font-normal">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Full Prompt */}
        <div className="space-y-2">
          <button
            onClick={() => setShowPrompt(!showPrompt)}
            className="flex items-center gap-2 text-sm font-medium text-[#0A0A0A] hover:text-[#155DFC] transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            Full Prompt
            <svg
              className={`w-4 h-4 transition-transform ${showPrompt ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          {showPrompt && (
            <pre className="p-3 bg-[#F9FAFB] border border-[rgba(0,0,0,0.1)] rounded-lg text-xs overflow-x-auto whitespace-pre-wrap text-[#0A0A0A]">
              {full_prompt}
            </pre>
          )}
        </div>
      </div>
    </>
  );
};

export default ObservabilityDashboard;
