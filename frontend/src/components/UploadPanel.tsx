"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  AlertTriangle,
  Check,
  ChevronDown,
  CloudUpload,
  FileSpreadsheet,
  GitBranch,
  HardDrive,
  Plus,
  RefreshCw,
  Trash2,
  X
} from "lucide-react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { AnalysisResult } from "@/components/AnalysisResult";
import { useFeedback } from "@/components/FeedbackProvider";
import { useLocale } from "@/components/LocaleProvider";
import {
  AnalysisLoadingState,
  InlineNotice,
  PageHeader
} from "@/components/PagePrimitives";
import {
  useWorkspace,
  type DatasetUploadState
} from "@/components/WorkspaceProvider";
import {
  WorkspaceSourceSelect,
  useWorkspaceSources
} from "@/components/WorkspaceSource";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  analyzeDatasets,
  cleanupAllModels,
  cleanupLatestOnly,
  cleanupOldModels,
  getStorageStatus,
  type MultiTablePlan,
  type StorageStatus
} from "@/lib/api";

const acceptedTypes = ".csv,.xlsx,.xls,.json,application/json";
const maxFileBytes = 25 * 1024 * 1024;
const maxUploadFiles = 20;
const maxBatchBytes = 100 * 1024 * 1024;

type WorkspaceNotice = {
  tone: "success" | "info" | "warning" | "error";
  title: string;
  detail: string;
};

