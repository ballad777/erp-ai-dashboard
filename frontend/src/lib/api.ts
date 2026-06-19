export type NumericSummary = Record<
  string,
  {
    count: number | null;
    mean: number | null;
    std: number | null;
    min: number | null;
    "25%": number | null;
    "50%": number | null;
    "75%": number | null;
    max: number | null;
  }
>;

export type PlainSummary = {
  headline?: string;
  what_happened?: string;
  why_it_matters?: string;
  risk?: string;
  next_action?: string;
};

export type Confidence = {
  level?: "high" | "medium" | "low" | string;
  reason?: string;
  blocking_issues?: string[];
};

export type EvidenceItem = {
  label?: string;
  value?: string;
  source?: string;
};

export type TermDefinition = {
  term?: string;
  plain_explanation?: string;
  technical_definition?: string;
  formula?: string;
  how_to_read?: string;
  caveat?: string;
  value?: unknown;
  this_result_means?: string;
};

export type ResearchDetails = {
  method?: string;
  assumptions?: string[];
  parameters?: Record<string, unknown>;
  limitations?: string[];
  artifacts?: Array<string | null | undefined>;
};

export type ChartStory = {
  chart_type: string;
  title: string;
  chart_path?: string;
  chart_url?: string;
  explanation: string;
  key_findings: string;
  meaning: string;
  what_it_cannot_prove?: string;
  trend_interpretation: string;
  anomaly_note: string;
  business_insight: string;
  recommended_action: string;
};

export type DatasetAnalysis = {
  file_name: string;
  row_count: number;
  column_count: number;
  columns: string[];
  data_types: Record<string, string>;
  missing_values: Record<string, number>;
  numeric_summary: NumericSummary;
  recommended_target_columns?: string[];
  quality_report?: Record<string, unknown>;
  parser_warnings?: string[];
  dataset_hash?: string | null;
  schema_fingerprint?: string | null;
  run_id?: string | null;
  dataset_id?: string | null;
  run_manifest?: Record<string, unknown>;
  plain_summary?: PlainSummary;
  confidence?: Confidence;
  evidence?: EvidenceItem[];
  terms?: TermDefinition[];
  research_details?: ResearchDetails;
};

export type MergedDatasetAnalysis = DatasetAnalysis & {
  source_files: string[];
  source_file_count: number;
  source_row_counts: Record<string, number>;
  merge_strategy: string;
  merge_notes: string[];
  merge_plan?: Record<string, unknown>;
  source_file_column: string;
  source_row_column: string;
  common_columns: string[];
};

export type DatasetBatchItem = {
  file_name: string;
  success: boolean;
  analysis: DatasetAnalysis | null;
  error: string | null;
};

export type MultipleDatasetAnalysis = {
  datasets: DatasetBatchItem[];
  merged: MergedDatasetAnalysis | null;
  notes: string[];
};

export type ModelMetric = {
  model_key: string;
  model_name: string;
  model_family: string;
  r2: number;
  rmse: number;
  mae: number;
  training_time_seconds: number;
  accuracy: number | null;
  f1_score: number | null;
  automl_best_params: Record<string, unknown>;
  model_path: string;
  model_url: string;
};

export type ModelOption = {
  key: string;
  label: string;
  problem_type: "regression" | "classification";
  family: string;
  description: string;
  complexity: "low" | "medium" | "high";
  purpose?: string;
  suitable_data_types?: string[];
  difficulty_label?: string;
  use_cases?: string[];
};

export type GeneratedChart = {
  chart_type: string;
  title: string;
  chart_path: string;
  chart_url: string;
};

