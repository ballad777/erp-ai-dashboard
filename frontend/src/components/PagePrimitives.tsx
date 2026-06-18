"use client";

import Link from "next/link";
import {
  ArrowRight,
  CircleAlert,
  Database,
  LoaderCircle
} from "lucide-react";
import { motion, useReducedMotion } from "motion/react";
import { useLocale } from "@/components/LocaleProvider";
import { Button } from "@/components/ui/button";
import type { AnalysisJobProgress } from "@/lib/api";

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
  suppressActions = false
}: {
  eyebrow?: string;
  title: string;
  description: string;
  actions?: React.ReactNode;
  suppressActions?: boolean;
}) {
  return (
    <header className="page-heading">
      <div>
        {eyebrow ? <span className="page-eyebrow">{eyebrow}</span> : null}
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {actions && !suppressActions ? (
        <div className="page-heading-actions">{actions}</div>
      ) : null}
    </header>
  );
}

export function WorkspaceEmptyState({
  title,
  description,
  showAction = true
}: {
  title?: string;
  description?: string;
  showAction?: boolean;
}) {
  const { text, path } = useLocale();
  return (
    <section className="workspace-empty-state">
      <div className="empty-state-icon">
        <Database aria-hidden="true" />
      </div>
      <div>
        <h2>{title ?? text("先加入一份資料", "Add a dataset first")}</h2>
        <p>
          {description ??
            text(
              "模型、金融與報告功能會使用已讀取的真實資料，不顯示示範數據。",
              "Models, financial analysis, and reports use your ingested data and never substitute demo results."
            )}
        </p>
      </div>
      {showAction ? (
        <Button asChild variant="premium">
          <Link href={path("/app/data")}>
            {text("加入資料", "Add data")}
            <ArrowRight aria-hidden="true" />
          </Link>
        </Button>
      ) : null}
    </section>
  );
}

export function AnalysisLoadingState({
  title,
  steps,
  progress,
  onCancel,
  isCancelling = false
}: {
  title: string;
  steps: string[];
  progress?: AnalysisJobProgress | null;
  onCancel?: () => void;
  isCancelling?: boolean;
}) {
  const { text } = useLocale();
  const reducedMotion = useReducedMotion();
  const statusLabel = progress
    ? analysisStageLabel(progress.stage, text)
    : steps[0];

  return (
    <div className="analysis-loading-state" role="status" aria-live="polite">
      <div className="loading-state-header">
        <LoaderCircle aria-hidden="true" className="loading-spinner" />
        <div>
          <strong>{title}</strong>
          <motion.span
            key={progress?.stage ?? "waiting-for-backend"}
            initial={false}
            animate={{ opacity: 1, transform: "translate3d(0, 0, 0)" }}
            transition={{ duration: reducedMotion ? 0 : 0.16, ease: [0.23, 1, 0.32, 1] }}
          >
            {statusLabel}
          </motion.span>
        </div>
        {progress ? (
          <div className="loading-state-meta">
            {progress.total_items && progress.completed_items !== null ? (
              <span>
                {progress.completed_items} / {progress.total_items}
              </span>
            ) : null}
            <span>{formatElapsed(progress.elapsed_seconds, text)}</span>
          </div>
        ) : null}
      </div>
      <div
        className={`indeterminate-track ${
          progress?.total_items ? "is-determinate" : ""
        }`}
        aria-hidden="true"
      >
        <span
          style={
            progress?.total_items && progress.completed_items !== null
              ? {
                  transform: `scaleX(${Math.min(
                    1,
                    progress.completed_items / progress.total_items
                  )})`
                }
              : undefined
          }
        />
      </div>
      {onCancel ? (
        <Button
          type="button"
          variant="ghost"
          size="sm"
          disabled={isCancelling}
          onClick={onCancel}
        >
          {isCancelling
            ? text("正在取消", "Cancelling")
            : text("取消分析", "Cancel analysis")}
        </Button>
      ) : null}
    </div>
  );
}

function analysisStageLabel(
  stage: string,
  text: (traditionalChinese: string, english: string) => string
) {
  const labels: Record<string, [string, string]> = {
    queued: ["分析工作已排入佇列", "Analysis queued"],
    reading_data: ["正在讀取資料", "Reading data"],
    profiling_data: ["正在建立資料輪廓", "Building the dataset profile"],
    detecting_problem: ["正在判斷問題類型", "Detecting the analysis type"],
    detecting_columns: ["正在偵測日期與價格/指數/數值欄位", "Detecting date and price / index / value columns"],
    selecting_models: ["正在選擇候選模型", "Selecting candidate models"],
    training_models: ["正在訓練候選模型", "Training candidate models"],
    evaluating_models: ["正在比較模型結果", "Comparing model results"],
    calculating_indicators: ["正在計算金融指標", "Calculating financial indicators"],
    forecasting: ["正在建立時間序列預測", "Building the time-series forecast"],
    generating_charts: ["正在產生圖表", "Generating charts"],
    generating_insights: ["正在整理洞察與限制", "Preparing insights and limitations"],
    building_outputs: ["正在保存分析輸出", "Saving analysis outputs"],
    building_report: ["正在排版 Word 報告", "Building the Word report"],
    completed: ["分析完成", "Analysis complete"],
    cancelled: ["分析已取消", "Analysis cancelled"]
  };
  const label = labels[stage] ?? ["後端正在執行分析", "The backend is running the analysis"];
  return text(label[0], label[1]);
}

function formatElapsed(
  elapsedSeconds: number,
  text: (traditionalChinese: string, english: string) => string
) {
  const rounded = Math.max(0, Math.round(elapsedSeconds));
  return text(`已執行 ${rounded} 秒`, `${rounded}s elapsed`);
}

export function WorkspaceRestoringState() {
  const { text } = useLocale();
  return (
    <div className="workspace-restoring" role="status" aria-live="polite">
      <LoaderCircle aria-hidden="true" className="loading-spinner" />
      <div>
        <strong>{text("正在恢復工作區", "Restoring workspace")}</strong>
        <span>
          {text(
            "載入已保存的資料、分析結果與目前進度。",
            "Loading saved files, analysis results, and workspace state."
          )}
        </span>
      </div>
    </div>
  );
}

export function ResultReveal({ children }: { children: React.ReactNode }) {
  const reducedMotion = useReducedMotion();
  return (
    <motion.div
      initial={reducedMotion ? false : { opacity: 0, transform: "translate3d(0, 8px, 0)" }}
      animate={{ opacity: 1, transform: "translate3d(0, 0, 0)" }}
      transition={{ duration: reducedMotion ? 0 : 0.22, ease: [0.23, 1, 0.32, 1] }}
    >
      {children}
    </motion.div>
  );
}

export function InlineNotice({
  tone = "info",
  title,
  children
}: {
  tone?: "info" | "warning" | "error";
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className={`inline-notice is-${tone}`} role={tone === "error" ? "alert" : "status"}>
      <CircleAlert aria-hidden="true" />
      <div>
        <strong>{title}</strong>
        <div>{children}</div>
      </div>
    </div>
  );
}