export function UploadPanel() {
  const { text } = useLocale();
  const { playError, playSuccess } = useFeedback();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const {
    uploads,
    setUploads,
    mergedResult,
    setMergedResult,
    multiTablePlan,
    setMultiTablePlan,
    batchNotes,
    setBatchNotes,
    error,
    setError,
    setPanelStates,
    setActiveSourceId,
    clearWorkspace
  } = useWorkspace();
  const { activeSource } = useWorkspaceSources();
  const [notice, setNotice] = useState<WorkspaceNotice | null>(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const [clearArmed, setClearArmed] = useState(false);

  const isLoading = uploads.some((upload) => upload.isLoading);
  const completedCount = uploads.filter((upload) => upload.result).length;
  const failedCount = uploads.filter((upload) => upload.error).length;

  const totalSizeLabel = useMemo(() => {
    const totalBytes = uploads.reduce((sum, upload) => sum + upload.file.size, 0);
    if (totalBytes === 0) return "0 MB";
    return `${(totalBytes / 1024 / 1024).toFixed(2)} MB`;
  }, [uploads]);

  useEffect(() => {
    if (!notice) return;
    const timer = window.setTimeout(() => setNotice(null), 4200);
    return () => window.clearTimeout(timer);
  }, [notice]);

  useEffect(() => {
    if (!clearArmed) return;
    const timer = window.setTimeout(() => setClearArmed(false), 3200);
    return () => window.clearTimeout(timer);
  }, [clearArmed]);

  function addFiles(files: File[]) {
    const existingIds = new Set(uploads.map((upload) => upload.id));
    const seenIds = new Set(existingIds);
    const newUploads: DatasetUploadState[] = [];
    const rejectionReasons = new Set<string>();
    let nextTotalBytes = uploads.reduce((sum, upload) => sum + upload.file.size, 0);

    for (const file of files) {
      if (!isAcceptedFile(file)) {
        rejectionReasons.add(text("格式不支援", "Unsupported format"));
        continue;
      }
      if (file.size > maxFileBytes) {
        rejectionReasons.add(text("單檔超過 25 MB", "A file exceeds 25 MB"));
        continue;
      }

      const upload = createUpload(file);
      if (seenIds.has(upload.id)) {
        rejectionReasons.add(text("檔案重複", "Duplicate file"));
        continue;
      }
      if (seenIds.size >= maxUploadFiles) {
        rejectionReasons.add(text(`最多 ${maxUploadFiles} 個檔案`, `Maximum ${maxUploadFiles} files`));
        continue;
      }
      if (nextTotalBytes + file.size > maxBatchBytes) {
        rejectionReasons.add(text("總容量超過 100 MB", "Batch exceeds 100 MB"));
        continue;
      }

      seenIds.add(upload.id);
      nextTotalBytes += file.size;
      newUploads.push(upload);
    }

    setUploads((current) => {
      const currentIds = new Set(current.map((upload) => upload.id));
      return [...current, ...newUploads.filter((upload) => !currentIds.has(upload.id))];
    });
    setMergedResult(null);
    setMultiTablePlan(null);
    setBatchNotes([]);
    setError(null);

    if (newUploads.length > 0) {
      setNotice({
        tone: rejectionReasons.size > 0 ? "warning" : "info",
        title: text("檔案已加入", "Files added"),
        detail:
          rejectionReasons.size > 0
            ? text(
                `${newUploads.length} 個已加入；其餘未加入：${Array.from(rejectionReasons).join("、")}。`,
                `${newUploads.length} added. Others were skipped: ${Array.from(rejectionReasons).join(", ")}.`
              )
            : text(
                `${newUploads.length} 個檔案等待讀取。`,
                `${newUploads.length} files are waiting to be ingested.`
              )
      });
    } else if (files.length > 0) {
      setNotice({
        tone: "warning",
        title: text("沒有新增檔案", "No new files added"),
        detail:
          rejectionReasons.size > 0
            ? Array.from(rejectionReasons).join("、")
            : text("選取的檔案已在佇列中。", "The selected files are already in the queue.")
      });
    }
  }

  async function analyzeUploads() {
    if (uploads.length === 0) {
      setError(text("請先加入至少一個 CSV、Excel 或 JSON 檔案。", "Add at least one CSV, Excel, or JSON file first."));
      return;
    }

    setError(null);
    setMergedResult(null);
    setMultiTablePlan(null);
    setBatchNotes([]);
    setPanelStates({});
    setUploads((current) =>
      current.map((upload) => ({
        ...upload,
        result: null,
        error: null,
        isLoading: true
      }))
    );

    try {
      const batchResult = await analyzeDatasets(uploads.map((upload) => upload.file));
      setUploads((current) =>
        current.map((upload, index) => {
          const item = batchResult.datasets[index];
          return {
            ...upload,
            result: item?.success ? item.analysis : null,
            error: item?.success ? null : item?.error ?? text("資料集分析失敗。", "Dataset analysis failed."),
            isLoading: false
          };
        })
      );
      setMergedResult(batchResult.merged);
      setMultiTablePlan(batchResult.multi_table_plan ?? null);
      setBatchNotes(batchResult.notes);

      const firstSuccessfulIndex = batchResult.datasets.findIndex((item) => item.success);
      setActiveSourceId(
        batchResult.merged
          ? "merged"
          : firstSuccessfulIndex >= 0
            ? uploads[firstSuccessfulIndex].id
            : null
      );

      const successfulCount = batchResult.datasets.filter((item) => item.success).length;
      const unsuccessfulCount = batchResult.datasets.length - successfulCount;
      setNotice({
        tone: unsuccessfulCount > 0 ? "warning" : "success",
        title: unsuccessfulCount > 0
          ? text("部分檔案需要檢查", "Some files need attention")
          : text("資料讀取完成", "Data ingestion complete"),
        detail:
          unsuccessfulCount > 0
            ? text(
                `${successfulCount} 個成功，${unsuccessfulCount} 個失敗。`,
                `${successfulCount} succeeded and ${unsuccessfulCount} failed.`
              )
            : text(
                `${successfulCount} 個檔案已由後端完成分析。`,
                `${successfulCount} files were analyzed by the backend.`
              )
      });
      playSuccess();
    } catch (caughtError) {
      setUploads((current) =>
        current.map((upload) => ({ ...upload, isLoading: false }))
      );
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : text("多檔資料集分析失敗。", "Multi-file analysis failed.");
      setError(message);
      setNotice({
        tone: "error",
        title: text("資料讀取失敗", "Data ingestion failed"),
        detail: message
      });
      playError();
    }
  }

  function removeUpload(id: string) {
    const removedFile = uploads.find((upload) => upload.id === id);
    setUploads((current) => current.filter((upload) => upload.id !== id));
    setMergedResult(null);
    setMultiTablePlan(null);
    setBatchNotes([]);
    setError(null);
    setPanelStates({});
    setNotice({
      tone: "info",
      title: text("已移除檔案", "File removed"),
      detail: removedFile?.file.name ?? text("檔案已移除。", "The file was removed.")
    });
  }

  function handleClear() {
    if (!clearArmed) {
      setClearArmed(true);
      return;
    }
    clearWorkspace();
    setClearArmed(false);
    setNotice({
      tone: "info",
      title: text("工作區已清空", "Workspace cleared"),
      detail: text("檔案與目前分析狀態已重置。", "Files and current analysis state were reset.")
    });
  }

  return (
    <>
      <AnimatePresence initial={false}>
        {notice ? (
          <WorkspaceToast notice={notice} onClose={() => setNotice(null)} />
        ) : null}
      </AnimatePresence>

      <PageHeader
        eyebrow={text("資料工作區", "Data workspace")}
        title={text("先整理資料，再開始分析", "Prepare the data before analyzing")}
        description={text(
          "一次加入多個 CSV、Excel 或 JSON。後端會回傳真實欄位、缺失值、品質檢查與數值摘要。",
          "Add multiple CSV, Excel, or JSON files. The backend returns real columns, missing-value counts, quality checks, and numeric summaries."
        )}
        actions={
          <Button type="button" variant="premium" onClick={() => inputRef.current?.click()}>
            <Plus aria-hidden="true" />
            {text("加入檔案", "Add files")}
          </Button>
        }
      />

      <div className="data-workspace-grid">
        <form
          className="data-intake-panel"
          onSubmit={(event) => {
            event.preventDefault();
            void analyzeUploads();
          }}
        >
          <div className="panel-heading-row">
            <div>
              <span>{text("資料匯入", "Data intake")}</span>
              <h2>{text("上傳佇列", "Upload queue")}</h2>
            </div>
            <Badge variant={completedCount > 0 ? "success" : "outline"}>
              {completedCount > 0
                ? text(`${completedCount} 個可分析`, `${completedCount} ready`)
                : text("等待資料", "Waiting for data")}
            </Badge>
          </div>

          <div
            className={`data-dropzone ${isDragActive ? "is-drag-active" : ""}`}
            onDragEnter={(event) => {
              event.preventDefault();
              setIsDragActive(true);
            }}
            onDragOver={(event) => event.preventDefault()}
            onDragLeave={(event) => {
              if (!event.currentTarget.contains(event.relatedTarget as Node | null)) {
                setIsDragActive(false);
              }
            }}
            onDrop={(event) => {
              event.preventDefault();
              setIsDragActive(false);
              addFiles(Array.from(event.dataTransfer.files));
            }}
          >
            <input
              ref={inputRef}
              className="sr-only"
              type="file"
              name="datasets"
              autoComplete="off"
              accept={acceptedTypes}
              multiple
              onChange={(event) => {
                addFiles(Array.from(event.target.files ?? []));
                event.target.value = "";
              }}
            />
            <span className="dropzone-symbol">
              <CloudUpload aria-hidden="true" />
            </span>
            <div>
              <h3>{isDragActive ? text("放開即可加入", "Drop to add") : text("拖曳檔案到這裡", "Drag files here")}</h3>
              <p>{text("CSV、XLSX、XLS、JSON；單檔 25 MB，最多 20 檔、合計 100 MB。", "CSV, XLSX, XLS, or JSON. Up to 25 MB each, 20 files, and 100 MB total.")}</p>
            </div>
            <Button type="button" variant="outline" onClick={() => inputRef.current?.click()}>
              {text("選擇檔案", "Choose files")}
            </Button>
          </div>

          {uploads.length > 0 ? (
            <>
              <dl className="intake-metrics">
                <div><dt>{text("檔案", "Files")}</dt><dd>{uploads.length}</dd></div>
                <div><dt>{text("大小", "Size")}</dt><dd>{totalSizeLabel}</dd></div>
                <div><dt>{text("成功", "Ready")}</dt><dd>{completedCount}</dd></div>
                <div><dt>{text("失敗", "Failed")}</dt><dd>{failedCount}</dd></div>
              </dl>

              <div className="upload-queue" aria-label={text("上傳檔案佇列", "Upload queue")}>
                {uploads.map((upload) => (
                  <div key={upload.id} className="upload-queue-row">
                    <span className="queue-file-icon">
                      <FileSpreadsheet aria-hidden="true" />
                    </span>
                    <span className="queue-file-name">
                      <strong>{upload.file.name}</strong>
                      <small>{formatBytes(upload.file.size)}</small>
                    </span>
                    <FileState upload={upload} />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon-sm"
                      aria-label={text(`移除 ${upload.file.name}`, `Remove ${upload.file.name}`)}
                      disabled={isLoading}
                      onClick={() => removeUpload(upload.id)}
                    >
                      <X aria-hidden="true" />
                    </Button>
                  </div>
                ))}
              </div>

              <div className="intake-actions">
                <Button
                  type="button"
                  variant={clearArmed ? "destructive" : "ghost"}
                  disabled={isLoading}
                  onClick={handleClear}
                >
                  <Trash2 aria-hidden="true" />
                  {clearArmed
                    ? text("再次點擊確認清空", "Click again to clear")
                    : text("清空", "Clear")}
                </Button>
                <Button type="submit" variant="premium" disabled={isLoading}>
                  {isLoading ? text("讀取中", "Ingesting") : text("讀取全部", "Ingest all")}
                </Button>
              </div>
            </>
          ) : null}

          {isLoading ? (
            <AnalysisLoadingState
              title={text("正在建立資料輪廓", "Building dataset profiles")}
              steps={[
                text("解析檔案與欄位型別", "Parsing files and column types"),
                text("計算缺失值與數值分布", "Calculating missing values and numeric distributions"),
                text("建立合併資料摘要", "Building the merged dataset summary")
              ]}
            />
          ) : null}

          {error ? (
            <InlineNotice tone="error" title={text("無法讀取資料", "Unable to ingest data")}>
              {error}
            </InlineNotice>
          ) : null}

          {batchNotes.length > 0 ? (
            <details className="data-notes">
              <summary>
                <span>{text("批次讀取備註", "Batch ingestion notes")}</span>
                <ChevronDown aria-hidden="true" />
              </summary>
              <ul>
                {batchNotes.map((note) => <li key={note}>{note}</li>)}
              </ul>
            </details>
          ) : null}
        </form>

        <aside className="data-flow-panel" aria-labelledby="data-flow-title">
          <div className="panel-heading-row">
            <div>
              <span>{text("處理流程", "Process")}</span>
              <h2 id="data-flow-title">{text("資料準備狀態", "Data readiness")}</h2>
            </div>
          </div>
          <ol className="data-flow-list">
            <FlowStep
              title={text("資料理解", "Data understanding")}
              detail={completedCount > 0 ? text(`${completedCount} 個檔案已完成輪廓`, `${completedCount} profiles ready`) : uploads.length > 0 ? text("等待後端讀取", "Waiting for backend") : text("尚未加入資料", "No files yet")}
              complete={uploads.length > 0}
              active={uploads.length === 0}
            />
            <FlowStep
              title={text("合併策略", "Merge strategy")}
              detail={multiTablePlan?.label ?? (completedCount > 1 ? text("等待策略", "Waiting for strategy") : text("單檔不需合併", "Single file"))}
              complete={Boolean(multiTablePlan) || completedCount === 1}
              active={isLoading}
            />
            <FlowStep
              title={text("分析目標", "Analysis goal")}
              detail={activeSource ? text("確認目標後再建模", "Confirm the goal before modeling") : text("讀取後啟用", "Enabled after ingestion")}
              complete={Boolean(activeSource)}
              active={!isLoading && completedCount > 0 && !activeSource}
            />
            <FlowStep
              title={text("模型 / 圖表 / 報告", "Models / charts / reports")}
              detail={activeSource ? text("依確認目的執行", "Run after confirmation") : text("等待資料", "Waiting for data")}
              complete={false}
              active={false}
            />
          </ol>
          <StorageManagement />
        </aside>
      </div>

      {activeSource ? (
        <section className="data-explorer">
          <div className="explorer-toolbar">
            <div>
              <span>{text("資料探索", "Data exploration")}</span>
              <h2>{text("重點先行，細節按需展開", "Start with key findings and reveal detail as needed")}</h2>
            </div>
            <WorkspaceSourceSelect />
          </div>
          {activeSource.isMerged && mergedResult?.merge_notes.length ? (
            <InlineNotice title={text("合併方式", "Merge method")}>
              {mergedResult.merge_notes[0]}
            </InlineNotice>
          ) : null}
          {multiTablePlan ? <MergeStrategyPanel plan={multiTablePlan} /> : null}
          <AnalysisResult result={activeSource.dataset} />
        </section>
      ) : null}
    </>
  );
}

function WorkspaceToast({
  notice,
  onClose
}: {
  notice: WorkspaceNotice;
  onClose: () => void;
}) {
  const { text } = useLocale();
  const reducedMotion = useReducedMotion();
  return (
    <motion.div
      className={`workspace-toast is-${notice.tone}`}
      role={notice.tone === "error" ? "alert" : "status"}
      aria-live="polite"
      initial={reducedMotion ? false : { opacity: 0, transform: "translate3d(0, -12px, 0) scale(.98)" }}
      animate={{ opacity: 1, transform: "translate3d(0, 0, 0) scale(1)" }}
      exit={{ opacity: 0, transform: reducedMotion ? "none" : "translate3d(0, -6px, 0) scale(.99)" }}
      transition={{ duration: reducedMotion ? 0 : 0.18, ease: [0.23, 1, 0.32, 1] }}
    >
      <span className="workspace-toast-dot" />
      <div>
        <strong>{notice.title}</strong>
        <p>{notice.detail}</p>
      </div>
      <button type="button" onClick={onClose} aria-label={text("關閉通知", "Close notification")}>
        <X aria-hidden="true" />
      </button>
    </motion.div>
  );
}

function FileState({ upload }: { upload: DatasetUploadState }) {
  const { text } = useLocale();
  if (upload.isLoading) return <Badge variant="secondary">{text("讀取中", "Ingesting")}</Badge>;
  if (upload.result) return <Badge variant="success"><Check aria-hidden="true" />{text("已讀取", "Ready")}</Badge>;
  if (upload.error) return <Badge variant="destructive">{text("失敗", "Failed")}</Badge>;
  return <Badge variant="outline">{text("等待", "Waiting")}</Badge>;
}

function MergeStrategyPanel({ plan }: { plan: MultiTablePlan }) {
  const { text } = useLocale();
  const keys = plan.join_key_candidates ?? [];
  const warnings = plan.warnings ?? [];
  return (
    <section className="merge-strategy-panel" aria-labelledby="merge-strategy-title">
      <div className="panel-heading-row">
        <div>
          <span>{text("合併策略", "Merge strategy")}</span>
          <h2 id="merge-strategy-title">{plan.label ?? text("策略待確認", "Strategy pending")}</h2>
        </div>
        <Badge variant={plan.recommended_strategy === "multi_table_relationship" ? "success" : "outline"}>
          {plan.confidence_score ? `${plan.confidence_score}%` : text("需確認", "Review")}
        </Badge>
      </div>
      {plan.reason ? <p className="strategy-reason">{plan.reason}</p> : null}
      {keys.length > 0 ? (
        <div className="strategy-key-grid">
          {keys.slice(0, 6).map((candidate) => (
            <div key={`${candidate.key}-${candidate.files?.join("-")}`} className="strategy-key-card">
              <GitBranch aria-hidden="true" />
              <span>{candidate.key}</span>
              <small>{candidate.files?.slice(0, 3).join("、")}</small>
            </div>
          ))}
        </div>
      ) : null}
      {warnings.length > 0 ? (
        <InlineNotice tone="warning" title={text("合併前請確認", "Check before merging")}>
          {warnings.join(" ")}
        </InlineNotice>
      ) : null}
    </section>
  );
}

function StorageManagement() {
  const { text } = useLocale();
  const [status, setStatus] = useState<StorageStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void getStorageStatus()
      .then((nextStatus) => {
        if (!cancelled) setStatus(nextStatus);
      })
      .catch(() => {
        if (!cancelled) setMessage(text("儲存空間狀態暫時無法讀取。", "Storage status is temporarily unavailable."));
      });
    return () => {
      cancelled = true;
    };
  }, [text]);

  async function runCleanup(action: "old" | "all" | "latest") {
    setIsLoading(true);
    setMessage(null);
    try {
      const response =
        action === "old"
          ? await cleanupOldModels()
          : action === "all"
            ? await cleanupAllModels()
            : await cleanupLatestOnly();
      setStatus(response.status);
      setMessage(text("儲存空間已更新。", "Storage has been updated."));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : text("清理失敗。", "Cleanup failed."));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="storage-management-panel" aria-labelledby="storage-management-title">
      <div className="panel-heading-row">
        <div>
          <span>{text("儲存空間", "Storage")}</span>
          <h2 id="storage-management-title">{text("輸出管理", "Output management")}</h2>
        </div>
        <HardDrive aria-hidden="true" />
      </div>
      {status ? (
        <>
          <dl className="storage-metric-grid">
            <div><dt>{text("總量", "Total")}</dt><dd>{formatMegabytes(status.generated_outputs.mb)}</dd></div>
            <div><dt>{text("模型", "Models")}</dt><dd>{formatMegabytes(status.models.mb)}</dd></div>
            <div><dt>{text("圖表", "Charts")}</dt><dd>{formatMegabytes(status.charts.mb)}</dd></div>
            <div><dt>{text("報告", "Reports")}</dt><dd>{formatMegabytes(status.reports.mb)}</dd></div>
          </dl>
          {status.warning ? (
            <InlineNotice tone="error" title={text("模型資料夾過大", "Model folder is too large")}>
              {status.warning_message ?? text("模型輸出資料夾過大，建議清理舊模型。", "The model output folder is too large. Clean old models.")}
            </InlineNotice>
          ) : null}
        </>
      ) : (
        <p className="storage-placeholder">{text("正在讀取儲存狀態。", "Reading storage status.")}</p>
      )}
      {message ? (
        <p className="storage-message">
          <AlertTriangle aria-hidden="true" />
          {message}
        </p>
      ) : null}
      <div className="storage-actions">
        <Button type="button" variant="outline" size="sm" disabled={isLoading} onClick={() => void runCleanup("old")}>
          <RefreshCw aria-hidden="true" />
          {text("清除舊模型", "Clean old models")}
        </Button>
        <Button type="button" variant="outline" size="sm" disabled={isLoading} onClick={() => void runCleanup("latest")}>
          {text("只保留最新", "Keep latest")}
        </Button>
        <Button type="button" variant="destructive" size="sm" disabled={isLoading} onClick={() => void runCleanup("all")}>
          {text("清除全部模型", "Clear all models")}
        </Button>
      </div>
    </section>
  );
}

function FlowStep({
  title,
  detail,
  complete,
  active
}: {
  title: string;
  detail: string;
  complete: boolean;
  active: boolean;
}) {
  return (
    <li className={`${complete ? "is-complete" : ""} ${active ? "is-active" : ""}`}>
      <span>{complete ? <Check aria-hidden="true" /> : null}</span>
      <div>
        <strong>{title}</strong>
        <small>{detail}</small>
      </div>
    </li>
  );
}

function createUpload(file: File): DatasetUploadState {
  return {
    id: `${file.name}-${file.lastModified}-${file.size}`,
    file,
    result: null,
    error: null,
    isLoading: false
  };
}

function isAcceptedFile(file: File) {
  return /\.(csv|xlsx|xls|json)$/i.test(file.name);
}

function formatBytes(bytes: number) {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

function formatMegabytes(value: number) {
  if (value >= 1024) return `${(value / 1024).toFixed(2)} GB`;
  return `${value.toFixed(2)} MB`;
}