export type ModelAnalysis = {
  file_name: string;
  target_column: string;
  analysis_mode: "auto" | "regression" | "classification";
  problem_type: "regression" | "classification";
  row_count_used: number;
  source_row_count?: number | null;
  feature_count_used: number;
  model_results: ModelMetric[];
  model_selection_mode: "auto" | "custom";
  automl_mode: "off" | "quick";
  selected_model_keys: string[];
  available_models: ModelOption[];
  recommended_models: ModelOption[];
  model_results_path: string;
  model_results_url: string;
  cleaned_dataset_path: string;
  cleaned_dataset_url: string;
  chart_path: string;
  chart_url: string;
  charts: GeneratedChart[];
  selected_chart_types: string[];
  notes: string[];
  run_id?: string | null;
  dataset_id?: string | null;
  run_manifest?: Record<string, unknown>;
  plain_summary?: PlainSummary;
  confidence?: Confidence;
  evidence?: EvidenceItem[];
  terms?: TermDefinition[];
  chart_stories?: ChartStory[];
  model_guidance?: DecisionBrief["model_guidance"];
  research_details?: ResearchDetails;
};

export type GeneratedCode = {
  file_name: string;
  target_column: string;
  model_name: string;
  analysis_mode: "auto" | "regression" | "classification";
  problem_type: "regression" | "classification";
  selected_chart_types: string[];
  python_path: string;
  python_url: string;
  python_content: string;
  notebook_path: string;
  notebook_url: string;
  notebook_content: string;
  dataset_path: string;
  notes: string[];
  run_id?: string | null;
  dataset_id?: string | null;
  run_manifest?: Record<string, unknown>;
};

export type FinancialAnalysis = {
  file_name: string;
  date_column: string;
  price_column: string;
  row_count_used: number;
  latest_price: number | null;
  latest_return: number | null;
  latest_volatility: number | null;
  latest_rsi: number | null;
  latest_macd: number | null;
  latest_macd_signal: number | null;
  var_95: number | null;
  var_99: number | null;
  trend_label: string;
  summary: string[];
  forecast_points: Array<{ date: string; predicted_price: number | null }>;
  charts: GeneratedChart[];
  indicator_path: string;
  indicator_url: string;
  notes: string[];
  run_id?: string | null;
  dataset_id?: string | null;
  run_manifest?: Record<string, unknown>;
  plain_summary?: PlainSummary;
  confidence?: Confidence;
  forecast_reliability?: {
    level?: "high" | "medium" | "low" | string;
    reason?: string;
    recommended_action?: string;
    should_show_warning?: boolean;
    max_deviation_ratio?: number | null;
    forecast_label?: string;
  };
  evidence?: EvidenceItem[];
  terms?: TermDefinition[];
  chart_stories?: ChartStory[];
  research_details?: ResearchDetails;
};

export type AgentStep = {
  agent_name: string;
  status: string;
  summary: string;
  outputs: Record<string, unknown>;
};

export type AgentWorkflow = {
  file_name: string;
  target_column: string;
  agent_steps: AgentStep[];
  executive_summary: string[];
  decision_brief?: DecisionBrief;
  llm_provider: string;
  dataset_summary: Record<string, unknown>;
  model_analysis: ModelAnalysis;
  financial_analysis: FinancialAnalysis | null;
  notes: string[];
  run_id?: string | null;
  dataset_id?: string | null;
  run_manifest?: Record<string, unknown>;
};

export type DecisionBrief = {
  summary_title?: string;
  plain_language_summary?: {
    what_happened?: string;
    why_it_matters?: string;
    risks?: string;
    opportunities?: string;
    next_step?: string;
  };
  executive_summary?: string[];
  priority_findings?: Array<{
    level: string;
    label: string;
    title: string;
    summary: string;
    evidence: string;
    recommended_action: string;
  }>;
  model_guidance?: {
    problem_type?: string;
    problem_type_label?: string;
    target_column?: string;
    selection_logic?: string;
    baseline_summary?: string;
    best_model_summary?: string;
    recommended_models?: Array<{
      model_key?: string;
      model_name?: string;
      purpose?: string;
      suitable_data_types?: string[];
      difficulty?: string;
      use_cases?: string[];
      why_recommended?: string;
      expected_output?: string;
      recommendation_score?: string;
      evaluation_summary?: string;
    }>;
  };
  chart_interpretations?: ChartStory[];
  report_sections?: Array<Record<string, string>>;
  risk_and_limitations?: string[];
  ai_conclusion?: string;
};

export type GeneratedReport = {
  file_name: string;
  target_column: string;
  report_path: string;
  report_url: string;
  workflow: AgentWorkflow;
  notes: string[];
  run_id?: string | null;
  dataset_id?: string | null;
  run_manifest?: Record<string, unknown>;
};

