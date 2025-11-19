import axios from 'axios';
import type {
  ChatRequest,
  ChatResponse,
  DatasetListResponse,
  DatasetUploadResponse,
  DatasetInfo,
  ConfigResponse,
  ConfigUpdate,
  EvaluationSubmit,
  EvaluationInfo,
  EvaluationListResponse,
  BatchEvaluationRequest,
  BatchEvaluationResponse,
} from '../types';

// Create axios instance with base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Chat API
export const chat = async (request: ChatRequest): Promise<ChatResponse> => {
  const response = await api.post<ChatResponse>('/api/chat', request);
  return response.data;
};

// Dataset API
export const getDatasets = async (): Promise<DatasetListResponse> => {
  const response = await api.get<DatasetListResponse>('/api/datasets');
  return response.data;
};

export const uploadDataset = async (
  file: File,
  name: string,
  chunkSize: number = 500,
  chunkOverlap: number = 50,
  chunkingStrategy: string = 'sentences'
): Promise<DatasetUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('name', name);
  formData.append('chunk_size', chunkSize.toString());
  formData.append('chunk_overlap', chunkOverlap.toString());
  formData.append('chunking_strategy', chunkingStrategy);

  const response = await api.post<DatasetUploadResponse>('/api/datasets/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const updateDataset = async (
  id: string,
  updates: { name?: string; enabled?: boolean }
): Promise<DatasetInfo> => {
  const response = await api.patch<DatasetInfo>(`/api/datasets/${id}`, updates);
  return response.data;
};

export const deleteDataset = async (id: string): Promise<void> => {
  await api.delete(`/api/datasets/${id}`);
};

// Config API
export const getConfig = async (): Promise<ConfigResponse> => {
  const response = await api.get<ConfigResponse>('/api/config');
  return response.data;
};

export const updateConfig = async (config: ConfigUpdate): Promise<ConfigResponse> => {
  const response = await api.patch<ConfigResponse>('/api/config', config);
  return response.data;
};

// Evaluation API
export const submitEvaluation = async (evaluation: EvaluationSubmit): Promise<EvaluationInfo> => {
  const response = await api.post<EvaluationInfo>('/api/evaluate', evaluation);
  return response.data;
};

export const getEvaluations = async (limit: number = 100): Promise<EvaluationListResponse> => {
  const response = await api.get<EvaluationListResponse>('/api/evaluations', {
    params: { limit },
  });
  return response.data;
};

export const batchEvaluate = async (
  request: BatchEvaluationRequest
): Promise<BatchEvaluationResponse> => {
  const response = await api.post<BatchEvaluationResponse>('/api/evaluate/batch', request);
  return response.data;
};

// Health check
export const healthCheck = async (): Promise<any> => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
