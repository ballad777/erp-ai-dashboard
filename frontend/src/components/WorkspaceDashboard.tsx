"use client";

import Link from "next/link";
import {
  ArrowRight,
  BookOpenText,
  BrainCircuit,
  ChartNoAxesCombined,
  Check,
  Database,
  FileCode2,
  FileText,
  Layers3
} from "lucide-react";
import { useLocale } from "@/components/LocaleProvider";
import { PageHeader, WorkspaceEmptyState } from "@/components/PagePrimitives";
import { WorkspaceDetailPanel } from "@/components/WorkspaceDetailPanel";
import { WorkspaceInsightGrid } from "@/components/WorkspaceInsightGrid";
import {
  useWorkspace,
  workspaceSourceKey
} from "@/components/WorkspaceProvider";
import {
  useWorkspaceSources,
  type WorkspaceSource
} from "@/components/WorkspaceSource";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type {
  FinancialAnalysis,
  GeneratedCode,
  GeneratedReport,
  ModelAnalysis
} from "@/lib/api";

export function WorkspaceDashboard() {
  const { text, path } = useLocale();
  const { panelStates } = useWorkspace();
  const { sources, activeSource, completedUploads } = useWorkspaceSources();
  const sourceKey = activeSource
    ? workspaceSourceKey(
        activeSource.file,
        activeSource.files,
        activeSource.isMerged
      )
    : "";
  const modelResult = findResult<ModelAnalysis>(
    panelStates,
    sourceKey,
    ":model:result"
  );
  const financeResult = findResult<FinancialAnalysis>(
    panelStates,
    sourceKey,
    ":finance:result"
  );
  const reportResult = findResult<GeneratedReport>(
    panelStates,
    sourceKey,
    ":agent:report"
  );
  const codeResult = findResult<GeneratedCode>(
    panelStates,
    sourceKey,
    ":result",
    ":code:"
  );

  const completedStates = {
    data: Boolean(activeSource),
    model: Boolean(modelResult),
    finance: Boolean(financeResult),
    report: Boolean(reportResult)
  };
  const nextAction = getNextAction({
    activeSource,
    modelResult,
    reportResult,
    text,
    path
  });
  const insights = activeSource
    ? [
        activeSource.dataset.plain_summary?.headline,
        modelResult?.plain_summary?.headline,
        financeResult?.plain_summary?.headline,
        reportResult?.workflow.decision_brief?.plain_language_summary?.next_step,
        modelResult?.plain_summary?.risk,
        financeResult?.plain_summary?.risk,
        ...getDatasetQualityInsights(activeSource.dataset, text)
      ]
        .filter((insight): insight is string => Boolean(insight?.trim()))
        .slice(0, 3)
    : [];
  const metrics = activeSource
    ? getDatasetMetrics(activeSource.dataset, text)
    : [];
  const trend = modelResult?.charts[0]
    ? {
        title: modelResult.charts[0].title,
        detail:
          modelResult.chart_stories?.[0]?.key_findings ??
          text(
            `模型分析已產生 ${modelResult.charts.length} 張圖表。`,
            `Model analysis produced ${modelResult.charts.length} charts.`
          ),
        href: path("/app/models")
      }
    : financeResult?.charts[0]
      ? {
          title: financeResult.charts[0].title,
          detail: financeResult.summary[0] ?? financeResult.trend_label,
          href: path("/app/finance")
        }
      : null;
  const analysisRoutes = [
    {
      href: path("/app/data"),
      label: text("資料理解", "Data understanding"),
      description: text("欄位、型別、缺失值與數值分布", "Columns, types, missing values, and distributions"),
      icon: Database,
      completed: completedStates.data
    },
    {
      href: path("/app/models"),
      label: text("模型分析", "Model analysis"),
      description: text("自動推薦、模型比較、圖表與程式碼", "Recommendations, comparison, charts, and code"),
      icon: BrainCircuit,
      completed: completedStates.model
    },
    {
      href: path("/app/finance"),
      label: text("金融分析", "Financial analysis"),
      description: text("報酬率、波動率、RSI、MACD 與預測", "Return, volatility, RSI, MACD, and forecast"),
      icon: ChartNoAxesCombined,
      completed: completedStates.finance
    },
    {
      href: path("/app/charts"),
      label: text("名詞解釋", "Terminology"),
      description: text("RMSE、MAE、R²、RSI 等指標白話說明", "Plain-language explanations for RMSE, MAE, R², RSI, and more"),
      icon: BookOpenText,
      completed: completedStates.data
    },
    {
      href: path("/app/reports"),
      label: text("分析報告", "Analysis report"),
      description: text("分析摘要、代理流程與 Word 報告", "Summary, agent workflow, and Word report"),
      icon: FileText,
      completed: completedStates.report
    }
  ];

  return (
    <>
      <PageHeader
        eyebrow={text("工作區總覽", "Workspace overview")}
        title={text("先看重點，再決定下一步", "See what matters, then choose the next step")}
        description={text(
          "所有數字都來自目前工作區的真實資料與後端分析結果。",
          "Every number comes from the current workspace and a real backend analysis."
        )}
        suppressActions={!activeSource}
        actions={
          <Button asChild variant="premium">
            <Link href={nextAction.href}>
              {nextAction.label}
              <ArrowRight aria-hidden="true" />
            </Link>
          </Button>
        }
      />

      {activeSource ? (
        <div className="dashboard-stack">
          <WorkspaceInsightGrid
            insights={insights}
            nextAction={{ label: nextAction.label, href: nextAction.href }}
            metrics={metrics}
            trend={trend}
          />

          <div className="dashboard-decision-grid is-single">
            <section className="analysis-map" aria-labelledby="analysis-map-title">
              <div className="section-title-row">
                <div>
                  <span>{text("分析地圖", "Analysis map")}</span>
                  <h2 id="analysis-map-title">{text("目前進度", "Current progress")}</h2>
                </div>
                <Badge variant="outline">
                  {Object.values(completedStates).filter(Boolean).length} / 4
                </Badge>
              </div>
              <div className="analysis-route-list">
                {analysisRoutes.map((route) => {
                  const Icon = route.icon;
                  return (
                    <Link key={route.href} href={route.href} className="analysis-route-row">
                      <span className={`route-state ${route.completed ? "is-complete" : ""}`}>
                        {route.completed ? <Check aria-hidden="true" /> : <Icon aria-hidden="true" />}
                      </span>
                      <span>
                        <strong>{route.label}</strong>
                        <small>{route.description}</small>
                      </span>
                      <Badge variant={route.completed ? "success" : "secondary"}>
                        {route.completed
                          ? text("已有結果", "Ready")
                          : text("尚未執行", "Not run")}
                      </Badge>
                    </Link>
                  );
                })}
              </div>
            </section>
          </div>

          {(modelResult || financeResult || reportResult || codeResult) ? (
            <section className="workspace-outcomes" aria-labelledby="outcomes-title">
              <div className="section-title-row">
                <div>
                  <span>{text("已完成成果", "Completed outcomes")}</span>
                  <h2 id="outcomes-title">{text("先看結論", "Start with the conclusion")}</h2>
                </div>
              </div>
              <div className="workspace-outcome-grid">
                {modelResult ? <ModelOutcome result={modelResult} /> : null}
                {financeResult ? (
                  <Outcome
                    icon={<ChartNoAxesCombined aria-hidden="true" />}
                    label={text("金融訊號", "Financial signal")}
                    title={financeResult.trend_label}
                    detail={financeResult.summary[0] ?? text("金融分析已完成。", "Financial analysis completed.")}
                    href={path("/app/finance")}
                  />
                ) : null}
                {codeResult ? (
                  <Outcome
                    icon={<FileCode2 aria-hidden="true" />}
                    label={text("程式碼", "Code")}
                    title={codeResult.file_name}
                    detail={text("Python 與 Notebook 可在頁內預覽。", "Python and notebook content can be previewed in the product.")}
                    href={path("/app/models")}
                  />
                ) : null}
                {reportResult ? (
                  <Outcome
                    icon={<FileText aria-hidden="true" />}
                    label={text("最新報告", "Latest report")}
                    title={reportResult.file_name}
                    detail={reportResult.workflow.executive_summary[0] ?? text("分析報告已完成。", "The analysis report is ready.")}
                    href={path("/app/reports")}
                  />
                ) : null}
              </div>
            </section>
          ) : null}

          <section className="source-ledger" aria-labelledby="source-ledger-title">
            <div className="section-title-row">
              <div>
                <span>{text("資料來源", "Data sources")}</span>
                <h2 id="source-ledger-title">{text("目前工作區", "Current workspace")}</h2>
              </div>
              <Badge variant="outline">
                {text(`${completedUploads.length} 個檔案`, `${completedUploads.length} files`)}
              </Badge>
            </div>
            <div className="source-ledger-list">
              {sources.map((source) => (
                <div key={source.id} className="source-ledger-row">
                  <span className="source-ledger-icon">
                    {source.isMerged ? <Layers3 aria-hidden="true" /> : <Database aria-hidden="true" />}
                  </span>
                  <span>
                    <strong>{source.label}</strong>
                    <small>{source.detail}</small>
                  </span>
                  <span className="source-ledger-meta">
                    {text(
                      `${source.dataset.recommended_target_columns?.length ?? 0} 個建議目標`,
                      `${source.dataset.recommended_target_columns?.length ?? 0} suggested targets`
                    )}
                  </span>
                </div>
              ))}
            </div>
          </section>
        </div>
      ) : (
        <WorkspaceEmptyState
          title={text("從第一份資料開始", "Start with your first dataset")}
          description={text(
            "加入真實 CSV、Excel 或 JSON 後，工作區才會顯示資料品質、分析進度與下一步建議。",
            "Add a real CSV, Excel, or JSON file to unlock quality checks, analysis progress, and next-step recommendations."
          )}
        />
      )}
    </>
  );
}