export type AnalysisJobProgress = {
  job_id: string;
  kind: string;
  status: "queued" | "running" | "completed" | "failed" | "cancelled";
  stage: string;
  message: string;
  completed_items: number | null;
  total_items: number | null;
  elapsed_seconds: number;
  cancel_requested: boolean;
};

export type AnalysisJobOptions = {
  onProgress?: (progress: AnalysisJobProgress) => void;
  onJobCreated?: (jobId: string) => void;
};

const LOCAL_API_BASE_URL = "http://127.0.0.1:8002";

const API_BASE_URL = resolveApiBaseUrl();

const REQUEST_TIMEOUTS = {
  dataset: 90_000,
  analysis: 300_000
} as const;

type RequestJsonOptions = {
  body?: BodyInit;
  fallbackMessage: string;
  timeoutMs: number;
};

function resolveApiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "");
  if (configured) {
    return configured;
  }

  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    if (host === "localhost" || host === "127.0.0.1") {
      return LOCAL_API_BASE_URL;
    }
  }

  return "";
}

async function requestJson<T>(
  path: string,
  { body, fallbackMessage, timeoutMs }: RequestJsonOptions
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      body,
      signal: controller.signal
    });
    const payload: unknown = await response.json().catch(() => null);

    if (!response.ok) {
      const detail = extractApiErrorMessage(payload, fallbackMessage);
      throw new Error(localizeApiMessage(detail));
    }

    return payload as T;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error(clientText("分析等待時間過長，請縮小資料量後再試一次。", "The analysis took too long. Try a smaller dataset."));
    }
    if (error instanceof TypeError) {
      throw new Error(clientText("目前無法連線到分析服務，請檢查網路後重試。", "The analysis service is unavailable. Check the connection and try again."));
    }
    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }
}

function extractApiErrorMessage(payload: unknown, fallbackMessage: string): string {
  if (!payload || typeof payload !== "object" || !("detail" in payload)) {
    return fallbackMessage;
  }

  const { detail } = payload as { detail?: unknown };
  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (!item || typeof item !== "object") return null;
        const maybeMessage = "msg" in item ? (item as { msg?: unknown }).msg : null;
        return typeof maybeMessage === "string" ? maybeMessage : null;
      })
      .filter((message): message is string => Boolean(message));

    if (messages.length > 0) {
      return messages.join("；");
    }
  }

  return fallbackMessage;
}

export async function analyzeDataset(file: File): Promise<DatasetAnalysis> {
  const formData = new FormData();
  formData.append("file", file);

  return requestJson<DatasetAnalysis>("/api/datasets/analyze", {
    body: formData,
    fallbackMessage: "資料集分析失敗。",
    timeoutMs: REQUEST_TIMEOUTS.dataset
  });
}

export async function analyzeDatasets(files: File[]): Promise<MultipleDatasetAnalysis> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });

  return requestJson<MultipleDatasetAnalysis>("/api/datasets/analyze-multiple", {
    body: formData,
    fallbackMessage: "多檔資料集分析失敗。",
    timeoutMs: REQUEST_TIMEOUTS.dataset
  });
}

export async function analyzeModels(
  file: File,
  targetColumn: string,
  analysisMode: "auto" | "regression" | "classification",
  chartTypes: string[],
  modelSelectionMode: "auto" | "custom",
  selectedModels: string[],
  automlMode: "off" | "quick",
  jobOptions?: AnalysisJobOptions
): Promise<ModelAnalysis> {
  const formData = new FormData();
  formData.append("files", file);
  formData.append("target_column", targetColumn);
  formData.append("analysis_mode", analysisMode);
  formData.append("chart_types", chartTypes.join(","));
  formData.append("model_selection_mode", modelSelectionMode);
  formData.append("selected_models", selectedModels.join(",") || "auto");
  formData.append("automl_mode", automlMode);

  const result = await runAnalysisJob<ModelAnalysis>(
    "/api/jobs/models",
    formData,
    "模型分析失敗。",
    jobOptions
  );

  return withModelAnalysisUrls(result);
}

