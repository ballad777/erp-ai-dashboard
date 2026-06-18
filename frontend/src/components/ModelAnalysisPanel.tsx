"use client";

import { useEffect, useId, useMemo, useRef, useState } from "react";
import {
  BarChart3,
  Check,
  ChevronDown,
  Download,
  Play,
  Trophy
} from "lucide-react";
import { AnalysisModeSelector } from "@/components/analysis/AnalysisModeSelector";
import { AnalysisRecommendationPanel } from "@/components/analysis/AnalysisRecommendationPanel";
import { InlineCodeViewer } from "@/components/analysis/InlineCodeViewer";
import { AnalysisStepRail, type AnalysisWorkspaceStep } from "@/components/analysis/AnalysisStepRail";
import { DatasetMetricStrip } from "@/components/analysis/DatasetMetricStrip";
import { ModelSelectionDrawer } from "@/components/analysis/ModelSelectionDrawer";
import { useFeedback } from "@/components/FeedbackProvider";
import {
  ChartStoryPanel,
  EvidenceList,
  InsightHeadline,
  MetricExplainer,
  PlainSummaryGrid,
  ResearchDetailsDrawer,
  useReadingDepth
} from "@/components/InsightExplainers";
import { useLocale } from "@/components/LocaleProvider";
import {
  AnalysisLoadingState,
  InlineNotice,
  ResultReveal
} from "@/components/PagePrimitives";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  useWorkspacePanelState,
  workspaceSourceKey
} from "@/components/WorkspaceProvider";
import {
  analyzeMergedModels,
  analyzeModels,
  cancelAnalysisJob,
  generateCode,
  generateMergedCode,
  type AnalysisJobProgress,
  type DatasetAnalysis,
  type GeneratedCode,
  type ModelAnalysis
} from "@/lib/api";

type AnalysisMode = "auto" | "regression" | "classification";
type ChartSelectionMode = "auto" | "custom";
type ModelSelectionMode = "auto" | "custom";
type AutoMLMode = "off" | "quick";

type ModelAnalysisPanelProps = {
  dataset: DatasetAnalysis;
  file?: File;
  files?: File[];
  title?: string;
  description?: string;
  isMerged?: boolean;
};

const chartOptions = [
  { value: "model_comparison", label: "模型比較圖" },
  { value: "feature_importance", label: "特徵重要性" },
  { value: "predicted_vs_actual", label: "預測值與實際值" },
  { value: "residual_plot", label: "殘差圖" }
];

const modelOptions = [
  {
    key: "linear_regression",
    label: "線性迴歸",
    problemType: "regression",
    description: "快速可解釋的回歸基準。"
  },
  {
    key: "ridge",
    label: "Ridge 迴歸",
    problemType: "regression",
    description: "適合共線性較高的中小型資料。"
  },
  {
    key: "lasso",
    label: "Lasso 迴歸",
    problemType: "regression",
    description: "具備特徵篩選效果。"
  },
  {
    key: "elastic_net",
    label: "ElasticNet 迴歸",
    problemType: "regression",
    description: "結合 Ridge 與 Lasso 的穩健線性模型。"
  },
  {
    key: "decision_tree_regressor",
    label: "決策樹迴歸",
    problemType: "regression",
    description: "探索非線性規則與局部決策。"
  },
  {
    key: "random_forest",
    label: "隨機森林",
    problemType: "regression",
    description: "穩健的表格資料非線性模型。"
  },
  {
    key: "extra_trees_regressor",
    label: "Extra Trees 迴歸",
    problemType: "regression",
    description: "強隨機化集成模型。"
  },
  {
    key: "gradient_boosting_regressor",
    label: "Gradient Boosting 迴歸",
    problemType: "regression",
    description: "中小型資料常見高精度模型。"
  },
  {
    key: "xgboost_regressor",
    label: "XGBoost 迴歸",
    problemType: "regression",
    description: "高效梯度提升回歸模型。"
  },
  {
    key: "lightgbm_regressor",
    label: "LightGBM 迴歸",
    problemType: "regression",
    description: "輕量化梯度提升回歸模型。"
  },
  {
    key: "knn_regressor",
    label: "KNN 迴歸",
    problemType: "regression",
    description: "低維度平滑資料的鄰近推估。"
  },
  {
    key: "svr",
    label: "SVR 支援向量迴歸",
    problemType: "regression",
    description: "非線性低維資料探索。"
  },
  {
    key: "logistic_regression",
    label: "Logistic Regression",
    problemType: "classification",
    description: "快速可解釋的分類基準。"
  },
  {
    key: "decision_tree_classifier",
    label: "決策樹分類",
    problemType: "classification",
    description: "可解釋的非線性分類規則。"
  },
  {
    key: "random_forest_classifier",
    label: "隨機森林分類",
    problemType: "classification",
    description: "穩健表格資料分類模型。"
  },
  {
    key: "extra_trees_classifier",
    label: "Extra Trees 分類",
    problemType: "classification",
    description: "檢查分類特徵穩定性。"
  },
  {
    key: "gradient_boosting_classifier",
    label: "Gradient Boosting 分類",
    problemType: "classification",
    description: "逐步修正分類錯誤。"
  },
  {
    key: "xgboost_classifier",
    label: "XGBoost 分類",
    problemType: "classification",
    description: "高效梯度提升分類模型。"
  },
  {
    key: "lightgbm_classifier",
    label: "LightGBM 分類",
    problemType: "classification",
    description: "輕量化梯度提升分類模型。"
  },
  {
    key: "knn_classifier",
    label: "KNN 分類",
    problemType: "classification",
    description: "低維度平滑邊界分類。"
  },
  {
    key: "svc",
    label: "SVC 支援向量分類",
    problemType: "classification",
    description: "非線性分類邊界探索。"
  }
] as const;

