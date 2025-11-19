// Type definitions for the RAG Learning Prototype

export interface ChatRequest {
  query: string;
  top_k?: number;
  enabled_datasets?: string[];
  model?: string;
  temperature?: number;
  max_tokens?: number;
  min_score?: number;
}

export interface ChunkInfo {
  text: string;
  score: number;
  metadata: {
    dataset_id: string;
    dataset_name: string;
    source_title: string;
    chunk_index: number;
    char_count: number;
    created_at: string;
  };
}

export interface ObservabilityStep {
  name: string;
  latency_ms: number;
  details: Record<string, any>;
}

export interface ObservabilityData {
  total_latency_ms: number;
  steps: ObservabilityStep[];
  full_prompt: string;
}

export interface ChatResponse {
  answer: string;
  observability: ObservabilityData;
}

export interface DatasetInfo {
  id: string;
  name: string;
  enabled: boolean;
  num_chunks: number;
  file_size: number;
  chunk_size: number;
  chunk_overlap: number;
  chunking_strategy: string;
  created_at: string;
  updated_at: string;
}

export interface DatasetListResponse {
  datasets: DatasetInfo[];
  total: number;
}

export interface DatasetUploadResponse {
  dataset_id: string;
  dataset_name: string;
  num_chunks: number;
  file_size: number;
  chunk_size: number;
  chunk_overlap: number;
  chunking_strategy: string;
  status: string;
  message: string;
}

export interface ConfigResponse {
  default_chunk_size: number;
  default_chunk_overlap: number;
  default_top_k: number;
  default_temperature: number;
  default_model: string;
  default_max_tokens: number;
  default_min_score: number;
  system_prompt: string;
}

export interface ConfigUpdate {
  default_chunk_size?: number;
  default_chunk_overlap?: number;
  default_top_k?: number;
  default_temperature?: number;
  default_model?: string;
  default_max_tokens?: number;
  default_min_score?: number;
  system_prompt?: string;
}

export interface EvaluationSubmit {
  query: string;
  response: string;
  retrieved_chunks: ChunkInfo[];
  rating?: number;
  notes?: string;
  config?: Record<string, any>;
  observability_data?: ObservabilityData;
}

export interface EvaluationInfo {
  id: number;
  query: string;
  response: string;
  rating?: number;
  notes?: string;
  num_chunks: number;
  response_length: number;
  avg_chunk_score: number;
  config?: Record<string, any>;
  observability_data?: ObservabilityData;
  created_at: string;
}

export interface EvaluationListResponse {
  evaluations: EvaluationInfo[];
  total: number;
}

export interface TestQuestion {
  question: string;
  expected_keywords: string[];
  expected_source?: string;
}

export interface BatchEvaluationRequest {
  test_questions: TestQuestion[];
  top_k?: number;
  model?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface BatchEvaluationResult {
  question: string;
  answer: string;
  expected_keywords: string[];
  keywords_found: string[];
  keyword_coverage: number;
  observability: ObservabilityData;
}

export interface BatchEvaluationResponse {
  total_questions: number;
  avg_keyword_coverage: number;
  avg_latency_ms: number;
  results: BatchEvaluationResult[];
  evaluated_at: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  observability?: ObservabilityData;
  timestamp: Date;
}
