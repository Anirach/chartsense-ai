export interface Patient {
  id: number;
  hn: string;
  name: string;
  age: number;
  sex: string;
  pmh: string[];
  allergies: string[];
}

export interface Encounter {
  id: number;
  encounter_id: string;
  patient_id: number;
  admit_date: string;
  dc_date: string | null;
  ward: string;
  los: number;
  status: string;
  chief_complaint: string | null;
  patient?: Patient;
  diagnoses?: DiagnosisItem[];
  observations?: ObservationItem[];
  orders?: OrderItem[];
  progress_notes?: ProgressNoteItem[];
}

export interface DiagnosisItem {
  id: number;
  icd_code: string;
  description: string;
  dx_type: string;
  source: string;
  confidence: number | null;
}

export interface ObservationItem {
  id: number;
  obs_type: string;
  code: string;
  display_name: string;
  value: string;
  unit: string;
  abnormal_flag: boolean;
}

export interface OrderItem {
  id: number;
  category: string;
  standard_code: string;
  display_name: string;
  status: string;
}

export interface ProgressNoteItem {
  id: number;
  date_time: string;
  text: string;
  author: string;
}

export interface DifferentialDiagnosis {
  rank: number;
  icd_code: string;
  description: string;
  description_th: string;
  probability: number;
  reasoning: string;
  evidence: string[];
  cpg_reference: string | null;
}

export interface PreDiagnosisResponse {
  differentials: DifferentialDiagnosis[];
  primary_disease_group: string;
  confidence_note: string;
}

export interface OrderSuggestion {
  category: string;
  code: string;
  display_name: string;
  priority: string;
  rationale: string;
  cpg_source: string | null;
}

export interface OrderSuggestionResponse {
  orders: OrderSuggestion[];
  disease_group: string;
  personalization_notes: string[];
}

export interface RiskScoreDetail {
  tool_name: string;
  score: number;
  max_score: number;
  components: Record<string, number>;
  interpretation: string;
  mortality_risk: string | null;
}

export interface AdmissionDecisionResponse {
  recommendation: string;
  risk_level: string;
  risk_scores: RiskScoreDetail[];
  reasoning: string;
  suggested_ward: string;
}

export interface ChartGap {
  rule_id: string;
  category: string;
  description: string;
  severity: string;
  suggested_action: string | null;
  suggested_code: string | null;
}

export interface CategoryBreakdown {
  category: string;
  score: number;
  max_score: number;
  weight: number;
  items_found: number;
  items_expected: number;
}

export interface ChartScoreResponse {
  encounter_id: string;
  total_score: number;
  grade: string;
  breakdown: CategoryBreakdown[];
  gaps: ChartGap[];
  evaluated_at: string;
}

export interface CodeSuggestionItem {
  id: number;
  icd_code: string;
  description: string;
  dx_type: string;
  confidence: number;
  evidence: string[];
  rw_impact: number;
  status: string;
}

export interface CodeSuggestionResponse {
  encounter_id: string;
  suggestions: CodeSuggestionItem[];
  rw_before: number;
  rw_after: number;
  rw_delta: number;
  revenue_impact_thb: number;
  drg: string | null;
}

export interface Rule {
  id: number;
  rule_id: string;
  category: string;
  name: string;
  description: string | null;
  weight: number;
  condition: Record<string, unknown>;
  active: boolean;
}

export interface CPGTemplate {
  id: number;
  template_id: string;
  disease_group: string;
  name: string;
  description: string | null;
  orders: Record<string, unknown>[];
  criteria: Record<string, unknown>;
  version: string;
}
