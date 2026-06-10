"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AgentReportPanel } from "@/components/AgentReportPanel";
import { AnalysisResult } from "@/components/AnalysisResult";
import { FinancialAnalysisPanel } from "@/components/FinancialAnalysisPanel";
import { ModelAnalysisPanel } from "@/components/ModelAnalysisPanel";
import { SystemStatus } from "@/components/SystemStatus";
import {
  analyzeDatasets,
  type DatasetAnalysis,
  type MergedDatasetAnalysis
} from "@/lib/api";

const acceptedTypes = ".csv,.xlsx,.xls";

type DatasetUpload = {
  id: string;
  file: File;
  result: DatasetAnalysis | null;
  error: string | null;
  isLoading: boolean;
};

type ProgressStatus = "complete" | "active" | "ready" | "waiting" | "error";

type ProgressStep = {
  title: string;
  detail: string;
  status: ProgressStatus;
};

export function UploadPanel() {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const formRef = useRef<HTMLFormElement | null>(null);
  const [uploads, setUploads] = useState<DatasetUpload[]>([]);
  const [mergedResult, setMergedResult] = useState<MergedDatasetAnalysis | null>(null);
  const [batchNotes, setBatchNotes] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const isLoading = uploads.some((upload) => upload.isLoading);
  const completedUploads = uploads.filter((upload) => upload.result);
  const completedCount = completedUploads.length;
  const failedCount = uploads.filter((upload) => upload.error).length;
  const mergedFiles = completedUploads.map((upload) => upload.file);
  const workspaceState = isLoading
    ? "讀取中"
    : uploads.length === 0
      ? "等待資料"
      : failedCount > 0
        ? "需要檢查"
        : completedCount > 0
          ? "可進行分析"
          : "準備讀取";
  const readinessPercent =
    uploads.length === 0
      ? 0
      : Math.round(((completedCount + (isLoading ? 0.35 : 0)) / uploads.length) * 100);

  const totalSizeLabel = useMemo(() => {
    const totalBytes = uploads.reduce((sum, upload) => sum + upload.file.size, 0);
    if (totalBytes === 0) return "0 MB";
    return `${(totalBytes / 1024 / 1024).toFixed(2)} MB`;
  }, [uploads]);

  const progressSteps = useMemo<ProgressStep[]>(() => {
    const uploadStatus: ProgressStatus = uploads.length > 0 ? "complete" : "waiting";
    const readStatus: ProgressStatus = failedCount > 0
      ? "error"
      : isLoading
        ? "active"
        : completedCount > 0
          ? "complete"
          : uploads.length > 0
            ? "ready"
            : "waiting";
    const exploreStatus: ProgressStatus = completedCount > 0
      ? "complete"
      : isLoading
        ? "active"
        : "waiting";
    const mergeStatus: ProgressStatus = mergedResult
      ? "complete"
      : completedCount >= 2
        ? "ready"
        : "waiting";
    const analysisStatus: ProgressStatus = completedCount > 0 ? "ready" : "waiting";

    return [
      {
        title: "資料上傳",
        detail: uploads.length > 0 ? `已加入 ${uploads.length} 檔` : "等待加入檔案",
        status: uploadStatus
      },
      {
        title: "資料讀取",
        detail: isLoading ? "後端正在解析檔案" : `${completedCount} 成功 / ${failedCount} 失敗`,
        status: readStatus
      },
      {
        title: "資料探索",
        detail: completedCount > 0 ? "欄位、缺失值與摘要已回傳" : "讀取後自動建立",
        status: exploreStatus
      },
      {
        title: "合併分析",
        detail: mergedResult ? "合併輪廓已建立" : "成功讀取 2 檔以上可啟用",
        status: mergeStatus
      },
      {
        title: "模型與金融分析",
        detail: completedCount > 0 ? "可選目標欄位與分析模式" : "等待資料摘要",
        status: analysisStatus
      },
      {
        title: "報告與程式碼",
        detail: completedCount > 0 ? "可在結果區生成與預覽" : "分析完成後啟用",
        status: analysisStatus
      }
    ];
  }, [completedCount, failedCount, isLoading, mergedResult, uploads.length]);

  const analyzeUploads = useCallback(async () => {
    if (uploads.length === 0) {
      setError("請先選擇至少一個 CSV 或 Excel 檔案。");
      return;
    }

    setError(null);
    setMergedResult(null);
    setBatchNotes([]);
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
            error: item?.success ? null : item?.error ?? "資料集分析失敗。",
            isLoading: false
          };
        })
      );
      setMergedResult(batchResult.merged);
      setBatchNotes(batchResult.notes);
    } catch (caughtError) {
      setUploads((current) =>
        current.map((upload) => ({
          ...upload,
          isLoading: false
        }))
      );
      setError(
        caughtError instanceof Error ? caughtError.message : "多檔資料集分析失敗。"
      );
    }
  }, [uploads]);

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void analyzeUploads();
  }

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    setUploads((current) => {
      const existingIds = new Set(current.map((upload) => upload.id));
      const newUploads = files
        .map(createUpload)
        .filter((upload) => !existingIds.has(upload.id));
      return [...current, ...newUploads];
    });
    setMergedResult(null);
    setBatchNotes([]);
    setError(null);
    event.target.value = "";
  }

  function removeUpload(id: string) {
    setUploads((current) => current.filter((upload) => upload.id !== id));
    setMergedResult(null);
    setBatchNotes([]);
    setError(null);
  }

  const clearUploads = useCallback(() => {
    setUploads([]);
    setMergedResult(null);
    setBatchNotes([]);
    setError(null);
  }, []);

  useEffect(() => {
    function openFiles() {
      inputRef.current?.click();
    }

    function analyzeFiles() {
      formRef.current?.requestSubmit();
    }

    window.addEventListener("smartfinance:open-files", openFiles);
    window.addEventListener("smartfinance:analyze-files", analyzeFiles);
    window.addEventListener("smartfinance:clear-files", clearUploads);

    return () => {
      window.removeEventListener("smartfinance:open-files", openFiles);
      window.removeEventListener("smartfinance:analyze-files", analyzeFiles);
      window.removeEventListener("smartfinance:clear-files", clearUploads);
    };
  }, [clearUploads]);

  return (
    <div className="workbench-layout">
      <WorkbenchSidebar
        completedCount={completedCount}
        failedCount={failedCount}
        readinessPercent={readinessPercent}
        totalSizeLabel={totalSizeLabel}
        uploadCount={uploads.length}
        workspaceState={workspaceState}
      />

      <main id="top" className="workbench-main">
        <section className="workbench-topbar">
          <div>
            <div className="workbench-kicker">上傳與分析工作台</div>
            <h1>把資料放進來，讓系統接手判斷</h1>
            <p>
              多檔匯入後會先回傳真實欄位摘要，再依資料內容啟用合併分析、
              模型推薦、金融指標與報告生成。
            </p>
          </div>
          <div className="workbench-topbar-actions">
            <StatusBadge status={workspaceState} />
            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="primary-action glow-button"
            >
              選擇檔案
            </button>
          </div>
        </section>

        <form
          ref={formRef}
          onSubmit={handleSubmit}
          id="data-upload"
          className="upload-stage-card"
        >
          <div className="stage-card-header">
            <div>
              <span>01</span>
              <h2>多檔資料上傳</h2>
              <p>可一次選多個檔案，也能分批加入。相同檔案會自動避免重複加入。</p>
            </div>
            <div className="stage-actions">
              <button
                type="button"
                onClick={clearUploads}
                disabled={isLoading || uploads.length === 0}
                className="quiet-button"
              >
                清空
              </button>
              <button
                type="submit"
                disabled={isLoading || uploads.length === 0}
                className="primary-action glow-button"
              >
                {isLoading ? "讀取中..." : "讀取全部"}
              </button>
            </div>
          </div>

          <div
            className="upload-dropzone workbench-dropzone"
            onClick={() => inputRef.current?.click()}
          >
            <input
              ref={inputRef}
              className="sr-only"
              type="file"
              accept={acceptedTypes}
              multiple
              onChange={handleFileChange}
            />
            <div className="dropzone-icon">
              <UploadIcon />
            </div>
            <div>
              <h3>
                {uploads.length > 0
                  ? `已加入 ${uploads.length} 個檔案`
                  : "拖曳或選擇 CSV / Excel 檔案"}
              </h3>
              <p>支援 CSV、XLSX、XLS。讀取後會顯示每份資料的欄位、缺失值與數值摘要。</p>
            </div>
            <button
              type="button"
              onClick={(event) => {
                event.stopPropagation();
                inputRef.current?.click();
              }}
              className="dropzone-button"
            >
              加入檔案
            </button>
          </div>

          {uploads.length > 0 ? (
            <div className="upload-summary-grid">
              <UploadMetric label="檔案數" value={`${uploads.length}`} />
              <UploadMetric label="總大小" value={totalSizeLabel} />
              <UploadMetric label="成功讀取" value={`${completedCount} 檔`} />
              <UploadMetric label="失敗" value={`${failedCount} 檔`} />
            </div>
          ) : null}

          {uploads.length > 0 ? (
            <div className="file-queue">
              {uploads.map((upload) => (
                <div key={upload.id} className="file-row">
                  <div className="file-row-main">
                    <span className="file-icon">CSV</span>
                    <div>
                      <h3>{upload.file.name}</h3>
                      <p>{(upload.file.size / 1024 / 1024).toFixed(3)} MB</p>
                    </div>
                  </div>
                  <div className="file-row-actions">
                    <FileStateLabel upload={upload} />
                    <button
                      type="button"
                      onClick={(event) => {
                        event.stopPropagation();
                        removeUpload(upload.id);
                      }}
                      disabled={isLoading}
                      className="quiet-button is-small"
                    >
                      移除
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : null}

          {error ? (
            <div className="mt-6 rounded-md border border-red-200 bg-red-50 px-5 py-4 text-base font-medium text-red-700">
              {error}
            </div>
          ) : null}

          {batchNotes.length > 0 ? (
            <div className="mt-6 rounded-md border border-amber-200 bg-amber-50 p-5">
              <h2 className="text-base font-semibold text-amber-900">批次讀取備註</h2>
              <ul className="mt-3 space-y-2 text-base leading-7 text-amber-900">
                {batchNotes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </form>

        {mergedResult ? (
          <section id="merge-analysis" className="analysis-stack">
            <div className="result-intro-card">
              <div>
                <span>02</span>
                <h2>智慧合併分析</h2>
                <p>
                  已依欄位名稱合併成功讀取的檔案，並保留來源檔案欄位與來源列號。
                  你可以直接在合併資料上執行模型、金融與報告分析。
                </p>
              </div>
              <div className="upload-summary-grid is-compact">
                <UploadMetric label="來源檔案" value={`${mergedResult.source_file_count}`} />
                <UploadMetric label="合併列數" value={mergedResult.row_count.toLocaleString()} />
                <UploadMetric label="共同欄位" value={mergedResult.common_columns.length.toLocaleString()} />
              </div>
            </div>

            <div className="merge-notes">
              <h3>合併判斷</h3>
              <ul>
                {mergedResult.merge_notes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            </div>

            <AnalysisResult result={mergedResult} />
            <AgentReportPanel
              dataset={mergedResult}
              files={mergedFiles}
              isMerged
              title="合併資料 AI 分析與報告"
              description="整合資料摘要、模型分析、金融分析、圖表整理與 Word 報告輸出。"
            />
            <FinancialAnalysisPanel
              dataset={mergedResult}
              files={mergedFiles}
              isMerged
              title="合併資料金融分析"
              description="當合併資料含有日期與價格欄位時，系統會重新合併成功讀取的檔案並產出金融指標、圖表與指標 CSV。"
            />
            <ModelAnalysisPanel
              dataset={mergedResult}
              files={mergedFiles}
              isMerged
              title="合併資料模型分析"
              description="系統會重新將成功讀取的檔案合併後訓練模型，適合比較多份資料合在一起後的整體趨勢。"
            />
          </section>
        ) : null}

        {uploads.length > 0 ? (
          <section id="individual-analysis" className="analysis-stack">
            {uploads.map((upload, index) => (
              <article key={upload.id} className="dataset-result-block">
                <div className="result-intro-card">
                  <div>
                    <span>{String(index + 3).padStart(2, "0")}</span>
                    <h2>檔案 {index + 1}：{upload.file.name}</h2>
                    <p>每個檔案仍可獨立顯示摘要，並執行模型、金融、報告與程式碼生成。</p>
                  </div>
                  <FileStateLabel upload={upload} />
                </div>

                {upload.error ? (
                  <div className="rounded-md border border-red-200 bg-red-50 px-5 py-4 text-base font-medium text-red-700">
                    {upload.error}
                  </div>
                ) : null}

                {upload.result ? (
                  <>
                    <AnalysisResult result={upload.result} />
                    <AgentReportPanel dataset={upload.result} file={upload.file} />
                    <FinancialAnalysisPanel dataset={upload.result} file={upload.file} />
                    <ModelAnalysisPanel dataset={upload.result} file={upload.file} />
                  </>
                ) : null}
              </article>
            ))}
          </section>
        ) : null}
      </main>

      <aside className="workbench-rail">
        <AnalysisProgressRail steps={progressSteps} />
        <section className="rail-card">
          <div className="rail-card-title">快速鍵</div>
          <div className="shortcut-list">
            <Shortcut label="開啟命令中心" command="⌘ K" />
            <Shortcut label="選擇檔案" command="⌘ U" />
            <Shortcut label="讀取全部" command="⌘ ↵" />
          </div>
        </section>
        <section className="rail-card">
          <div className="rail-card-title">系統狀態</div>
          <SystemStatus />
          <p className="rail-note">前端只顯示後端回傳的真實分析結果。</p>
        </section>
      </aside>
    </div>
  );
}

function WorkbenchSidebar({
  completedCount,
  failedCount,
  readinessPercent,
  totalSizeLabel,
  uploadCount,
  workspaceState
}: {
  completedCount: number;
  failedCount: number;
  readinessPercent: number;
  totalSizeLabel: string;
  uploadCount: number;
  workspaceState: string;
}) {
  const items = [
    { label: "資料匯入", href: "#data-upload" },
    { label: "資料探索", href: "#individual-analysis" },
    { label: "合併分析", href: "#merge-analysis" },
    { label: "模型分析", href: "#individual-analysis" },
    { label: "金融分析", href: "#individual-analysis" },
    { label: "報告中心", href: "#individual-analysis" }
  ];

  return (
    <aside className="workbench-sidebar">
      <div className="sidebar-brand-row">
        <div className="brand-mark">智</div>
        <div>
          <strong>智能金融資料分析</strong>
          <span>{workspaceState}</span>
        </div>
      </div>
      <nav className="sidebar-nav">
        {items.map((item, index) => (
          <a key={item.label} href={item.href} className={index === 0 ? "is-active" : ""}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            {item.label}
          </a>
        ))}
      </nav>
      <div className="sidebar-summary">
        <div>
          <span>準備度</span>
          <strong>{Math.min(readinessPercent, 100)}%</strong>
        </div>
        <div className="workspace-progress" aria-label={`準備度 ${readinessPercent}%`}>
          <span style={{ width: `${Math.min(readinessPercent, 100)}%` }} />
        </div>
        <dl>
          <div>
            <dt>檔案</dt>
            <dd>{uploadCount}</dd>
          </div>
          <div>
            <dt>成功</dt>
            <dd>{completedCount}</dd>
          </div>
          <div>
            <dt>失敗</dt>
            <dd>{failedCount}</dd>
          </div>
          <div>
            <dt>大小</dt>
            <dd>{totalSizeLabel}</dd>
          </div>
        </dl>
      </div>
    </aside>
  );
}

function AnalysisProgressRail({ steps }: { steps: ProgressStep[] }) {
  return (
    <section className="rail-card">
      <div className="rail-card-title">分析流程進度</div>
      <div className="progress-list">
        {steps.map((step) => (
          <div key={step.title} className={`progress-step is-${step.status}`}>
            <span className="progress-dot" />
            <div>
              <strong>{step.title}</strong>
              <small>{step.detail}</small>
            </div>
            <em>{statusLabel(step.status)}</em>
          </div>
        ))}
      </div>
    </section>
  );
}

function StatusBadge({ status }: { status: string }) {
  return <span className="status-badge">{status}</span>;
}

function Shortcut({ label, command }: { label: string; command: string }) {
  return (
    <div className="shortcut-row">
      <span>{label}</span>
      <kbd>{command}</kbd>
    </div>
  );
}

function FileStateLabel({ upload }: { upload: DatasetUpload }) {
  const label = upload.isLoading
    ? "讀取中"
    : upload.result
      ? "已讀取"
      : upload.error
        ? "讀取失敗"
        : "等待讀取";

  return <span className={`file-state is-${stateClass(upload)}`}>{label}</span>;
}

function stateClass(upload: DatasetUpload) {
  if (upload.isLoading) return "active";
  if (upload.result) return "complete";
  if (upload.error) return "error";
  return "waiting";
}

function statusLabel(status: ProgressStatus) {
  if (status === "complete") return "完成";
  if (status === "active") return "執行中";
  if (status === "ready") return "可執行";
  if (status === "error") return "需處理";
  return "等待中";
}

function createUpload(file: File): DatasetUpload {
  return {
    id: `${file.name}-${file.lastModified}-${file.size}`,
    file,
    result: null,
    error: null,
    isLoading: false
  };
}

function UploadMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="upload-metric">
      <div>{label}</div>
      <strong>{value}</strong>
    </div>
  );
}

function UploadIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 16V7" />
      <path d="m8 11 4-4 4 4" />
      <path d="M7 18.5H6.5a4.5 4.5 0 0 1-.4-8.98A6 6 0 0 1 17.7 8.4 4.75 4.75 0 0 1 18 18.5h-.8" />
    </svg>
  );
}
