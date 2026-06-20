import type { DatasetUploadState } from "@/components/WorkspaceProvider";
import type { MergedDatasetAnalysis, MultiTablePlan } from "@/lib/api";

export type WorkspaceSnapshot = {
  version: 1;
  savedAt: number;
  uploads: DatasetUploadState[];
  mergedResult: MergedDatasetAnalysis | null;
  multiTablePlan?: MultiTablePlan | null;
  batchNotes: string[];
  panelStates: Record<string, unknown>;
  activeSourceId: string | null;
};

const databaseName = "intelligent-finance-workspace";
const databaseVersion = 1;
const storeName = "workspace";
const snapshotKey = "current";

export async function loadWorkspaceSnapshot() {
  if (!("indexedDB" in window)) return null;
  const database = await openDatabase();
  try {
    return await new Promise<WorkspaceSnapshot | null>((resolve, reject) => {
      const transaction = database.transaction(storeName, "readonly");
      const request = transaction.objectStore(storeName).get(snapshotKey);
      request.onsuccess = () => {
        const value = request.result as WorkspaceSnapshot | undefined;
        resolve(value?.version === 1 ? value : null);
      };
      request.onerror = () => reject(request.error);
    });
  } finally {
    database.close();
  }
}

export async function saveWorkspaceSnapshot(snapshot: WorkspaceSnapshot) {
  if (!("indexedDB" in window)) return;
  const database = await openDatabase();
  try {
    await new Promise<void>((resolve, reject) => {
      const transaction = database.transaction(storeName, "readwrite");
      transaction.objectStore(storeName).put(snapshot, snapshotKey);
      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
      transaction.onabort = () => reject(transaction.error);
    });
  } finally {
    database.close();
  }
}

export async function clearWorkspaceSnapshot() {
  if (!("indexedDB" in window)) return;
  const database = await openDatabase();
  try {
    await new Promise<void>((resolve, reject) => {
      const transaction = database.transaction(storeName, "readwrite");
      transaction.objectStore(storeName).delete(snapshotKey);
      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
      transaction.onabort = () => reject(transaction.error);
    });
  } finally {
    database.close();
  }
}

function openDatabase() {
  return new Promise<IDBDatabase>((resolve, reject) => {
    const request = window.indexedDB.open(databaseName, databaseVersion);
    request.onupgradeneeded = () => {
      const database = request.result;
      if (!database.objectStoreNames.contains(storeName)) {
        database.createObjectStore(storeName);
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}
