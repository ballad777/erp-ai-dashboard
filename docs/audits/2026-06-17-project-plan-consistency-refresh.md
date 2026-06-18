# 2026-06-17 專案與計畫一致性複查

## 結論

目前專案比 2026-06-15 的稽核結果更接近「封閉測試版」計畫：公開 artifact 路徑、部署定位、Node 版本、重複 CTA、工作台可讀性與進度體驗等短期風險都有明顯改善。

但專案仍未達到先前「資料分析 SaaS / 資料科學工作台」完整建議計畫。現在比較像是「可跑 demo 與封閉測試的本機/單機分析工具」，還不是可公開上線、可多人使用、可重現稽核的資料科學平台。

一致性判斷：

| 面向 | 一致性 | 判斷 |
| --- | --- | --- |
| 0-3 天穩定化修正 | 高 | C1/C2/M3/M6 多數已修正或緩解 |
| 聚焦分析工作台 UI | 中高 | 架構與互動已接近計畫，但仍缺瀏覽器視覺驗證與語法高亮 |
| 公開 SaaS 安全基礎 | 低 | 缺 Auth、Project ownership、rate limit、正式授權模型 |
| 資料科學核心能力 | 中低 | 基礎分析可跑，但品質檢查、合併邏輯、模型驗證仍偏初階 |
| 可重現與治理 | 低 | 缺 Run Manifest、資料/模型版本、artifact provenance |
| 可擴展後端架構 | 低 | jobs 仍在記憶體與 thread 執行，無 DB/Queue/Worker/SSE |

## 本次驗證

- 後端測試：`37 passed`
- 前端測試：`61 passed`
- TypeScript typecheck：通過
- Next.js production build：通過
- Browser 視覺驗證：未完成。本次嘗試打開 `http://127.0.0.1:3010` 與 `http://localhost:3010` 時，Codex Browser webview attach 逾時。因此本報告的 UI 判斷主要來自程式碼、測試與 build，不包含實際桌面/手機寬度截圖驗證。

## 已一致或明顯改善的部分

### 1. Artifact 公開路徑已從「直接公開」改成 token endpoint

證據：

- `backend/app/services/artifact_access.py:19` 建立 artifact URL。
- `backend/app/services/artifact_access.py:51` 驗證 token。
- `backend/app/services/artifact_access.py:118` 讀取 `ARTIFACT_SIGNING_SECRET`，未設定時使用 process-local secret。
- `backend/app/main.py:130` 改由 `/api/artifacts/{token}` 回傳檔案。
- `frontend/next.config.js:10` 只代理 `/api/:path*`，已無 `/generated_outputs` 代理。

優點：

- 已移除最危險的公開 `/generated_outputs` 直連模式。
- HMAC token 可防止猜路徑與竄改路徑。
- response header 有 `private, no-store`，比原本公開靜態檔合理。
- 測試涵蓋 token 竄改、過期、路徑跳脫、缺檔、非檔案與舊公開路徑 404。

缺點：

- 仍是 bearer URL，任何拿到 URL 的人都可在有效期內讀取。
- token 沒綁 user、project、dataset、run，也沒有 revoke/audit。
- 未設定 `ARTIFACT_SIGNING_SECRET` 時，服務重啟會讓舊 token 失效；封閉測試可接受，正式環境不可接受。
- `backend/app/main.py:144` 允許 SVG inline 回傳；如果未來允許使用者上傳或產生 SVG，需要再評估內容安全。

判斷：C1 從 critical 降為 high residual risk，但還沒達到公開 SaaS 標準。

### 2. 部署定位已改為封閉測試

證據：

- `DEPLOYMENT.md:1` 標示為封閉測試部署指南。
- `DEPLOYMENT.md:67` 起提醒不適合公開匿名使用或敏感資料。
- `frontend/src/components/EnvironmentNotice.tsx:10` 顯示封閉測試與敏感資料提醒。

優點：

- 產品承諾與實際安全能力更一致。
- 使用者進入產品前能看到限制，降低誤用。
- 文件有提醒 artifact signing secret。

缺點：

- 這是定位修正，不是安全能力本身。
- notice 常駐在多個頁面上，對商業產品質感有視覺摩擦；短期誠實是優點，長期應改成環境/權限感知提示。

判斷：C2 已修正。

### 3. Node 版本與 build 環境已對齊

證據：