export function ModelAnalysisPanel({
  dataset,
  file,
  files = [],
  title = "模型分析與圖表產出",
  description,
  isMerged = false
}: ModelAnalysisPanelProps) {
  const { isEnglish, text } = useLocale();
  const { playError, playSuccess } = useFeedback();
  const recommendedTargets = dataset.recommended_target_columns ?? [];
  const defaultTarget =
    recommendedTargets.find((column) => dataset.columns.includes(column)) ??
    dataset.columns[dataset.columns.length - 1] ??
    "";
  const sourceKey = workspaceSourceKey(file, files, isMerged);
  const [targetColumn, setTargetColumn] = useWorkspacePanelState(
    `${sourceKey}:model:target`,
    defaultTarget
  );
  const [analysisMode, setAnalysisMode] = useWorkspacePanelState<AnalysisMode>(
    `${sourceKey}:model:analysis-mode`,
    "auto"
  );
  const [chartSelectionMode, setChartSelectionMode] =
    useWorkspacePanelState<ChartSelectionMode>(
      `${sourceKey}:model:chart-selection`,
      "auto"
    );
  const [modelSelectionMode, setModelSelectionMode] =
    useWorkspacePanelState<ModelSelectionMode>(
      `${sourceKey}:model:model-selection`,
      "auto"
    );
  const [automlMode, setAutomlMode] = useWorkspacePanelState<AutoMLMode>(
    `${sourceKey}:model:automl`,
    "quick"
  );
  const [selectedModels, setSelectedModels] = useWorkspacePanelState<string[]>(
    `${sourceKey}:model:selected-models`,
    ["ridge", "random_forest", "gradient_boosting_regressor"]
  );
  const [selectedCharts, setSelectedCharts] = useWorkspacePanelState<string[]>(
    `${sourceKey}:model:selected-charts`,
    ["model_comparison", "feature_importance", "predicted_vs_actual"]
  );
  const [result, setResult] = useWorkspacePanelState<ModelAnalysis | null>(
    `${sourceKey}:model:result`,
    null
  );
  const [error, setError] = useWorkspacePanelState<string | null>(
    `${sourceKey}:model:error`,
    null
  );
  const [isLoading, setIsLoading] = useWorkspacePanelState(
    `${sourceKey}:model:loading`,
    false
  );
  const [jobProgress, setJobProgress] = useState<AnalysisJobProgress | null>(null);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [isCancelling, setIsCancelling] = useState(false);

  const visibleModelOptions = useMemo(() => {
    if (analysisMode === "auto") {
      return modelOptions;
    }
    return modelOptions.filter((option) => option.problemType === analysisMode);
  }, [analysisMode]);
  const localizedChartOptions = chartOptions.map((option) => ({
    ...option,
    label:
      option.value === "model_comparison"
        ? text("模型比較圖", "Model comparison")
        : option.value === "feature_importance"
          ? text("特徵重要性", "Feature importance")
          : option.value === "predicted_vs_actual"
            ? text("預測值與實際值", "Predicted vs actual")
            : text("殘差圖", "Residual plot")
  }));

  const featureCount = useMemo(
    () => Math.max(dataset.columns.length - (targetColumn ? 1 : 0), 0),
    [dataset.columns.length, targetColumn]
  );
  const workspaceStep: AnalysisWorkspaceStep = result
    ? "result"
    : isLoading
      ? "running"
      : "method";
  const runDisabledReason =
    !targetColumn
      ? text("請先選擇目標欄位", "Choose a target column first")
      : modelSelectionMode === "custom" && selectedModels.length === 0
        ? text("請至少選擇一個模型", "Choose at least one model")
        : chartSelectionMode === "custom" && selectedCharts.length === 0
          ? text("請至少選擇一張圖表", "Choose at least one chart")
          : null;
  const drawerModelOptions = visibleModelOptions.map((option) => ({
    ...option,
    description: isEnglish ? modelDescriptionEnglish(option.key) : option.description
  }));

  useEffect(() => {
    if (analysisMode === "auto") {
      return;
    }

    setSelectedModels((current) => {
      const compatible = current.filter((modelKey) =>
        visibleModelOptions.some((option) => option.key === modelKey)
      );
      if (compatible.length > 0) {
        return compatible;
      }
      return visibleModelOptions.slice(0, 3).map((option) => option.key);
    });
  }, [analysisMode, visibleModelOptions]);

  async function handleRunModels() {
    if (!targetColumn) {
      setError(text("請先選擇目標欄位。", "Choose a target column first."));
      return;
    }

    if (chartSelectionMode === "custom" && selectedCharts.length === 0) {
      setError(text("請至少選擇一種要產出的圖表。", "Choose at least one chart."));
      return;
    }

    if (modelSelectionMode === "custom" && selectedModels.length === 0) {
      setError(text("請至少選擇一個要執行的模型。", "Choose at least one model."));
      return;
    }

    if (isMerged && files.length < 2) {
      setError(text("合併模型分析至少需要 2 個成功讀取的檔案。", "Merged model analysis needs at least two successfully ingested files."));
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);
    setJobProgress(null);
    setActiveJobId(null);

    const startedAt = performance.now();
    try {
      const requestedCharts =
        chartSelectionMode === "auto" ? ["auto"] : selectedCharts;
      const requestedModels =
        modelSelectionMode === "auto" ? ["auto"] : selectedModels;
      const modelAnalysis = isMerged
        ? await analyzeMergedModels(
            files,
            targetColumn,
            analysisMode,
            requestedCharts,
            modelSelectionMode,
            requestedModels,
            automlMode,
            {
              onProgress: setJobProgress,
              onJobCreated: setActiveJobId
            }
          )
        : await analyzeModels(
            assertSingleFile(file),
            targetColumn,
            analysisMode,
            requestedCharts,
            modelSelectionMode,
            requestedModels,
            automlMode,
            {
              onProgress: setJobProgress,
              onJobCreated: setActiveJobId
            }
          );
      setResult(modelAnalysis);
      if (performance.now() - startedAt >= 3000) playSuccess();
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : text("模型分析失敗。", "Model analysis failed.");
      setError(message);
      if (!isCancellationMessage(message)) playError();
    } finally {
      setIsLoading(false);
      setActiveJobId(null);
    }
  }

  async function handleCancelAnalysis() {
    if (!activeJobId) return;
    setIsCancelling(true);
    try {
      await cancelAnalysisJob(activeJobId);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : text("無法取消目前分析。", "Unable to cancel the current analysis.")
      );
    } finally {
      setIsCancelling(false);
    }
  }

  function toggleChart(chartType: string) {
    setResult(null);
    setSelectedCharts((current) =>
      current.includes(chartType)
        ? current.filter((item) => item !== chartType)
        : [...current, chartType]
    );
  }

  function toggleModel(modelKey: string) {
    setResult(null);
    setSelectedModels((current) =>
      current.includes(modelKey)
        ? current.filter((item) => item !== modelKey)
        : [...current, modelKey]
    );
  }

  return (
    <section className="analysis-focus-workspace" aria-busy={isLoading}>
      <div className="analysis-focus-header">
        <div>
          <h2>
            {isEnglish && title === "模型分析與圖表產出"
              ? "Choose an analysis approach"
              : title}
          </h2>
          <p className="ui-copy-secondary">
            {description ??
              text(
                "先確認目標與方法，系統再依真實資料選出候選模型。",
                "Confirm the target and approach before the system selects candidates from the real dataset."
              )}
          </p>
        </div>
      </div>

      <AnalysisStepRail current={workspaceStep} />

      <div className="analysis-focus-grid">
        <div className="analysis-primary-stage">
          <label>
            <span className="ui-copy-primary text-base font-semibold">
              {text("目標欄位", "Target column")}
            </span>
            <select
              name="model-target-column"
              autoComplete="off"
              value={targetColumn}
              onChange={(event) => {
                setTargetColumn(event.target.value);
                setResult(null);
                setError(null);
              }}
            >
              {dataset.columns.map((column) => (
                <option key={column} value={column}>
                  {column}
                </option>
              ))}
            </select>
          </label>

          {recommendedTargets.length > 0 ? (
            <div className="recommended-targets">
              <span>{text("建議目標欄位", "Suggested targets")}</span>
              <div>
                {recommendedTargets.map((column) => (
                  <button
                    key={column}
                    type="button"
                    aria-pressed={targetColumn === column}
                    onClick={() => {
                      setTargetColumn(column);
                      setResult(null);
                      setError(null);
                    }}
                  >
                    {column}
                  </button>
                ))}
              </div>
            </div>
          ) : null}

          <AnalysisModeSelector
            value={analysisMode}
            onChange={(value) => {
              setAnalysisMode(value);
              setResult(null);
              setError(null);
            }}
          />

          <DatasetMetricStrip
            rows={dataset.row_count}
            features={featureCount}
            models={visibleModelOptions.length}
          />

          <section className="analysis-strategy-card" aria-label={text("模型策略", "Model strategy")}>
            <div>
              <span>{text("模型策略", "Model strategy")}</span>
              <strong>
                {modelSelectionMode === "auto"
                  ? text("由系統自動推薦模型", "Let the system recommend models")
                  : text("手動選擇要執行的模型", "Choose models manually")}
              </strong>
            </div>
            <div className="analysis-segmented-control">
              <button
                type="button"
                aria-pressed={modelSelectionMode === "auto"}
                onClick={() => {
                  setModelSelectionMode("auto");
                  setResult(null);
                  setError(null);
                }}
              >
                {text("自動推薦模型", "Recommend models")}
              </button>
              <button
                type="button"
                aria-pressed={modelSelectionMode === "custom"}
                onClick={() => {
                  setModelSelectionMode("custom");
                  setResult(null);
                  setError(null);
                }}
              >
                {text("手動選擇模型", "Choose models manually")}
              </button>
            </div>
            {modelSelectionMode === "auto" ? (
              <p className="ui-copy-secondary">
                {text(
                  "自動模式會依資料列數、特徵數、欄位型態、缺失比例與問題類型，選出適合的模型組合。",
                  "Automatic mode uses row count, feature count, column types, missingness, and problem type to select suitable models."
                )}
              </p>
            ) : null}
          </section>

          <ModelSelectionDrawer
            open={modelSelectionMode === "custom"}
            options={drawerModelOptions}
            selected={selectedModels}
            onToggle={toggleModel}
            onClear={() => {
              setResult(null);
              setSelectedModels([]);
            }}
          />

          <details className="advanced-settings">
            <summary>
              <span>
                <strong>{text("進階設定", "Advanced settings")}</strong>
                <small>{text("AutoML、圖表與輸出控制", "AutoML, charts, and output controls")}</small>
              </span>
              <ChevronDown aria-hidden="true" />
            </summary>
            <div className="advanced-settings-content">
              <fieldset className="strategy-fieldset">
                <legend className="text-base font-semibold text-ink">
                  {text("AutoML 調參", "AutoML tuning")}
                </legend>
                <div className="mt-3 grid gap-3 md:grid-cols-2">
                  {[
                    {
                      value: "quick" as AutoMLMode,
                      label: "Quick AutoML",
                      body: text(
                        "對支援模型執行小型參數搜尋，回傳最佳參數。",
                        "Run a small parameter search for supported models and return the best settings."
                      )
                    },
                    {
                      value: "off" as AutoMLMode,
                      label: text("關閉調參", "Disable tuning"),
                      body: text(
                        "使用模型預設參數，速度較快。",
                        "Use model defaults for a faster run."
                      )
                    }
                  ].map((mode) => (
                    <label
                      key={mode.value}
                      className={`rounded-md border p-4 transition ${
                        automlMode === mode.value
                          ? "border-navy bg-blue-50"
                          : "border-line bg-slate-50 hover:border-navy"
                      }`}
                    >
                      <input
                        type="radio"
                        name={`${dataset.file_name}-automl-mode`}
                        value={mode.value}
                        checked={automlMode === mode.value}
                        onChange={() => {
                          setAutomlMode(mode.value);
                          setResult(null);
                          setError(null);
                        }}
                        className="mr-2"
                      />
                      <span className="text-base font-semibold text-ink">
                        {mode.label}
                      </span>
                      <p className="ui-option-description mt-2 text-sm leading-6">
                        {mode.body}
                      </p>
                    </label>
                  ))}
                </div>
              </fieldset>

              <fieldset className="strategy-fieldset">
                <legend className="text-base font-semibold text-ink">
                  {text("圖表產出", "Chart output")}
                </legend>
                <div className="mt-3 flex flex-wrap gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setChartSelectionMode("auto");
                      setResult(null);
                      setError(null);
                    }}
                    className={`h-11 rounded-md border px-4 text-base font-semibold transition ${
                      chartSelectionMode === "auto"
                        ? "border-brand bg-brand text-white"
                        : "border-line bg-white text-ink hover:border-brand"
                    }`}
                  >
                    {text("自動選最適合圖表", "Select suitable charts")}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setChartSelectionMode("custom");
                      setResult(null);
                      setError(null);
                    }}
                    className={`h-11 rounded-md border px-4 text-base font-semibold transition ${
                      chartSelectionMode === "custom"
                        ? "border-brand bg-brand text-white"
                        : "border-line bg-white text-ink hover:border-brand"
                    }`}
                  >
                    {text("手動選擇圖表", "Choose charts manually")}
                  </button>
                </div>

                {chartSelectionMode === "custom" ? (
                  <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                    {localizedChartOptions.map((option) => (
                      <label
                        key={option.value}
                        className={`flex min-h-12 items-center rounded-md border px-4 py-3 text-base font-medium transition ${
                          selectedCharts.includes(option.value)
                            ? "border-navy bg-blue-50 text-ink"
                            : "border-line bg-white text-ink hover:border-navy"
                        }`}
                      >
                        <input
                          type="checkbox"
                          name="selected-charts"
                          value={option.value}
                          checked={selectedCharts.includes(option.value)}
                          onChange={() => toggleChart(option.value)}
                          className="mr-3 h-4 w-4"
                        />
                        {option.label}
                      </label>
                    ))}
                  </div>
                ) : (
                  <p className="analysis-surface-card ui-copy-secondary mt-4 p-4 text-base leading-7">
                    {text(
                      "自動模式會依問題型態與欄位組成產出模型比較、特徵重要性、預測值與實際值；回歸問題會再加入殘差圖。",
                      "Automatic mode chooses model comparison, feature importance, and predicted-versus-actual charts, then adds a residual plot for regression."
                    )}
                  </p>
                )}
              </fieldset>
            </div>
          </details>

          <div className="analysis-next-action">
            <div>
              <span>{text("清楚的下一步", "A clear next step")}</span>
              <strong>
                {runDisabledReason ??
                  text("開始比較候選模型", "Start comparing candidate models")}
              </strong>
              {runDisabledReason ? (
                <p id="analysis-run-disabled-reason" className="ui-copy-secondary">
                  {runDisabledReason}
                </p>
              ) : null}
            </div>
            <Button
              type="button"
              onClick={handleRunModels}
              disabled={Boolean(runDisabledReason) || isLoading}
              aria-describedby={
                runDisabledReason ? "analysis-run-disabled-reason" : undefined
              }
              variant="premium"
              size="lg"
            >
              {isLoading ? <Spinner /> : <Play aria-hidden="true" />}
              {isLoading
                ? text("模型執行中", "Running models")
                : text("執行模型分析", "Run model analysis")}
            </Button>
          </div>
        </div>

        <AnalysisRecommendationPanel
          dataset={dataset}
          targetColumn={targetColumn}
          analysisMode={analysisMode}
          availableModelCount={visibleModelOptions.length}
        />
      </div>

      {error ? (
        <InlineNotice tone="error" title={text("模型分析無法執行", "Model analysis cannot run")}>{error}</InlineNotice>
      ) : null}

      {isLoading ? (
        <AnalysisLoadingState
          title={text("正在評估模型組合", "Evaluating model candidates")}
          steps={[
            text("判斷問題類型與資料規模", "Detecting the problem type and dataset size"),
            text("訓練候選模型並計算指標", "Training candidate models and calculating metrics"),
            text("整理最佳模型、圖表與輸出檔", "Preparing the best model, charts, and output files")
          ]}
          progress={jobProgress}
          onCancel={activeJobId ? handleCancelAnalysis : undefined}
          isCancelling={isCancelling}
        />
      ) : null}

      {result ? (
        <ResultReveal>
          <ModelAnalysisResult
            result={result}
            file={file}
            files={files}
            isMerged={isMerged}
          />
        </ResultReveal>
      ) : null}
    </section>
  );
}

