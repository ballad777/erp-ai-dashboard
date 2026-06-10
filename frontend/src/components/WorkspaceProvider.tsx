"use client";

import {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
  type Dispatch,
  type ReactNode,
  type SetStateAction
} from "react";
import type { DatasetAnalysis, MergedDatasetAnalysis } from "@/lib/api";

export type DatasetUploadState = {
  id: string;
  file: File;
  result: DatasetAnalysis | null;
  error: string | null;
  isLoading: boolean;
};

type WorkspaceContextValue = {
  uploads: DatasetUploadState[];
  setUploads: Dispatch<SetStateAction<DatasetUploadState[]>>;
  mergedResult: MergedDatasetAnalysis | null;
  setMergedResult: Dispatch<SetStateAction<MergedDatasetAnalysis | null>>;
  batchNotes: string[];
  setBatchNotes: Dispatch<SetStateAction<string[]>>;
  error: string | null;
  setError: Dispatch<SetStateAction<string | null>>;
  panelStates: Record<string, unknown>;
  setPanelStates: Dispatch<SetStateAction<Record<string, unknown>>>;
  clearWorkspace: () => void;
};

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [uploads, setUploads] = useState<DatasetUploadState[]>([]);
  const [mergedResult, setMergedResult] = useState<MergedDatasetAnalysis | null>(null);
  const [batchNotes, setBatchNotes] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [panelStates, setPanelStates] = useState<Record<string, unknown>>({});

  const clearWorkspace = useCallback(() => {
    setUploads([]);
    setMergedResult(null);
    setBatchNotes([]);
    setError(null);
    setPanelStates({});
  }, []);

  return (
    <WorkspaceContext.Provider
      value={{
        uploads,
        setUploads,
        mergedResult,
        setMergedResult,
        batchNotes,
        setBatchNotes,
        error,
        setError,
        panelStates,
        setPanelStates,
        clearWorkspace
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error("useWorkspace 必須在 WorkspaceProvider 內使用。");
  }
  return context;
}

export function useWorkspacePanelState<T>(
  key: string,
  initialValue: T | (() => T)
): [T, Dispatch<SetStateAction<T>>] {
  const { panelStates, setPanelStates } = useWorkspace();
  const initialRef = useRef<{ key: string; value: T } | null>(null);

  if (!initialRef.current || initialRef.current.key !== key) {
    initialRef.current = {
      key,
      value:
        typeof initialValue === "function"
          ? (initialValue as () => T)()
          : initialValue
    };
  }

  const hasStoredValue = Object.prototype.hasOwnProperty.call(panelStates, key);
  const value = hasStoredValue
    ? (panelStates[key] as T)
    : initialRef.current.value;

  const setValue = useCallback<Dispatch<SetStateAction<T>>>(
    (action) => {
      setPanelStates((current) => {
        const currentValue = Object.prototype.hasOwnProperty.call(current, key)
          ? (current[key] as T)
          : initialRef.current!.value;
        const nextValue =
          typeof action === "function"
            ? (action as (previous: T) => T)(currentValue)
            : action;

        if (Object.is(currentValue, nextValue)) {
          return current;
        }
        return { ...current, [key]: nextValue };
      });
    },
    [key, setPanelStates]
  );

  return [value, setValue];
}

export function workspaceSourceKey(
  file: File | undefined,
  files: File[],
  isMerged: boolean
) {
  if (isMerged) {
    return `merged:${files.map(fileIdentity).sort().join("|")}`;
  }
  return file ? `file:${fileIdentity(file)}` : "file:unknown";
}

function fileIdentity(file: File) {
  return `${file.name}:${file.size}:${file.lastModified}`;
}
