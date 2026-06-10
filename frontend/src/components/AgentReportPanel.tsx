"use client";

import { useMemo } from "react";
import {
  useWorkspacePanelState,
  workspaceSourceKey
} from "@/components/WorkspaceProvider";
import {
  generateMergedReport,
  generateReport,
  runAgentWorkflow,
  runMergedAgentWorkflow,
  type AgentWorkflow,
  type DatasetAnalysis,
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

  const sourceLabel = useMemo(
    () => (isMerged ? `${files.length} 個檔案合併` : "單一檔案"),
    [files.length, isMerged]
  );

  async function handleRunAgents() {
    if (!targetColumn) {
      setError("請先選擇分析目標欄位。");
      return;
    }
    if (isMerged && files.length < 2) {
      setError("合併分析至少需要 2 個成功讀取的檔案。");
      return;
    }

    setIsRunning(true);
    setError(null);
    setWorkflow(null);
    setReport(null);

    try {
      const nextWorkflow = isMerged
        ? await runMergedAgentWorkflow(
            files,
            targetColumn,
            analysisMode,
            ["auto"],
            "auto",
            ["auto"],
            automlMode
          )
        : await runAgentWorkflow(
            assertSingleFile(file),
            targetColumn,
            analysisMode,
            ["auto"],
            "auto",
            ["auto"],
            automlMode
          );
      setWorkflow(nextWorkflow);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "AI 協作分析失敗。");
    } finally {
      setIsRunning(false);
    }
  }

  async function handleGenerateReport() {
    if (!targetColumn) {
      setError("請先選擇報告目標欄位。");
      return;
    }

    setIsGeneratingReport(true);
    setError(null);
    setReport(null);

    try {
      const nextReport = isMerged
        ? await generateMergedReport(
            files,
            targetColumn,
            analysisMode,
            ["auto"],
            "auto",
            ["auto"],
            automlMode
          )
        : await generateReport(
            assertSingleFile(file),
            targetColumn,
            analysisMode,
            ["auto"],
            "auto",
            ["auto"],
            automlMode
          );
      setReport(nextReport);
      setWorkflow(nextReport.workflow);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "分析報告生成失敗。");
    } finally {
      setIsGeneratingReport(false);
    }
  }

  return (
    <section className="surface-card p-6 sm:p-7">
      <div className="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
        <div className="max-w-4xl">
          <div className="text-base font-semibold text-navy">AI 協作分析</div>
          <h2 className="mt-2 text-2xl font-semibold text-ink">{title}</h2>
          <p className="mt-3 text-base leading-7 text-muted">{description}</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={handleRunAgents}
            disabled={isRunning || isGeneratingReport}
            className="h-12 rounded-xl bg-navy px-6 text-base font-semibold text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {isRunning ? "分析執行中..." : "執行 AI 分析"}
          </button>
          <button
            type="button"
            onClick={handleGenerateReport}
            disabled={isRunning || isGeneratingReport}
            className="glow-button h-12 rounded-xl bg-gradient-to-r from-brand via-sky-500 to-navy px-6 text-base font-semibold text-white transition disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {isGeneratingReport ? "報告生成中..." : "生成 Word 報告"}
          </button>
        </div>
      </div>

      <div className="mt-6 grid gap-5 2xl:grid-cols-[minmax(260px,340px)_1fr]">
        <div className="space-y-4">
          <label className="block">
            <span className="text-base font-semibold text-ink">目標欄位</span>
            <select
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
            <span className="text-base font-semibold text-ink">分析模式</span>
            <select
              value={analysisMode}
              onChange={(event) => {
                setAnalysisMode(event.target.value as AnalysisMode);
                setWorkflow(null);
                setReport(null);
              }}
              className="mt-2 h-12 w-full rounded-md border border-line bg-white px-4 text-base text-ink outline-none transition focus:border-navy focus:ring-2 focus:ring-blue-100"
            >
              <option value="auto">自動判斷</option>
              <option value="regression">回歸</option>
              <option value="classification">分類</option>
            </select>
          </label>
          <label className="block">
            <span className="text-base font-semibold text-ink">AutoML</span>
            <select
              value={automlMode}
              onChange={(event) => {
                setAutomlMode(event.target.value as AutoMLMode);
                setWorkflow(null);
                setReport(null);
              }}
              className="mt-2 h-12 w-full rounded-md border border-line bg-white px-4 text-base text-ink outline-none transition focus:border-navy focus:ring-2 focus:ring-blue-100"
            >
              <option value="quick">Quick AutoML</option>
              <option value="off">關閉調參</option>
            </select>
          </label>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <MiniMetric label="資料來源" value={sourceLabel} />
          <MiniMetric label="欄位數" value={dataset.column_count.toLocaleString()} />
          <MiniMetric label="資料列" value={dataset.row_count.toLocaleString()} />
        </div>
      </div>

      {error ? (
        <div className="mt-6 rounded-md border border-red-200 bg-red-50 px-5 py-4 text-base font-medium text-red-700">
          {error}
        </div>
      ) : null}

      {workflow ? <AgentWorkflowResult workflow={workflow} /> : null}

      {report ? (
        <div className="mt-6 rounded-md border border-brand bg-teal-50 p-5">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div>
              <h3 className="text-xl font-semibold text-ink">Word 報告已生成</h3>
              <p className="mt-2 break-all text-base leading-7 text-muted">
                {report.report_path}
              </p>
            </div>
            <a
              href={report.report_url}
              download
              className="rounded-md bg-brand px-5 py-3 text-base font-semibold text-white transition hover:bg-teal-800"
            >
              下載 analysis_report.docx
            </a>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function AgentWorkflowResult({ workflow }: { workflow: AgentWorkflow }) {
  return (
    <div className="mt-7 space-y-6">
      <div className="rounded-2xl border border-blue-100 bg-slate-50/80 p-5">
        <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h3 className="text-xl font-semibold text-ink">AI 摘要</h3>
            <p className="mt-1 text-base text-muted">摘要來源：{workflow.llm_provider}</p>
          </div>
          <MiniMetric label="分析代理" value={`${workflow.agent_steps.length}`} />
        </div>
        <ul className="mt-4 space-y-2 text-base leading-7 text-muted">
          {workflow.executive_summary.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>

      <div className="grid gap-4 xl:grid-cols-5">
        {workflow.agent_steps.map((step) => (
          <article key={`${step.agent_name}-${step.summary}`} className="rounded-md border border-line bg-white p-4">
            <div className="text-sm font-semibold text-navy">{step.agent_name}</div>
            <div className="mt-2 text-base font-semibold text-ink">{step.status}</div>
            <p className="mt-2 text-sm leading-6 text-muted">{step.summary}</p>
          </article>
        ))}
      </div>
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

function assertSingleFile(file: File | undefined): File {
  if (!file) {
    throw new Error("缺少 AI 分析需要的檔案。");
  }

  return file;
}