function ModelAnalysisResult({
  result,
  file,
  files,
  isMerged
}: {
  result: ModelAnalysis;
  file?: File;
  files: File[];
  isMerged: boolean;
}) {
  const { text } = useLocale();
  const { depth } = useReadingDepth();
  const isClassification = result.problem_type === "classification";
  const [activeChart, setActiveChart] = useState(result.charts[0]?.chart_type ?? "");
  const chartTabId = useId();
  const chartTabRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const bestMetric = useMemo(
    () =>
      result.model_results.reduce((best, current) => {
        if (isClassification) {
          return (current.f1_score ?? current.accuracy ?? 0) >
            (best.f1_score ?? best.accuracy ?? 0)
            ? current
            : best;
        }
        return current.rmse < best.rmse ? current : best;
      }),
    [isClassification, result.model_results]
  );
  const visibleChart =
    result.charts.find((chart) => chart.chart_type === activeChart) ??
    result.charts[0];
  const visibleChartStory =
    result.chart_stories?.find((story) => story.chart_type === visibleChart?.chart_type) ??
    result.chart_stories?.[0];
  const nextAction = isClassification
    ? text(
        "先檢查 F1 與 Accuracy 是否同時可接受，再查看完整模型比較。",
        "Confirm that F1 and accuracy are both acceptable before reviewing the full comparison."
      )
    : text(
        "先比較 RMSE 與 R²，再查看特徵重要性與殘差。",
        "Compare RMSE and R² before reviewing feature importance and residuals."
      );

  function handleChartKeyDown(
    event: React.KeyboardEvent<HTMLButtonElement>,
    index: number
  ) {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const nextIndex =
      event.key === "Home"
        ? 0
        : event.key === "End"
          ? result.charts.length - 1
          : event.key === "ArrowRight"
            ? (index + 1) % result.charts.length
            : (index - 1 + result.charts.length) % result.charts.length;
    setActiveChart(result.charts[nextIndex].chart_type);
    chartTabRefs.current[nextIndex]?.focus();
  }

  return (
    <div className="analysis-result-stack">
      <section className="model-winner">
        <div className="winner-icon">
          <Trophy aria-hidden="true" />
        </div>
        <div className="winner-copy">
          <span>{text("本次最佳模型", "Best model in this run")}</span>
          <h3>{bestMetric.model_name}</h3>
          <p>
            {isClassification
              ? `F1 ${formatNullableMetric(bestMetric.f1_score)}，Accuracy ${formatNullableMetric(bestMetric.accuracy)}`
              : `RMSE ${formatMetric(bestMetric.rmse)}，R² ${formatMetric(bestMetric.r2)}`}
          </p>
        </div>
        <Badge variant="success">
          <Check aria-hidden="true" />
          {result.problem_type === "regression"
            ? text("回歸", "Regression")
            : text("分類", "Classification")}
        </Badge>
      </section>

      <InsightHeadline
        title={text("模型結論", "Model conclusion")}
        summary={result.plain_summary}
        confidence={result.confidence}
        evidence={result.evidence}
      />

      <PlainSummaryGrid summary={result.plain_summary} />

      {depth !== "simple" ? (
        <>
          <EvidenceList evidence={result.evidence} />
          <MetricExplainer terms={result.terms} />
        </>
      ) : null}

      <dl className="result-kpi-strip">
        <div><dt>{text("使用資料列", "Rows used")}</dt><dd>{result.row_count_used.toLocaleString()}</dd></div>
        <div><dt>{text("使用特徵", "Features used")}</dt><dd>{result.feature_count_used.toLocaleString()}</dd></div>
        <div><dt>{text("完成模型", "Models completed")}</dt><dd>{result.model_results.length.toLocaleString()}</dd></div>
        <div><dt>{text("產出圖表", "Charts generated")}</dt><dd>{result.charts.length.toLocaleString()}</dd></div>
        <div>
          <dt>AutoML</dt>
          <dd>{result.automl_mode === "quick" ? "Quick" : text("關閉", "Off")}</dd>
        </div>
      </dl>

      <section className="result-next-action">
        <span>{text("建議下一步", "Suggested next step")}</span>
        <strong>{nextAction}</strong>
      </section>

      <section className="result-section">
        <div className="result-section-heading">
          <div>
            <span>{text("視覺比較", "Visual comparison")}</span>
            <h3>{text("模型圖表", "Model charts")}</h3>
          </div>
          <Badge variant="outline">{text(`${result.charts.length} 張`, `${result.charts.length} charts`)}</Badge>
        </div>
        {result.charts.length > 0 ? (
          <>
            <div className="chart-tablist" role="tablist" aria-label={text("模型圖表", "Model charts")}>
              {result.charts.map((chart, index) => (
                <button
                  key={chart.chart_type}
                  ref={(node) => { chartTabRefs.current[index] = node; }}
                  id={`${chartTabId}-${chart.chart_type}-tab`}
                  type="button"
                  role="tab"
                  aria-selected={visibleChart?.chart_type === chart.chart_type}
                  aria-controls={`${chartTabId}-chart-panel`}
                  tabIndex={visibleChart?.chart_type === chart.chart_type ? 0 : -1}
                  className={visibleChart?.chart_type === chart.chart_type ? "is-active" : ""}
                  onClick={() => setActiveChart(chart.chart_type)}
                  onKeyDown={(event) => handleChartKeyDown(event, index)}
                >
                  <BarChart3 aria-hidden="true" />
                  {chart.title}
                </button>
              ))}
            </div>
            {visibleChart ? (
              <div
                id={`${chartTabId}-chart-panel`}
                role="tabpanel"
                aria-labelledby={`${chartTabId}-${visibleChart.chart_type}-tab`}
              >
                {visibleChartStory ? (
                  <ChartStoryPanel
                    story={visibleChartStory}
                    imageUrl={visibleChart.chart_url}
                    imageAlt={visibleChart.title}
                  />
                ) : (
                  <figure className="featured-chart">
                    <figcaption>
                      <strong>{visibleChart.title}</strong>
                      <span>{visibleChart.chart_path}</span>
                    </figcaption>
                    <img
                      src={visibleChart.chart_url}
                      alt={visibleChart.title}
                      width={1200}
                      height={760}
                      loading="lazy"
                    />
                  </figure>
                )}
              </div>
            ) : null}
          </>
        ) : (
          <p className="tab-empty-state">{text("本次分析沒有產生圖表。", "This analysis did not generate charts.")}</p>
        )}
      </section>

      <section className="result-output-bar">
        <div>
          <span>{text("分析輸出", "Analysis outputs")}</span>
          <strong>{text("模型結果與清理後資料", "Model results and cleaned data")}</strong>
        </div>
        <div>
          {depth === "research" ? (
            <ResearchDetailsDrawer
              details={result.research_details}
              title={text("模型研究細節", "Model research details")}
            />
          ) : null}
          <Button asChild variant="outline">
            <a href={result.model_results_url} download>
              <Download aria-hidden="true" />
              {text("模型結果 XLSX", "Model results XLSX")}
            </a>
          </Button>
          <Button asChild variant="outline">
            <a href={result.cleaned_dataset_url} download>
              <Download aria-hidden="true" />
              {text("清理後 CSV", "Cleaned CSV")}
            </a>
          </Button>
        </div>
      </section>

      <details className="result-disclosure">
        <summary>
          <span>
            <strong>{text("完整模型比較", "Full model comparison")}</strong>
            <small>{text(`${result.model_results.length} 個模型與全部評估指標`, `${result.model_results.length} models and all evaluation metrics`)}</small>
          </span>
          <ChevronDown aria-hidden="true" />
        </summary>
        <div className="result-disclosure-content">
          <div className="model-table-shell">
            <table>
              <thead>
                <tr>
                  <th scope="col">{text("模型", "Model")}</th>
                  <th scope="col">{text("家族", "Family")}</th>
                  <th scope="col">R²</th>
                  <th scope="col">RMSE</th>
                  <th scope="col">MAE</th>
                  {isClassification ? (
                    <>
                      <th scope="col">Accuracy</th>
                      <th scope="col">F1</th>
                    </>
                  ) : null}
                  <th scope="col">{text("訓練時間", "Training time")}</th>
                  <th scope="col">{text("參數", "Parameters")}</th>
                  <th scope="col">{text("模型檔", "Model file")}</th>
                </tr>
              </thead>
              <tbody>
                {result.model_results.map((metric) => (
                  <tr key={metric.model_name} className={metric.model_key === bestMetric.model_key ? "is-best" : ""}>
                    <th scope="row">
                      {metric.model_name}
                      {metric.model_key === bestMetric.model_key ? <Badge variant="success">{text("最佳", "Best")}</Badge> : null}
                    </th>
                    <td>{metric.model_family}</td>
                    <td className="tabular">{formatMetric(metric.r2)}</td>
                    <td className="tabular">{formatMetric(metric.rmse)}</td>
                    <td className="tabular">{formatMetric(metric.mae)}</td>
                    {isClassification ? (
                      <>
                        <td className="tabular">{formatNullableMetric(metric.accuracy)}</td>
                        <td className="tabular">{formatNullableMetric(metric.f1_score)}</td>
                      </>
                    ) : null}
                    <td className="tabular">{text(`${formatMetric(metric.training_time_seconds)} 秒`, `${formatMetric(metric.training_time_seconds)} sec`)}</td>
                    <td>{formatParams(metric.automl_best_params, text("預設", "Default"))}</td>
                    <td>
                      <a href={metric.model_url} download className="table-download-link">
                        <Download aria-hidden="true" />
                        {text("下載", "Download")}
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </details>

      {result.notes.length > 0 ? (
        <InlineNotice tone="warning" title={text("模型備註", "Model notes")}>
          <ul>{result.notes.map((note) => <li key={note}>{note}</li>)}</ul>
        </InlineNotice>
      ) : null}

      <CodeGenerationPanel
        result={result}
        file={file}
        files={files}
        isMerged={isMerged}
      />
    </div>
  );
}

function CodeGenerationPanel({
  result,
  file,
  files,
  isMerged
}: {
  result: ModelAnalysis;
  file?: File;
  files: File[];
  isMerged: boolean;
}) {
  const { text } = useLocale();
  const bestModelName = useMemo(() => {
    return result.model_results.reduce((best, current) => {
      if (result.problem_type === "classification") {
        return (current.f1_score ?? current.accuracy ?? 0) >
          (best.f1_score ?? best.accuracy ?? 0)
          ? current
          : best;
      }
      return current.rmse < best.rmse ? current : best;
    }).model_name;
  }, [result.model_results, result.problem_type]);
  const sourceKey = workspaceSourceKey(file, files, isMerged);
  const codeKey = `${sourceKey}:code:${result.target_column}`;
  const [selectedModelName, setSelectedModelName] = useWorkspacePanelState(
    `${codeKey}:model`,
    bestModelName
  );
  const [generatedCode, setGeneratedCode] =
    useWorkspacePanelState<GeneratedCode | null>(`${codeKey}:result`, null);
  const [codeError, setCodeError] = useWorkspacePanelState<string | null>(
    `${codeKey}:error`,
    null
  );
  const [isGenerating, setIsGenerating] = useWorkspacePanelState(
    `${codeKey}:loading`,
    false
  );
  async function handleGenerateCode() {
    setIsGenerating(true);
    setCodeError(null);
    setGeneratedCode(null);

    try {
      const generated = isMerged
        ? await generateMergedCode(
            files,
            result.target_column,
            selectedModelName,
            result.analysis_mode,
            result.selected_chart_types
          )
        : await generateCode(
            assertSingleFile(file),
            result.target_column,
            selectedModelName,
            result.analysis_mode,
            result.selected_chart_types
          );
      setGeneratedCode(generated);
    } catch (caughtError) {
      setCodeError(caughtError instanceof Error ? caughtError.message : text("程式碼生成失敗。", "Code generation failed."));
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <section className="code-generation-panel" aria-busy={isGenerating}>
      <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
        <div className="max-w-4xl">
          <h3 className="text-2xl font-semibold text-ink">{text("分析程式碼生成", "Analysis code generation")}</h3>
          <p className="ui-copy-secondary mt-3 text-base leading-7">
            {text(
              "依照目前目標欄位、分析模式、圖表選擇與指定模型，系統會產生可下載的 Python 腳本與 Notebook。",
              "Generate a downloadable Python script and notebook from the current target, analysis mode, chart selection, and model."
            )}
          </p>
        </div>
        <Button
          type="button"
          onClick={handleGenerateCode}
          disabled={isGenerating}
          variant="default"
          size="lg"
        >
          {isGenerating ? <Spinner /> : null}
          {isGenerating ? text("正在生成", "Generating") : text("生成程式碼", "Generate code")}
        </Button>
      </div>

      <div className="mt-5 grid gap-4 2xl:grid-cols-[minmax(260px,340px)_1fr]">
        <label className="block">
          <span className="text-base font-semibold text-ink">{text("主要模型", "Primary model")}</span>
          <select
            name="code-primary-model"
            autoComplete="off"
            value={selectedModelName}
            onChange={(event) => {
              setSelectedModelName(event.target.value);
              setGeneratedCode(null);
              setCodeError(null);
            }}
            className="mt-2 h-12 w-full rounded-md border border-line bg-white px-4 text-base text-ink outline-none transition focus:border-navy focus:ring-2 focus:ring-blue-100"
          >
            {result.model_results.map((metric) => (
              <option key={metric.model_name} value={metric.model_name}>
                {metric.model_name}
              </option>
            ))}
          </select>
        </label>

        <div className="grid gap-3 md:grid-cols-3">
          <MiniMetric label={text("預設最佳模型", "Default best model")} value={bestModelName} />
          <MiniMetric
            label={text("程式碼圖表", "Code charts")}
            value={text(`${result.selected_chart_types.length} 種`, `${result.selected_chart_types.length} types`)}
          />
          <MiniMetric
            label={text("資料來源", "Data source")}
            value={isMerged ? text(`${files.length} 個檔案合併`, `${files.length} merged files`) : text("單一檔案", "Single file")}
          />
        </div>
      </div>

      {codeError ? (
        <InlineNotice tone="error" title={text("程式碼生成失敗", "Code generation failed")}>
          {codeError}
        </InlineNotice>
      ) : null}

      {isGenerating ? (
        <AnalysisLoadingState
          title={text("正在產生可執行程式碼", "Generating executable code")}
          steps={[
            text("整理資料清理流程", "Preparing the data-cleaning workflow"),
            text("寫入模型訓練與評估", "Writing model training and evaluation"),
            text("建立 Python 與 Notebook 輸出", "Building Python and notebook outputs")
          ]}
        />
      ) : null}

      {generatedCode ? (
        <ResultReveal>
        <div className="generated-code-result">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <h4 className="text-xl font-semibold text-ink">{text("已生成輸出檔案", "Generated output files")}</h4>
              <p className="ui-copy-secondary mt-2 text-base leading-7">
                {text("主要模型", "Primary model")}：{generatedCode.model_name}；{text("資料檔", "Dataset")}：
                <span className="break-all"> {generatedCode.dataset_path}</span>
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button asChild>
                <a href={generatedCode.python_url} download>
                  <Download aria-hidden="true" />
                  Python
                </a>
              </Button>
              <Button asChild variant="outline">
                <a href={generatedCode.notebook_url} download>
                  <Download aria-hidden="true" />
                  Notebook
                </a>
              </Button>
            </div>
          </div>

          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <OutputPath label={text("Python 檔案", "Python file")} value={generatedCode.python_path} />
            <OutputPath label={text("Notebook 檔案", "Notebook file")} value={generatedCode.notebook_path} />
          </div>

          {generatedCode.notes.length > 0 ? (
            <ul className="ui-copy-secondary mt-4 space-y-2 text-base leading-7">
              {generatedCode.notes.map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
          ) : null}

          <div className="mt-5">
            <div className="mb-3 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <h5 className="text-lg font-semibold text-ink">{text("程式碼預覽", "Code preview")}</h5>
                <p className="ui-copy-secondary mt-1 text-sm leading-6">
                  {text("這裡直接顯示本次生成的分析程式碼，下載前即可檢查內容。", "Inspect the generated analysis code here before downloading it.")}
                </p>
              </div>
            </div>
            <InlineCodeViewer
              pythonContent={generatedCode.python_content}
              notebookContent={generatedCode.notebook_content}
              pythonPath={generatedCode.python_path}
              notebookPath={generatedCode.notebook_path}
            />
          </div>
        </div>
        </ResultReveal>
      ) : null}
    </section>
  );
}

function OutputPath({ label, value }: { label: string; value: string }) {
  return (
    <div className="analysis-output-path p-4">
      <div className="ui-output-label text-sm font-semibold">{label}</div>
      <div className="ui-output-value mt-2 break-all font-mono text-sm">{value}</div>
    </div>
  );
}

function MiniMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="analysis-mini-metric px-5 py-4">
      <div className="ui-metric-label text-sm font-semibold">{label}</div>
      <div className="ui-metric-value mt-1 break-words text-xl font-semibold">{value}</div>
    </div>
  );
}

function formatMetric(value: number): string {
  return value.toLocaleString(undefined, { maximumFractionDigits: 4 });
}

function formatNullableMetric(value: number | null): string {
  return value === null ? "-" : formatMetric(value);
}

function formatParams(params: Record<string, unknown>, defaultLabel = "預設"): string {
  const entries = Object.entries(params);
  if (entries.length === 0) {
    return defaultLabel;
  }
  return entries.map(([key, value]) => `${key}=${String(value)}`).join("，");
}

function modelDescriptionEnglish(modelKey: string) {
  const descriptions: Record<string, string> = {
    linear_regression: "A fast, interpretable regression baseline.",
    ridge: "A stable linear model for correlated features.",
    lasso: "A linear model that can also select features.",
    elastic_net: "A balanced combination of Ridge and Lasso.",
    decision_tree_regressor: "Readable nonlinear rules and local decisions.",
    random_forest: "A robust nonlinear model for tabular data.",
    extra_trees_regressor: "A highly randomized tree ensemble.",
    gradient_boosting_regressor: "A strong boosting model for small and medium datasets.",
    xgboost_regressor: "An efficient gradient-boosting regressor.",
    lightgbm_regressor: "A lightweight gradient-boosting regressor.",
    knn_regressor: "Neighbor-based estimates for smooth, low-dimensional data.",
    svr: "Support-vector regression for nonlinear low-dimensional data.",
    logistic_regression: "A fast, interpretable classification baseline.",
    decision_tree_classifier: "Readable nonlinear classification rules.",
    random_forest_classifier: "A robust classifier for tabular data.",
    extra_trees_classifier: "A randomized ensemble for classification stability.",
    gradient_boosting_classifier: "A boosting classifier that corrects errors iteratively.",
    xgboost_classifier: "An efficient gradient-boosting classifier.",
    lightgbm_classifier: "A lightweight gradient-boosting classifier.",
    knn_classifier: "Neighbor-based classification for smooth boundaries.",
    svc: "Support-vector classification for nonlinear boundaries."
  };
  return descriptions[modelKey] ?? "A supported candidate model.";
}

function assertSingleFile(file: File | undefined): File {
  if (!file) {
    throw new Error("缺少模型分析需要的檔案。");
  }

  return file;
}

function isCancellationMessage(message: string) {
  return message.includes("已取消") || message.toLowerCase().includes("cancelled");
}
