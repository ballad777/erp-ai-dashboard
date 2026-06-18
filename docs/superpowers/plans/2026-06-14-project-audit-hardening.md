# Project Audit Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan.

**Goal:** 修正完整專案稽核中最高優先的部署、上傳安全、API 可靠性與前端操作問題，並以自動化測試和實際瀏覽器驗證結果。

**Architecture:** 保留既有 Next.js + FastAPI 架構。後端在 API 邊界統一驗證批次上傳並隱藏內部錯誤；前端以共用 request helper 統一處理逾時與錯誤，再於檔案進入工作區前套用相同限制。大範圍服務拆分、驗證、限流與工作佇列列為後續架構工作。

**Tech Stack:** Next.js 16、React 19、TypeScript、Tailwind CSS、FastAPI、pandas、scikit-learn、pytest

---

### Task 1: 建立安全回歸測試

**Files:**
- Create: `backend/tests/test_api_hardening.py`
- Modify: `backend/app/services/dataset_analyzer.py`
- Modify: `backend/app/main.py`

- [x] 測試批次檔案數與總容量限制。
- [x] 測試未預期錯誤不回傳例外原文。
- [x] 測試 API 安全標頭。

### Task 2: 修正後端 API 邊界

**Files:**
- Modify: `backend/app/services/dataset_analyzer.py`
- Modify: `backend/app/main.py`

- [x] 新增 20 檔、單檔 25 MB、批次 100 MB 的一致限制。
- [x] 所有多檔端點進入服務前統一驗證。
- [x] 將解析與 500 錯誤改成不洩漏底層資訊的訊息。
- [x] 增加 API 安全標頭並保留伺服器端完整 log。

### Task 3: 強化前端請求與上傳體驗

**Files:**
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/components/UploadPanel.tsx`
- Modify: `frontend/src/components/AppShell.tsx`

- [x] 以共用 request helper 取代重複 fetch 流程。
- [x] 為資料讀取與長時間分析設定分級逾時及一致錯誤訊息。
- [x] 上傳前檢查格式、單檔大小、檔案數與批次容量。
- [x] 移除資料頁重複的頂部動作並補足 input 語意。

### Task 4: 修正表單語意與部署

**Files:**
- Modify: `frontend/src/components/ModelAnalysisPanel.tsx`
- Modify: `frontend/src/components/FinancialAnalysisPanel.tsx`
- Modify: `frontend/src/components/AgentReportPanel.tsx`
- Modify: `frontend/src/components/WorkspaceSource.tsx`
- Modify: `Dockerfile`

- [x] 為主要 select、radio、checkbox 加入穩定名稱。
- [x] 修正不存在的 `frontend/public` Docker 複製來源。

### Task 5: 文件與完整驗證

**Files:**
- Modify: `README.md`
- Modify: `PROGRESS.md`

- [x] 記錄上傳限制、安全修正與仍待處理的產品級風險。
- [ ] 執行後端測試、TypeScript、production build、Docker 靜態檢查與 `git diff --check`。（除 Docker daemon 未啟動外均完成）
- [x] 以瀏覽器驗證 390px 與 1440px 的五個主要頁面、導覽與水平溢位。