- `Dockerfile:1` 與 `Dockerfile:15` 使用 `node:22-bookworm-slim`。
- `frontend/package.json:5` 要求 `node >=22.13.0`。

優點：

- Docker build 與本機 engines 不再矛盾。
- 降低部署時前端 dependency 或 Next.js 行為差異。

缺點：

- 仍需要在 CI/CD 明確固定 Node 與 npm 版本，避免 lockfile 與 runtime 漂移。

判斷：M6 已修正。

### 4. 聚焦工作台方向與近期 UI 計畫大致一致

證據：

- `frontend/src/components/analysis/AnalysisStepRail.tsx:31` 提供步驟導覽。
- `frontend/src/components/analysis/AnalysisModeSelector.tsx:43` 使用 fieldset/radio 表達分析模式。
- `frontend/src/components/analysis/AnalysisRecommendationPanel.tsx:20` 根據資料輪廓產生建議。
- `frontend/src/components/analysis/InlineCodeViewer.tsx:33` 提供程式碼檢視與切換。
- `frontend/src/components/analysis/ModelSelectionDrawer.tsx:45` 提供模型選擇 drawer。

優點：

- UI 從「功能堆疊」轉向「單一分析流程」，符合聚焦流程台的計畫。
- 使用真實狀態與測試覆蓋，沒有用假進度掩飾。
- 互動元件使用 fieldset/radio、`aria-current` 等語意化做法，可維護性較好。

缺點：

- `InlineCodeViewer` 目前是行號與純文字檢視，還不是計畫中的語法高亮。
- Browser 視覺 QA 本次沒有成功，無法確認桌面/手機寬度、對比、實際 spacing 與互動品質。
- 工作台改善偏前端體驗，尚未補上後端 Run Manifest、資料版本與模型重現能力。

判斷：UI 計畫部分一致，但產品底層還沒跟上。

## 不一致與缺口

### P0-1. 缺 PostgreSQL / Project / Dataset / Run / Artifact 的持久化領域模型

證據：

- 專案目前沒有 migrations、Alembic、SQLAlchemy/ORM、PostgreSQL schema 或 repository layer。
- `backend/app/services/analysis_jobs.py:37` 使用全域 `_jobs` dict。
- `backend/app/services/analysis_jobs.py:39` job TTL 是 4 小時。

影響：

- 無法可靠保存使用者、專案、資料集、分析 run、artifact、模型結果與權限關係。
- 服務重啟後工作狀態消失。
- 無法建立「可重現分析」與「專案歷史」這兩個 SaaS 核心價值。

優點：

- 單機 demo 很快，架構簡單。
- 封閉測試時容易 debug。

缺點：

- 一旦多人使用、部署多個 instance、或要追蹤歷史結果，現在架構會直接卡住。
- 後續補 DB 時需要重新整理 artifact、job、report 的 identity 與關聯。

建議優先度：最高。這是下一階段最該補的地基。

### P0-2. Job 執行仍是 in-memory + thread，未符合 Queue/Worker/SSE 計畫

證據：

- `backend/app/services/analysis_jobs.py:56` 使用 `asyncio.create_task(asyncio.to_thread(...))` 執行分析。
- `frontend/src/lib/api.ts:650` 前端每 450ms polling job 狀態。
- 專案未看到 Redis/RQ/Celery/Arq、worker process、job retry、backpressure、cancel token 持久化。

影響：

- 長任務與多使用者同時執行時，API process 會承擔所有運算壓力。
- 沒有 queue depth、retry、timeout、cancel、worker health 的正式治理。
- polling 頻率高，使用者增加後會浪費 API 資源。

優點：

- 現階段實作成本低，測試通過，進度可用。

缺點：

- 不可水平擴展。
- 服務重啟會失去 job state。
- 無法承載大量檔案與模型訓練。

建議優先度：最高，應和 PostgreSQL / Run Manifest 一起設計。

### P0-3. 權限與安全仍不符合公開產品計畫

缺口：

- 無登入/Auth。
- 無 Project ownership。
- 無每個 dataset/run/artifact 的授權檢查。
- 無 rate limit。
- 無 retention policy 執行機制。
- 無惡意檔案、公式注入、敏感資料掃描。
- 無操作 audit log。

影響：

- 不適合公開匿名上線。
- 不適合處理企業資料、個資或財務敏感資料。
- token artifact endpoint 只能降低公開路徑風險，不能取代權限系統。