function DatasetBrief({ source }: { source: WorkspaceSource }) {
  const { text } = useLocale();
  const dataset = source.dataset;
  const totalCells = dataset.row_count * Math.max(dataset.column_count, 1);
  const missingTotal = Object.values(dataset.missing_values).reduce(
    (sum, count) => sum + count,
    0
  );
  const qualityScore = Math.max(
    0,
    Math.round((1 - missingTotal / Math.max(totalCells, 1)) * 100)
  );
  const missingColumns = Object.entries(dataset.missing_values)
    .filter(([, count]) => count > 0)
    .sort(([, left], [, right]) => right - left)
    .slice(0, 3);

  return (
    <section className="dataset-brief" aria-labelledby="dataset-brief-title">
      <div className="section-title-row">
        <div>
          <span>{text("目前資料", "Current dataset")}</span>
          <h2 id="dataset-brief-title">{source.label}</h2>
        </div>
        <Badge variant={qualityScore >= 90 ? "success" : "warning"}>
          {text(`品質 ${qualityScore}%`, `Quality ${qualityScore}%`)}
        </Badge>
      </div>
      <dl className="brief-metrics">
        <div><dt>{text("資料列", "Rows")}</dt><dd>{dataset.row_count.toLocaleString()}</dd></div>
        <div><dt>{text("欄位", "Columns")}</dt><dd>{dataset.column_count.toLocaleString()}</dd></div>
        <div><dt>{text("數值欄位", "Numeric")}</dt><dd>{Object.keys(dataset.numeric_summary).length.toLocaleString()}</dd></div>
        <div><dt>{text("缺失值", "Missing")}</dt><dd>{missingTotal.toLocaleString()}</dd></div>
      </dl>
      <div className="brief-findings">
        <h3>{text("優先注意", "Review first")}</h3>
        {missingColumns.length > 0 ? (
          <ul>
            {missingColumns.map(([column, count]) => (
              <li key={column}>
                <span>{column}</span>
                <strong>{text(`${count.toLocaleString()} 筆缺失`, `${count.toLocaleString()} missing`)}</strong>
              </li>
            ))}
          </ul>
        ) : (
          <p>{text("目前沒有偵測到缺失值，可直接進入下一階段。", "No missing values were detected. The dataset is ready for the next stage.")}</p>
        )}
      </div>
      {dataset.recommended_target_columns?.length ? (
        <div className="target-suggestions">
          <span>{text("建議目標欄位", "Suggested targets")}</span>
          <div>
            {dataset.recommended_target_columns.slice(0, 4).map((column) => (
              <Badge key={column} variant="outline">{column}</Badge>
            ))}
          </div>
        </div>
      ) : null}
    </section>
  );
}