export async function analyzeMergedModels(
  files: File[],
  targetColumn: string,
  analysisMode: "auto" | "regression" | "classification",
  chartTypes: string[],
  modelSelectionMode: "auto" | "custom",
  selectedModels: string[],
  automlMode: "off" | "quick",
  jobOptions?: AnalysisJobOptions
): Promise<ModelAnalysis> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });
  formData.append("target_column", targetColumn);
  formData.append("analysis_mode", analysisMode);
  formData.append("chart_types", chartTypes.join(","));
  formData.append("model_selection_mode", modelSelectionMode);
  formData.append("selected_models", selectedModels.join(",") || "auto");
  formData.append("automl_mode", automlMode);

  const result = await runAnalysisJob<ModelAnalysis>(
    "/api/jobs/models",
    formData,
    "合併模型分析失敗。",
    jobOptions
  );

  return withModelAnalysisUrls(result);
}

export async function generateCode(
  file: File,
  targetColumn: string,
  modelName: string,
  analysisMode: "auto" | "regression" | "classification",
  chartTypes: string[]
): Promise<GeneratedCode> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("target_column", targetColumn);
  formData.append("model_name", modelName);
  formData.append("analysis_mode", analysisMode);
  formData.append("chart_types", chartTypes.join(","));

  const result = await requestJson<GeneratedCode>("/api/code/generate", {
    body: formData,
    fallbackMessage: "程式碼生成失敗。",
    timeoutMs: REQUEST_TIMEOUTS.analysis
  });

  return withGeneratedCodeUrls(result);
}

export async function generateMergedCode(
  files: File[],
  targetColumn: string,
  modelName: string,
  analysisMode: "auto" | "regression" | "classification",
  chartTypes: string[]
): Promise<GeneratedCode> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });
  formData.append("target_column", targetColumn);
  formData.append("model_name", modelName);
  formData.append("analysis_mode", analysisMode);
  formData.append("chart_types", chartTypes.join(","));

  const result = await requestJson<GeneratedCode>("/api/code/generate-merged", {
    body: formData,
    fallbackMessage: "合併資料程式碼生成失敗。",
    timeoutMs: REQUEST_TIMEOUTS.analysis
  });

  return withGeneratedCodeUrls(result);
}

export async function analyzeFinance(
  file: File,
  dateColumn?: string,
  priceColumn?: string,
  jobOptions?: AnalysisJobOptions
): Promise<FinancialAnalysis> {
  const formData = new FormData();
  formData.append("files", file);
  appendOptionalColumn(formData, "date_column", dateColumn);
  appendOptionalColumn(formData, "price_column", priceColumn);

  const result = await runAnalysisJob<FinancialAnalysis>(
    "/api/jobs/finance",
    formData,
    "金融分析失敗。",
    jobOptions
  );

  return withFinancialUrls(result);
}

export async function analyzeMergedFinance(
  files: File[],
  dateColumn?: string,
  priceColumn?: string,
  jobOptions?: AnalysisJobOptions
): Promise<FinancialAnalysis> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });
  appendOptionalColumn(formData, "date_column", dateColumn);
  appendOptionalColumn(formData, "price_column", priceColumn);

  const result = await runAnalysisJob<FinancialAnalysis>(
    "/api/jobs/finance",
    formData,
    "合併金融分析失敗。",
    jobOptions
  );

  return withFinancialUrls(result);
}

export async function runAgentWorkflow(
  file: File,
  targetColumn: string,
  analysisMode: "auto" | "regression" | "classification",
  chartTypes: string[],
  modelSelectionMode: "auto" | "custom",
  selectedModels: string[],
  automlMode: "off" | "quick",
  jobOptions?: AnalysisJobOptions
): Promise<AgentWorkflow> {
  const formData = new FormData();
  formData.append("files", file);
  appendWorkflowFields(formData, targetColumn, analysisMode, chartTypes, modelSelectionMode, selectedModels, automlMode);

  const result = await runAnalysisJob<AgentWorkflow>(
    "/api/jobs/agents",
    formData,
    "AI 協作分析失敗。",
    jobOptions
  );

  return withAgentWorkflowUrls(result);
}

