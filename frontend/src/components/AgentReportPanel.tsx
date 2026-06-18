"use client";

import { useMemo, useState } from "react";
import {
  BarChart3,
  Bot,
  Check,
  ChevronDown,
  Download,
  FileText,
  Lightbulb,
  Play
} from "lucide-react";
import { useFeedback } from "@/components/FeedbackProvider";
import { useLocale } from "@/components/LocaleProvider";
import {
  AnalysisLoadingState,
  InlineNotice,
  ResultReveal
} from "@/components/PagePrimitives";
import {
  useWorkspacePanelState,
  workspaceSourceKey
} from "@/components/WorkspaceProvider";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  cancelAnalysisJob,
  generateMergedReport,
  generateReport,
  runAgentWorkflow,
  runMergedAgentWorkflow,
  type AnalysisJobProgress,
  type AgentWorkflow,
  type DatasetAnalysis,
  type DecisionBrief,
  type GeneratedReport
} from "@/lib/api";

type AgentReportPanelProps = {
  dataset: DatasetAnalysis;
  file?: File;
  files?: File[];
  isMerged?: boolean;
  title?: string;
  description?: string;
};

type AnalysisMode = "auto" | "regression" | "classification";
type AutoMLMode = "off" | "quick";

export function AgentReportPanel({
  dataset,
  file,
  files = [],
  isMerged = false,
  title = "AI 協作分析與報告",
  description = "由資料理解、模型分析、金融分析、視覺化與報告代理完成完整分析流程，並可產生 Word 報告。"
}: AgentReportPanelProps) {
  const { isEnglish, text } = useLocale();
  const { playError, playSuccess } = useFeedback();
  const recommendedTargets = dataset.recommended_target_columns ?? [];
  const defaultTarget =
    recommendedTargets.find((column) => dataset.columns.includes(column)) ??
    dataset.columns[dataset.columns.length - 1] ??
    "";
  const sourceKey = workspaceSourceKey(file, files, isMerged);
  const [targetColumn, setTargetColumn] = useWorkspacePanelState(
    `${sourceKey}:agent:target`,
    defaultTarget
  );
  const [analysisMode, setAnalysisMode] = useWorkspacePanelState<AnalysisMode>(
    `${sourceKey}:agent:analysis-mode`,
    "auto"
  );
  const [automlMode, setAutomlMode] = useWorkspacePanelState<AutoMLMode>(
    `${sourceKey}:agent:automl`,
    "quick"
  );
  const [workflow, setWorkflow] =
    useWorkspacePanelState<AgentWorkflow | null>(
      `${sourceKey}:agent:workflow`,
      null
    );
  const [report, setReport] = useWorkspacePanelState<GeneratedReport | null>(
    `${sourceKey}:agent:report`,
    null
  );
  const [error, setError] = useWorkspacePanelState<string | null>(
    `${sourceKey}:agent:error`,
    null
  );
  const [isRunning, setIsRunning] = useWorkspacePanelState(
    `${sourceKey}:agent:running`,
    false
  );
  const [isGeneratingReport, setIsGeneratingReport] = useWorkspacePanelState(
    `${sourceKey}:agent:report-loading`,
    false
  );
  const [reportGeneratedAt, setReportGeneratedAt] = useWorkspacePanelState<string | null>(
    `${sourceKey}:agent:report-generated-at`,
    null
  );
  const [jobProgress, setJobProgress] = useState<AnalysisJobProgress | null>(null);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [isCancelling, setIsCancelling] = useState(false);

  const sourceLabel = useMemo(
    () => (
      isMerged
        ? text(`${files.length} 個檔案合併`, `${files.length} merged files`)
        : text("單一檔案", "Single file")
    ),
    [files.length, isMerged, text]
  );

  async function handleRunAgents() {
    if (!targetColumn) {
      setError(text("請先選擇分析目標欄位。", "Choose an analysis target first."));
      return;
    }
    if (isMerged && files.length < 2) {
      setError(text("合併分析至少需要 2 個成功讀取的檔案。", "Merged analysis needs at least two successfully ingested files."));
      return;
    }

    setIsRunning(true);
    setError(null);
    setWorkflow(null);
    setReport(null);
    setJobProgress(null);
    setActiveJobId(null);
    const startedAt = performance.now();

    try {
      const jobOptions = {
        onJobCreated: setActiveJobId,
        onProgress: setJobProgress
      };
      const nextWorkflow = isMerged
        ? await runMergedAgentWorkflow(
            files,
            targetColumn,
            analysisMode,
            ["auto"],
            "auto",
            ["auto"],
            automlMode,
            jobOptions
          )
        : await runAgentWorkflow(
            assertSingleFile(file),
            targetColumn,
            analysisMode,
            ["auto"],
            "auto",
            ["auto"],
            automlMode,
            jobOptions
          );
      setWorkflow(nextWorkflow);
      if (performance.now() - startedAt >= 3000) playSuccess();
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : text("協作分析失敗。", "Collaborative analysis failed.");
      if (!isCancellationMessage(message)) {
        setError(message);
        playError();
      }
    } finally {
      setIsRunning(false);
      setActiveJobId(null);
      setIsCancelling(false);
    }
  }

  async function handleGenerateReport() {
    if (!targetColumn) {
      setError(text("請先選擇報告目標欄位。", "Choose a report target first."));
      return;
    }

    setIsGeneratingReport(true);
    setError(null);
    setReport(null);
    setJobProgress(null);
    setActiveJobId(null);

    try {
      const jobOptions = {
        onJobCreated: setActiveJobId,
        onProgress: setJobProgress
      };
      const nextReport = isMerged
        ? await generateMergedReport(
            files,
            targetColumn,
            analysisMode,
            ["auto"],
            "auto",
            ["auto"],
            automlMode,
            jobOptions
          )
        : await generateReport(
            assertSingleFile(file),
            targetColumn,
            analysisMode,
            ["auto"],
            "auto",
            ["auto"],
            automlMode,
            jobOptions
          );
      setReport(nextReport);
      setWorkflow(nextReport.workflow);
      setReportGeneratedAt(new Date().toISOString());
      playSuccess();
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : text("分析報告生成失敗。", "Report generation failed.");
      if (!isCancellationMessage(message)) {
        setError(message);
        playError();
      }
    } finally {
      setIsGeneratingReport(false);
      setActiveJobId(null);
      setIsCancelling(false);
    }
  }

  async function handleCancelAnalysis() {
    if (!activeJobId || isCancelling) return;
    setIsCancelling(true);
    try {
      await cancelAnalysisJob(activeJobId);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : text("無法取消目前分析。", "Unable to cancel the current analysis.")
      );
      setIsCancelling(false);
    }
  }

  return (
    <section
      className="analysis-tool-panel"
      aria-busy={isRunning || isGeneratingReport}
    >
      <div className="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
        <div className="max-w-4xl">
          <div className="text-base font-semibold text-navy">{text("協作分析", "Collaborative analysis")}</div>
          <h2 className="mt-2 text-2xl font-semibold text-ink">
            {isEnglish && title === "AI 協作分析與報告" ? "Analysis and reports" : title}
          </h2>
          <p className="ui-copy-secondary mt-3 text-base leading-7">
            {isEnglish && description.startsWith("由資料理解")
              ? "Run data understanding, modeling, financial analysis, visualization, and report stages against the current dataset."
              : description}
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Button
            type="button"
            onClick={handleRunAgents}
            disabled={isRunning || isGeneratingReport}
            variant="outline"
            size="lg"
          >
            {isRunning ? <Spinner /> : <Play aria-hidden="true" />}
            {isRunning ? text("分析執行中", "Running analysis") : text("執行完整分析", "Run full analysis")}
          </Button>
          <Button
            type="button"
            onClick={handleGenerateReport}
            disabled={isRunning || isGeneratingReport}
            variant="premium"
            size="lg"
          >
            {isGeneratingReport ? <Spinner /> : <FileText aria-hidden="true" />}
            {isGeneratingReport ? text("報告生成中", "Generating report") : text("生成 Word 報告", "Generate Word report")}
          </Button>
        </div>
      </div>

      <div className="mt-6 grid gap-5 2xl:grid-cols-[minmax(260px,340px)_1fr]">
        <div className="space-y-4">
          <label className="block">
            <span className="text-base font-semibold text-ink">{text("目標欄位", "Target column")}</span>
            <select
              name="report-target-column"
              autoComplete="off"
              value={targetColumn}
              onChange={(event) => {
                setTargetColumn(event.target.value);
                setWorkflow(null);
                setReport(null);
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
          <label className="block">
            <span className="text-base font-semibold text-ink">{text("分析模式", "Analysis mode")}</span>
            <select
              name="report-analysis-mode"
              autoComplete="off"
              value={analysisMode}
              onChange={(event) => {
                setAnalysisMode(event.target.value as AnalysisMode);
                setWorkflow(null);
                setReport(null);
              }}
              className="mt-2 h-12 w-full rounded-md border border-line bg-white px-4 text-base text-ink outline-none transition focus:border-navy focus:ring-2 focus:ring-blue-100"
            >
              <option value="auto">{text("自動判斷", "Automatic")}</option>
              <option value="regression">{text("回歸", "Regression")}</option>
              <option value="classification">{text("分類", "Classification")}</option>
            </select>
          </label>
          <label className="block">
            <span className="text-base font-semibold text-ink">AutoML</span>
            <select
              name="report-automl-mode"
              autoComplete="off"
              value={automlMode}
              onChange={(event) => {
                setAutomlMode(event.target.value as AutoMLMode);
                setWorkflow(null);
                setReport(null);
              }}
              className="mt-2 h-12 w-full rounded-md border border-line bg-white px-4 text-base text-ink outline-none transition focus:border-navy focus:ring-2 focus:ring-blue-100"
            >
              <option value="quick">Quick AutoML</option>
              <option value="off">{text("關閉調參", "Disable tuning")}</option>
            </select>
          </label>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <MiniMetric label={text("資料來源", "Data source")} value={sourceLabel} />
          <MiniMetric label={text("欄位數", "Columns")} value={dataset.column_count.toLocaleString()} />
          <MiniMetric label={text("資料列", "Rows")} value={dataset.row_count.toLocaleString()} />
        </div>
      </div>

      {error ? (
        <InlineNotice tone="error" title={text("分析流程無法完成", "The analysis workflow could not finish")}>
          {error}
        </InlineNotice>
      ) : null}

      {isRunning || isGeneratingReport ? (
        <AnalysisLoadingState
          title={isGeneratingReport ? text("正在整理交付報告", "Preparing the deliverable report") : text("分析代理正在協作", "Analysis agents are working")}
          steps={
            isGeneratingReport
              ? [
                  text("執行資料與模型分析", "Running data and model analysis"),
                  text("提煉結論與風險說明", "Extracting findings and limitations"),
                  text("排版並輸出 Word 報告", "Formatting and exporting the Word report")
                ]
              : [
                  text("資料代理建立資料輪廓", "The data agent is building the profile"),
                  text("模型與金融代理執行分析", "Model and finance agents are running"),
                  text("報告代理整理管理摘要", "The report agent is preparing the summary")
                ]
          }
          progress={jobProgress}
          onCancel={activeJobId ? handleCancelAnalysis : undefined}
          isCancelling={isCancelling}
        />
      ) : null}

      {workflow ? (
        <ResultReveal>
          <AgentWorkflowResult workflow={workflow} />
        </ResultReveal>
      ) : null}

      {report ? (
        <ResultReveal>
        <div className="report-ready">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div className="report-ready-copy">
              <span className="report-ready-icon"><Check aria-hidden="true" /></span>
              <div>
              <h3 className="text-xl font-semibold text-ink">{text("Word 報告已生成", "Word report generated")}</h3>
              <p className="ui-copy-tertiary mt-2 break-all text-base leading-7">
                {report.report_path}
              </p>
              {reportGeneratedAt ? (
                <small className="report-generated-at">
                  {text("產生時間", "Generated")}：{new Intl.DateTimeFormat(isEnglish ? "en" : "zh-TW", {
                    dateStyle: "medium",
                    timeStyle: "short"
                  }).format(new Date(reportGeneratedAt))}
                </small>
              ) : null}
              </div>
            </div>
            <Button asChild>
              <a href={report.report_url} download>
                <Download aria-hidden="true" />
                {text("下載 Word 報告", "Download Word report")}
              </a>
            </Button>
          </div>
        </div>
        </ResultReveal>
      ) : null}
    </section>
  );
}

export function AgentWorkflowResult({ workflow }: { workflow: AgentWorkflow }) {
  const { text } = useLocale();
  const brief = workflow.decision_brief;
  const summary = brief?.executive_summary?.length
    ? brief.executive_summary
    : workflow.executive_summary;
  const plainSummary = brief?.plain_language_summary;
  const priorityFindings = brief?.priority_findings ?? [];
  const chartInterpretations = brief?.chart_interpretations ?? [];
  const modelGuidance = brief?.model_guidance;

  return (
    <div className="analysis-result-stack">
      <section className="advisor-brief-hero">
        <div className="advisor-brief-copy">
          <span className="agent-summary-icon"><Bot aria-hidden="true" /></span>
          <div>
            <span>{text("AI 顧問摘要", "AI advisor brief")}</span>
            <h3>{brief?.summary_title ?? text("把分析結果翻譯成下一步", "Analysis translated into next steps")}</h3>
            <p>{summary[0] ?? text("分析流程已完成。", "The analysis workflow is complete.")}</p>
          </div>
        </div>
        <div className="advisor-next-step">
          <span>{text("建議下一步", "Next step")}</span>
          <strong>{plainSummary?.next_step ?? summary[summary.length - 1]}</strong>
          <small>{text("摘要來源", "Summary source")}：{workflow.llm_provider}</small>
        </div>
      </section>

      {plainSummary ? <PlainLanguageSummary brief={brief} /> : null}

      {priorityFindings.length ? (
        <section className="decision-priority-section" aria-labelledby="decision-priority-heading">
          <div className="section-kicker">
            <Lightbulb aria-hidden="true" />
            <span>{text("先看這些", "Read these first")}</span>
          </div>
          <h3 id="decision-priority-heading">{text("分析結果優先級", "Result priorities")}</h3>
          <div className="decision-priority-grid">
            {priorityFindings.map((finding) => (
              <article key={`${finding.label}-${finding.title}`} className={`decision-finding is-${finding.level}`}>
                <span>{finding.label}</span>
                <h4>{finding.title}</h4>
                <p>{finding.summary}</p>
                <dl>
                  <div>
                    <dt>{text("依據", "Evidence")}</dt>
                    <dd>{finding.evidence}</dd>
                  </div>
                  <div>
                    <dt>{text("建議", "Action")}</dt>
                    <dd>{finding.recommended_action}</dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
        </section>
      ) : (
        <section className="agent-summary">
          <div className="agent-summary-heading">
            <span className="agent-summary-icon"><Bot aria-hidden="true" /></span>
            <div>
              <span>{text("管理摘要", "Executive summary")}</span>
              <h3>{summary[0] ?? text("分析流程已完成", "The analysis workflow is complete")}</h3>
            </div>
            <Badge variant="success">{text(`${workflow.agent_steps.length} 個代理完成`, `${workflow.agent_steps.length} agents complete`)}</Badge>
          </div>
          <ul>
            {summary.slice(1).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <small>{text("摘要來源", "Summary source")}：{workflow.llm_provider}</small>
        </section>
      )}

      {modelGuidance ? <ModelGuidanceSection guidance={modelGuidance} /> : null}

      {chartInterpretations.length ? (
        <details className="result-disclosure advisor-chart-disclosure" open>
          <summary>
            <span>
              <strong>{text("逐圖解讀", "Chart-by-chart interpretation")}</strong>
              <small>{text(`${chartInterpretations.length} 張圖表都有說明、發現、意義與建議`, `${chartInterpretations.length} charts include explanations, findings, meaning, and actions`)}</small>
            </span>
            <ChevronDown aria-hidden="true" />
          </summary>
          <div className="result-disclosure-content advisor-chart-list">
            {chartInterpretations.map((chart) => (
              <article key={`${chart.chart_type}-${chart.title}`} className="chart-interpretation-card">
                <div className="chart-interpretation-copy">
                  <div className="section-kicker">
                    <BarChart3 aria-hidden="true" />
                    <span>{chart.title}</span>
                  </div>
                  <InterpretationBlock label={text("圖表說明", "What it shows")} value={chart.explanation} />
                  <InterpretationBlock label={text("關鍵發現", "Key finding")} value={chart.key_findings} />
                  <InterpretationBlock label={text("代表意義", "Meaning")} value={chart.meaning} />
                  <InterpretationBlock label={text("建議行動", "Recommended action")} value={chart.recommended_action} />
                  <details className="micro-disclosure">
                    <summary>
                      {text("查看更多解讀", "More interpretation")}
                      <ChevronDown aria-hidden="true" />
                    </summary>
                    <InterpretationBlock label={text("趨勢解讀", "Trend")} value={chart.trend_interpretation} />
                    <InterpretationBlock label={text("異常說明", "Anomalies")} value={chart.anomaly_note} />
                    <InterpretationBlock label={text("商業洞察", "Business insight")} value={chart.business_insight} />
                  </details>
                </div>
                {chart.chart_url ? (
                  <figure>
                    <img src={chart.chart_url} alt={chart.title} loading="lazy" />
                  </figure>
                ) : null}
              </article>
            ))}
          </div>
        </details>
      ) : null}

      <details className="result-disclosure">
        <summary>
          <span>
            <strong>{text("查看代理執行紀錄", "View agent execution log")}</strong>
            <small>{text(`${workflow.agent_steps.length} 個分析階段與後端回傳摘要`, `${workflow.agent_steps.length} analysis stages and backend summaries`)}</small>
          </span>
          <ChevronDown aria-hidden="true" />
        </summary>
        <div className="result-disclosure-content agent-step-list">
          {workflow.agent_steps.map((step, index) => (
            <article key={`${step.agent_name}-${step.summary}`}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <div>
                <strong>{step.agent_name}</strong>
                <p>{step.summary}</p>
              </div>
              <Badge variant="success">{step.status}</Badge>
            </article>
          ))}
        </div>
      </details>
    </div>
  );
}

function PlainLanguageSummary({ brief }: { brief?: DecisionBrief }) {
  const { text } = useLocale();
  const items = [
    [text("發生了什麼", "What happened"), brief?.plain_language_summary?.what_happened],
    [text("為什麼重要", "Why it matters"), brief?.plain_language_summary?.why_it_matters],
    [text("風險", "Risks"), brief?.plain_language_summary?.risks],
    [text("機會", "Opportunities"), brief?.plain_language_summary?.opportunities]
  ].filter(([, value]) => value);

  return (
    <section className="plain-summary-grid" aria-label={text("一般人可讀摘要", "Plain-language summary")}>
      {items.map(([label, value]) => (
        <article key={label}>
          <span>{label}</span>
          <p>{value}</p>
        </article>
      ))}
    </section>
  );
}

function ModelGuidanceSection({
  guidance
}: {
  guidance: NonNullable<DecisionBrief["model_guidance"]>;
}) {
  const { text } = useLocale();
  const models = guidance.recommended_models ?? [];

  return (
    <details className="result-disclosure model-guidance-disclosure" open>
      <summary>
        <span>
          <strong>{text("模型推薦不是讓你猜", "Model recommendations explained")}</strong>
          <small>{guidance.selection_logic}</small>
        </span>
        <ChevronDown aria-hidden="true" />
      </summary>
      <div className="result-disclosure-content">
        <div className="model-guidance-headline">
          <div>
            <span>{text("分析任務", "Task")}</span>
            <strong>{guidance.problem_type_label} · {guidance.target_column}</strong>
          </div>
          <div>
            <span>Baseline</span>
            <strong>{guidance.baseline_summary}</strong>
          </div>
          <div>
            <span>{text("目前最佳", "Current best")}</span>
            <strong>{guidance.best_model_summary}</strong>
          </div>
        </div>
        <div className="model-guidance-grid">
          {models.map((model) => (
            <article key={model.model_key ?? model.model_name}>
              <div className="model-guidance-card-head">
                <div>
                  <span>{model.difficulty}</span>
                  <h4>{model.model_name}</h4>
                </div>
                <Badge variant="outline">{model.recommendation_score}</Badge>
              </div>
              <p>{model.purpose}</p>
              <InterpretationBlock label={text("為什麼推薦", "Why recommended")} value={model.why_recommended ?? ""} />
              <InterpretationBlock label={text("預期可得到", "Expected output")} value={model.expected_output ?? ""} />
              <InterpretationBlock label={text("實際評估", "Evaluation")} value={model.evaluation_summary ?? ""} />
              {model.use_cases?.length ? (
                <div className="model-use-case-list">
                  {model.use_cases.slice(0, 4).map((useCase) => (
                    <span key={useCase}>{useCase}</span>
                  ))}
                </div>
              ) : null}
            </article>
          ))}
        </div>
      </div>
    </details>
  );
}

function InterpretationBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="interpretation-block">
      <span>{label}</span>
      <p>{value}</p>
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

function assertSingleFile(file: File | undefined): File {
  if (!file) {
    throw new Error("缺少 AI 分析需要的檔案。");
  }

  return file;
}

function isCancellationMessage(message: string) {
  return message.includes("已取消") || message.toLowerCase().includes("cancelled");
}