function ModelOutcome({ result }: { result: ModelAnalysis }) {
  const { text, path } = useLocale();
  if (result.model_results.length === 0) {
    return (
      <Outcome
        icon={<BrainCircuit aria-hidden="true" />}
        label={text("模型分析", "Model analysis")}
        title={text("尚無可比較結果", "No comparable result")}
        detail={text(
          "請回到模型工作區檢查分析設定。",
          "Review the analysis settings in the model workspace."
        )}
        href={path("/app/models")}
      />
    );
  }
  const best = result.model_results.reduce((currentBest, current) => {
    if (result.problem_type === "classification") {
      return (current.f1_score ?? current.accuracy ?? 0) >
        (currentBest.f1_score ?? currentBest.accuracy ?? 0)
        ? current
        : currentBest;
    }
    return current.rmse < currentBest.rmse ? current : currentBest;
  });
  const detail =
    result.problem_type === "classification"
      ? `F1 ${formatMetric(best.f1_score)} · Accuracy ${formatMetric(best.accuracy)}`
      : `RMSE ${formatMetric(best.rmse)} · R² ${formatMetric(best.r2)}`;

  return (
    <WorkspaceDetailPanel
      title={text("模型結果詳情", "Model result details")}
      closeLabel={text("關閉詳情", "Close details")}
      trigger={
        <button type="button" className="workspace-outcome">
          <span className="workspace-outcome-icon">
            <BrainCircuit aria-hidden="true" />
          </span>
          <span>
            <small>{text("最佳模型", "Best model")}</small>
            <strong>{best.model_name}</strong>
            <p>{detail}</p>
          </span>
          <span className="workspace-outcome-link">
            {text("查看", "View")}
            <ArrowRight aria-hidden="true" />
          </span>
        </button>
      }
    >
      <div className="model-detail-summary">
        <div>
          <span>{text("目標欄位", "Target column")}</span>
          <strong>{result.target_column}</strong>
        </div>
        <div>
          <span>{text("問題類型", "Problem type")}</span>
          <strong>{result.problem_type}</strong>
        </div>
        <div>
          <span>{text("使用資料列", "Rows used")}</span>
          <strong>{result.row_count_used.toLocaleString()}</strong>
        </div>
        <div>
          <span>{text("特徵數", "Features")}</span>
          <strong>{result.feature_count_used.toLocaleString()}</strong>
        </div>
      </div>
      <div className="model-detail-ranking">
        {result.model_results.map((model, index) => (
          <div key={model.model_key}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <strong>{model.model_name}</strong>
            <small>
              {result.problem_type === "classification"
                ? `F1 ${formatMetric(model.f1_score)}`
                : `RMSE ${formatMetric(model.rmse)}`}
            </small>
          </div>
        ))}
      </div>
      <Button asChild variant="outline">
        <Link href={path("/app/models")}>
          {text("開啟模型工作區", "Open model workspace")}
          <ArrowRight aria-hidden="true" />
        </Link>
      </Button>
    </WorkspaceDetailPanel>
  );
}