export async function runMergedAgentWorkflow(
  files: File[],
  targetColumn: string,
  analysisMode: "auto" | "regression" | "classification",
  chartTypes: string[],
  modelSelectionMode: "auto" | "custom",
  selectedModels: string[],
  automlMode: "off" | "quick",
  jobOptions?: AnalysisJobOptions
): Promise<AgentWorkflow> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });
  appendWorkflowFields(formData, targetColumn, analysisMode, chartTypes, modelSelectionMode, selectedModels, automlMode);

  const result = await runAnalysisJob<AgentWorkflow>(
    "/api/jobs/agents",
    formData,
    "合併 AI 協作分析失敗。",
    jobOptions
  );

  return withAgentWorkflowUrls(result);
}

export async function generateReport(
  file: File,
  targetColumn: string,
  analysisMode: "auto" | "regression" | "classification",
  chartTypes: string[],
  modelSelectionMode: "auto" | "custom",
  selectedModels: string[],
  automlMode: "off" | "quick",
  jobOptions?: AnalysisJobOptions
): Promise<GeneratedReport> {
  const formData = new FormData();
  formData.append("files", file);
  appendWorkflowFields(formData, targetColumn, analysisMode, chartTypes, modelSelectionMode, selectedModels, automlMode);

  const result = await runAnalysisJob<GeneratedReport>(
    "/api/jobs/reports",
    formData,
    "分析報告生成失敗。",
    jobOptions
  );

  return withReportUrls(result);
}

export async function generateMergedReport(
  files: File[],
  targetColumn: string,
  analysisMode: "auto" | "regression" | "classification",
  chartTypes: string[],
  modelSelectionMode: "auto" | "custom",
  selectedModels: string[],
  automlMode: "off" | "quick",
  jobOptions?: AnalysisJobOptions
): Promise<GeneratedReport> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });
  appendWorkflowFields(formData, targetColumn, analysisMode, chartTypes, modelSelectionMode, selectedModels, automlMode);

  const result = await runAnalysisJob<GeneratedReport>(
    "/api/jobs/reports",
    formData,
    "合併分析報告生成失敗。",
    jobOptions
  );

  return withReportUrls(result);
}

function withGeneratedCodeUrls(result: GeneratedCode): GeneratedCode {
  return {
    ...result,
    python_url: `${API_BASE_URL}${result.python_url}`,
    notebook_url: `${API_BASE_URL}${result.notebook_url}`
  };
}

function withModelAnalysisUrls(result: ModelAnalysis): ModelAnalysis {
  return {
    ...result,
    chart_url: result.chart_url ? `${API_BASE_URL}${result.chart_url}` : "",
    model_results_url: `${API_BASE_URL}${result.model_results_url}`,
    cleaned_dataset_url: `${API_BASE_URL}${result.cleaned_dataset_url}`,
    model_results: result.model_results.map((metric) => ({
      ...metric,
      model_url: `${API_BASE_URL}${metric.model_url}`
    })),
    charts: result.charts.map((chart) => ({
      ...chart,
      chart_url: `${API_BASE_URL}${chart.chart_url}`
    }))
  };
}

function withFinancialUrls(result: FinancialAnalysis): FinancialAnalysis {
  return {
    ...result,
    indicator_url: `${API_BASE_URL}${result.indicator_url}`,
    charts: result.charts.map((chart) => ({
      ...chart,
      chart_url: `${API_BASE_URL}${chart.chart_url}`
    }))
  };
}

function withAgentWorkflowUrls(result: AgentWorkflow): AgentWorkflow {
  return {
    ...result,
    model_analysis: withModelAnalysisUrls(result.model_analysis),
    financial_analysis: result.financial_analysis
      ? withFinancialUrls(result.financial_analysis)
      : null
  };
}

function withReportUrls(result: GeneratedReport): GeneratedReport {
  return {
    ...result,
    report_url: `${API_BASE_URL}${result.report_url}`,
    workflow: withAgentWorkflowUrls(result.workflow)
  };
}

