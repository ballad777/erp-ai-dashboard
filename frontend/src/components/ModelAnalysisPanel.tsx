"use client";

import { useEffect, useMemo, useState } from "react";
import {
  analyzeMergedModels,
  analyzeModels,
  generateCode,
  generateMergedCode,
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

const problemTypeLabels = {
  regression: "回歸",
  classification: "分類"
};

const analysisModes: Array<{ value: AnalysisMode; label: string; description: string }> = [
  {
    value: "auto",
    label: "自動選擇",
    description: "由系統依目標欄位型態與資料分布判斷。"
  },
  {
    value: "regression",
    label: "回歸分析",
    description: "適合連續數值預測，例如價格、銷售額、報酬率。"
  },
  {
    value: "classification",
    label: "分類分析",
    description: "適合類別或狀態判斷，例如是否靠近捷運、風險等級。"
  }
];

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
  const recommendedTargets = dataset.recommended_target_columns ?? [];
  const defaultTarget =
    recommendedTargets.find((column) => dataset.columns.includes(column)) ??
    dataset.columns[dataset.columns.length - 1] ??
    "";
  const [targetColumn, setTargetColumn] = useState(defaultTarget);
  const [analysisMode, setAnalysisMode] = useState<AnalysisMode>("auto");
  const [chartSelectionMode, setChartSelectionMode] =
    useState<ChartSelectionMode>("auto");
  const [modelSelectionMode, setModelSelectionMode] =
    useState<ModelSelectionMode>("auto");
  const [automlMode, setAutomlMode] = useState<AutoMLMode>("quick");
  const [selectedModels, setSelectedModels] = useState<string[]>([
    "ridge",
    "random_forest",
    "gradient_boosting_regressor"
  ]);
  const [selectedCharts, setSelectedCharts] = useState<string[]>([
    "model_comparison",
    "feature_importance",
    "predicted_vs_actual"
  ]);
  const [result, setResult] = useState<ModelAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const visibleModelOptions = useMemo(() => {
    if (analysisMode === "auto") {
      return modelOptions;
    }
    return modelOptions.filter((option) => option.problemType === analysisMode);
  }, [analysisMode]);

  const featureCount = useMemo(
    () => Math.max(dataset.columns.length - (targetColumn ? 1 : 0), 0),
    [dataset.columns.length, targetColumn]
  );

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
      setError("請先選擇目標欄位。");
      return;
    }

    if (chartSelectionMode === "custom" && selectedCharts.length === 0) {
      setError("請至少選擇一種要產出的圖表。");
      return;
    }

    if (modelSelectionMode === "custom" && selectedModels.length === 0) {
      setError("請至少選擇一個要執行的模型。");
      return;
    }

    if (isMerged && files.length < 2) {
      setError("合併模型分析至少需要 2 個成功讀取的檔案。");
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

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
            automlMode
          )
        : await analyzeModels(
            assertSingleFile(file),
            targetColumn,
            analysisMode,
            requestedCharts,
            modelSelectionMode,
            requestedModels,
            automlMode
          );
      setResult(modelAnalysis);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "模型分析失敗。");
    } finally {
      setIsLoading(false);
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
    <section className="surface-card p-6 sm:p-7">
      <div className="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
        <div className="max-w-4xl">
          <h2 className="text-2xl font-semibold text-ink">{title}</h2>
          <p className="mt-3 text-base leading-7 text-muted">
            {description ??
              "選擇目標欄位、分析模式與想產出的圖表。使用「自動選擇」時，系統會依資料型態選擇最適合的分析與圖表組合。"}
          </p>
        </div>
        <button
          type="button"
          onClick={handleRunModels}
          disabled={isLoading}
          className="h-12 rounded-xl bg-navy px-6 text-base font-semibold text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {isLoading ? "模型執行中..." : "執行模型分析"}
        </button>
      </div>

      <div className="mt-7 grid gap-6 2xl:grid-cols-[minmax(260px,340px)_1fr]">
        <div className="space-y-5">
          <label className="block">
            <span className="text-base font-semibold text-ink">目標欄位</span>
            <select
              value={targetColumn}
              onChange={(event) => {
                setTargetColumn(event.target.value);
                setResult(null);
                setError(null);
              }}
              className="mt-2 h-12 w-full rounded-md border border-line bg-white px-4 text-base text-ink outline-none transition focus:border-brand focus:ring-2 focus:ring-teal-100"
            >
              {dataset.columns.map((column) => (
                <option key={column} value={column}>
                  {column}
                </option>
              ))}
            </select>
          </label>

          {recommendedTargets.length > 0 ? (
            <div className="rounded-md border border-teal-100 bg-teal-50 p-4">
              <div className="text-sm font-semibold text-teal-900">
                智慧建議目標欄位
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                {recommendedTargets.map((column) => (
                  <button
                    key={column}
                    type="button"
                    onClick={() => {
                      setTargetColumn(column);
                      setResult(null);
                      setError(null);
                    }}
                    className={`rounded-md border px-3 py-2 text-sm font-semibold transition ${
                      targetColumn === column
                        ? "border-brand bg-brand text-white"
                        : "border-teal-200 bg-white text-teal-900 hover:border-brand"
                    }`}
                  >
                    {column}
                  </button>
                ))}
              </div>
            </div>
          ) : null}

          <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
            <MiniMetric label="資料列" value={dataset.row_count.toLocaleString()} />
            <MiniMetric label="特徵欄位" value={featureCount.toLocaleString()} />
            <MiniMetric label="可用模型" value={visibleModelOptions.length.toLocaleString()} />
          </div>
        </div>

        <div className="space-y-6">
          <fieldset>
            <legend className="text-base font-semibold text-ink">分析模式</legend>
            <div className="mt-3 grid gap-3 md:grid-cols-3">
              {analysisModes.map((mode) => (
                <label
                  key={mode.value}
                  className={`rounded-md border p-4 transition ${
                    analysisMode === mode.value
                      ? "border-brand bg-teal-50"
                      : "border-line bg-slate-50 hover:border-brand"
                  }`}
                >
                  <input
                    type="radio"
                    name={`${dataset.file_name}-analysis-mode`}
                    value={mode.value}
                    checked={analysisMode === mode.value}
                    onChange={() => {
                      setAnalysisMode(mode.value);
                      setResult(null);
                      setError(null);
                    }}
                    className="mr-2"
                  />
                  <span className="text-base font-semibold text-ink">{mode.label}</span>
                  <p className="mt-2 text-sm leading-6 text-muted">{mode.description}</p>
                </label>
              ))}
            </div>
          </fieldset>

          <fieldset>
            <legend className="text-base font-semibold text-ink">模型策略</legend>
            <div className="mt-3 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => {
                  setModelSelectionMode("auto");
                  setResult(null);
                  setError(null);
                }}
                className={`h-11 rounded-md border px-4 text-base font-semibold transition ${
                  modelSelectionMode === "auto"
                    ? "border-brand bg-brand text-white"
                    : "border-line bg-white text-ink hover:border-brand"
                }`}
              >
                自動推薦模型
              </button>
              <button
                type="button"
                onClick={() => {
                  setModelSelectionMode("custom");
                  setResult(null);
                  setError(null);
                }}
                className={`h-11 rounded-md border px-4 text-base font-semibold transition ${
                  modelSelectionMode === "custom"
                    ? "border-brand bg-brand text-white"
                    : "border-line bg-white text-ink hover:border-brand"
                }`}
              >
                手動選擇模型
              </button>
            </div>

            {modelSelectionMode === "custom" ? (
              <div className="mt-4 grid gap-3 md:grid-cols-2 2xl:grid-cols-3">
                {visibleModelOptions.map((option) => (
                  <label
                    key={option.key}
                    className={`flex min-h-[92px] flex-col rounded-md border px-4 py-3 text-base transition ${
                      selectedModels.includes(option.key)
                        ? "border-navy bg-blue-50 text-ink"
                        : "border-line bg-white text-muted hover:border-navy"
                    }`}
                  >
                    <span className="flex items-center gap-3 font-semibold">
                      <input
                        type="checkbox"
                        checked={selectedModels.includes(option.key)}
                        onChange={() => toggleModel(option.key)}
                        className="h-4 w-4"
                      />
                      {option.label}
                    </span>
                    <span className="mt-2 text-sm leading-6 text-muted">
                      {option.problemType === "regression" ? "回歸" : "分類"}｜
                      {option.description}
                    </span>
                  </label>
                ))}
              </div>
            ) : (
              <p className="mt-4 rounded-md border border-line bg-slate-50 p-4 text-base leading-7 text-muted">
                自動模式會依資料列數、特徵數、欄位型態、缺失比例與問題類型，
                選出最適合的模型組合，不再固定執行同一批模型。
              </p>
            )}
          </fieldset>

          <fieldset>
            <legend className="text-base font-semibold text-ink">AutoML 調參</legend>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {[
                {
                  value: "quick" as AutoMLMode,
                  label: "Quick AutoML",
                  body: "對支援模型執行小型參數搜尋，回傳最佳參數。"
                },
                {
                  value: "off" as AutoMLMode,
                  label: "關閉調參",
                  body: "使用模型預設參數，速度較快。"
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
                  <span className="text-base font-semibold text-ink">{mode.label}</span>
                  <p className="mt-2 text-sm leading-6 text-muted">{mode.body}</p>
                </label>
              ))}
            </div>
          </fieldset>

          <fieldset>
            <legend className="text-base font-semibold text-ink">圖表產出</legend>
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
                自動選最適合圖表
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
                手動選擇圖表
              </button>
            </div>

            {chartSelectionMode === "custom" ? (
              <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                {chartOptions.map((option) => (
                  <label
                    key={option.value}
                    className={`flex min-h-12 items-center rounded-md border px-4 py-3 text-base font-medium transition ${
                      selectedCharts.includes(option.value)
                        ? "border-navy bg-blue-50 text-ink"
                        : "border-line bg-white text-muted hover:border-navy"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedCharts.includes(option.value)}
                      onChange={() => toggleChart(option.value)}
                      className="mr-3 h-4 w-4"
                    />
                    {option.label}
                  </label>
                ))}
              </div>
            ) : (
              <p className="mt-4 rounded-md border border-line bg-slate-50 p-4 text-base leading-7 text-muted">
                自動模式會依問題型態與欄位組成產出模型比較、特徵重要性、
                預測值與實際值；回歸問題會再加入殘差圖。
              </p>
            )}
          </fieldset>
        </div>
      </div>

      {error ? (
        <div className="mt-6 rounded-md border border-red-200 bg-red-50 px-5 py-4 text-base font-medium text-red-700">
          {error}
        </div>
      ) : null}

      {result ? (
        <ModelAnalysisResult
          result={result}
          file={file}
          files={files}
          isMerged={isMerged}
        />
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
  const isClassification = result.problem_type === "classification";

  return (
    <div className="mt-8 space-y-7">
      <div className="grid gap-4 md:grid-cols-5">
        <MiniMetric label="判斷問題" value={problemTypeLabels[result.problem_type]} />
        <MiniMetric label="使用資料列" value={result.row_count_used.toLocaleString()} />
        <MiniMetric label="使用特徵" value={result.feature_count_used.toLocaleString()} />
        <MiniMetric label="產出圖表" value={`${result.charts.length} 張`} />
        <MiniMetric
          label="AutoML"
          value={result.automl_mode === "quick" ? "Quick 調參" : "關閉"}
        />
      </div>

      <div className="rounded-2xl border border-blue-100 bg-slate-50/80 p-5">
        <h3 className="text-base font-semibold text-ink">輸出檔案</h3>
        <div className="mt-4 flex flex-wrap gap-3">
          <a
            href={result.model_results_url}
            download
            className="rounded-md bg-navy px-5 py-3 text-base font-semibold text-white transition hover:bg-blue-800"
          >
            下載 model_results.xlsx
          </a>
          <a
            href={result.cleaned_dataset_url}
            download
            className="rounded-md border border-line bg-white px-5 py-3 text-base font-semibold text-ink transition hover:border-brand hover:text-brand"
          >
            下載 cleaned_dataset.csv
          </a>
        </div>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          <OutputPath label="模型結果" value={result.model_results_path} />
          <OutputPath label="清理後資料" value={result.cleaned_dataset_path} />
        </div>
      </div>

      <div className="rounded-2xl border border-blue-100 bg-slate-50/80 p-5">
        <h3 className="text-base font-semibold text-ink">本次模型組合</h3>
        <div className="mt-3 flex flex-wrap gap-2">
          {result.model_results.map((metric) => (
            <span
              key={metric.model_key}
              className="rounded-md border border-line bg-white px-3 py-2 text-sm font-semibold text-muted"
            >
              {metric.model_name}
            </span>
          ))}
        </div>
        {result.model_selection_mode === "auto" && result.recommended_models.length > 0 ? (
          <p className="mt-3 text-base leading-7 text-muted">
            系統已依資料特性推薦 {result.recommended_models.length} 個模型。
          </p>
        ) : null}
      </div>

      <div className="overflow-x-auto rounded-md border border-line">
        <table className="min-w-[1280px] w-full text-left text-base">
          <thead className="bg-slate-50 text-sm uppercase text-muted">
            <tr>
              <th className="px-5 py-4 font-semibold">模型</th>
              <th className="px-5 py-4 font-semibold">家族</th>
              <th className="px-5 py-4 font-semibold">R2</th>
              <th className="px-5 py-4 font-semibold">RMSE</th>
              <th className="px-5 py-4 font-semibold">MAE</th>
              {isClassification ? (
                <>
                  <th className="px-5 py-4 font-semibold">Accuracy</th>
                  <th className="px-5 py-4 font-semibold">F1</th>
                </>
              ) : null}
              <th className="px-5 py-4 font-semibold">訓練時間</th>
              <th className="px-5 py-4 font-semibold">AutoML 參數</th>
              <th className="px-5 py-4 font-semibold">模型檔</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {result.model_results.map((metric) => (
              <tr key={metric.model_name}>
                <td className="px-5 py-4 font-medium text-ink">{metric.model_name}</td>
                <td className="px-5 py-4 text-muted">{metric.model_family}</td>
                <td className="px-5 py-4 text-muted">{formatMetric(metric.r2)}</td>
                <td className="px-5 py-4 text-muted">{formatMetric(metric.rmse)}</td>
                <td className="px-5 py-4 text-muted">{formatMetric(metric.mae)}</td>
                {isClassification ? (
                  <>
                    <td className="px-5 py-4 text-muted">
                      {metric.accuracy === null ? "-" : formatMetric(metric.accuracy)}
                    </td>
                    <td className="px-5 py-4 text-muted">
                      {metric.f1_score === null ? "-" : formatMetric(metric.f1_score)}
                    </td>
                  </>
                ) : null}
                <td className="px-5 py-4 text-muted">
                  {formatMetric(metric.training_time_seconds)} 秒
                </td>
                <td className="px-5 py-4 text-muted">
                  {formatParams(metric.automl_best_params)}
                </td>
                <td className="px-5 py-4">
                  <a
                    href={metric.model_url}
                    download
                    className="rounded-md border border-line bg-white px-3 py-2 text-sm font-semibold text-ink transition hover:border-brand hover:text-brand"
                  >
                    下載
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        {result.charts.map((chart) => (
          <figure
            key={chart.chart_path}
            className="rounded-md border border-line bg-slate-50 p-5"
          >
            <figcaption className="mb-4 flex flex-col gap-1">
              <span className="text-lg font-semibold text-ink">{chart.title}</span>
              <span className="break-all text-sm text-muted">{chart.chart_path}</span>
            </figcaption>
            <img
              src={chart.chart_url}
              alt={chart.title}
              className="w-full rounded-md border border-line bg-white"
            />
          </figure>
        ))}
      </div>

      {result.notes.length > 0 ? (
        <div className="rounded-md border border-amber-200 bg-amber-50 p-5">
          <h3 className="text-base font-semibold text-amber-900">模型備註</h3>
          <ul className="mt-3 space-y-2 text-base leading-7 text-amber-900">
            {result.notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </div>
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
  const bestModelName = useMemo(() => {
    return result.model_results.reduce((best, current) =>
      current.rmse < best.rmse ? current : best
    ).model_name;
  }, [result.model_results]);
  const [selectedModelName, setSelectedModelName] = useState(bestModelName);
  const [generatedCode, setGeneratedCode] = useState<GeneratedCode | null>(null);
  const [codeError, setCodeError] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [previewMode, setPreviewMode] = useState<"python" | "notebook">("python");

  async function handleGenerateCode() {
    setIsGenerating(true);
    setCodeError(null);
    setGeneratedCode(null);
    setPreviewMode("python");

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
      setCodeError(caughtError instanceof Error ? caughtError.message : "程式碼生成失敗。");
    } finally {
      setIsGenerating(false);
    }
  }

  return (
    <section className="rounded-2xl border border-blue-200 bg-blue-50/80 p-6 shadow-[0_16px_36px_rgba(29,78,216,0.08)]">
      <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
        <div className="max-w-4xl">
          <h3 className="text-2xl font-semibold text-ink">AI 程式碼生成</h3>
          <p className="mt-3 text-base leading-7 text-muted">
            依照目前目標欄位、分析模式、圖表選擇與指定模型，系統會產生可下載的
            Python 腳本與 Notebook。
          </p>
        </div>
        <button
          type="button"
          onClick={handleGenerateCode}
          disabled={isGenerating}
          className="h-12 rounded-xl bg-navy px-6 text-base font-semibold text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {isGenerating ? "生成中..." : "生成程式碼"}
        </button>
      </div>

      <div className="mt-5 grid gap-4 2xl:grid-cols-[minmax(260px,340px)_1fr]">
        <label className="block">
          <span className="text-base font-semibold text-ink">主要模型</span>
          <select
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
          <MiniMetric label="預設最佳模型" value={bestModelName} />
          <MiniMetric
            label="程式碼圖表"
            value={`${result.selected_chart_types.length} 種`}
          />
          <MiniMetric
            label="資料來源"
            value={isMerged ? `${files.length} 個檔案合併` : "單一檔案"}
          />
        </div>
      </div>

      {codeError ? (
        <div className="mt-5 rounded-md border border-red-200 bg-red-50 px-5 py-4 text-base font-medium text-red-700">
          {codeError}
        </div>
      ) : null}

      {generatedCode ? (
        <div className="mt-6 rounded-md border border-line bg-white p-5">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <h4 className="text-xl font-semibold text-ink">已生成輸出檔案</h4>
              <p className="mt-2 text-base leading-7 text-muted">
                主要模型：{generatedCode.model_name}；資料檔：
                <span className="break-all"> {generatedCode.dataset_path}</span>
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <a
                href={generatedCode.python_url}
                download
                className="rounded-md bg-brand px-5 py-3 text-base font-semibold text-white transition hover:bg-teal-800"
              >
                下載 generated_code.py
              </a>
              <a
                href={generatedCode.notebook_url}
                download
                className="rounded-md border border-line bg-white px-5 py-3 text-base font-semibold text-ink transition hover:border-navy hover:text-navy"
              >
                下載 notebook.ipynb
              </a>
            </div>
          </div>

          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <OutputPath label="Python 檔案" value={generatedCode.python_path} />
            <OutputPath label="Notebook 檔案" value={generatedCode.notebook_path} />
          </div>

          {generatedCode.notes.length > 0 ? (
            <ul className="mt-4 space-y-2 text-base leading-7 text-muted">
              {generatedCode.notes.map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
          ) : null}

          <div className="mt-5">
            <div className="mb-3 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <h5 className="text-lg font-semibold text-ink">程式碼預覽</h5>
                <p className="mt-1 text-sm leading-6 text-muted">
                  這裡直接顯示本次生成的分析程式碼，下載前即可檢查內容。
                </p>
              </div>
              <div className="flex rounded-xl border border-line bg-slate-50 p-1">
                {[
                  { value: "python" as const, label: "Python" },
                  { value: "notebook" as const, label: "Notebook" }
                ].map((mode) => (
                  <button
                    key={mode.value}
                    type="button"
                    onClick={() => setPreviewMode(mode.value)}
                    className={`rounded-lg px-4 py-2 text-sm font-semibold transition ${
                      previewMode === mode.value
                        ? "bg-white text-navy shadow-[0_8px_22px_rgba(15,23,42,0.08)]"
                        : "text-muted hover:text-ink"
                    }`}
                  >
                    {mode.label}
                  </button>
                ))}
              </div>
            </div>
            <div className="code-window">
              <div className="flex items-center justify-between border-b border-white/10 px-4 py-3 text-xs font-semibold text-slate-300">
                <span>{previewMode === "python" ? generatedCode.python_path : generatedCode.notebook_path}</span>
                <span>{previewMode === "python" ? "PY" : "IPYNB"}</span>
              </div>
              <pre className="max-h-[520px] overflow-auto p-4 text-sm leading-6 text-slate-100">
                <code>
                  {previewMode === "python"
                    ? generatedCode.python_content
                    : generatedCode.notebook_content}
                </code>
              </pre>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function OutputPath({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-blue-100 bg-slate-50/80 p-4">
      <div className="text-sm font-semibold text-muted">{label}</div>
      <div className="mt-2 break-all font-mono text-sm text-ink">{value}</div>
    </div>
  );
}

function MiniMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-blue-100 bg-white/78 px-5 py-4 shadow-[0_12px_28px_rgba(15,23,42,0.045)]">
      <div className="text-sm font-semibold text-muted">{label}</div>
      <div className="mt-1 break-words text-xl font-semibold text-ink">{value}</div>
    </div>
  );
}

function formatMetric(value: number): string {
  return value.toLocaleString(undefined, { maximumFractionDigits: 4 });
}

function formatParams(params: Record<string, unknown>): string {
  const entries = Object.entries(params);
  if (entries.length === 0) {
    return "預設";
  }
  return entries.map(([key, value]) => `${key}=${String(value)}`).join("，");
}

function assertSingleFile(file: File | undefined): File {
  if (!file) {
    throw new Error("缺少模型分析需要的檔案。");
  }

  return file;
}