優點：

- 目前封閉測試定位誠實，沒有過度承諾。

缺點：

- 產品若要從 demo 走到 SaaS，這會是最大阻塞。

建議優先度：最高。

### P1-1. 資料合併與資料品質仍偏簡化

證據：

- `backend/app/services/dataset_analyzer.py:163` 多檔案直接 `pd.concat(...)`。
- `backend/app/services/dataset_analyzer.py:177` 沒共同欄位時只加入 warning，不會要求使用者選 Join/Append 策略。
- `backend/app/services/dataset_analyzer.py:256` 目前主要提供 missing values 類摘要。

缺口：

- 缺 Join/Append preview。
- 缺 key 偵測、欄位 mapping、型別衝突處理。
- 缺 duplicate、constant column、ID/high cardinality、outlier、class imbalance、target leakage、date frequency 等資料品質檢查。

優點：

- 對簡單 CSV demo 夠快。
- 使用者不需要先理解資料建模概念就能得到結果。

缺點：

- 對真實商業資料容易產生錯誤合併。
- 使用者可能在不知情下拿錯資料訓練模型。

建議優先度：高。

### P1-2. 模型驗證仍不能支撐「可信資料科學」定位

證據：

- `backend/app/services/model_runner.py:309` 使用單次 `train_test_split`。
- `backend/app/services/model_runner.py:368` 對結果計算 R2/RMSE/MAE。
- `backend/app/services/model_runner.py:382` 分類任務才額外計算 accuracy。
- `backend/app/services/model_runner.py:417` 以同一個 test split 選 best model。
- `backend/app/services/model_runner.py:1134` 只在部分模型上做簡化 `GridSearchCV`。

缺口：

- 缺 stratified split、time-aware split、cross-validation strategy。
- 缺 classification/regression metric 分流的產品化呈現。
- 缺 baseline model、confidence interval、error analysis、feature importance 的一致解釋。
- 缺 leakage guard 與獨立 holdout。

優點：

- 已能跑多模型比較與基本 metrics。
- 適合教學、demo、快速探索。

缺點：

- 不足以宣稱是完整 AutoML 或可信模型選擇。
- 對時間序列、分類不平衡、小資料集容易誤導。

建議優先度：高。

### P1-3. 財務/時間序列分析仍是基礎線性預測

證據：

- `backend/app/services/financial_analyzer.py:22` 使用 `LinearRegression`。
- `backend/app/services/financial_analyzer.py:513` 起建立價格預測。
- `backend/app/services/financial_analyzer.py:522` 建立線性模型。

缺口：

- 無 backtesting。
- 無季節性/趨勢拆解。
- 無 Prophet/ARIMA/ETS 或 baseline 比較。
- 無預測區間與誤差報告。

優點：

- 快速、可解釋、依賴少。

缺點：

- 對金融資料的可靠性不足。
- 若 UI 呈現像正式預測，使用者可能過度信任。

建議優先度：高，但應在資料與 run 基礎完成後再做。

### P1-4. Agent 還不是自然語言驅動的 Analysis Plan

證據：

- `backend/app/services/agent_orchestrator.py:114` 起是固定資料/模型/財務/視覺/report workflow。
- `backend/app/services/agent_orchestrator.py:276` 起的 LLM 主要用於 summary，不是規劃與執行策略。

缺口：

- 使用者不能用自然語言指定分析目標後產生可審核 plan。
- 沒有 planner、tool selection、step confirmation、run graph。
- 沒有將 plan 與 artifact、code、report 做完整關聯。

優點：

- 固定 pipeline 比 agentic workflow 穩定，測試與 debug 成本低。

缺點：

- 和「智慧資料分析助理」或「資料科學家工作台」定位仍有差距。

建議優先度：中高。不要早於 DB/Run/Artifact 模型。

### P1-5. 產生程式碼與 report 還不能完整重現當次分析

證據：

- `backend/app/services/code_generator.py:110` 起是獨立產生分析程式。
- `backend/app/services/code_generator.py:529` 起的模型程式會重新訓練。
- `README.md:677` 仍指出 PDF 報告未實作。

缺口：

- 無 Run Manifest。
- 無資料 hash、schema fingerprint、split seed、模型參數、artifact provenance。
- code export 不是「當次 run 的精準重現腳本」。
- PDF/HTML report 與分享流程仍未完成。

優點：

