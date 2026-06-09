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

export type DatasetAnalysis = {
  file_name: string;
  row_count: number;
  column_count: number;
  columns: string[];
  data_types: Record<string, string>;
  missing_values: Record<string, number>;
  numeric_summary: NumericSummary;
  recommended_target_columns?: string[];
};

export type MergedDatasetAnalysis = DatasetAnalysis & {
  source_files: string[];
  source_file_count: number;
  source_row_counts: Record<string, number>;
  merge_strategy: string;
  merge_notes: string[];
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
  llm_provider: string;
  dataset_summary: Record<string, unknown>;
  model_analysis: ModelAnalysis;
  financial_analysis: FinancialAnalysis | null;
  notes: string[];
};

export type GeneratedReport = {
  file_name: string;
  target_column: string;
  report_path: string;
  report_url: string;
  workflow: AgentWorkflow;
  notes: string[];
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "";

export async function analyzeDataset(file: File): Promise<DatasetAnalysis> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/datasets/analyze`, {
    method: "POST",
    body: formData
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      payload && typeof payload.detail === "string"
        ? payload.detail
        : "資料集分析失敗。";
    throw new Error(detail);
  }

  return payload as DatasetAnalysis;
}

export async function analyzeDatasets(files: File[]): Promise<MultipleDatasetAnalysis> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });

  const response = await fetch(`${API_BASE_URL}/api/datasets/analyze-multiple`, {
    method: "POST",
    body: formData
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      payload && typeof payload.detail === "string"
        ? payload.detail
        : "多檔資料集分析失敗。";
    throw new Error(detail);
  }

  return payload as MultipleDatasetAnalysis;
}

export async function analyzeModels(
  file: File,
  targetColumn: string,
  analysisMode: "auto" | "regression" | "classification",
  chartTypes: string[],
  modelSelectionMode: "auto" | "custom",
  selectedModels: string[],
  automlMode: "off" | "quick"
): Promise<ModelAnalysis> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("target_column", targetColumn);
  formData.append("analysis_mode", analysisMode);
  formData.append("chart_types", chartTypes.join(","));
  formData.append("model_selection_mode", modelSelectionMode);
  formData.append("selected_models", selectedModels.join(",") || "auto");
  formData.append("automl_mode", automlMode);

  const response = await fetch(`${API_BASE_URL}/api/models/analyze`, {
    method: "POST",
    body: formData
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      payload && typeof payload.detail === "string"
        ? payload.detail
        : "模型分析失敗。";
    throw new Error(detail);
  }

  const result = payload as ModelAnalysis;

  return withModelAnalysisUrls(result);
}

export async function analyzeMergedModels(
  files: File[],
  targetColumn: string,
  analysisMode: "auto" | "regression" | "classification",
  chartTypes: string[],
  modelSelectionMode: "auto" | "custom",
  selectedModels: string[],
  automlMode: "off" | "quick"
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

  const response = await fetch(`${API_BASE_URL}/api/models/analyze-merged`, {
    method: "POST",
    body: formData
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      payload && typeof payload.detail === "string"
        ? payload.detail
        : "合併模型分析失敗。";
    throw new Error(detail);
  }

  const result = payload as ModelAnalysis;

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

  const response = await fetch(`${API_BASE_URL}/api/code/generate`, {
    method: "POST",
    body: formData
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      payload && typeof payload.detail === "string"
        ? payload.detail
        : "程式碼生成失敗。";
    throw new Error(detail);
  }

  return withGeneratedCodeUrls(payload as GeneratedCode);
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

  const response = await fetch(`${API_BASE_URL}/api/code/generate-merged`, {
    method: "POST",
    body: formData
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      payload && typeof payload.detail === "string"
        ? payload.detail
        : "合併資料程式碼生成失敗。";
    throw new Error(detail);
  }

  return withGeneratedCodeUrls(payload as GeneratedCode);
}

export async function analyzeFinance(
  file: File,
  dateColumn?: string,
  priceColumn?: string
): Promise<FinancialAnalysis> {
  const formData = new FormData();
  formData.append("file", file);
  appendOptionalColumn(formData, "date_column", dateColumn);
  appendOptionalColumn(formData, "price_column", priceColumn);

  const response = await fetch(`${API_BASE_URL}/api/finance/analyze`, {
    method: "POST",
    body: formData
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      payload && typeof payload.detail === "string"
        ? payload.detail
        : "金融分析失敗。";
    throw new Error(detail);
  }

  return withFinancialUrls(payload as FinancialAnalysis);
}

export async function analyzeMergedFinance(
  files: File[],
  dateColumn?: string,
  priceColumn?: string
): Promise<FinancialAnalysis> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });
  appendOptionalColumn(formData, "date_column", dateColumn);
  appendOptionalColumn(formData, "price_column", priceColumn);

  const response = await fetch(`${API_BASE_URL}/api/finance/analyze-merged`, {
    method: "POST",
    body: formData
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      payload && typeof payload.detail === "string"
        ? payload.detail
        : "合併金融分析失敗。";
    throw new Error(detail);
  }

  return withFinancialUrls(payload as FinancialAnalysis);
}

export async function runAgentWorkflow(
  file: File,
  targetColumn: string,
  analysisMode: "auto" | "regression" | "classification",
  chartTypes: string[],
  modelSelectionMode: "auto" | "custom",
  selectedModels: string[],
  automlMode: "off" | "quick"
): Promise<AgentWorkflow> {
  const formData = new FormData();
  formData.append("file", file);
  appendWorkflowFields(formData, targetColumn, analysisMode, chartTypes, modelSelectionMode, selectedModels, automlMode);

  const response = await fetch(`${API_BASE_URL}/api/agents/analyze`, {
    method: "POST",
    body: formData
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      payload && typeof payload.detail === "string"
        ? payload.detail
        : "AI 協作分析失敗。";
    throw new Error(detail);
  }

  return withAgentWorkflowUrls(payload as AgentWorkflow);
}

export async function runMergedAgentWorkflow(
  files: File[],
  targetColumn: string,
  analysisMode: "auto" | "regression" | "classification",
  chartTypes: string[],
  modelSelectionMode: "auto" | "custom",
  selectedModels: string[],
  automlMode: "off" | "quick"
): Promise<AgentWorkflow> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });
  appendWorkflowFields(formData, targetColumn, analysisMode, chartTypes, modelSelectionMode, selectedModels, automlMode);

  const response = await fetch(`${API_BASE_URL}/api/agents/analyze-merged`, {
    method: "POST",
    body: formData
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      payload && typeof payload.detail === "string"
        ? payload.detail
        : "合併 AI 協作分析失敗。";
    throw new Error(detail);
  }

  return withAgentWorkflowUrls(payload as AgentWorkflow);
}

export async function generateReport(
  file: File,
  targetColumn: string,
  analysisMode: "auto" | "regression" | "classification",
  chartTypes: string[],
  modelSelectionMode: "auto" | "custom",
  selectedModels: string[],
  automlMode: "off" | "quick"
): Promise<GeneratedReport> {
  const formData = new FormData();
  formData.append("file", file);
  appendWorkflowFields(formData, targetColumn, analysisMode, chartTypes, modelSelectionMode, selectedModels, automlMode);

  const response = await fetch(`${API_BASE_URL}/api/reports/generate`, {
    method: "POST",
    body: formData
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      payload && typeof payload.detail === "string"
        ? payload.detail
        : "分析報告生成失敗。";
    throw new Error(detail);
  }

  return withReportUrls(payload as GeneratedReport);
}

export async function generateMergedReport(
  files: File[],
  targetColumn: string,
  analysisMode: "auto" | "regression" | "classification",
  chartTypes: string[],
  modelSelectionMode: "auto" | "custom",
  selectedModels: string[],
  automlMode: "off" | "quick"
): Promise<GeneratedReport> {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file);
  });
  appendWorkflowFields(formData, targetColumn, analysisMode, chartTypes, modelSelectionMode, selectedModels, automlMode);

  const response = await fetch(`${API_BASE_URL}/api/reports/generate-merged`, {
    method: "POST",
    body: formData
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const detail =
      payload && typeof payload.detail === "string"
        ? payload.detail
        : "合併分析報告生成失敗。";
    throw new Error(detail);
  }

  return withReportUrls(payload as GeneratedReport);
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
