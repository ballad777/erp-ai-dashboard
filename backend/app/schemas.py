from pydantic import BaseModel, Field


class DatasetAnalysisResponse(BaseModel):
    file_name: str = Field(..., examples=["housing_sample.csv"])
    row_count: int = Field(..., ge=0)
    column_count: int = Field(..., ge=0)
    columns: list[str]
    data_types: dict[str, str]
    missing_values: dict[str, int]
    numeric_summary: dict[str, dict[str, float | int | None]]
    recommended_target_columns: list[str] = Field(default_factory=list)


class MergedDatasetAnalysisResponse(DatasetAnalysisResponse):
    source_files: list[str]
    source_file_count: int
    source_row_counts: dict[str, int]
    merge_strategy: str
    merge_notes: list[str]
    source_file_column: str
    source_row_column: str
    common_columns: list[str]


class DatasetBatchItem(BaseModel):
    file_name: str
    success: bool
    analysis: DatasetAnalysisResponse | None = None
    error: str | None = None


class MultipleDatasetAnalysisResponse(BaseModel):
    datasets: list[DatasetBatchItem]
    merged: MergedDatasetAnalysisResponse | None = None
    notes: list[str]


class ErrorResponse(BaseModel):
    detail: str


class ModelMetric(BaseModel):
    model_key: str
    model_name: str
    model_family: str
    r2: float
    rmse: float
    mae: float
    training_time_seconds: float
    accuracy: float | None = None
    f1_score: float | None = None
    automl_best_params: dict[str, object] = Field(default_factory=dict)
    model_path: str
    model_url: str


class ModelOption(BaseModel):
    key: str
    label: str
    problem_type: str
    family: str
    description: str
    complexity: str


class GeneratedChart(BaseModel):
    chart_type: str
    title: str
    chart_path: str
    chart_url: str


class ModelAnalysisResponse(BaseModel):
    file_name: str
    target_column: str
    analysis_mode: str
    problem_type: str
    row_count_used: int
    feature_count_used: int
    model_results: list[ModelMetric]
    model_selection_mode: str
    automl_mode: str
    selected_model_keys: list[str]
    available_models: list[ModelOption]
    recommended_models: list[ModelOption]
    model_results_path: str
    model_results_url: str
    cleaned_dataset_path: str
    cleaned_dataset_url: str
    chart_path: str
    chart_url: str
    charts: list[GeneratedChart]
    selected_chart_types: list[str]
    notes: list[str]


class GeneratedCodeResponse(BaseModel):
    file_name: str
    target_column: str
    model_name: str
    analysis_mode: str
    problem_type: str
    selected_chart_types: list[str]
    python_path: str
    python_url: str
    python_content: str
    notebook_path: str
    notebook_url: str
    notebook_content: str
    dataset_path: str
    notes: list[str]


class FinancialAnalysisResponse(BaseModel):
    file_name: str
    date_column: str
    price_column: str
    row_count_used: int
    latest_price: float | None = None
    latest_return: float | None = None
    latest_volatility: float | None = None
    latest_rsi: float | None = None
    latest_macd: float | None = None
    latest_macd_signal: float | None = None
    var_95: float | None = None
    var_99: float | None = None
    trend_label: str
    summary: list[str]
    forecast_points: list[dict[str, float | str | None]]
    charts: list[GeneratedChart]
    indicator_path: str
    indicator_url: str
    notes: list[str]


class AgentStepResponse(BaseModel):
    agent_name: str
    status: str
    summary: str
    outputs: dict[str, object] = Field(default_factory=dict)


class AgentWorkflowResponse(BaseModel):
    file_name: str
    target_column: str
    agent_steps: list[AgentStepResponse]
    executive_summary: list[str]
    llm_provider: str
    dataset_summary: dict[str, object]
    model_analysis: ModelAnalysisResponse
    financial_analysis: FinancialAnalysisResponse | None = None
    notes: list[str]


class ReportResponse(BaseModel):
    file_name: str
    target_column: str
    report_path: str
    report_url: str
    workflow: AgentWorkflowResponse
    notes: list[str]