function appendWorkflowFields(
  formData: FormData,
  targetColumn: string,
  analysisMode: "auto" | "regression" | "classification",
  chartTypes: string[],
  modelSelectionMode: "auto" | "custom",
  selectedModels: string[],
  automlMode: "off" | "quick"
) {
  formData.append("target_column", targetColumn);
  formData.append("analysis_mode", analysisMode);
  formData.append("chart_types", chartTypes.join(","));
  formData.append("model_selection_mode", modelSelectionMode);
  formData.append("selected_models", selectedModels.join(",") || "auto");
  formData.append("automl_mode", automlMode);
}

function appendOptionalColumn(formData: FormData, key: string, value?: string) {
  if (value && value !== "__auto__") {
    formData.append(key, value);
  }
}

export async function cancelAnalysisJob(jobId: string) {
  const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`, {
    method: "DELETE"
  });
  if (!response.ok) {
    throw new Error(clientText("無法取消目前分析。", "Unable to cancel the current analysis."));
  }
}

async function runAnalysisJob<T>(
  path: string,
  formData: FormData,
  fallbackMessage: string,
  options?: AnalysisJobOptions
): Promise<T> {
  const started = await requestJson<{
    job_id: string;
    status: string;
    stage: string;
  }>(path, {
    body: formData,
    fallbackMessage,
    timeoutMs: REQUEST_TIMEOUTS.dataset
  });
  options?.onJobCreated?.(started.job_id);
  const deadline = Date.now() + REQUEST_TIMEOUTS.analysis;

  while (Date.now() < deadline) {
    const response = await fetch(`${API_BASE_URL}/api/jobs/${started.job_id}`, {
      method: "GET",
      cache: "no-store"
    });
    const payload = (await response.json().catch(() => null)) as
      | (AnalysisJobProgress & {
          result: T | null;
          error: string | null;
        })
      | null;

    if (!response.ok || !payload) {
      throw new Error(clientText("無法取得分析進度。", "Unable to retrieve analysis progress."));
    }

    options?.onProgress?.(payload);
    if (payload.status === "completed" && payload.result) {
      return payload.result;
    }
    if (payload.status === "failed") {
      throw new Error(localizeApiMessage(payload.error || fallbackMessage));
    }
    if (payload.status === "cancelled") {
      throw new Error(clientText("分析已取消。", "Analysis cancelled."));
    }

    await new Promise((resolve) => window.setTimeout(resolve, 450));
  }

  throw new Error(clientText("分析等待時間過長，請稍後重試。", "The analysis took too long. Please try again."));
}

function clientText(traditionalChinese: string, english: string) {
  return document.documentElement.lang === "en" ? english : traditionalChinese;
}

function localizeApiMessage(message: string) {
  if (document.documentElement.lang !== "en") return message;
  const messages: Record<string, string> = {
    "分析已取消。": "Analysis cancelled.",
    "請先選擇目標欄位。": "Choose a target column first.",
    "指定的目標欄位不存在。": "The selected target column does not exist.",
    "目標欄位全部都是缺失值，無法訓練模型。":
      "The target column contains only missing values.",
    "除了目標欄位外沒有可用特徵。":
      "No usable features remain after excluding the target.",
    "資料列太少，至少需要 5 筆有效資料才能訓練模型。":
      "At least five valid rows are required to train models.",
    "金融分析至少需要 6 筆有效日期與價格資料。":
      "Financial analysis requires at least six valid date and price rows.",
    "金融分析至少需要 6 筆有效日期與價格/指數/數值資料。":
      "Financial analysis requires at least six valid date and price / index / value rows.",
    "指定的價格/指數/數值欄位不存在。":
      "The selected price / index / value column does not exist.",
    "指定的價格/指數/數值欄位無法有效轉換為數值。":
      "The selected price / index / value column cannot be converted into enough numeric values.",
    "無法自動偵測價格/指數/數值欄位，請手動指定可轉換為數值的欄位。":
      "Unable to detect a price / index / value column. Choose a numeric column manually.",
    "伺服器暫時無法完成分析，請稍後再試。":
      "The server could not complete the analysis. Please try again."
  };
  return messages[message] ?? message;
}
