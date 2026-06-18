"use client";

import { useEffect, useMemo } from "react";
import { Database, Layers3 } from "lucide-react";
import { useLocale } from "@/components/LocaleProvider";
import {
  useWorkspace,
  type DatasetUploadState
} from "@/components/WorkspaceProvider";
import type { DatasetAnalysis } from "@/lib/api";

export type WorkspaceSource = {
  id: string;
  label: string;
  detail: string;
  dataset: DatasetAnalysis;
  file?: File;
  files: File[];
  isMerged: boolean;
};

export function useWorkspaceSources() {
  const { text } = useLocale();
  const {
    uploads,
    mergedResult,
    activeSourceId,
    setActiveSourceId
  } = useWorkspace();

  const completedUploads = useMemo(
    () => uploads.filter(hasAnalysis),
    [uploads]
  );

  const sources = useMemo<WorkspaceSource[]>(() => {
    const individualSources = completedUploads.map((upload) => ({
      id: upload.id,
      label: upload.result.file_name,
      detail: text(
        `${upload.result.row_count.toLocaleString()} 列 · ${upload.result.column_count.toLocaleString()} 欄`,
        `${upload.result.row_count.toLocaleString()} rows · ${upload.result.column_count.toLocaleString()} columns`
      ),
      dataset: upload.result,
      file: upload.file,
      files: [],
      isMerged: false
    }));

    if (!mergedResult) return individualSources;

    return [
      {
        id: "merged",
        label: text("合併資料集", "Merged dataset"),
        detail: text(
          `${mergedResult.source_file_count} 個來源 · ${mergedResult.row_count.toLocaleString()} 列`,
          `${mergedResult.source_file_count} sources · ${mergedResult.row_count.toLocaleString()} rows`
        ),
        dataset: mergedResult,
        files: completedUploads.map((upload) => upload.file),
        isMerged: true
      },
      ...individualSources
    ];
  }, [completedUploads, mergedResult, text]);

  const fallbackSourceId = sources[0]?.id ?? null;
  const resolvedSourceId =
    activeSourceId && sources.some((source) => source.id === activeSourceId)
      ? activeSourceId
      : fallbackSourceId;
  const activeSource =
    sources.find((source) => source.id === resolvedSourceId) ?? null;

  useEffect(() => {
    if (resolvedSourceId !== activeSourceId) {
      setActiveSourceId(resolvedSourceId);
    }
  }, [activeSourceId, resolvedSourceId, setActiveSourceId]);

  return {
    sources,
    activeSource,
    activeSourceId: resolvedSourceId,
    setActiveSourceId,
    completedUploads
  };
}

export function WorkspaceSourceSelect({
  compact = false
}: {
  compact?: boolean;
}) {
  const { text } = useLocale();
  const {
    sources,
    activeSourceId,
    setActiveSourceId
  } = useWorkspaceSources();

  if (sources.length === 0) return null;

  return (
    <label className={`source-select ${compact ? "is-compact" : ""}`}>
      <span className="sr-only">{text("目前資料來源", "Current data source")}</span>
      {sources.length > 1 ? (
        <Layers3 aria-hidden="true" />
      ) : (
        <Database aria-hidden="true" />
      )}
      <select
        aria-label={text("目前資料來源", "Current data source")}
        name="workspace-source"
        autoComplete="off"
        value={activeSourceId ?? ""}
        onChange={(event) => setActiveSourceId(event.target.value)}
      >
        {sources.map((source) => (
          <option key={source.id} value={source.id}>
            {source.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function hasAnalysis(
  upload: DatasetUploadState
): upload is DatasetUploadState & { result: DatasetAnalysis } {
  return upload.result !== null;
}
