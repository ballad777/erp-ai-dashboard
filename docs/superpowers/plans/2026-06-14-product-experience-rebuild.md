# Product Experience Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 將既有真實分析功能整理成 `/` 品牌首頁與 `/app` 分析工作區，提供繁中／英文、可恢復的工作狀態、清楚的分析節奏與完整響應式體驗。

**Architecture:** 保留 Next.js App Router、FastAPI 與既有同步分析 API。前端以共用 Locale、Workspace 與 Feedback providers 管理語言、IndexedDB 工作區快照與可選音效；品牌首頁和工作區共用設計 tokens，但使用不同資訊密度。舊路由只做 server redirect，不複製頁面實作。

**Tech Stack:** Next.js 16、React 19、TypeScript、Tailwind CSS、Motion、Lucide、FastAPI、pandas、scikit-learn、pytest

---

### Task 1: 建立路由與雙語基礎

**Files:**
- Create: `frontend/src/components/LocaleProvider.tsx`
- Create: `frontend/src/components/LanguageSwitch.tsx`
- Modify: `frontend/src/app/layout.tsx`
- Create: `frontend/src/app/en/layout.tsx`
- Create: `frontend/src/app/en/page.tsx`
- Create: `frontend/src/app/app/page.tsx`
- Create: `frontend/src/app/app/data/page.tsx`
- Create: `frontend/src/app/app/models/page.tsx`
- Create: `frontend/src/app/app/finance/page.tsx`
- Create: `frontend/src/app/app/reports/page.tsx`
- Create: `frontend/src/app/en/app/page.tsx`
- Create: `frontend/src/app/en/app/data/page.tsx`
- Create: `frontend/src/app/en/app/models/page.tsx`
- Create: `frontend/src/app/en/app/finance/page.tsx`
- Create: `frontend/src/app/en/app/reports/page.tsx`
- Modify: `frontend/src/app/upload/page.tsx`
- Modify: `frontend/src/app/models/page.tsx`
- Modify: `frontend/src/app/finance/page.tsx`
- Modify: `frontend/src/app/reports/page.tsx`

- [x] 建立 `LocaleProvider`，由 `/en` layout 覆寫預設繁中語系。
- [x] 讓語言切換保留目前子路由，並以 cookie 保存偏好。
- [x] 建立 `/app/*` 工作區頁面與 `/en/app/*` 英文頁面。
- [x] 將 `/upload`、`/models`、`/finance`、`/reports` 改為 server redirect。
- [x] 執行 `npm run typecheck`，確認路由與型別可建置。

### Task 2: 建立品牌首頁

**Files:**
- Create: `frontend/src/components/MarketingShell.tsx`
- Create: `frontend/src/components/MarketingHome.tsx`
- Create: `frontend/src/components/ProductPreview.tsx`
- Modify: `frontend/src/app/page.tsx`
- Modify: `frontend/src/app/en/page.tsx`
- Modify: `frontend/src/components/MotionPrimitives.tsx`
- Modify: `frontend/src/app/globals.css`

- [x] 建立 sticky marketing header、手機 sheet 與工作區 CTA。
- [x] 實作核心 Hero 文案、真實能力說明與產品元件預覽。
- [x] 實作分析旅程、資料、模型、金融、交付、真實分析與 final CTA。
- [x] 所有 CTA 連至實際 `/app` 功能，不建立假按鈕。
- [x] 加入克制的 ambient canvas、scroll reveal、hover 與 reduced-motion。

### Task 3: 重整工作區導覽與總覽

**Files:**
- Modify: `frontend/src/components/AppShell.tsx`
- Create: `frontend/src/components/WorkspaceDashboard.tsx`
- Modify: `frontend/src/components/PagePrimitives.tsx`
- Modify: `frontend/src/components/WorkspaceToolPages.tsx`
- Modify: `frontend/src/components/WorkspaceSource.tsx`
- Modify: `frontend/src/app/globals.css`

- [x] 將導覽改為 `/app` 路由並支援英文前綴。
- [x] 建立桌面側欄、平板導覽與手機底部導覽。
- [x] 依真實工作區狀態計算「建議下一步」。
- [x] 結果總覽先顯示重點、依據與下一步，再揭露技術細節。
- [x] 所有空狀態導向真實資料上傳頁。

### Task 4: 完整雙語化核心操作

**Files:**
- Modify: `frontend/src/components/UploadPanel.tsx`
- Modify: `frontend/src/components/AnalysisResult.tsx`
- Modify: `frontend/src/components/ModelAnalysisPanel.tsx`
- Modify: `frontend/src/components/FinancialAnalysisPanel.tsx`
- Modify: `frontend/src/components/AgentReportPanel.tsx`
- Modify: `frontend/src/components/PagePrimitives.tsx`
- Modify: `frontend/src/components/WorkspaceToolPages.tsx`

- [x] 翻譯頁面標題、表單、按鈕、狀態、錯誤與無障礙文字。
- [x] 保留使用者檔名、欄位名稱、模型 key 與程式碼原文。
- [x] 英文模式仍呼叫同一組真實 API。
- [x] 確認程式碼與 Notebook 內容能在頁內切換預覽。

### Task 5: 持久化與回饋系統

**Files:**
- Create: `frontend/src/lib/workspace-storage.ts`
- Create: `frontend/src/components/FeedbackProvider.tsx`
- Modify: `frontend/src/components/WorkspaceProvider.tsx`
- Modify: `frontend/src/components/PagePrimitives.tsx`
- Modify: `frontend/src/components/UploadPanel.tsx`
- Modify: `frontend/src/components/ModelAnalysisPanel.tsx`
- Modify: `frontend/src/components/FinancialAnalysisPanel.tsx`
- Modify: `frontend/src/components/AgentReportPanel.tsx`

- [x] 用 IndexedDB 保存 File blobs、資料摘要、分析結果與目前來源。
- [x] 載入時恢復工作區，並將殘留 loading 狀態重設為 false。
- [x] 加入 hydration loading 狀態，避免短暫顯示錯誤空畫面。
- [x] 加入預設關閉的介面音效，只在長任務成功或錯誤時觸發。
- [x] 清空工作區時同步刪除持久化資料。

### Task 6: 文件與驗證

**Files:**
- Modify: `README.md`
- Modify: `PROGRESS.md`

- [x] 記錄新路由、雙語、持久化、音效與實際啟動方式。
- [x] 執行 `backend/.venv/bin/python -m pytest backend/tests -q`。
- [x] 執行 `npm run typecheck`。
- [x] 執行 `npm run build -- --webpack`。
- [x] 執行 `git diff --check`。
- [x] 啟動 FastAPI 與 Next.js。
- [x] 用瀏覽器檢查 `/`、`/app`、`/app/data`、`/en`、`/en/app`。
- [x] 在 390px、768px、1280px 驗證導覽、上傳、結果與水平溢位。