function Outcome({
  icon,
  label,
  title,
  detail,
  href
}: {
  icon: React.ReactNode;
  label: string;
  title: string;
  detail: string;
  href: string;
}) {
  const { text } = useLocale();
  return (
    <Link href={href} className="workspace-outcome">
      <span className="workspace-outcome-icon">{icon}</span>
      <span>
        <small>{label}</small>
        <strong>{title}</strong>
        <p>{detail}</p>
      </span>
      <span className="workspace-outcome-link">
        {text("查看", "View")}
        <ArrowRight aria-hidden="true" />
      </span>
    </Link>
  );
}

function findResult<T>(
  panelStates: Record<string, unknown>,
  sourceKey: string,
  suffix: string,
  includes = ""
) {
  if (!sourceKey) return null;
  const result = Object.entries(panelStates).find(
    ([key, value]) =>
      key.startsWith(sourceKey) &&
      key.endsWith(suffix) &&
      key.includes(includes) &&
      value !== null &&
      value !== false
  );
  return (result?.[1] as T | undefined) ?? null;
}

function getNextAction({
  activeSource,
  modelResult,
  reportResult,
  text,
  path
}: {
  activeSource: WorkspaceSource | null;
  modelResult: ModelAnalysis | null;
  reportResult: GeneratedReport | null;
  text: (traditionalChinese: string, english: string) => string;
  path: (pathname: string) => string;
}) {
  if (!activeSource) {
    return {
      href: path("/app/data"),
      label: text("加入第一份資料", "Add your first dataset"),
      detail: text("上傳 CSV、Excel 或 JSON，建立可以持續使用的分析工作區。", "Upload a CSV, Excel, or JSON file to create a reusable analysis workspace."),
      outcome: text("完成後會先得到欄位、品質與可能目標。", "You will first get columns, quality checks, and likely targets.")
    };
  }
  if (!modelResult) {
    return {
      href: path("/app/models"),
      label: text("比較適合的模型", "Compare suitable models"),
      detail: text("系統已讀取資料輪廓，可以依目標欄位推薦候選模型。", "The dataset profile is ready, so the workspace can recommend candidates for a target column."),
      outcome: text("你會得到最佳模型、指標、圖表與可重現程式碼。", "You will get the best model, metrics, charts, and reproducible code.")
    };
  }
  if (!reportResult) {
    return {
      href: path("/app/reports"),
      label: text("整理分析報告", "Build the analysis report"),
      detail: text("模型結果已完成，可以把重點、依據與限制整理成報告。", "Model results are ready to be packaged with evidence and limitations."),
      outcome: text("報告會使用目前工作區的真實結果重新生成。", "The report will be regenerated from the current workspace results.")
    };
  }
  return {
    href: path("/app/reports"),
    label: text("回顧最新成果", "Review the latest outcome"),
    detail: text("目前工作區已完成主要分析與報告，可以檢視或加入新資料。", "The primary analysis and report are ready for review or a new dataset."),
    outcome: text("所有輸出仍保留在目前工作區。", "All outputs remain available in the current workspace.")
  };
}