- 對學習與展示仍有價值。

缺點：

- 對審計、交付、團隊協作與企業採用不足。

建議優先度：高。

### P2-1. 視覺化與 dashboard 能力仍未達完整工具計畫

目前狀態：

- 後端主要產生 Matplotlib PNG。
- 未看到 Plotly、互動式 dashboard、chart builder、exported HTML report 的完整落地。

優點：

- 低依賴、輸出穩定、容易測試。

缺點：

- 與主流資料分析工具的互動探索能力有差距。
- 使用者無法在圖上 drill down、篩選、重組或分享互動結果。

建議優先度：中。先補資料/run 基礎，再補互動 chart。

### P2-2. 文件與任務追蹤仍有歷史漂移

觀察：

- 2026-06-15 舊稽核報告已追加最新修正摘要，但長文件中仍保留大量歷史段落。
- `PROGRESS.md` 也包含多個時間點的紀錄，部分舊段落仍描述已修正的公開 artifact 問題。
- master roadmap 仍列出 Phase B-G 多份尚不存在或尚未落地的計畫文件。

優點：

- 保留歷史脈絡，方便追蹤修正。

缺點：

- 新加入者容易讀到舊風險描述，以為仍是當前狀態。
- 實作已完成但 checklist 未同步時，會降低計畫可信度。

建議優先度：中。需要一份短版 `CURRENT_STATUS.md` 或 roadmap index，標明目前真實狀態。

## 優點總結

1. 短期風險修正有效：公開 artifact、部署定位、Node build mismatch、重複 CTA 都有改善。
2. 測試狀態良好：後端、前端、typecheck、build 都通過。
3. UI 開始走向聚焦流程：step rail、mode selector、recommendation panel、model drawer 都符合「先引導再執行」方向。
4. 產品誠實度提升：目前明確標示封閉測試與不適合敏感資料。
5. 架構仍簡單：短期 demo、封閉測試與快速迭代成本低。

## 缺點總結

1. 還沒有 SaaS 必要的身份、權限、專案與資料持久化模型。
2. 長任務架構仍不適合多人與大量運算。
3. 資料科學可信度不足，尤其是合併、品質檢查、模型驗證、時間序列。
4. code/report/export 不能精準重現 run。
5. 視覺化仍偏靜態圖，不像完整分析工具。
6. 文件有歷史漂移，計畫與現況需要更清楚分層。

## 建議修正順序

### 第一優先：產品地基

1. 建立 PostgreSQL schema：User、Project、Dataset、AnalysisRun、Artifact、ModelResult。
2. 建立 Run Manifest：資料 hash、schema fingerprint、參數、split、模型、metrics、artifact 清單。
3. 將 artifact token 綁定 run/project/user，加入 revoke、audit、retention。
4. 引入 Auth 與 Project ownership。

### 第二優先：長任務架構

1. 將 `analysis_jobs.py` 從 in-memory dict 移到 DB-backed job state。
2. 引入 Redis + worker。
3. 支援 retry、timeout、cancel、queue status。
4. 將前端 polling 改為 SSE 或較低頻率 fallback polling。

### 第三優先：資料可信度

1. 多檔上傳先讓使用者選 Join / Append / Separate analysis。
2. 做資料品質報告：duplicates、constant、missing pattern、outlier、imbalance、leakage、date frequency。
3. 在 UI 顯示「可用於模型」與「需要修正」的欄位原因。

### 第四優先：模型與報告

1. 實作 stratified/time-aware split 與 baseline。
2. 分 regression/classification/time-series 呈現不同 metrics。
3. 讓 code export 精準重現 Run Manifest。
4. 完成 HTML/PDF report 與可分享 artifact。

### 第五優先：UI 品質補強

1. 補 InlineCodeViewer 語法高亮。
2. 做桌面與手機寬度 Browser QA。
3. 將環境提醒改成可收合或根據部署環境顯示。
4. 補完整 loading、empty、error、success、destructive states 的視覺驗證。

## 最終判斷

目前專案和「短期穩定化 + 聚焦工作台」計畫大致一致；和「完整資料科學 SaaS 平台」計畫仍明顯不一致。

下一步不應再優先加更多表面功能，而是先補 Project/Run/Artifact/Auth/Queue 這條主幹。否則後面做 dashboard、agent、PDF、分享、AutoML，都會缺少可靠的資料歸屬、權限與重現基礎。
