"use client";

import { useMemo, useRef, useState } from "react";
import { AgentReportPanel } from "@/components/AgentReportPanel";
import { AnalysisResult } from "@/components/AnalysisResult";
import { FinancialAnalysisPanel } from "@/components/FinancialAnalysisPanel";
import { ModelAnalysisPanel } from "@/components/ModelAnalysisPanel";
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

export function UploadPanel() {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [uploads, setUploads] = useState<DatasetUpload[]>([]);
  const [mergedResult, setMergedResult] = useState<MergedDatasetAnalysis | null>(null);
  const [batchNotes, setBatchNotes] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const isLoading = uploads.some((upload) => upload.isLoading);
  const completedUploads = uploads.filter((upload) => upload.result);
  const completedCount = completedUploads.length;
  const failedCount = uploads.filter((upload) => upload.error).length;
  const mergedFiles = completedUploads.map((upload) => upload.file);

  const totalSizeLabel = useMemo(() => {
    const totalBytes = uploads.reduce((sum, upload) => sum + upload.file.size, 0);
    if (totalBytes === 0) return "0 MB";
    return `${(totalBytes / 1024 / 1024).toFixed(2)} MB`;
  }, [uploads]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

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

  function clearUploads() {
    setUploads([]);
    setMergedResult(null);
    setBatchNotes([]);
    setError(null);
  }

  return (
    <div className="space-y-8">
      <section className="surface-card relative isolate overflow-hidden p-6 sm:p-8 lg:p-10">
        <div className="hero-wave hero-wave-left" />
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div className="max-w-4xl">
            <div className="inline-flex rounded-full border border-sky-200 bg-white/72 px-4 py-2 text-sm font-semibold text-brand">
              分析工作台
            </div>
            <h1 className="mt-5 text-4xl font-semibold tracking-normal text-ink sm:text-5xl">
              上傳資料，開始建立洞察
            </h1>
            <p className="mt-4 max-w-3xl text-lg leading-8 text-muted">
              匯入 CSV 或 Excel，系統會完成資料摘要、合併判斷、模型分析、金融指標與報告輸出。
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-3 xl:max-w-[560px]">
            <UploadMetric label="已加入" value={`${uploads.length} 檔`} />
            <UploadMetric label="成功讀取" value={`${completedCount} 檔`} />
            <UploadMetric label="總大小" value={totalSizeLabel} />
          </div>
        </div>
      </section>

      <form
        onSubmit={handleSubmit}
        className="surface-card p-6 sm:p-8"
      >
        <div className="flex flex-col gap-7 xl:flex-row xl:items-start xl:justify-between">
          <div className="max-w-4xl">
            <h2 className="text-3xl font-semibold tracking-normal text-ink">
              資料匯入
            </h2>
            <p className="mt-3 text-lg leading-8 text-muted">
              可一次加入多個 CSV 或 Excel 檔案。系統會整批讀取檔案，
              並在成功讀取兩個以上檔案時建立智慧合併分析。
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={clearUploads}
              disabled={isLoading || uploads.length === 0}
              className="h-12 rounded-xl border border-line bg-white px-6 text-base font-semibold text-ink transition hover:border-brand hover:text-brand disabled:cursor-not-allowed disabled:text-slate-400"
            >
              清空檔案
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="glow-button h-12 rounded-xl bg-gradient-to-r from-brand via-sky-500 to-navy px-7 text-base font-semibold text-white transition disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {isLoading ? "整批讀取中..." : "讀取全部檔案"}
            </button>
          </div>
        </div>

        <div
          className="upload-dropzone mt-7 p-6 sm:p-7"
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
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="text-lg font-semibold text-ink">
                {uploads.length > 0
                  ? `已加入 ${uploads.length} 個檔案`
                  : "選擇一個或多個 CSV / Excel 檔案"}
              </div>
              <div className="mt-2 text-base leading-7 text-muted">
                可分多次加入檔案；相同檔名、大小與修改時間的檔案會自動避免重複加入。
              </div>
            </div>
            <button
              type="button"
              onClick={(event) => {
                event.stopPropagation();
                inputRef.current?.click();
              }}
              className="h-11 rounded-xl border border-sky-200 bg-white px-5 text-base font-semibold text-ink transition hover:border-brand hover:text-brand"
            >
              加入檔案
            </button>
          </div>

          {uploads.length > 0 ? (
            <div className="mt-6 grid gap-3 lg:grid-cols-3">
              <UploadMetric label="檔案數" value={`${uploads.length}`} />
              <UploadMetric label="總大小" value={totalSizeLabel} />
              <UploadMetric
                label="讀取狀態"
                value={`${completedCount} 成功 / ${failedCount} 失敗`}
              />
            </div>
          ) : null}

          {uploads.length > 0 ? (
            <div className="mt-5 grid gap-3">
              {uploads.map((upload) => (
                <div
                  key={upload.id}
                  className="flex flex-col gap-3 rounded-xl border border-blue-100 bg-white/82 px-4 py-3 shadow-[0_12px_30px_rgba(15,23,42,0.04)] md:flex-row md:items-center md:justify-between"
                >
                  <div>
                    <div className="text-base font-semibold text-ink">
                      {upload.file.name}
                    </div>
                    <div className="text-sm text-muted">
                      {(upload.file.size / 1024 / 1024).toFixed(3)} MB
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-sm font-semibold text-muted">
                      {upload.isLoading
                        ? "讀取中"
                        : upload.result
                          ? "已讀取"
                          : upload.error
                            ? "讀取失敗"
                            : "等待讀取"}
                    </div>
                    <button
                      type="button"
                      onClick={(event) => {
                        event.stopPropagation();
                        removeUpload(upload.id);
                      }}
                      disabled={isLoading}
                      className="h-9 rounded-xl border border-line px-3 text-sm font-semibold text-muted transition hover:border-red-300 hover:text-red-700 disabled:cursor-not-allowed disabled:text-slate-400"
                    >
                      移除
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : null}
        </div>

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
        <section className="surface-card space-y-7 border-brand/40 p-6 sm:p-8">
          <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
            <div className="max-w-5xl">
              <div className="text-base font-semibold text-brand">智慧合併分析</div>
              <h2 className="mt-2 text-3xl font-semibold text-ink">
                合併資料集摘要
              </h2>
              <p className="mt-3 text-lg leading-8 text-muted">
                已依欄位名稱合併成功讀取的檔案，並保留來源檔案欄位與來源列號。
                你可以直接在合併資料上選擇目標欄位並執行模型分析。
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-3 xl:max-w-[560px]">
              <UploadMetric
                label="來源檔案"
                value={`${mergedResult.source_file_count}`}
              />
              <UploadMetric
                label="合併列數"
                value={mergedResult.row_count.toLocaleString()}
              />
              <UploadMetric
                label="共同欄位"
                value={mergedResult.common_columns.length.toLocaleString()}
              />
            </div>
          </div>

          <div className="rounded-2xl border border-teal-100 bg-teal-50/80 p-5">
            <h3 className="text-base font-semibold text-teal-950">合併判斷</h3>
            <ul className="mt-3 space-y-2 text-base leading-7 text-teal-950">
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
        <section className="space-y-10">
          {uploads.map((upload, index) => (
            <article key={upload.id} className="space-y-7">
              <div className="surface-card p-5 sm:p-6">
                <div className="flex flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
                  <div>
                    <h2 className="text-2xl font-semibold text-ink">
                      檔案 {index + 1}：{upload.file.name}
                    </h2>
                    <p className="mt-2 text-base text-muted">
                      每個檔案仍可獨立顯示摘要與執行模型分析。
                    </p>
                  </div>
                  <span className="text-base font-semibold text-muted">
                    {upload.result
                      ? "資料讀取完成"
                      : upload.error
                        ? "資料讀取失敗"
                        : upload.isLoading
                          ? "資料讀取中"
                          : "尚未讀取"}
                  </span>
                </div>
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
    </div>
  );
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
    <div className="rounded-2xl border border-blue-100 bg-white/78 px-5 py-4 shadow-[0_12px_28px_rgba(15,23,42,0.045)]">
      <div className="text-sm font-semibold text-muted">{label}</div>
      <div className="mt-1 break-words text-xl font-semibold text-ink">{value}</div>
    </div>
  );
}
