export type AssessmentLabel = 'LIKELY CREDIBLE' | 'UNCERTAIN' | 'LIKELY MISLEADING' | 'UNCERTAIN / NEEDS VERIFICATION';

export interface ModelScores {
  logistic_regression?: number;
  linear_svm?: number;
  gradient_boosting?: number;
  transformer?: number;
  [key: string]: number | undefined;
}

export interface PredictionDetail {
  label: string;
  raw_score: number;
  calibrated_probability: number;
  confidence: number;
  confidence_level: 'High' | 'Medium' | 'Low' | 'None';
  model_agreement: 'High' | 'Medium' | 'Low' | 'N/A';
  agreement_score: number;
  ood_score: number;
  model_scores: ModelScores;
  summary: string;
  limitations: string;
}

export interface ClaimItem {
  claim_id: string;
  text: string;
  sentence_index: number;
  claim_type: 'factual' | 'numerical' | 'attribution' | 'causal' | 'opinion' | 'prediction';
  confidence: number;
  verification_priority: 'High' | 'Medium' | 'Low';
  keywords: string[];
}

export interface EvidenceItem {
  source_name: string;
  url?: string;
  title: string;
  publisher?: string;
  retrieved_at: string;
  relevance_score: number;
  evidence_type: 'supporting' | 'contradicting' | 'contextual' | 'unclear';
  summary: string;
}

export interface HighlightSpan {
  text: string;
  start_char: number;
  end_char: number;
  influence_level: 'high' | 'medium' | 'low';
  direction: 'supports_misleading' | 'supports_credible';
  weight: number;
  explanation: string;
}

export interface ExplanationDetail {
  supporting_signals: [string, number][];
  counter_signals: [string, number][];
  structural_deviations: [string, number, number][];
  highlighted_spans: HighlightSpan[];
}

export interface AnalysisResponse {
  id: string;
  title: string;
  input_type: 'article' | 'headline' | 'url';
  source_url?: string;
  language: string;
  status: string;
  created_at: string;
  prediction?: PredictionDetail;
  claims: ClaimItem[];
  evidence: EvidenceItem[];
  explanation?: ExplanationDetail;
}

export interface AnalysisListItem {
  id: string;
  title: string;
  input_type: string;
  source_url?: string;
  status: string;
  created_at: string;
  label?: string;
  confidence?: number;
  calibrated_probability?: number;
}

export interface ModelMetrics {
  model_name: string;
  model_version: string;
  dataset_name: string;
  sample_count: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  macro_f1: number;
  roc_auc: number;
  pr_auc: number;
  brier_score: number;
  expected_calibration_error: number;
  confusion_matrix: number[][];
}

export interface ModelVersionData {
  id: string;
  version_tag: string;
  model_type: string;
  status: 'TRAINED' | 'EVALUATED' | 'STAGING' | 'PRODUCTION' | 'RETIRED';
  metrics?: ModelMetrics;
  created_at: string;
}

export interface UserProfile {
  id: string;
  email: string;
  role: 'USER' | 'ADMIN';
  is_active: boolean;
  created_at: string;
}

export interface AnalyticsOverview {
  total_analyses: number;
  total_users: number;
  total_feedbacks: number;
  assessment_distribution: Record<string, number>;
  average_confidence: number;
  uncertain_rate: number;
  failure_rate: number;
  average_inference_latency_ms: number;
  analyses_by_input_type: Record<string, number>;
}

export interface AuditLogItem {
  id: string;
  actor_id?: string;
  action: string;
  target_type: string;
  target_id: string;
  details: Record<string, any>;
  created_at: string;
}

export interface SystemHealthData {
  status: string;
  database: string;
  redis: string;
  ml_models: string;
  active_model_version: string;
  environment: string;
  timestamp: string;
}