function formatMetric(value: number | null) {
  return value === null ? "—" : value.toFixed(3);
}

function getDatasetQualityInsights(
  dataset: WorkspaceSource["dataset"],
  text: ReturnType<typeof useLocale>["text"]
) {
  const missing = Object.entries(dataset.missing_values)
    .filter(([, count]) => count > 0)
    .sort(([, left], [, right]) => right - left);

  if (missing.length === 0) {
    return [
      text(
        "目前未偵測到缺失值。",
        "No missing values were detected."
      )
    ];
  }

  const [column, count] = missing[0];
  return [
    text(
      `${column} 有 ${count.toLocaleString()} 筆缺失值，應先確認處理方式。`,
      `${column} has ${count.toLocaleString()} missing values and should be reviewed first.`
    )
  ];
}

function getDatasetMetrics(
  dataset: WorkspaceSource["dataset"],
  text: ReturnType<typeof useLocale>["text"]
) {
  const totalCells = dataset.row_count * Math.max(dataset.column_count, 1);
  const missingTotal = Object.values(dataset.missing_values).reduce(
    (sum, count) => sum + count,
    0
  );
  const completeness = Math.max(
    0,
    Math.round((1 - missingTotal / Math.max(totalCells, 1)) * 100)
  );
  const qualityReport = dataset.quality_report as
    | { quality_score?: number }
    | undefined;
  const qualityScore =
    typeof qualityReport?.quality_score === "number"
      ? qualityReport.quality_score
      : completeness;

  return [
    {
      label: text("資料筆數", "Rows"),
      value: dataset.row_count.toLocaleString()
    },
    {
      label: text("欄位", "Columns"),
      value: dataset.column_count.toLocaleString()
    },
    {
      label: text("可信資料品質", "Data confidence"),
      value: `${qualityScore}%`
    }
  ];
}
