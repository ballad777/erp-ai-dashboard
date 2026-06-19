# 智能金融資料分析開發進度

## 2026-06-17：徹底修正外掛注入造成的 Hydration Overlay，並重新驗證真實資料分析

### 已完成檔案

- `frontend/src/app/layout.tsx`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/MarketingShell.tsx`
- `frontend/src/components/LanguageSwitch.tsx`
- `frontend/src/components/__tests__/AppShell.test.tsx`
- `frontend/src/components/__tests__/RootLayout.test.tsx`
- `PROGRESS.md`

### 新增功能與修正

- 重新檢查使用者提供的錯誤檔，確認這次 hydration mismatch 已不是單純手機導覽連結問題，而是瀏覽器外掛 `hive_keychain.js` 將 `chrome-extension://...` script 插入 `<head>`，與產品 theme 初始化 script 發生 head 子節點順序衝突。
- 將 `finai-product-theme-init` 從 React 管理的 `<head>` 移到 `<body>` 第一個 script，避免外掛污染 head 時觸發 Next.js hydration overlay。
- AppShell 的 skip link 也加入 `suppressHydrationWarning`，避免外掛替 `#main-content` 連結加 `keychainify-checked` class 時報錯。
- MarketingShell 與 LanguageSwitch 的常駐連結同步加入外掛容錯，避免首頁與語言切換連結出現同型 hydration mismatch。
- 新增 `RootLayout.test.tsx`，鎖定 theme bootstrap script 不得再出現在 head-managed markup。
- 擴大 `AppShell.test.tsx`，改為模擬外掛替所有 shell `<a>` 加 `keychainify-checked`，而不是只測手機導覽。

### 如何啟動

```bash
cd frontend
npm run dev -- --hostname 127.0.0.1 --port 3012
```

後端測試用：

```bash
cd backend
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8002
```

### 如何測試

```bash
cd frontend
npm run test:run -- RootLayout.test.tsx
npm run test:run -- AppShell.test.tsx MarketingShell.test.tsx ThemePicker.test.tsx
npm run test:run
npm run typecheck
npm run build -- --webpack

cd ../backend
.venv/bin/pytest tests/test_dataset_analyzer.py tests/test_model_runner.py tests/test_api_hardening.py -q
```

真實資料 API 驗證：

```bash
curl -sS -X POST http://127.0.0.1:8002/api/datasets/analyze-multiple \
  -F files=@sample_datasets/housing_sample.csv

curl -sS -X POST http://127.0.0.1:8002/api/datasets/analyze-multiple \
  -F files=@sample_datasets/stock_prices_sample.csv

curl -sS -X POST http://127.0.0.1:8002/api/models/analyze \
  -F file=@sample_datasets/housing_sample.csv \
  -F target_column=price_usd \
  -F analysis_mode=regression \
  -F chart_types=model_comparison,feature_importance,predicted_vs_actual,residual_plot \
  -F model_selection_mode=auto \
  -F selected_models=auto \
  -F automl_mode=off
```

### 本次驗證結果

- `RootLayout.test.tsx`：先紅後綠；修正前可重現 head script 問題，修正後 1 passed。
- `AppShell.test.tsx MarketingShell.test.tsx ThemePicker.test.tsx`：3 個測試檔、12 passed。
- `npm run test:run`：19 個測試檔、69 passed。
- `npm run typecheck`：通過。
- `npm run build -- --webpack`：通過。
- `backend/.venv/bin/pytest tests/test_dataset_analyzer.py tests/test_model_runner.py tests/test_api_hardening.py -q`：17 passed。
- Browser 驗收 `http://127.0.0.1:3012/app/data`：
  - 頁面 title 為「智能金融資料分析」。
  - DOM 有「資料工作區」與「上傳佇列」，不是空白頁。
  - 未偵測到 `A tree hydrated` 或 `Console Error` overlay。
  - 本次 reload 後 console 沒有 hydration、tree hydrated、keychainify、hive_keychain 或 `finai-product-theme-init` 相關錯誤。
  - `finai-product-theme-init` 目前位於 `BODY`，head 內數量為 0。
  - 從「資料」切到「模型」再切回「資料」後，仍無相關錯誤。
- 真實資料摘要驗證：
  - `housing_sample.csv`：後端回傳 12 筆、6 欄、`age_years` 缺失 1；與 pandas 直接讀 CSV 的列數、欄數、缺失值與所有數值摘要完全一致，`comparison_errors: []`。
  - `stock_prices_sample.csv`：後端回傳 12 筆、7 欄、`close` 缺失 1；與 pandas 直接讀 CSV 的列數、欄數、缺失值與所有數值摘要完全一致，`comparison_errors: []`。
- 真實模型分析驗證：
  - 使用 `housing_sample.csv` 與 target `price_usd` 呼叫 `/api/models/analyze`，HTTP 200。
  - 回傳 `row_count_used=12`、`feature_count_used=5`，與原始 CSV 對應。
  - 實際訓練 8 個模型並產生 4 張圖表。
  - 已檢查 4 個圖表檔案存在且非空白：model comparison、feature importance、predicted vs actual、residual plot。

### Known Issues

- 使用者瀏覽器若啟用會修改 DOM 的外掛，仍可能在尚未加 `suppressHydrationWarning` 的非主要內容連結上造成 React attribute mismatch；目前已處理 RootLayout、AppShell、MarketingShell 與 LanguageSwitch 的主要入口。
- 本輪 Browser 可成功截圖；若使用者分頁仍顯示舊 overlay，通常是舊 dev overlay 狀態殘留，請重新整理或重開該分頁。
- 模型分數會受資料量與 train/test split 影響；本輪只驗證模型確實使用上傳資料、結果欄位正確、圖表真實產生，不宣稱小型 sample 的模型有正式商業預測力。

### 下一階段要做什麼

- 若再次出現 hydration mismatch，優先確認錯誤 diff 指向哪個具體元素，再加入對應回歸測試，不再用單點猜測修法。
- 可新增一個全站 hydration smoke test，批量模擬外掛替所有主要 shell 連結加 class，覆蓋首頁與工作區主要頁。

## 2026-06-17：修正瀏覽器外掛造成的 Next.js Hydration 錯誤

### 已完成檔案

- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/__tests__/AppShell.test.tsx`
- `PROGRESS.md`

### 新增功能與修正

- 依使用者提供的 Next.js console error 追查，根因是瀏覽器外掛在 React hydration 前替導覽連結加入 `keychainify-checked` class。
- AppShell 的品牌連結、桌面導覽、上方加入資料連結與手機導覽連結已加入 `suppressHydrationWarning`，讓外掛注入的非應用程式 class 不再觸發 Next.js hydration mismatch overlay。
- 此修正只針對外部環境修改 DOM 屬性的情境，不改動資料分析、模型分析或報告邏輯。
- 新增回歸測試，模擬外掛在 `.mobile-product-nav a` 上加入 `keychainify-checked`，並確認 hydration 不再輸出 `A tree hydrated but some attributes...` 錯誤。

### 如何啟動

```bash
cd frontend
npm run dev -- --hostname 127.0.0.1 --port 3012
```

測試網址：

```text
http://127.0.0.1:3012/app/data
```

### 如何測試

```bash
cd frontend
npm run test:run -- AppShell.test.tsx
npm run typecheck
npm run build -- --webpack
```

人工驗收：

1. 開啟 `http://127.0.0.1:3012/app/data`。
2. 重新整理頁面。
3. 確認沒有 Next.js hydration error overlay。
4. 點選底部或側邊工作區導覽，往返「模型」與「資料」。
5. 確認 console 沒有 `hydrated`、`hydration`、`keychainify` 相關錯誤。

### 本次驗證結果

- `npm run test:run -- AppShell.test.tsx`：1 個測試檔、4 passed。
- `npm run typecheck`：通過。
- `npm run build -- --webpack`：通過。
- Browser 驗收：
  - `http://127.0.0.1:3012/app/data` 可正常載入，title 為「智能金融資料分析」。
  - DOM 顯示「資料工作區」等有效內容，不是空白頁。
  - 未偵測到 `A tree hydrated` 或 `Console Error` overlay。
  - console error/warn 中沒有 hydration、tree hydrated、keychainify 相關訊息。
  - 從「資料」切到「模型」再切回「資料」後，仍無相關錯誤。

### Known Issues

- Browser screenshot API 在本輪驗收時回報 CDP `Page.captureScreenshot` 逾時；已改用 DOM、URL、console logs 與導覽互動作為驗證證據。
- 如果使用者仍看到舊 overlay，通常是舊 dev overlay 狀態未清除；請重新整理頁面或重開該分頁。

### 下一階段要做什麼

- 若後續還有其他外掛注入屬性造成 hydration mismatch，優先用同樣方式建立可重現測試，再只針對受影響的穩定導覽/控制元素處理。

## 2026-06-17：修正資料領域誤判，禁止把 Price 直接視為房價

### 已完成檔案

- `backend/app/services/insight_narrative.py`
- `backend/tests/test_insight_narrative.py`
- `PROGRESS.md`

### 新增功能與修正

- 修正資料摘要敘事層 `_infer_dataset_kind` 的錯誤規則。
- 舊規則只要欄位含 `price` 就可能判斷為「房價或不動產資料」，導致汽車銷售資料 `quikr_car.csv` 被錯誤標示。
- 新規則把 `price` 視為一般價格欄位，不再作為房價證據。
- 房價或不動產資料必須同時具有足夠不動產欄位證據，例如 `house`、`housing`、`property`、`bedroom`、`sqft`、`坪`、`屋齡`、`房屋`、`樓層` 等。
- 新增汽車銷售資料辨識，當欄位包含 `car`、`vehicle`、`kms_driven`、`fuel_type`、`transmission`、`engine`、`里程`、`燃料` 等足夠證據時，標示為「汽車銷售資料」。
- 一般商品或交易資料只有 `Price`、`quantity` 等欄位時，保守標示為「價格或交易表格資料」，不冒充特定產業。

### 如何啟動

```bash
cd backend
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8002
```

前端維持：

```bash
cd frontend
npm run dev -- --hostname 127.0.0.1 --port 3012
```

### 如何測試

```bash
cd backend
.venv/bin/pytest tests/test_insight_narrative.py -q
.venv/bin/pytest -q
```

人工/API 驗收：

1. 上傳欄位包含 `name, company, year, Price, kms_driven, fuel_type` 的汽車資料。
2. 資料摘要 headline 應顯示「汽車銷售資料」。
3. headline 不應出現「房價」或「不動產」。

### 本次驗證結果

- `backend/.venv/bin/pytest tests/test_insight_narrative.py -q`：2 passed。
- `backend/.venv/bin/pytest tests/test_insight_narrative.py tests/test_dataset_analyzer.py -q`：7 passed。
- `backend/.venv/bin/pytest tests/test_api_hardening.py -q`：5 passed。
- `backend/.venv/bin/pytest -q`：46 passed。
- HTTP API 實測 `quikr_car_sample.csv`：
  - 欄位：`name, company, year, Price, kms_driven, fuel_type`
  - 回傳 headline：`這份資料看起來偏向「汽車銷售資料」...`
  - 未出現「房價」或「不動產」。

### 下一階段要做什麼

- 將資料領域推論改成可回傳 evidence 與 confidence 的結構化結果，讓前端能顯示「為什麼判斷為此資料類型」。
- 增加更多常見公開資料集測試：二手車、零售商品、醫療、體育、一般價格表，避免單一欄位造成產業誤判。

## 2026-06-17：報告中心改成 AI 顧問式決策解讀

### 已完成檔案

- `backend/app/services/insight_narrative.py`
- `backend/app/services/agent_orchestrator.py`
- `backend/app/services/model_runner.py`
- `backend/app/services/report_generator.py`
- `backend/app/schemas.py`
- `backend/tests/test_agent_report.py`
- `frontend/src/lib/api.ts`
- `frontend/src/components/AgentReportPanel.tsx`
- `frontend/src/components/__tests__/AgentReportPanel.test.tsx`
- `frontend/src/app/globals.css`

### 新增功能

- 新增「決策敘事層」：把資料品質、模型結果、金融分析與圖表轉換成一般人可讀的分析摘要。
- 報告 API 現在回傳 `decision_brief`，包含：
  - `plain_language_summary`
  - `priority_findings`
  - `model_guidance`
  - `chart_interpretations`
  - `report_sections`
  - `risk_and_limitations`
  - `ai_conclusion`
- 報告中心改成顧問式閱讀順序：先看 10 秒摘要、優先級、風險/機會/下一步，再展開模型與圖表證據。
- 每張圖表都新增解讀欄位：圖表說明、關鍵發現、代表意義、趨勢解讀、異常說明、商業洞察、建議行動。
- 模型選項新增一般人可讀欄位：模型用途、適用資料類型、使用難度、適用場景。
- Word 報告升級為顧問式章節，包含分析目的、分析方法、分析結果、結果解讀、商業意義、建議行動、風險與限制、AI 結論摘要。

### 如何啟動

本輪測試使用不干擾既有服務的新埠：

後端：

```bash
cd backend
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001
```

前端：

```bash
cd frontend
INTERNAL_API_BASE_URL=http://127.0.0.1:8001 npm run build -- --webpack
npm run start -- --hostname 127.0.0.1 --port 3011
```

### 如何測試

後端：

```bash
cd backend
.venv/bin/pytest -q
```

前端：

```bash
cd frontend
npm run typecheck
npm run test:run
INTERNAL_API_BASE_URL=http://127.0.0.1:8001 npm run build -- --webpack
```

真實報告 API 手動測試：

```bash
curl -s -X POST http://127.0.0.1:8001/api/reports/generate \
  -F file=@sample_datasets/stock_prices_sample.csv \
  -F target_column=close \
  -F analysis_mode=regression \
  -F chart_types=model_comparison,feature_importance,predicted_vs_actual,residual_plot \
  -F model_selection_mode=custom \
  -F selected_models=ridge,random_forest \
  -F automl_mode=off
```

回傳應包含 `decision_brief.priority_findings`、`decision_brief.model_guidance`、`decision_brief.chart_interpretations` 與 `report_url`。

### Known Issues

- `decision_brief` 目前是本機規則式解讀；若未設定 `OPENAI_API_KEY`，系統會明確標示 `local_rule_based`，不假裝使用 LLM。
- 圖表解讀會使用目前已產生的模型結果與資料品質摘要推導；尚未做更深層的殘差分群、特徵交互或因果推論。
- Word 目前輸出 DOCX；PDF 與 ZIP 套件仍未啟用。

### 下一階段

- 將圖表解讀加入更細的數據證據，例如前 N 個重要特徵、最大誤差樣本、殘差群聚摘要。
- 將報告中心接入專案歷史，讓使用者可回看每次分析的摘要與建議。
- 若要正式對外，補正式登入、權限、資料保留政策與 audit UI。

## 2026-06-17：依一致性複查補產品地基、Run Manifest 與資料品質治理

### 已完成檔案

- `CURRENT_STATUS.md`
- `README.md`
- `DEPLOYMENT.md`
- `backend/app/database/__init__.py`
- `backend/app/database/connection.py`
- `backend/app/database/repository.py`
- `backend/database/postgres_schema.sql`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/services/artifact_access.py`
- `backend/app/services/analysis_jobs.py`
- `backend/app/services/dataset_analyzer.py`
- `backend/app/services/model_runner.py`
- `backend/app/services/run_governance.py`
- `backend/tests/test_dataset_analyzer.py`
- `backend/tests/test_model_runner.py`
- `backend/tests/test_run_governance.py`
- `frontend/src/lib/api.ts`
- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/components/MarketingHome.tsx`
- `frontend/src/components/WorkspaceDashboard.tsx`
- `frontend/src/components/ProductPreview.tsx`
- `frontend/src/app/layout.tsx`
- `frontend/src/app/en/layout.tsx`

### 新增功能

- 新增本機可執行持久化層，預設建立 `.local/finai.sqlite3`。
- 新增 PostgreSQL DDL：User、Project、Dataset、AnalysisRun、Artifact、ModelResult、AnalysisJob、AuditLog。
- 新增 `GET /api/auth/session`，提供封閉測試 demo identity 與 project context。
- 主要分析 API 會建立 `run_id`、`dataset_id` 與 `run_manifest`。
- Run Manifest 會記錄輸入檔 SHA-256、參數、模型結果與 artifact 清單。
- Artifact token 會在 run context 內綁定 `artifact_id`、`run_id`、`project_id`、`user_id`，下載時寫入 audit log。
- Job state 寫入資料庫；記憶體仍保留作為執行中取消控制。
- 新增 API rate limit middleware，預設每 IP + path 每分鐘 180 次。
- 上傳支援 JSON，前後端格式提示同步更新。
- 資料分析新增品質報告：缺失值、重複列、常數欄位、高基數欄位、ID-like 欄位、IQR 異常值、類別不平衡、日期頻率、疑似 target leakage。
- 多檔合併新增合併策略建議、Join key 候選與 schema conflict 檢查。
- 模型分析新增 baseline model；分類任務在可行時使用 stratified split。
- 模型前處理會將類別欄位明確轉成字串，避免同欄位混合數字/文字造成 OneHotEncoder 失敗。

### 如何啟動

後端：

```bash
cd backend
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm run build
npm run start -- --hostname 127.0.0.1 --port 3010
```

### 如何測試

後端測試：

```bash
cd backend
.venv/bin/pytest -q
```

目前結果：`40 passed`。

可用 API 手動確認：

```bash
curl -sS http://127.0.0.1:8000/api/auth/session
curl -sS -X POST -F file=@sample_datasets/housing_sample.csv http://127.0.0.1:8000/api/datasets/analyze
```

回傳應包含 `run_id`、`dataset_id`、`schema_fingerprint`、`quality_report` 與 `run_manifest`。

### Known Issues

- 目前執行 repository 仍是 SQLite fallback；`backend/database/postgres_schema.sql` 已提供 PostgreSQL schema，但尚未接 PostgreSQL driver/repository。
- 尚未接入正式登入、OAuth、密碼驗證或多租戶 Project ownership。
- 尚未接入 Redis / Queue / Worker；長任務仍由 API process 內 thread 執行。
- 尚未提供 SSE；前端仍使用 polling。
- 尚未完成 artifact revoke UI、retention scheduler 與 audit 查詢介面。
- 尚未完成 Prophet/ARIMA/ETS、正式 backtesting、預測區間與時間序列驗證。
- 尚未完成 PDF 報告、一鍵 ZIP 套件與互動式 Plotly dashboard。

### 下一階段

- 將 SQLite repository 抽換為 PostgreSQL repository，導入 migration。
- 將 analysis job 移到 Redis/worker，支援 retry、timeout、cancel 與 worker health。
- 將前端 polling 改成 SSE，保留低頻 fallback polling。
- 補 artifact revoke/retention/audit 管理 API 與 UI。

## 2026-06-17：本機服務啟動、API 串接與瀏覽器驗收

### 已完成檔案

- `PROGRESS.md`

### 新增功能

- 本次沒有新增功能，主要補齊前一輪受環境限制而未完成的本機服務與瀏覽器驗收。

### 如何啟動

後端：

```bash
cd backend
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm run start -- --hostname 127.0.0.1 --port 3010
```

測試網址：

- `http://localhost:3010`
- `http://localhost:3010/app/data`
- `http://localhost:3010/app/models`

### 如何測試

已完成本機服務連線測試：

```bash
curl -sS http://127.0.0.1:8000/health
curl -I -sS http://127.0.0.1:3010
```

結果：FastAPI health endpoint 回傳 `{"status":"ok","service":"智能金融資料分析 API"}`；Next.js production preview 回傳 HTTP 200。

已完成單檔資料分析 API 測試：

```bash
curl -sS -X POST \
  -F file=@sample_datasets/housing_sample.csv \
  http://127.0.0.1:8000/api/datasets/analyze
```

結果：後端讀取 `housing_sample.csv`，回傳 12 筆、6 欄、`age_years` 1 筆缺失值、數值欄位摘要與推薦目標欄位。

已完成模型分析 API 測試：

```bash
curl -sS -X POST \
  -F target_column=price_usd \
  -F analysis_mode=auto \
  -F chart_types=auto \
  -F model_selection_mode=auto \
  -F selected_models=auto \
  -F automl_mode=off \
  -F file=@sample_datasets/housing_sample.csv \
  http://127.0.0.1:8000/api/models/analyze
```

結果：後端自動判斷為 regression，推薦並訓練 Ridge、Lasso、ElasticNet、Random Forest、Gradient Boosting、XGBoost、KNN；同時產生模型比較、特徵重要性、預測值與實際值、殘差圖與短效 artifact URL。

已完成程式碼與 Notebook 產出 API 測試：

```bash
curl -sS -X POST \
  -F target_column=price_usd \
  -F model_name=ridge \
  -F analysis_mode=auto \
  -F chart_types=auto \
  -F file=@sample_datasets/housing_sample.csv \
  http://127.0.0.1:8000/api/code/generate
```

結果：產生 `generated_code.py`、`notebook.ipynb`、內嵌程式碼內容與短效下載 URL。

已完成金融分析 API 測試：

```bash
curl -sS -X POST \
  -F file=@sample_datasets/stock_prices_sample.csv \
  http://127.0.0.1:8000/api/finance/analyze
```

結果：後端自動偵測 `date` 與 `close`，產生 MA、報酬率、波動率、RSI、MACD、VaR、預測點與金融圖表。

已完成報告 API 測試：

```bash
curl -sS -X POST \
  -F target_column=price_usd \
  -F analysis_mode=auto \
  -F chart_types=auto \
  -F model_selection_mode=auto \
  -F selected_models=auto \
  -F automl_mode=off \
  -F file=@sample_datasets/housing_sample.csv \
  http://127.0.0.1:8000/api/reports/generate
```

結果：產生 Word 報告、代理流程摘要、模型分析結果與短效下載 URL；未設定 `OPENAI_API_KEY` 時明確回傳本機規則摘要，不假裝 LLM 執行。

已完成多檔上傳與合併分析 API 測試：

```bash
curl -sS -X POST \
  -F files=@sample_datasets/housing_sample.csv \
  -F files=@sample_datasets/stock_prices_sample.csv \
  http://127.0.0.1:8000/api/datasets/analyze-multiple
```

結果：兩個檔案都讀取成功，並產生 24 筆、15 欄的合併資料摘要、來源檔案欄位、來源列號與合併說明。

已完成 Browser 驗收：

- `http://localhost:3010/` 桌機尺寸：首頁可渲染、標題為「智能金融資料分析」、核心 Hero 與 CTA 存在、console error 為 0。
- `http://localhost:3010/app/data` 桌機尺寸：資料頁可渲染、console error 為 0。
- `http://localhost:3010/app/models` 桌機尺寸：模型頁可渲染、聚焦流程與空狀態存在、console error 為 0。
- 配色選單：存在「配色」按鈕，選單內沒有「套用」按鈕，點擊主題後選單關閉，符合點擊立即套用的互動。
- 390 × 844 手機尺寸：首頁與模型頁都可渲染、console error 為 0。

### Known Issues

- Browser 工具目前沒有可用的檔案選擇 API，因此前端 `<input type="file">` 的實際檔案選取沒有用瀏覽器工具完成；本輪已用真實後端 API 上傳檔案驗證資料讀取、模型訓練與產物輸出。
- 目前仍是本機封閉測試，不是正式多使用者部署；artifact token 已是短效 URL，但尚未接入 user/project/tenant 權限。
- 一鍵 ZIP 套件依使用者先前要求暫不啟用。

### 下一階段

- 若要做可分享版本，下一階段應優先處理正式登入、專案/使用者資料隔離、持久化資料庫、背景任務佇列與公開部署設定。

## 2026-06-16：稽核對齊修正、短效產物下載與聚焦模型工作區

### 已完成檔案

- `backend/app/main.py`
- `backend/app/services/artifact_access.py`
- `backend/app/services/code_generator.py`
- `backend/app/services/financial_analyzer.py`
- `backend/app/services/model_runner.py`
- `backend/app/services/report_generator.py`
- `backend/tests/test_artifact_access.py`
- `frontend/next.config.js`
- `frontend/src/app/product-interface.css`
- `frontend/src/app/product-motion.css`
- `frontend/src/components/ThemeProvider.tsx`
- `frontend/src/components/ThemePicker.tsx`
- `frontend/src/components/PagePrimitives.tsx`
- `frontend/src/components/ModelAnalysisPanel.tsx`
- `frontend/src/components/WorkspaceToolPages.tsx`
- `frontend/src/components/analysis/AnalysisStepRail.tsx`
- `frontend/src/components/analysis/AnalysisModeSelector.tsx`
- `frontend/src/components/analysis/DatasetMetricStrip.tsx`
- `frontend/src/components/analysis/AnalysisRecommendationPanel.tsx`
- `frontend/src/components/analysis/ModelSelectionDrawer.tsx`
- `frontend/src/components/analysis/InlineCodeViewer.tsx`
- `frontend/src/components/__tests__/AnalysisWorkspace.test.tsx`
- `frontend/src/components/__tests__/InlineCodeViewer.test.tsx`
- `frontend/src/components/__tests__/SemanticColorUsage.test.ts`
- `frontend/src/components/__tests__/ThemePicker.test.tsx`
- `frontend/src/components/__tests__/ThemeProvider.test.tsx`
- `README.md`
- `PROGRESS.md`
- `docs/audits/2026-06-15-project-plan-consistency-audit.md`

### 新增功能

- 後端移除 `/generated_outputs/*` 公開靜態直出，改由 `/api/artifacts/{token}` 提供短效 HMAC capability URL。
- 模型、圖表、程式碼、Notebook、Word 報告、清理後 CSV 與模型結果 XLSX 的下載 URL 都改為 artifact token URL。
- 配色選擇器改為點擊立即套用並保存，不再需要「套用／取消」。
- 修正分析面板低對比文字與不支援的 `bg-white/78` class，改用語意色彩與實色 surface。
- 模型頁改為聚焦流程台：分析步驟、目標欄位、建議目標、分析模式、資料摘要、模型策略、清楚下一步與建議面板。
- 手動模型選擇改為可搜尋、可篩選、可清除的漸進式抽屜。
- 沒有後端 progress 時，loading 不再輪播假步驟，只顯示等待後端狀態；有 progress 時才顯示後端 stage。
- 程式碼預覽改為 `InlineCodeViewer`，支援 Python / Notebook 分頁、行號與複製。
- README 已更新封閉測試定位、即時配色、短效 artifact URL 與聚焦模型流程。

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

Production preview：

```bash
cd frontend
npm run build
npm run start -- --hostname 127.0.0.1 --port 3010
```

### 如何測試

目前已執行：

```bash
cd backend
.venv/bin/pytest -q
```

結果：37 passed，71 warnings。

```bash
cd frontend
npm run test:run
npm run typecheck
npm run build -- --webpack
git diff --check
```

結果：16 個測試檔、61 個測試通過；TypeScript typecheck 通過；Next.js production build 通過；diff whitespace 檢查通過。

本機服務驗收：

- 前端 production preview 已成功啟動於 `http://127.0.0.1:3010`。
- 後端 FastAPI HTTP 服務在沙盒內啟動時遇到 `listen EPERM`；改用授權模式啟動時，系統因額度限制拒絕授權，因此本輪未完成瀏覽器端 API 串接驗收。
- Browser 外掛拒絕開啟 `http://127.0.0.1:3010`，原因為目前瀏覽器安全政策封鎖該網址；本輪未繞過該限制。

Demo 流程：

1. 啟動後端與前端。
2. 到 `/app/data` 上傳 `sample_datasets/housing_sample.csv`。
3. 到 `/app/models`，確認「選擇分析方式」只顯示主要決策與清楚下一步。
4. 點選「配色」，確認點擊任一配色會立即套用，沒有套用按鈕。
5. 執行模型分析，確認 loading 階段來自後端 progress。
6. 產生程式碼，確認 Python / Notebook 可在頁面內切換、複製與下載。
7. 點擊下載連結，確認走 `/api/artifacts/{token}`。

### Known Issues

- capability URL 是封閉測試保護，不是正式 user/project/tenant authorization。
- 未完成 PostgreSQL、Project ownership、Analysis Run Manifest、Redis Worker、SSE 與 restart recovery。
- `ARTIFACT_SIGNING_SECRET` 若未設定，token 會在服務重啟後失效；正式封閉測試部署應設定穩定 secret。
- SVG artifact 目前會以 inline image 顯示；若未來允許使用者生成 SVG，需再加強 MIME 與內容限制。
- 一鍵 ZIP 套件依使用者要求暫不啟用。
- 本輪已完成測試、typecheck 與 production build；Browser 實機驗收因瀏覽器安全政策封鎖 `http://127.0.0.1:3010` 未完成。
- 後端 HTTP 開埠驗收因本機沙盒權限與授權額度限制未完成；後端分析邏輯已由 pytest / TestClient 覆蓋。

### 下一階段

- Phase B：PostgreSQL domain model、Analysis Run Manifest、私人 artifact authorization、auth/project ownership、Redis worker、SSE progress 與 rate limit。

## 2026-06-15：通用分析平台階段 A，產品介面

### 已完成檔案

- `frontend/src/lib/themes.ts`
- `frontend/src/app/product-themes.css`
- `frontend/src/app/product-interface.css`
- `frontend/src/app/product-motion.css`
- `frontend/src/components/ThemeProvider.tsx`
- `frontend/src/components/ThemePicker.tsx`
- `frontend/src/components/DataLensHero.tsx`
- `frontend/src/components/WorkspaceDetailPanel.tsx`
- `frontend/src/components/WorkspaceInsightGrid.tsx`
- `frontend/src/components/ui/popover.tsx`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/MarketingHome.tsx`
- `frontend/src/components/MarketingShell.tsx`
- `frontend/src/components/WorkspaceDashboard.tsx`
- `frontend/src/components/WorkspaceToolPages.tsx`
- `frontend/src/components/MotionPrimitives.tsx`
- `frontend/src/app/app/charts/page.tsx`
- `frontend/src/app/en/app/charts/page.tsx`
- `frontend/src/components/__tests__/`
- `frontend/vitest.config.ts`
- `frontend/src/test/setup.ts`
- `README.md`
- `PROGRESS.md`

### 新增功能

- 首頁改為固定兩行的 Data Lens Hero：「看懂資料。」「找到下一步。」。
- 右側資料分析視覺可依滑鼠位置移動透鏡，觸控與 reduced motion 會自動降級。
- 建立十套語意配色，支援即時預覽、套用、取消、首屏同步初始化與本機持久化。
- 深色配色同步更新既有 `--color-*` 變數，避免表格、表單或結果面板殘留亮色。
- 桌面工作區改為 72px icon rail，平板與手機改用底部導覽。
- 新增中英文 `/app/charts` 路由，未產生真實圖表時不顯示示範圖。
- 總覽頁先顯示最多三個真實洞察、資料概況與下一步，再顯示完整流程與成果。
- 模型結果新增桌面側欄／手機底部抽屜詳情，支援 Escape、背景關閉與焦點回復。
- 加入 Vitest、Testing Library 與 jsdom，覆蓋配色、Hero、導覽、詳情面板與洞察層級。

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端開發模式：

```bash
cd frontend
npm install
npm run dev
```

正式模式：

```bash
cd frontend
npm run build
npm run start -- --hostname 127.0.0.1 --port 3010
```

### 如何測試

```bash
cd frontend
npm run test:run
npm run typecheck
npm run build
```

```bash
cd backend
source .venv/bin/activate
pytest -q
```

Demo 流程：

1. 開啟 `/app/data`，上傳 `sample_datasets/housing_sample.csv` 與 `sample_datasets/stock_prices_sample.csv`。
2. 確認兩個檔案都成功讀取，並可切換單檔與合併資料。
3. 在模型頁選擇 `price_usd`，使用自動模式，確認系統判斷為回歸並依資料推薦模型。
4. 在金融頁使用股票資料，確認日期與 `close` 自動偵測，以及 RSI、MACD、波動率、VaR 與預測。
5. 在模型結果中產生程式碼，確認 Python 與 Notebook 內容可直接在頁內預覽。
6. 在報告頁產生 Word 報告，確認輸出寫入 `generated_outputs/reports/`。

### 本次驗證結果

- 前端測試：30 個測試全部通過。
- 前端型別檢查：通過。
- Next.js production build：通過，包含 `/app/charts` 與 `/en/app/charts`。
- 後端測試：23 個測試全部通過。
- Browser：1440×900、834×1112、390×844 均無水平溢出。
- Browser：Hero 固定兩行，資料透鏡可互動，十套配色可預覽與保存。
- Browser：手機導覽觸控高度 50px，配色面板未被裁切，Escape 會關閉並回復焦點。
- 真實多檔 API：兩個 sample dataset 均成功讀取並產生 24 筆合併摘要。
- 真實自動模型 API：房價資料判斷為回歸，自動選出 7 個候選模型並產生 4 張圖。
- 真實金融 API：產生 RSI、MACD、波動率、VaR 與 5 個預測點。
- 真實輸出：已產生 Python、Notebook、Word 報告、PNG 圖表與 joblib 模型檔。

### Known Issues

- 一鍵 ZIP 套件依使用者要求暫不啟用。
- Browser runtime 沒有文件化的檔案選擇 API，因此上傳流程以真實 FastAPI multipart API、前端元件測試與 Browser 頁面狀態分開驗證。
- Python 3.14 會出現 FastAPI / Starlette 的 `asyncio.iscoroutinefunction` deprecation warnings，不影響目前 23 個測試結果。
- 圖表工作區目前集中呈現既有真實分析狀態；更完整的跨分析圖表索引會在後續資料持久化階段擴充。

### 下一階段

- PostgreSQL、Redis、背景 Worker 與跨裝置持久化分析任務。
- 擴充通用型分類、分群、異常偵測、時間序列與 AutoML 後端能力。
- 登入與跨裝置記憶功能仍依先前決定暫緩。

## 2026-06-09：第一階段，基礎專案

### 已完成檔案

- `README.md`
- `PROGRESS.md`
- `.gitignore`
- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/services/dataset_analyzer.py`
- `backend/tests/test_dataset_analyzer.py`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/next.config.js`
- `frontend/postcss.config.js`
- `frontend/tailwind.config.ts`
- `frontend/tsconfig.json`
- `frontend/src/app/globals.css`
- `frontend/src/app/layout.tsx`
- `frontend/src/app/page.tsx`
- `frontend/src/app/upload/page.tsx`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/components/AnalysisResult.tsx`
- `frontend/src/lib/api.ts`
- `sample_datasets/housing_sample.csv`
- `sample_datasets/stock_prices_sample.csv`
- `generated_outputs/README.md`
- `generated_outputs/charts/.gitkeep`
- `generated_outputs/reports/.gitkeep`
- `generated_outputs/code/.gitkeep`
- `generated_outputs/models/.gitkeep`
- `generated_outputs/data/.gitkeep`

### 新增功能

- 建立 Next.js + React + Tailwind CSS 前端專案結構。
- 建立 FastAPI 後端專案結構。
- 建立首頁，顯示目前平台階段與可用流程。
- 建立資料集上傳頁。
- 前端上傳表單會呼叫真實後端 API：`POST /api/datasets/analyze`。
- 後端可讀取 CSV / Excel，並回傳欄位名稱、資料筆數、欄位數、缺失值統計、欄位型別與數值欄位摘要。
- 前端可顯示後端實際分析結果。
- 建立 2 個測試資料集。
- 建立 `generated_outputs/` 與未來輸出子資料夾。
- 加入後端單元測試。

### 如何啟動

後端：

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

前端網址：

```text
http://localhost:3000
```

### 如何測試

後端測試：

```bash
cd backend
source .venv/bin/activate
pytest
```

手動 API 測試：

```bash
curl -X POST http://127.0.0.1:8000/api/datasets/analyze \
  -F "file=@sample_datasets/housing_sample.csv"
```

UI 測試：

1. 啟動後端與前端。
2. 打開 `http://localhost:3000/upload`。
3. 上傳 `sample_datasets/housing_sample.csv`。
4. 確認頁面顯示欄位、資料筆數、缺失值與數值摘要。

### 本次驗證結果

- `pip install -r requirements.txt`：通過。
- `pytest`：通過，1 個測試通過。
- `python -m compileall app tests`：通過。
- 真實 API 測試：`POST /api/datasets/analyze` 上傳 `housing_sample.csv` 成功。
- `npm install`：通過。
- `npm audit --audit-level=moderate`：通過，0 個漏洞。
- `npm run typecheck`：通過。
- `npm run build`：通過。
- Browser DOM 驗證：`/upload` 與 `/` 頁面可正常渲染；未選檔按下「分析資料集」會顯示錯誤提示。

### 環境與套件問題處理

- `pip install` 第一次因沙盒無法解析 PyPI DNS 失敗，已用授權網路安裝完成。
- Python 3.14.5 環境中 pandas/numpy 以原始碼建立 wheel，最終安裝成功。
- 原先 Next.js 15.1.4 安裝時出現安全性警告，已升級到 Next.js 16.2.7。
- PostCSS 安全性 advisory 已修正，使用 PostCSS 8.5.15 並加入 npm `overrides`。
- Next Turbopack build 在沙盒內因本機連接埠權限失敗，已用授權環境重跑並通過。
- Browser screenshot 在當前 session 逾時；已改用 Browser DOM snapshot、console logs 與互動檢查驗證頁面。

### 下一階段要做什麼

第二階段：模型分析功能。

## 2026-06-09：第二階段，模型分析功能與全繁體中文化

### 已完成檔案

- `README.md`
- `PROGRESS.md`
- `generated_outputs/README.md`
- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/services/dataset_analyzer.py`
- `backend/app/services/model_runner.py`
- `backend/tests/test_model_runner.py`
- `frontend/src/app/layout.tsx`
- `frontend/src/app/page.tsx`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/AnalysisResult.tsx`
- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/components/ModelAnalysisPanel.tsx`
- `frontend/src/lib/api.ts`

### 新增功能

- 新增模型分析 API：`POST /api/models/analyze`。
- 使用者上傳資料集並完成摘要後，可以選擇目標欄位。
- 後端會自動判斷回歸或分類問題。
- 後端會同時執行：
  - 線性迴歸
  - Ridge 迴歸
  - Lasso 迴歸
  - 隨機森林
- 後端會回傳模型比較表：
  - R2
  - RMSE
  - MAE
  - 訓練時間
- 後端會實際產生模型比較圖，並儲存在 `generated_outputs/charts/`。
- FastAPI 會公開 `generated_outputs/` 靜態檔案，讓前端可直接顯示圖片。
- 前端新增模型分析區塊，按鈕會呼叫真實模型 API。
- 前端、README、PROGRESS 與輸出資料夾說明已改成繁體中文。

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

### 如何測試

後端測試：

```bash
cd backend
source .venv/bin/activate
pytest
```

手動模型 API 測試：

```bash
curl -X POST http://127.0.0.1:8000/api/models/analyze \
  -F "file=@sample_datasets/housing_sample.csv" \
  -F "target_column=price_usd"
```

UI 測試：

1. 啟動後端與前端。
2. 打開 `http://localhost:3000/upload`。
3. 上傳 `sample_datasets/housing_sample.csv`。
4. 選擇 `price_usd` 作為目標欄位。
5. 點選「執行模型分析」。
6. 確認模型比較表與模型比較圖顯示在前端。

### 本次驗證結果

- `pip install -r requirements.txt`：通過，已成功安裝 scikit-learn 1.8.0 與 matplotlib 3.10.8。
- `pytest`：通過，3 個測試通過。
- `python -m compileall app tests`：通過。
- 真實資料摘要 API 測試：`POST /api/datasets/analyze` 可正常回傳資料摘要。
- 真實模型 API 測試：`POST /api/models/analyze` 使用 `price_usd` 作為目標欄位時，成功判斷為回歸問題並回傳 4 個模型結果。
- 真實模型 API 測試：`POST /api/models/analyze` 使用 `near_mrt` 作為目標欄位時，成功判斷為分類問題並回傳 4 個模型結果與分類備註。
- 模型比較圖已實際產生在 `generated_outputs/charts/`，並已檢查圖表非空白、中文字可正常顯示。
- `npm run typecheck`：通過。
- `npm run build`：通過。
- `npm audit --audit-level=moderate`：通過，0 個漏洞。
- Browser 驗證：首頁與上傳頁可正常渲染，繁體中文文案顯示正常，沒有錯誤覆蓋層，console error/warn 為空。
- Browser 互動驗證：未選檔按下「分析資料集」會顯示繁中錯誤提示。
- Browser 截圖：通過，已確認上傳頁第一屏畫面不是空白。

### 下一階段要做什麼

第三階段：Colab 式圖表輸出。

- 相關係數熱力圖
- 特徵重要性
- 預測值與實際值圖
- 殘差圖
- 圖片實際儲存在 `generated_outputs/charts/`

### 已知限制

- 第三階段到第七階段尚未實作。
- 第二階段分類問題會先將目標欄位轉成數值標籤，再依需求顯示 R2、RMSE、MAE；正式分類指標會在後續階段補強。
- 當時尚未永久保存上傳原始檔；第二階段只輸出模型比較圖。
- Browser runtime 目前沒有文件化的檔案輸入上傳方法，因此完整「瀏覽器自動上傳檔案」流程未用 Browser 自動化完成；檔案上傳與模型執行已用真實 API、前端型別檢查、前端 build 與頁面互動狀態驗證。

## 2026-06-09：第二階段加強與第三階段圖表輸出前半

### 已完成檔案

- `README.md`
- `PROGRESS.md`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/services/model_runner.py`
- `backend/pytest.ini`
- `backend/tests/test_model_runner.py`
- `frontend/src/app/page.tsx`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/components/ModelAnalysisPanel.tsx`
- `frontend/src/lib/api.ts`

### 新增功能

- 前端資料集上傳改為支援一次選擇多個 CSV / Excel 檔案。
- 多個檔案會逐一呼叫真實後端摘要 API，每個檔案都會顯示獨立摘要與模型分析入口。
- 模型分析新增使用者可選的分析模式：
  - 自動選擇
  - 回歸分析
  - 分類分析
- 模型分析新增圖表產出模式：
  - 系統自動選最適合圖表
  - 使用者手動選擇圖表
- 後端 `POST /api/models/analyze` 新增 `analysis_mode` 與 `chart_types` 表單欄位。
- 後端可依選擇產出多張真實 PNG 圖表：
  - 模型比較圖
  - 相關係數熱力圖
  - 特徵重要性
  - 預測值與實際值
  - 殘差圖
- 前端可顯示後端回傳的多張圖表。
- 整體版面加寬到 1800px，首頁、上傳頁、表格、卡片與按鈕字級和間距已放大。

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

### 如何測試

後端測試：

```bash
cd backend
source .venv/bin/activate
pytest
```

手動 API 測試，自動選擇分析與圖表：

```bash
curl -X POST http://127.0.0.1:8000/api/models/analyze \
  -F "file=@sample_datasets/housing_sample.csv" \
  -F "target_column=price_usd" \
  -F "analysis_mode=auto" \
  -F "chart_types=auto"
```

手動 API 測試，指定所有圖表：

```bash
curl -X POST http://127.0.0.1:8000/api/models/analyze \
  -F "file=@sample_datasets/housing_sample.csv" \
  -F "target_column=price_usd" \
  -F "analysis_mode=regression" \
  -F "chart_types=model_comparison,correlation_heatmap,feature_importance,predicted_vs_actual,residual_plot"
```

UI 測試：

1. 啟動後端與前端。
2. 打開 `http://localhost:3000/upload`。
3. 同時選擇 `sample_datasets/housing_sample.csv` 與 `sample_datasets/stock_prices_sample.csv`。
4. 點選「讀取全部檔案」。
5. 確認兩個檔案都顯示獨立資料摘要。
6. 在任一檔案的「模型分析與圖表產出」選擇目標欄位。
7. 選擇分析模式與圖表產出模式。
8. 點選「執行模型分析」。
9. 確認模型比較表與所有後端產出的圖表都顯示在前端。

### 本次驗證結果

- `pytest`：通過，4 個測試通過。
- `python -m compileall app tests`：通過。
- `npm run typecheck`：通過。
- `npm run build`：通過。沙盒內 Turbopack 綁定連接埠失敗，已用授權環境重跑並通過。
- `npm audit --audit-level=moderate`：通過，0 個漏洞。沙盒 DNS 無法解析 npm registry，已用授權網路重跑。
- 真實資料摘要 API 測試：`housing_sample.csv` 成功回傳 12 筆、6 欄摘要。
- 真實資料摘要 API 測試：`stock_prices_sample.csv` 成功回傳 12 筆、7 欄摘要。
- 真實模型 API 測試：`analysis_mode=auto`、`chart_types=auto` 成功判斷為回歸並產出 5 張圖表。
- 真實模型 API 測試：`analysis_mode=regression` 且指定 5 種圖表時，成功產出模型比較、相關係數熱力圖、特徵重要性、預測值與實際值、殘差圖。
- 圖表抽查：`generated_outputs/charts/correlation_heatmap_390267fa2b8347909fb13601007fa6e0.png` 非空白，中文字標題可顯示。
- Browser DOM 驗證：上傳頁已顯示多檔案文案，檔案 input 具有 `multiple=true`。
- Browser 互動驗證：未選檔按下「讀取全部檔案」會顯示「請先選擇至少一個 CSV 或 Excel 檔案。」。
- Browser console 驗證：沒有 error 或 warning。
- Browser screenshot：目前截圖通道逾時；已用 DOM snapshot、可見 DOM、互動檢查與 console logs 完成頁面驗證。

### 下一階段要做什麼

第四階段：AI 程式碼生成。

- 根據使用者選擇的模型產生 `generated_code.py`。
- 產生 `notebook.ipynb`。
- 前端提供下載按鈕。

### 已知限制

- 第三階段圖表輸出已完成主要圖表，但尚未整合到 ZIP 或報告。
- 分類分析目前仍依需求回傳 R2、RMSE、MAE；正式分類指標會在後續階段補強。
- 目前不永久保存上傳原始檔，因此重新整理頁面後需要重新上傳檔案。

## 2026-06-09：多檔上傳修復、移除熱力圖、智慧合併分析

### 已完成檔案

- `README.md`
- `PROGRESS.md`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/services/dataset_analyzer.py`
- `backend/app/services/model_runner.py`
- `backend/tests/test_dataset_analyzer.py`
- `backend/tests/test_model_runner.py`
- `frontend/src/app/page.tsx`
- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/components/ModelAnalysisPanel.tsx`
- `frontend/src/lib/api.ts`

### 新增功能

- 移除熱力圖：
  - 前端不再顯示熱力圖選項。
  - 後端自動圖表不再產生熱力圖。
  - 後端不再接受 `correlation_heatmap` 作為有效圖表類型。
- 多檔上傳修復：
  - 新增後端 API：`POST /api/datasets/analyze-multiple`。
  - 前端現在會一次送出整批檔案，不再逐檔呼叫單檔 API。
  - 前端可分多次加入檔案、避免重複加入、移除單一檔案、清空檔案。
  - 每個檔案會顯示獨立成功或錯誤狀態。
- 智慧合併分析：
  - 兩個以上檔案成功讀取後，後端會依欄位名稱垂直合併資料。
  - 合併資料會保留欄位聯集、來源檔案欄位與來源列號。
  - 合併摘要會顯示來源檔案數、合併列數、共同欄位數與合併判斷。
  - 新增後端 API：`POST /api/models/analyze-merged`。
  - 合併資料可直接執行模型分析與圖表輸出。
  - 後端會提供建議目標欄位，前端提供一鍵選用。

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

### 如何測試

後端測試：

```bash
cd backend
source .venv/bin/activate
pytest
```

多檔摘要 API：

```bash
curl -X POST http://127.0.0.1:8000/api/datasets/analyze-multiple \
  -F "files=@sample_datasets/housing_sample.csv" \
  -F "files=@sample_datasets/stock_prices_sample.csv"
```

合併模型分析 API：

```bash
curl -X POST http://127.0.0.1:8000/api/models/analyze-merged \
  -F "files=@sample_datasets/housing_sample.csv" \
  -F "files=@sample_datasets/stock_prices_sample.csv" \
  -F "target_column=price_usd" \
  -F "analysis_mode=auto" \
  -F "chart_types=auto"
```

UI 測試：

1. 啟動後端與前端。
2. 打開 `http://localhost:3000/upload`。
3. 加入 `housing_sample.csv` 與 `stock_prices_sample.csv`。
4. 點選「讀取全部檔案」。
5. 確認兩個檔案都顯示獨立摘要。
6. 確認畫面出現「智慧合併分析」。
7. 在「合併資料模型分析」選擇建議目標欄位。
8. 點選「執行模型分析」。
9. 確認圖表不包含熱力圖。

### 本次驗證結果

- `pytest`：通過，6 個測試通過。
- `python -m compileall app tests`：通過。
- `npm run typecheck`：通過。
- `npm run build`：通過。沙盒內 Turbopack 綁定連接埠失敗，已用授權環境重跑並通過。
- `npm audit --audit-level=moderate`：通過，0 個漏洞。沙盒 DNS 無法解析 npm registry，已用授權網路重跑。
- 真實多檔摘要 API 測試：一次上傳 `housing_sample.csv` 與 `stock_prices_sample.csv` 成功，回傳 2 個獨立摘要與 1 個合併摘要。
- 真實合併模型 API 測試：`analysis_mode=auto`、`chart_types=auto` 成功產出 4 張圖表。
- 合併模型 API 回傳圖表：模型比較圖、特徵重要性、預測值與實際值、殘差圖。
- 熱力圖驗證：自動圖表不再包含 `correlation_heatmap`；後端測試確認該圖表類型會被拒絕。
- Browser DOM 驗證：上傳頁有整批讀取與智慧合併文案，檔案 input 具有 `multiple=true`，頁面沒有熱力圖文字。
- Browser 互動驗證：未選檔按下「讀取全部檔案」會顯示繁中錯誤提示。
- Browser console 驗證：沒有 error 或 warning。

### 下一階段要做什麼

第四階段：AI 程式碼生成。

- 依使用者選擇的模型與圖表產生 `generated_code.py`。
- 產生 `notebook.ipynb`。
- 前端提供下載按鈕。

### 已知限制

- 合併策略目前是依欄位名稱垂直合併，尚未支援依 key 欄位 join。
- 合併後若多個檔案欄位差異很大，目標欄位只會使用有該目標值的資料列訓練。
- 分類分析目前仍依需求回傳 R2、RMSE、MAE；正式分類指標會在後續階段補強。
- 目前不永久保存上傳原始檔，重新整理頁面後需要重新上傳。

## 2026-06-09：第四階段，AI 程式碼生成

### 已完成檔案

- `README.md`
- `PROGRESS.md`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/services/code_generator.py`
- `backend/tests/test_code_generator.py`
- `frontend/src/components/ModelAnalysisPanel.tsx`
- `frontend/src/lib/api.ts`

### 新增功能

- 新增後端 API：`POST /api/code/generate`。
- 新增後端 API：`POST /api/code/generate-merged`。
- 單檔模型分析與合併資料模型分析都能生成程式碼。
- 後端會依目前設定產生：
  - `generated_code.py`
  - `notebook.ipynb`
- 生成的 Python 程式碼包含：
  - 讀取資料
  - 清理資料與缺失值補值
  - train/test split
  - 模型訓練
  - R2、RMSE、MAE 評估
  - 模型比較圖
  - 特徵重要性或係數重要性
  - 預測值與實際值
  - 殘差圖
- 後端會把本次使用的資料另存到 `generated_outputs/data/`，讓下載的程式碼能在專案內直接執行。
- 前端在模型分析完成後顯示「AI 程式碼生成」區塊。
- 使用者可以選擇主要模型後生成程式碼。
- 前端提供 `generated_code.py` 與 `notebook.ipynb` 下載按鈕。

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

### 如何測試

後端測試：

```bash
cd backend
source .venv/bin/activate
pytest
```

單檔程式碼生成 API：

```bash
curl -X POST http://127.0.0.1:8000/api/code/generate \
  -F "file=@sample_datasets/housing_sample.csv" \
  -F "target_column=price_usd" \
  -F "model_name=Ridge 迴歸" \
  -F "analysis_mode=regression" \
  -F "chart_types=model_comparison,feature_importance,predicted_vs_actual,residual_plot"
```

合併資料程式碼生成 API：

```bash
curl -X POST http://127.0.0.1:8000/api/code/generate-merged \
  -F "files=@sample_datasets/housing_sample.csv" \
  -F "files=@sample_datasets/stock_prices_sample.csv" \
  -F "target_column=price_usd" \
  -F "model_name=隨機森林" \
  -F "analysis_mode=auto" \
  -F "chart_types=auto"
```

UI 測試：

1. 啟動後端與前端。
2. 打開 `http://localhost:3000/upload`。
3. 上傳並讀取資料集。
4. 執行模型分析。
5. 在「AI 程式碼生成」選擇主要模型。
6. 點選「生成程式碼」。
7. 確認畫面顯示 `generated_code.py` 與 `notebook.ipynb` 下載按鈕。

### 本次驗證結果

- `pytest`：通過，9 個測試通過。
- `python -m compileall app tests`：通過。
- `npm run typecheck`：通過。
- `npm run build`：通過。沙盒內 Turbopack 綁定連接埠失敗，已用授權環境重跑並通過。
- 單元測試已確認生成的 Python 腳本包含 `train_test_split`、`SimpleImputer`、圖表生成函式。
- 單元測試已確認生成的 Notebook 是合法 nbformat 4 JSON。
- 單元測試已實際執行生成的 Python 腳本，確認不是假檔案。
- FastAPI in-process 測試已確認 `/api/code/generate` 回傳可下載 `.py` 與 `.ipynb` 檔案路徑。
- FastAPI in-process 測試已確認 `/api/code/generate-merged` 回傳可下載 `.py` 與 `.ipynb` 檔案路徑。
- 真實 API 測試曾成功產出：
  - `generated_outputs/code/generated_code_1339e0b190904c74baeaff27f7f972a9.py`
  - `generated_outputs/code/notebook_1339e0b190904c74baeaff27f7f972a9.ipynb`
  - `generated_outputs/data/housing_sample_1339e0b190904c74baeaff27f7f972a9.csv`
- 直接執行上述生成腳本：通過，成功輸出模型評估結果並生成 4 張圖表。
- 環境問題處理：生成腳本一開始會設定 `MPLCONFIGDIR` 到專案內可寫路徑，避免 Matplotlib 嘗試寫入使用者家目錄。
- 環境問題處理：生成腳本已加入中文字型候選設定，降低圖表中文字型警告。

### 下一階段要做什麼

第五階段：金融分析模式。

- 偵測日期與價格欄位。
- 產生 MA、報酬率、波動率、RSI、MACD。
- 顯示金融分析圖表。
- 產生簡短金融分析摘要。

### 已知限制

- 目前生成的程式碼會在專案內搭配 `generated_outputs/data/` 的資料檔執行；若只把 `.py` 單獨移到其他位置，需要一併移動資料檔或調整 `DATA_RELATIVE_PATH`。
- Notebook 目前以單一主要程式碼 cell 產生，後續可再拆成更像 Colab 的多段式教學流程。
- 目前尚未把程式碼、Notebook、圖表與資料集包成 ZIP；這會在第六階段完成。

## 2026-06-09：模型策略加強、白底簡潔介面與第五階段金融分析

### 已完成檔案

- `README.md`
- `PROGRESS.md`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/services/model_runner.py`
- `backend/app/services/code_generator.py`
- `backend/app/services/financial_analyzer.py`
- `backend/tests/test_model_runner.py`
- `backend/tests/test_financial_analyzer.py`
- `frontend/src/app/globals.css`
- `frontend/src/app/page.tsx`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/FinancialAnalysisPanel.tsx`
- `frontend/src/components/ModelAnalysisPanel.tsx`
- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/lib/api.ts`

### 新增功能

- 模型分析不再固定執行四種模型。
- 後端新增模型目錄與推薦邏輯，會依以下條件自動推薦模型：
  - 問題型態：回歸或分類
  - 資料列數
  - 特徵數
  - 類別欄位數
  - 缺失值比例
  - 目標欄位唯一值數量
- 後端支援更多模型：
  - 回歸：線性迴歸、Ridge、Lasso、ElasticNet、決策樹、隨機森林、Extra Trees、Gradient Boosting、KNN、SVR
  - 分類：Logistic Regression、決策樹、隨機森林、Extra Trees、Gradient Boosting、KNN、SVC
- 前端新增模型策略選項：
  - 自動推薦模型
  - 手動選擇模型
- 手動模型選擇會依使用者選擇的分析模式顯示相容模型，避免固定模型組合。
- 模型比較表新增模型 key、模型家族、Accuracy 與 F1。
- 程式碼生成已同步支援新增模型名稱。
- 第五階段金融分析已完成：
  - 新增 `POST /api/finance/analyze`
  - 新增 `POST /api/finance/analyze-merged`
  - 自動偵測日期欄位與價格欄位
  - 可由使用者手動指定日期與價格欄位
  - 計算 MA、報酬率、波動率、RSI、MACD
  - 產生金融摘要
  - 產生金融指標 CSV 到 `generated_outputs/data/`
  - 產生金融圖表到 `generated_outputs/charts/`
- 前端新增金融分析面板，支援單檔與合併資料。
- 網站依最新需求調整為白色背景、簡潔易讀的產品工具風格：
  - 保留原本 `ink`、`brand`、`navy`、`amber` 主色系
  - 移除深色背景、玻璃變形、網格光帶與強發光效果
  - 首頁改為清楚的白底資訊入口
  - 整體版面維持較寬、字級較大，優先提升可讀性

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

前端網址：

```text
http://localhost:3000
```

後端 API 文件：

```text
http://127.0.0.1:8000/docs
```

### 如何測試

後端完整測試：

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

前端測試：

```bash
cd frontend
npm run typecheck
npm run build
```

自動推薦模型 API：

```bash
curl -X POST http://127.0.0.1:8000/api/models/analyze \
  -F "file=@sample_datasets/housing_sample.csv" \
  -F "target_column=price_usd" \
  -F "analysis_mode=auto" \
  -F "chart_types=auto" \
  -F "model_selection_mode=auto" \
  -F "selected_models=auto"
```

手動模型選擇 API：

```bash
curl -X POST http://127.0.0.1:8000/api/models/analyze \
  -F "file=@sample_datasets/housing_sample.csv" \
  -F "target_column=price_usd" \
  -F "analysis_mode=regression" \
  -F "chart_types=model_comparison,feature_importance,predicted_vs_actual,residual_plot" \
  -F "model_selection_mode=custom" \
  -F "selected_models=ridge,random_forest,gradient_boosting_regressor,extra_trees_regressor"
```

金融分析 API：

```bash
curl -X POST http://127.0.0.1:8000/api/finance/analyze \
  -F "file=@sample_datasets/stock_prices_sample.csv"
```

UI 測試流程：

1. 啟動後端與前端。
2. 打開 `http://localhost:3000/upload`。
3. 加入 `housing_sample.csv` 與 `stock_prices_sample.csv`。
4. 點選「讀取全部檔案」。
5. 確認兩個檔案都顯示獨立摘要。
6. 在模型區切換「自動推薦模型」與「手動選擇模型」。
7. 選擇不同分析模式，確認手動模型清單會跟著調整。
8. 點選「執行模型分析」，確認模型比較與圖表由後端產生。
9. 在 `stock_prices_sample.csv` 或合併資料區塊點選「執行金融分析」。
10. 確認金融摘要、金融圖表與指標 CSV 下載按鈕顯示。

### 本次驗證結果

- `backend/.venv/bin/python -m pytest`：當時通過，13 個測試通過；後續已擴充到 15 個測試。
- `npm run typecheck`：通過。
- `npm run build`：通過。沙盒內 Turbopack 因本機 port binding 權限失敗，已用授權環境重跑並通過。
- 金融分析單元測試確認：
  - 可自動偵測 `date` 與 `close`
  - 可產生金融指標 CSV
  - 可產生 3 張真實 PNG 圖表
  - 非金融資料會被拒絕，不會假裝完成
- 模型分析測試確認：
  - 自動推薦不再固定四種模型
  - 手動模型選擇可限制指定模型
  - 不支援模型會回傳錯誤
  - 熱力圖已依需求拒絕
- 前端 TypeScript 檢查確認新增金融 API 型別與元件可編譯。
- 前端 production build 確認白底首頁、上傳頁與新增元件可打包。

### 下一階段要做什麼

第六階段：完整輸出套件。

- 一鍵下載 ZIP。
- ZIP 內包含：
  - `analysis_report.pdf` 或 `analysis_report.docx`
  - `generated_code.py`
  - `notebook.ipynb`
  - `cleaned_dataset.csv`
  - `model_results.xlsx`
  - `charts/`
  - `trained_models/`
- 前端提供 ZIP 下載按鈕。

### 已知限制

- 報告輸出與 trained model 檔案後續已補齊；ZIP 仍依最新需求未實作。
- 金融分析目前以單一價格序列或同日期平均值為主；若一個資料集包含多檔 ticker，後續可加入 ticker 分組分析。
- Browser 工具本次對 `localhost:3000` 開啟動作被安全政策拒絕，因此 UI 驗證以 TypeScript、Next build 與後端 in-process 測試為主。
- 目前工作目錄不是 git repository，無法建立 commit；本階段改以完整變更摘要記錄。

## 2026-06-09：依計畫書補齊非 ZIP 功能與淺色未來感介面

### 已完成檔案

- `README.md`
- `PROGRESS.md`
- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/services/model_runner.py`
- `backend/app/services/financial_analyzer.py`
- `backend/app/services/agent_orchestrator.py`
- `backend/app/services/report_generator.py`
- `backend/tests/test_agent_report.py`
- `backend/tests/test_financial_analyzer.py`
- `frontend/src/app/globals.css`
- `frontend/src/app/page.tsx`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/AgentReportPanel.tsx`
- `frontend/src/components/FinancialAnalysisPanel.tsx`
- `frontend/src/components/ModelAnalysisPanel.tsx`
- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/lib/api.ts`

### 新增功能

- 安裝並加入：
  - XGBoost
  - LightGBM
  - python-docx
- 模型分析新增 XGBoost / LightGBM 回歸與分類模型。
- 模型分析新增 Quick AutoML 小型參數搜尋。
- 每個模型結果會回傳 AutoML 最佳參數。
- 後端會保存 trained model 到 `generated_outputs/models/`。
- 後端會輸出：
  - `model_results.xlsx`
  - `cleaned_dataset.csv`
- 金融分析新增：
  - VaR 95%
  - VaR 99%
  - 5 期時間序列預測
  - 時間序列預測圖
- 新增 Multi-Agent API：
  - `POST /api/agents/analyze`
  - `POST /api/agents/analyze-merged`
- Agent 分工包含：
  - 資料理解代理
  - 模型分析代理
  - 金融分析代理
  - 視覺化代理
  - 報告代理
- 新增 AI 摘要流程：
  - 設定 `OPENAI_API_KEY` 時嘗試使用 OpenAI。
  - 未設定時使用本機規則摘要，並明確回傳 `local_rule_based`，不假裝 LLM 已執行。
- 新增 Word 報告 API：
  - `POST /api/reports/generate`
  - `POST /api/reports/generate-merged`
- Word 報告會包含資料摘要、Agent 紀錄、模型比較、金融分析與圖表。
- 前端新增「Multi-Agent 智慧分析與報告」面板。
- 前端模型面板新增 AutoML 控制、trained model 下載、model_results.xlsx 下載、cleaned_dataset.csv 下載。
- 前端金融面板新增 VaR 與預測結果顯示。
- 網站改為淺色科技新創風格：
  - 白色主題
  - 玻璃感面板
  - 藍綠漸層光帶
  - hover glow 按鈕
  - 清晰字體與寬版布局
- ZIP 套件依使用者要求未實作。

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

### 如何測試

後端完整測試：

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

前端測試：

```bash
cd frontend
npm run typecheck
npm run build
```

Multi-Agent API：

```bash
curl -X POST http://127.0.0.1:8000/api/agents/analyze \
  -F "file=@sample_datasets/stock_prices_sample.csv" \
  -F "target_column=close" \
  -F "analysis_mode=regression" \
  -F "model_selection_mode=custom" \
  -F "selected_models=ridge,random_forest" \
  -F "automl_mode=off"
```

Word 報告 API：

```bash
curl -X POST http://127.0.0.1:8000/api/reports/generate \
  -F "file=@sample_datasets/stock_prices_sample.csv" \
  -F "target_column=close" \
  -F "analysis_mode=regression" \
  -F "model_selection_mode=custom" \
  -F "selected_models=ridge,random_forest" \
  -F "automl_mode=off"
```

### 本次驗證結果

- `backend/.venv/bin/python -m pytest`：通過，15 個測試通過。
- `backend/.venv/bin/python -m compileall app tests`：通過。
- `npm run typecheck`：通過。
- `npm run build`：通過。沙盒內 Turbopack 因本機 port binding 權限失敗，已用授權環境重跑並通過。
- XGBoost / LightGBM / python-docx 已成功安裝。
- Agent API 測試確認資料理解代理、模型分析代理、金融分析代理會真實執行。
- Report API 測試確認 Word `.docx` 實際生成且檔案存在。
- 金融測試確認 VaR 與 5 期時間序列預測已回傳，圖表增加為 4 張。
- 前端 TypeScript 確認新增 Agent / Report / AutoML / VaR 型別可編譯。

### 下一階段要做什麼

依目前使用者要求，ZIP 套件先不做。若後續要做，可新增：

- 一鍵下載 ZIP。
- ZIP 內整合 Word 報告、程式碼、Notebook、cleaned dataset、model_results.xlsx、charts、trained models。
- 更完整的 LLM 對話式介面。
- 更進階的時間序列模型，例如 ARIMA、Prophet 或 LSTM。

### 已知限制

- 一鍵 ZIP 套件依使用者要求尚未實作。
- PDF 報告尚未實作，目前為 Word `.docx`。
- LLM 摘要需要 `OPENAI_API_KEY`；未設定時會使用本機規則摘要並明確標示。
- 背景「漂浮發光球體」已用柔和漸層光帶替代，避免干擾可讀性與主要資料操作。
- Browser 工具本次對 `localhost:3000` 開啟動作被安全政策拒絕，因此 UI 驗證以 TypeScript、Next build 與後端測試為主。
- 目前工作目錄不是 git repository，無法建立 commit；本階段改以完整變更摘要記錄。

## 2026-06-09：網站啟動修復與全面真實資料稽核

### 使用者需求

- 使用者回報目前無法打開網站測試。
- 需要做超全面檢查，確認不是假資料。
- 需要確認後台確實會依每個不同資料集與目標欄位做最適合的自動分析。

### 已完成檔案

- `backend/app/services/model_runner.py`
  - 新增 `manual` 模型選擇模式相容，會正規化為既有 `custom`。
  - 新增 macOS XGBoost / LightGBM OpenMP dylib 自動修復 fallback。
- `backend/app/services/agent_orchestrator.py`
  - Agent 名稱改為全繁體中文：資料理解代理、模型分析代理、金融分析代理、視覺化代理、報告代理。
- `backend/tests/test_model_runner.py`
  - 新增 `manual` 模型選擇別名測試。
- `backend/tests/test_agent_report.py`
  - 更新 Agent 名稱測試為繁體中文。
- `frontend/src/components/AgentReportPanel.tsx`
  - Multi-Agent 面板描述改為全繁體中文。
- `README.md`
  - 補充 XGBoost / LightGBM OpenMP 自動修復說明。
  - 補充模型可用性依實際 import 結果回傳，不假裝可用。
  - 更新第七階段驗收狀態。
  - 補充沙盒環境可用 `npm run build -- --webpack` 驗證 production build。
- `PROGRESS.md`
  - 記錄本次全面檢查與修正。

### 新增功能與修正

- 網站無法開啟原因確認：
  - 一開始 `localhost:3000` 與 `127.0.0.1:8000` 沒有服務在聽。
  - 沙盒內直接啟動 dev server 會被本機 port binding 權限擋住。
  - 使用授權後，Next.js 前端已在 `http://localhost:3000` 啟動。
  - 後端 `http://127.0.0.1:8000/health` 已確認回傳健康狀態。
- 修正 `model_selection_mode=manual`：
  - 原本 API 只接受 `custom`，但錯誤訊息與使用者語意都是手動選擇。
  - 現在 `manual` 會自動正規化為 `custom`。
- 修正 Agent 名稱非繁中問題：
  - 後端回傳與前端顯示都改為繁體中文名稱。
- 修正 XGBoost / LightGBM macOS OpenMP 問題：
  - 發現套件存在，但缺少系統 `libomp.dylib` 時無法載入。
  - 已把目前 `.venv` 內 XGBoost / LightGBM dylib 改指向 sklearn 內建 `libomp.dylib`。
  - 後端也新增自動修復 fallback，避免重新安裝後又變成不可用。

### 真實資料稽核結果

使用後端 TestClient 實際呼叫 API，沒有使用靜態假資料。

- 多檔上傳：
  - `housing_sample.csv`：真實讀取 12 筆、6 欄。
  - `stock_prices_sample.csv`：真實讀取 12 筆、7 欄。
  - 合併資料集：真實回傳 24 筆。
  - `stock_prices_sample.csv` 的 `close` 缺失值有正確統計為 1。
- 模型可用性：
  - 回歸模型可用數量：12。
  - 分類模型可用數量：9。
  - 已確認包含 XGBoost Regressor、LightGBM Regressor、XGBoost Classifier、LightGBM Classifier。
- 自動分析不是固定四種模型：
  - 房價 `price_usd` 自動判斷為回歸，推薦 Ridge、Lasso、ElasticNet、Random Forest、Gradient Boosting、XGBoost、KNN。
  - 房價 `near_mrt` 自動判斷為分類，推薦 Logistic Regression、Decision Tree、Random Forest、Gradient Boosting、XGBoost、KNN。
  - 臨時寬欄位缺失回歸資料自動推薦 Ridge、ElasticNet、Random Forest、Extra Trees、Gradient Boosting、LightGBM。
  - 三種資料形態的模型組合不同，已確認不是固定清單。
- 手動自由度：
  - `manual` 模式指定 `ridge,random_forest` 時，後端只執行 Ridge 與 Random Forest。
  - 手動指定圖表 `model_comparison,predicted_vs_actual` 時，只產生這兩種圖表。
- 圖表：
  - 自動圖表不包含熱力圖。
  - 回歸會產出模型比較、特徵重要性、預測值與實際值、殘差圖。
  - 分類會略過殘差圖。
- 金融分析：
  - `stock_prices_sample.csv` 以 `date` 與 `close` 執行。
  - 扣除缺失價格後使用 11 筆資料。
  - 產出 VaR 95%、VaR 99%、5 期預測與 4 張金融圖表。
- Multi-Agent 與報告：
  - Agent 步驟包含資料理解代理、模型分析代理、金融分析代理、視覺化代理、報告代理。
  - 未設定 `OPENAI_API_KEY` 時明確回傳 `local_rule_based`，沒有假裝 LLM 執行。
  - Word 報告 `.docx` 已實際生成。
- 輸出檔案：
  - 稽核檢查 19 個輸出檔案都存在且非空。
  - 包含 charts、trained models、model_results.xlsx、cleaned_dataset.csv、金融指標 CSV、Word 報告。
- 全面稽核總結：
  - 99 個檢查點通過。

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm run dev
```

可開啟：

```text
http://localhost:3000
http://localhost:3000/upload
http://127.0.0.1:8000/docs
```

### 如何測試

後端：

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

前端：

```bash
cd frontend
npm run typecheck
npm run build -- --webpack
```

本次結果：

- `python -m pytest`：16 passed。
- `npm run typecheck`：通過。
- `npm run build -- --webpack`：通過。
- 全面 API 稽核：99 checks passed。

### 下一階段要做什麼

- ZIP 套件依使用者要求仍先不做。
- 若後續繼續，可以補：
  - 一鍵 ZIP 下載。
  - 更完整的互動式 LLM 對話分析。
  - 更進階時間序列模型，例如 ARIMA、Prophet 或 LSTM。

### Known Issues

- Browser 工具在本 session 對 `localhost:3000` 開啟動作曾被安全政策拒絕，因此本次 UI 驗證改用本機服務健康檢查、TypeScript、Next production build 與後端 TestClient。
- 沙盒內直接跑 Turbopack build 可能出現 `binding to a port` 權限錯誤；使用 `npm run build -- --webpack` 可正常驗證 production build。
- 一鍵 ZIP 套件尚未實作，這是使用者明確要求暫時排除的項目。
- PDF 報告尚未實作，目前為 Word `.docx`。
- 未設定 `OPENAI_API_KEY` 時會使用本機規則摘要，且 API 明確標示 `local_rule_based`。
- 目前工作目錄不是 git repository，無法建立 commit；本階段改以完整變更摘要記錄。

## 2026-06-09：首頁產品化與品牌更名

### 使用者需求

- 網站不要再使用舊品牌名稱。
- 品牌名稱改為「智能金融資料分析」。
- 首頁風格要貼近使用者提供的參考圖。
- 刪除「目前 API 合約」、「第幾階段」與 Demo / 開發展示語氣。
- 直接整理成明天可以上架的正式產品頁。

### 已完成檔案

- `frontend/src/app/page.tsx`
  - 完整重做首頁。
  - 移除 API 合約卡片、開發階段卡片與測試資料流程語氣。
  - 新增正式產品 Hero、產品預覽介面、核心能力、範例資料集、分析成果與安全交付區塊。
- `frontend/src/components/AppShell.tsx`
  - 全站品牌改為「智能金融資料分析」。
  - 導覽列改為參考圖風格的白底玻璃導覽與漸層 CTA。
- `frontend/src/app/globals.css`
  - 新增白底科技風、漸層流線、玻璃面板、hover glow 按鈕與產品預覽樣式。
- `frontend/src/app/layout.tsx`
  - 瀏覽器標題改為「智能金融資料分析」。
- `frontend/src/components/UploadPanel.tsx`
  - 合併分析區改為正式產品語氣。
- `frontend/src/components/AgentReportPanel.tsx`
  - 將 Multi-Agent 顯示文案改為「AI 協作分析」。
- `frontend/src/components/ModelAnalysisPanel.tsx`
  - 將畫面上的「後端」文案改成「系統」。
- `frontend/src/lib/api.ts`
  - 將錯誤訊息中的 Multi-Agent 改成 AI 協作分析。
- `backend/app/main.py`
  - API 標題與健康檢查服務名稱改為「智能金融資料分析 API」。
- `backend/app/services/report_generator.py`
  - Word 報告標題改為「智能金融資料分析報告」。
- `backend/app/services/agent_orchestrator.py`
  - LLM prompt 品牌改為「智能金融資料分析」。
- `backend/app/services/code_generator.py`
  - 生成的 Python 與 Notebook 標題改為「智能金融資料分析」。
- `README.md`
  - 正式專案名稱改為「智能金融資料分析」。
- `frontend/package.json`
  - package name 改為 `smart-finance-analytics-frontend`。
- `frontend/package-lock.json`
  - 同步 package name。

### 新增功能與修正

- 首頁變成正式產品 landing page：
  - 左側大型品牌主標：「智能金融資料分析」。
  - 主要 CTA：「上傳資料集」。
  - 右側產品介面預覽。
  - 下方保留產品能力與交付成果，不再使用開發階段或 API 合約語氣。
  - 首頁範例資料集只保留專案內真實存在的 `stock_prices_sample.csv` 與 `housing_sample.csv`，不放不存在的假檔名。
- 全站品牌更名：
  - 前端顯示、metadata、後端 API docs、健康檢查、Word 報告、生成程式碼與 Notebook 都已同步。
- 全站前端掃描確認：
  - `frontend/src` 已無舊品牌名稱。
  - `frontend/src` 已無 `目前 API 合約`。
  - `frontend/src` 已無 `第幾階段` 類型文字。
  - `frontend/src` 已無 `Demo` / `DEMO`。
  - `frontend/src` 已無可見 `Multi-Agent` 或 `後端` 產品文案。

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm run dev
```

可開啟：

```text
http://localhost:3000
http://localhost:3000/upload
```

### 如何測試

```bash
cd frontend
npm run typecheck
npm run build -- --webpack
```

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

本次結果：

- `npm run typecheck`：通過。
- `npm run build -- --webpack`：通過。
- `python -m pytest`：16 passed。
- Next.js dev server 熱更新正常，首頁 `/` 回應 200。

### 下一步

- 若要正式部署，下一步應設定正式網域、production API URL、環境變數與部署平台。
- ZIP 套件仍依使用者前一輪要求暫不實作。

## 2026-06-10：縮放版面修正、上傳頁統一風格與程式碼預覽

### 使用者需求

- 網頁比例放大到 80% 以上時版面會跑掉，需要修正。
- 上傳資料頁風格與主頁差異太大，需要統一。
- 主頁色調不要太霓虹，但仍需要更多動畫與層次。
- 不要自行新增不存在的功能，但希望產品呈現不要只有一個功能頁。
- 生成的分析程式碼要能直接顯示在頁面裡，不只能下載。

### 已完成檔案

- `frontend/src/app/page.tsx`
  - 降低首頁最大字級，避免高縮放時大標擠壓。
  - 將首頁雙欄與三欄布局延後到更寬螢幕才啟用。
  - 新增「四層分析架構」區塊：資料層、模型層、金融層、交付層。
  - 色調改成更沉穩的青綠、天藍、深藍，不再過度霓虹。
- `frontend/src/components/AppShell.tsx`
  - 全站最大寬度從 1840px 收斂到 1600px。
  - Header 間距調整，並新增窄螢幕「上傳」入口。
- `frontend/src/app/globals.css`
  - 降低背景漸層飽和度。
  - 新增流線動畫、產品預覽微浮動、卡片進場、分析層級掃描線。
  - 新增 `surface-card`、`upload-dropzone`、`code-window` 共用樣式。
- `frontend/src/components/UploadPanel.tsx`
  - 上傳頁新增產品工作台 Hero。
  - 上傳區改為與首頁一致的玻璃面板與柔和漸層。
  - 合併資料與單檔分析外框改為統一產品卡片風格。
- `frontend/src/components/AnalysisResult.tsx`
  - 資料摘要卡片改為統一 surface-card。
- `frontend/src/components/FinancialAnalysisPanel.tsx`
  - 金融分析面板改為統一產品卡片風格。
  - 移除 `Phase 5` 顯示，改為「金融洞察」。
- `frontend/src/components/AgentReportPanel.tsx`
  - AI 協作分析面板改為統一產品卡片風格。
- `frontend/src/components/ModelAnalysisPanel.tsx`
  - 模型分析與 AI 程式碼生成面板改為統一產品卡片風格。
  - 新增頁內程式碼預覽，可切換 Python / Notebook。
- `frontend/src/lib/api.ts`
  - `GeneratedCode` 型別新增 `python_content` 與 `notebook_content`。
- `backend/app/schemas.py`
  - `GeneratedCodeResponse` 新增 `python_content` 與 `notebook_content`。
- `backend/app/services/code_generator.py`
  - 生成程式碼與 Notebook 後，除了檔案路徑與下載 URL，也回傳實際文字內容。
- `backend/tests/test_code_generator.py`
  - 新增測試確認 API 回傳的程式碼內容與實際檔案一致。

### 新增功能與修正

- 修正高縮放跑版：
  - 首頁大型文字降級。
  - 主要雙欄 / 三欄排版改到 `2xl` 以上才啟用。
  - 表單側欄固定寬度改為更彈性的 `minmax`，避免壓縮時撐破。
  - 上傳頁移除容易撐版的 `min-width`。
- 主頁層次強化：
  - 保留正式產品 Hero。
  - 新增四層分析架構，不新增假功能，只重新呈現既有能力。
  - 動畫改為流線、卡片進場、產品預覽微浮動與掃描線，降低霓虹感。
- 上傳頁風格統一：
  - 上傳頁、合併分析、資料摘要、金融分析、模型分析、AI 協作分析都改為相同玻璃卡片系統。
- 程式碼頁內顯示：
  - 使用者生成程式碼後，頁面會直接顯示 Python 程式碼。
  - 可切換 Notebook JSON 預覽。
  - 下載按鈕仍保留。
  - 內容來自後端生成結果，不是前端假資料。

### 如何測試

前端：

```bash
cd frontend
npm run typecheck
npm run build -- --webpack
```

後端：

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

本次結果：

- `npm run typecheck`：通過。
- `npm run build -- --webpack`：通過。
- `python -m pytest`：16 passed。
- `python -m pytest tests/test_code_generator.py`：3 passed。
- Next.js dev server 熱更新正常，首頁 `/` 與上傳頁 `/upload` 回應 200。

### Known Issues

- Browser 工具本 session 曾無法直接以瀏覽器插件開 localhost，因此本次驗證以 Next dev server 回應、TypeScript、production build 與後端測試為主。
- ZIP 套件仍依使用者要求暫不實作。

## 2026-06-10：公開分享準備與 AI 智能分析稽核

### 已完成檔案

- `frontend/next.config.js`
- `frontend/src/lib/api.ts`
- `backend/app/main.py`
- `README.md`
- `PROGRESS.md`

### 新增功能與修正

- 前端 API 預設改為同網域 `/api/*`，不再讓瀏覽器直接打 `127.0.0.1:8000`。
- Next.js 新增代理：
  - `/api/*` -> FastAPI `/api/*`
  - `/generated_outputs/*` -> FastAPI 靜態輸出檔
  - `/health` -> FastAPI 健康檢查
- 本機公開分享時只需要公開前端 port，後端由 Next.js 代理轉發，避免分享給別人後 API 指到對方電腦。
- 後端 CORS 新增 `FRONTEND_ORIGINS` 環境變數，方便正式分開部署時指定前端網域。
- README 補上本機公開分享、分開部署環境變數與 AI 智能判斷稽核結果。

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm run dev
```

若要本機暫時公開分享：

```bash
cd frontend
npx --yes localtunnel --port 3000
```

### 如何測試

前端：

```bash
cd frontend
npm run typecheck
npm run build -- --webpack
```

後端：

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

AI 智能分析稽核：

- `housing_sample.csv` target=`price_usd`：自動判斷為回歸，執行 7 種推薦模型。
- `housing_sample.csv` target=`near_mrt`：自動判斷為分類，執行 6 種推薦模型。
- 兩者模型清單不同，確認不是固定模型硬跑。
- `stock_prices_sample.csv`：金融分析成功產出趨勢摘要與 4 種金融圖表。
- 程式碼生成成功回傳頁內可顯示的 Python / Notebook 內容。
- Multi-Agent 工作流成功回傳 5 個代理步驟；未設定 OpenAI 金鑰時明確標示 `local_rule_based`。

### 本次驗證結果

- `npm run typecheck`：通過。
- `npm run build -- --webpack`：通過。
- `python -m pytest`：16 passed。
- FastAPI TestClient 真實 sample dataset 稽核：通過。
- 暫時公開網址：`https://bitter-meals-lead.loca.lt`。
- 公開網址首頁：HTTP 200。
- 公開網址 `/health`：HTTP 200，回傳 `{"status":"ok","service":"智能金融資料分析 API"}`。
- 公開網址 `POST /api/datasets/analyze`：HTTP 200，成功讀取 `housing_sample.csv`。
- 公開網址 `POST /api/models/analyze`：HTTP 200，target=`price_usd` 自動判斷為回歸並執行 7 種模型。

### 下一階段要做什麼

- 若要長期正式上架，需要選擇部署平台並設定公開網域、環境變數與持久化輸出儲存。
- 若只要暫時分享試用，可用 tunnel 工具取得公開網址。

### Known Issues

- 目前沒有內建一鍵 ZIP 套件，依使用者先前要求暫不實作。
- 若未設定 `OPENAI_API_KEY`，AI 摘要為本機規則摘要，不會呼叫外部 LLM。
- 本機 tunnel 是暫時公開網址，終端機關閉或網路中斷後會失效。

## 2026-06-10：正式雲端部署準備與手機版驗收

### 已完成檔案

- `Dockerfile`
- `.dockerignore`
- `scripts/start-production.sh`
- `render.yaml`
- `DEPLOYMENT.md`
- `README.md`
- `PROGRESS.md`
- `frontend/package.json`
- `generated_outputs/README.md`

### 新增功能與修正

- 新增正式 Docker 部署設定，讓 Next.js 前端與 FastAPI 後端可在同一個雲端容器內執行。
- 新增 Render Blueprint：GitHub repo 連上 Render 後可讀取 `render.yaml` 建立 web service。
- 新增正式啟動腳本：
  - 先啟動 FastAPI。
  - 等 `/health` 通過。
  - 再啟動 Next.js 對外服務。
- 新增 `.dockerignore`，避免把本機 `.venv`、`node_modules`、`.next` 與大量生成輸出放進 Docker image。
- 修正 `npm run typecheck`，避免乾淨 repo 或 `.next` 不存在時吃到舊 incremental cache 而失敗。
- 更新部署文件，明確註明 GitHub Pages 無法執行本專案後端功能。
- 更新 `generated_outputs/README.md`，移除舊品牌名稱與 demo 階段語氣。

### 如何啟動

本機開發：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm run dev
```

正式部署：

```bash
git init
git add .
git commit -m "Initial smart finance analysis platform"
git branch -M main
git remote add origin https://github.com/YOUR_ACCOUNT/YOUR_REPO.git
git push -u origin main
```

然後在 Render 使用 Blueprint 連接 GitHub repo。

### 如何測試

前端：

```bash
cd frontend
npm run typecheck
npm run build -- --webpack
```

後端：

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

手機版：

- Browser viewport：390 x 844。
- 測試頁面：`/` 與 `/upload`。
- 檢查項目：頁面標題、首屏內容、上傳 input、主要按鈕、console error、水平溢出。

### 本次驗證結果

- `npm run typecheck`：通過。
- `npm run build -- --webpack`：通過。
- `python -m pytest`：16 passed。
- 手機首頁 `/`：390px 寬度無水平捲動；console 無錯誤。
- 手機上傳頁 `/upload`：390px 寬度無水平捲動；file input 存在；console 無錯誤。
- 舊品牌關鍵字掃描：前端 UI、一般文件與檔名皆無舊品牌殘留。
- 本機已初始化 Git repo 並加入可部署檔案。

### Known Issues

- 本機 Docker Desktop 可啟動，但 `docker build` 在拉取 `node:20-bookworm-slim` Docker Hub metadata 時連續逾時，尚未完整跑到專案 build 步驟。
- 這是本機 Docker Hub 連線逾時；Render 雲端部署時會由 Render 自行拉取基底映像並建置。
- 目前 `gh` GitHub CLI 未安裝，且 GitHub connector 只能操作既有 repo，不能建立新 repo；需要使用者先建立 GitHub repository 或提供既有 repo 名稱。
- Render free plan 可能冷啟動，且 generated outputs 屬暫存；若要正式多人長期使用，建議升級方案或改接持久化儲存。

## 2026-06-10：Apple / iOS 風格產品體驗升級

### 已完成檔案

- `frontend/src/components/CommandCenter.tsx`
- `frontend/src/components/SystemStatus.tsx`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/app/page.tsx`
- `frontend/src/app/globals.css`
- `frontend/package.json`
- `README.md`
- `PROGRESS.md`

### 新增功能與修正

- 新增全站 Command Center：
  - `⌘ / Ctrl + K` 開啟快捷指令。
  - `⌘ / Ctrl + U` 在上傳頁開啟檔案選擇；其他頁面前往上傳工作台。
  - `⌘ / Ctrl + Enter` 在上傳頁讀取全部檔案。
  - `?` 開啟快捷指令。
  - `Esc` 關閉快捷指令。
- 新增真實系統狀態元件：
  - 會呼叫 `/health`。
  - 顯示在線、檢查中或需檢查。
  - 顯示實際延遲毫秒。
- 首頁新增更有層次的產品體驗：
  - 控制中心區塊。
  - 命令中心、工作台狀態、頁內程式碼三個系統細節。
  - 更完整的細節探索區塊，整理已存在能力，不新增假功能。
- 上傳頁新增工作台狀態列：
  - 依目前檔案佇列、成功讀取、錯誤數與讀取狀態顯示工作台狀態。
  - 顯示準備度進度條。
  - 新增加入檔案、讀取全部、清空佇列快速動作，全部接到真實功能。
- 視覺系統升級：
  - 更接近 iOS 產品感的白底、玻璃、柔和陰影、焦點狀態、快捷 keycap、命令面板與控制中心層次。
  - 保持原本青綠、天藍、深藍主色，不改成暗黑或過度霓虹。
- 移除未使用且內容含舊品牌的圖片資產。
- `npm run typecheck` 改為先執行 `next typegen`，避免乾淨環境缺少 Next route types。

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm run dev
```

### 如何測試

前端：

```bash
cd frontend
npm run typecheck
npm run build -- --webpack
```

後端：

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

瀏覽器互動：

- 桌機首頁 `/`：檢查 Command Center、系統狀態、控制中心區塊與水平溢出。
- 桌機 `/upload`：檢查工作台狀態列、快速動作與 file input。
- 手機 390 x 844：檢查首頁與上傳頁無水平溢出。

### 本次驗證結果

- `npm run typecheck`：通過。
- `npm run build -- --webpack`：通過。
- `python -m pytest`：16 passed。
- Browser 桌機首頁：Command Center 可開啟；系統狀態有呼叫 `/health`；無水平溢出；console 無錯誤。
- Browser Command Center：可從「前往上傳工作台」導到 `/upload`。
- Browser 桌機上傳頁：工作台狀態列與三個快速動作存在；file input 存在；無水平溢出；console 無錯誤。
- Browser 手機首頁與上傳頁 390px：無水平溢出；快捷 dock、上傳工作台與主要內容可見。

### Known Issues

- Command Center 目前只收納已存在的真實功能；若未來要加入更多快捷動作，需要先把對應 API 或 UI 功能做完。
- 檔案選擇器由瀏覽器安全機制控制，只有使用者互動觸發時才能開啟。

## 2026-06-10：清晰流程版首頁與上傳工作台重整

### 已完成檔案

- `frontend/src/app/page.tsx`
- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/app/globals.css`
- `README.md`
- `PROGRESS.md`

### 新增功能與修正

- 首頁重新整理為更接近參考圖的產品型版面：
  - 左側清楚說明「讓資料說話，讓決策更智慧」。
  - 右側產品預覽面板顯示資料任務、指標、模型趨勢與流程。
  - 下方以五步流程呈現：資料匯入、資料探索、模型分析、金融分析、報告輸出。
  - 加入多層分析引擎區塊，說明資料層、模型層、金融層與交付層。
- 上傳頁改成工作台式結構：
  - 左側流程導覽與準備度摘要。
  - 中央多檔上傳、檔案佇列、合併分析與各檔分析結果。
  - 右側分析流程進度、快捷鍵與真實系統狀態。
- 保留並串接原本所有真實功能：
  - 多檔 `input[type=file][multiple]`。
  - `POST /api/datasets/analyze-multiple`。
  - 合併分析、模型分析、金融分析、AI 協作報告與程式碼生成面板。
- 視覺上降低雜訊與霓虹感，改為白底、清楚層級、玻璃面板、柔和陰影與較穩定的資訊密度。
- 新增響應式規則，桌機為左側欄、主內容、右側欄，手機自動收成單欄。

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm run dev
```

### 如何測試

前端：

```bash
cd frontend
npm run typecheck
npm run build -- --webpack
```

後端：

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

瀏覽器：

1. 打開 `http://127.0.0.1:3000/`。
2. 確認首頁有產品預覽、五步流程與多層分析引擎。
3. 打開 `http://127.0.0.1:3000/upload`。
4. 確認上傳頁有左側流程導覽、中央上傳區與右側進度欄。
5. 用手機寬度 390 x 844 檢查首頁與上傳頁沒有水平捲動。

### 本次驗證結果

- `npm run typecheck`：通過。
- `npm run build -- --webpack`：通過。
- `python -m pytest`：16 passed。
- `curl http://127.0.0.1:3000/health`：回傳 `{"status":"ok","service":"智能金融資料分析 API"}`。
- Browser DOM 驗證：
  - 桌機首頁 1440 x 950：無水平溢出，5 個流程卡、4 個引擎卡、產品預覽存在。
  - 桌機上傳頁 1440 x 950：無水平溢出，`multiple` 上傳 input 存在，6 個流程進度、3 個右側欄卡片存在。
  - 手機首頁 390 x 844：無水平溢出，首頁主標與產品預覽存在。
  - 手機上傳頁 390 x 844：無水平溢出，工作台、上傳區、流程進度與多檔 input 存在。
  - Browser console error/warn：空。

### 下一階段要做什麼

- 若要再提升產品感，可針對模型分析、金融分析、AI 協作報告三個結果面板做同一套工作台風格重整。
- 若要公開部署，依 `DEPLOYMENT.md` 推到 GitHub 後使用 Render Blueprint 建立正式服務。

### Known Issues

- Browser plugin 在本次 session 的 `Page.captureScreenshot` 連續逾時，因此本輪視覺驗收以 DOM snapshot、console logs、viewport 尺寸與水平溢出量測為主，未取得可附上的 Browser 截圖。
- 首頁右側裝飾光帶會在幾何上超出 viewport，但父層 `overflow: hidden` 生效，實際 `scrollWidth` 與 `clientWidth` 相同，不會造成水平捲動。

## 2026-06-10：iOS 式視覺收斂與微互動

### 已完成檔案

- `frontend/src/app/globals.css`
- `frontend/src/app/page.tsx`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/CommandCenter.tsx`
- `frontend/src/components/UploadPanel.tsx`
- `README.md`
- `PROGRESS.md`

### 新增功能與修正

- 全站字級與元件密度重新收斂：
  - 縮小首頁主標、區塊標題、導覽、工作台標題、卡片文字與控制項。
  - 調整行高、間距與固定尺寸，讓桌機與手機畫面更精緻且不易位移。
- 降低霓虹感並加強層次：
  - 主色改為低飽和藍綠與深藍灰。
  - 建立低、中、高三層陰影 token，區分一般卡片、浮動面板與彈出層。
  - 收斂背景光帶、按鈕漸層、焦點框與圖表裝飾色。
- 加入 iOS 式微互動：
  - Command Center 增加背景淡入、面板縮放滑入、圓形關閉按鈕與空搜尋狀態。
  - 自動判斷依據、批次訊息、合併判斷、快速鍵及系統狀態改為可展開區塊。
  - 展開箭頭會旋轉，內容採用淡入下移動畫。
  - 工作台新增浮動通知，反映加入檔案、重複檔案、讀取完成、部分失敗、移除與清空等真實操作。
- 移除首頁假分析數字：
  - 首頁產品預覽改為「等待資料匯入」初始狀態。
  - 只呈現平台真實支援能力與尚未開始的流程，不顯示虛構模型分數或分析量。
  - 清除未使用的假圖表與固定百分比樣式。

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm run dev
```

### 如何測試

前端：

```bash
cd frontend
npm run typecheck
npm run build -- --webpack
```

後端：

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

操作檢查：

1. 開啟首頁，確認字級、低飽和色彩、卡片層次與「查看自動判斷依據」展開動畫。
2. 使用 `⌘ K` 或 `Ctrl K` 開啟 Command Center，測試搜尋、空狀態、關閉按鈕與背景點擊關閉。
3. 進入上傳工作台，加入多個檔案並確認通知內容由實際操作狀態產生。
4. 展開或收合批次訊息、合併判斷、快速鍵與系統狀態。
5. 執行真實資料讀取，確認通知、資料摘要與後續分析結果皆來自後端 API。

### 本次驗證結果

- `npm run typecheck`：通過。
- `npm run build -- --webpack`：通過。
- `python -m pytest`：16 passed。
- 原始碼掃描：首頁已無固定 `65%`、`68h` 或 `liveSignals` 假展示資料。
- `git diff --check`：通過。

### 下一階段要做什麼

- 將模型分析、金融分析、AI 協作報告與程式碼預覽面板進一步統一為相同的字級、展開層級與結果導覽方式。
- 公開部署後，以真實手機與桌機瀏覽器執行完整上傳、分析、報告及程式碼預覽流程。

### Known Issues

- 本次 Browser plugin 在導覽本機頁面時發生 CDP `Page.enable` / `Page.navigate` 逾時，且測試用 `127.0.0.1:3001` 被工具安全政策拒絕，因此未取得本輪自動化截圖。
- 本機已有一個無回應的 Next 開發程序占用 `3000`，production build 與 TypeScript 檢查仍正常；重新啟動開發伺服器前需先由本機終端結束該程序。

## 2026-06-10：分析流程防遮擋與工作階段保留

### 已完成檔案

- `frontend/src/app/layout.tsx`
- `frontend/src/app/page.tsx`
- `frontend/src/app/globals.css`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/components/ModelAnalysisPanel.tsx`
- `frontend/src/components/FinancialAnalysisPanel.tsx`
- `frontend/src/components/AgentReportPanel.tsx`
- `frontend/src/components/WorkspaceProvider.tsx`
- `frontend/src/components/CommandCenter.tsx`（移除）
- `frontend/src/components/SystemStatus.tsx`（移除）
- `README.md`
- `PROGRESS.md`

### 新增功能與修正

- 修正分析流程面板遮擋分析結果：
  - 移除右側 sticky 浮動流程欄。
  - 將六步分析進度改為主內容內的響應式摘要面板。
  - 桌機採三欄兩列，手機採單欄排列。
  - 工作台桌機版改為左側導覽加主內容兩欄，不再預留會壓縮結果區的右側欄。
- 移除快捷鍵與系統在線介面：
  - 導覽列不再顯示系統在線與延遲。
  - 移除快捷按鈕、浮動快捷入口、命令面板與工作台快捷鍵說明。
  - 首頁產品預覽不再顯示在線狀態。
- 新增工作階段狀態保留：
  - 根布局加入 `WorkspaceProvider`。
  - 保留上傳檔案、資料摘要、合併結果與批次訊息。
  - 保留模型設定、模型結果、金融結果、AI 工作流、Word 報告與程式碼預覽。
  - 從工作台回首頁再回到工作台時，不會因頁面元件卸載而清除資料。
  - 使用者按下「清空」或重新分析相同資料時，會同步清除失效的下游分析狀態。

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm run dev -- --hostname 127.0.0.1 --port 3000
```

網站：

```text
http://127.0.0.1:3000
```

### 如何測試

1. 進入 `/upload`，上傳並讀取至少一個 CSV 或 Excel。
2. 執行模型、金融或報告分析。
3. 點擊導覽列「首頁」，再點擊「上傳資料」。
4. 確認檔案、摘要與已完成的分析結果仍存在。
5. 確認分析流程進度位於主內容上方，不會覆蓋欄位清單、缺失值或模型結果。
6. 確認首頁與工作台均無快捷鍵、浮動命令入口及系統在線標示。
7. 點擊「清空」，確認工作階段資料與下游分析狀態全部移除。

### 本次驗證結果

- `npm run typecheck`：通過。
- `npm run build -- --webpack`：通過。
- `python -m pytest`：16 passed。
- Browser 桌機 1440 x 950：
  - 左側欄寬 238px，主內容寬 1120px。
  - 流程進度面板寬 1120px 且 `position: static`。
  - 無水平溢出，流程面板不會進入分析內容上方。
- Browser 手機寬度 599px：
  - 流程步驟改為單欄。
  - 無水平溢出。
- Browser 往返導覽：
  - `/upload` → `/` → `/upload` 正常。
  - 首頁與工作台均未出現「快速鍵」或「系統在線」。
  - console error / warn：空。
- 原始碼掃描：
  - 正式頁面與元件已無 `CommandCenter`、`SystemStatus`、快捷鍵或系統在線引用。

### 下一階段要做什麼

- 以使用者實際上傳的多檔資料做完整手動驗收，包含模型結果、金融結果、報告與程式碼預覽的往返保留。
- 若之後需要在整頁重新整理或關閉瀏覽器後仍保留檔案，可再評估 IndexedDB；目前不使用它，以避免未經使用者預期長期保存本機資料。

### Known Issues

- 瀏覽器基於安全限制，重新整理或關閉分頁後不能自動重新取得使用者的本機 `File`；目前保留範圍是同一瀏覽器分頁中的頁面往返。
- Browser 自動化工具不能操作 macOS 原生檔案選擇器，因此本輪無法自動替使用者選取本機 sample dataset；檔案選擇後的狀態結構已通過 TypeScript 與 production build 驗證。

## 2026-06-13：高級介面層次、微互動與動態背景

### 已完成檔案

- `frontend/components.json`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/tailwind.config.ts`
- `frontend/src/app/globals.css`
- `frontend/src/app/page.tsx`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/MotionPrimitives.tsx`
- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/components/ui/badge.tsx`
- `frontend/src/components/ui/button.tsx`
- `frontend/src/components/ui/skeleton.tsx`
- `frontend/src/components/ui/spinner.tsx`
- `frontend/src/lib/utils.ts`
- `README.md`
- `PROGRESS.md`

### 新增功能與修正

- 保留現有首頁、工作台與分析流程，不重新設計資訊架構。
- 建立統一介面 tokens：
  - 語意背景、文字、邊框、品牌、錯誤與狀態色。
  - 低、中、高表面陰影、控制項陰影與主要操作陰影。
  - 統一控制項與面板圓角，以及快速與大型轉場節奏。
- 加入 shadcn/ui primitives：
  - Button、Badge、Skeleton、Spinner。
  - 主要按鈕具備 hover、press、disabled、loading 與 focus-visible 狀態。
  - 圖示統一改用 Lucide，移除首頁手寫 SVG 圖示。
- 建立可重用 Motion 元件：
  - `AmbientCanvas`：24 秒與 29 秒週期的低透明度背景光場。
  - `RouteStage`：可中斷的頁面淡入與小幅位移轉場。
  - `ScrollReveal`：大型內容區塊一次性進場。
  - `PointerSurface`：只作用於產品預覽的低強度游標感應光暈。
- 強化表面層級：
  - 導覽列保留少量半透明材質。
  - 資料與分析面板改用較實體、可讀性更高的表面。
  - 使用細邊框、頂部高光、低飽和色彩與多層陰影區分前景、中景與背景。
- 強化工作台操作回饋：
  - 真實 API 讀取期間顯示 spinner 與 skeleton。
  - 加入檔案、重複、完成、部分失敗、移除與清空通知改為可中斷進出動畫。
  - 移除拖放區巢狀按鈕語意，鍵盤使用者可直接聚焦「選擇檔案」與「加入檔案」。
- 響應式與降級：
  - 1440px、1280px、768px、390px 均無水平溢位。
  - 手機隱藏桌機導覽與工作台側欄，主要操作自動滿寬。
  - 支援系統深色模式、`prefers-reduced-motion` 與觸控裝置低動態模式。
  - 背景持續動畫只使用 transform 與 opacity；手機停用游標光暈與預覽浮動。

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev -- --hostname 127.0.0.1 --port 3000
```

網站：

```text
http://127.0.0.1:3000
```

### 如何測試

前端：

```bash
cd frontend
npm run typecheck
npm run build
```

後端：

```bash
cd backend
./.venv/bin/pytest -q
```

真實 API：

```bash
curl -X POST http://127.0.0.1:8000/api/datasets/analyze-multiple \
  -F "files=@sample_datasets/housing_sample.csv" \
  -F "files=@sample_datasets/stock_prices_sample.csv"
```

```bash
curl -X POST http://127.0.0.1:8000/api/models/analyze \
  -F "file=@sample_datasets/housing_sample.csv" \
  -F "target_column=price_usd" \
  -F "analysis_mode=auto" \
  -F "chart_types=auto" \
  -F "model_selection_mode=auto" \
  -F "selected_models=auto"
```

### 本次驗證結果

- `npm run typecheck`：通過。
- `npm run build`：production build 通過。
- `./.venv/bin/pytest -q`：16 passed。
- 多檔 API：
  - `housing_sample.csv` 與 `stock_prices_sample.csv` 均成功讀取。
  - 真實合併結果為 24 列、15 欄、2 個來源檔案。
- 自動模型 API：
  - 自動判斷為回歸問題。
  - 依資料內容推薦 Ridge、Lasso、Elastic Net、Random Forest、Gradient Boosting、XGBoost、KNN。
  - 真實執行 7 個模型並生成模型比較、特徵重要性、預測對實際與殘差圖。
- Browser：
  - 首頁與 `/upload` 正常渲染，無 Next.js 錯誤覆蓋。
  - console error / warn：空。
  - 1440px、1280px、768px、390px 的 `scrollWidth` 均等於 `clientWidth`。
  - 首頁導覽與自動判斷下拉互動正常。
  - 「選擇檔案」可取得鍵盤 `focus-visible`。

### 下一階段要做什麼

- 公開環境以真實手機與 Safari、Chrome 各執行一次完整上傳、模型、金融、報告與程式碼預覽流程。
- 視正式部署效能資料調整背景光場透明度與低效能裝置門檻。
- 持續統一模型、金融與報告結果面板的狀態顏色與長內容閱讀密度。

### Known Issues

- Browser 自動化工具不能操作 macOS 原生檔案選擇器，因此前端選檔後的完整流程需人工點選本機檔案；本輪已用同一批 sample datasets 直接呼叫真實 FastAPI，驗證多檔合併與自動模型分析。
- Browser 本輪無法模擬作業系統深色偏好；深色 tokens 與 media query 已通過 production build，仍建議在正式 Safari 與 Chrome 各做一次人工視覺驗收。
- 開發模式左下角會出現 Next.js Dev Tools 按鈕；production build 不會顯示。

## 2026-06-14：五頁 AI SaaS 工作區與分析結果漸進揭露

### 已完成檔案

- `frontend/src/app/page.tsx`
- `frontend/src/app/upload/page.tsx`
- `frontend/src/app/models/page.tsx`
- `frontend/src/app/finance/page.tsx`
- `frontend/src/app/reports/page.tsx`
- `frontend/src/app/globals.css`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/PagePrimitives.tsx`
- `frontend/src/components/WorkspaceSource.tsx`
- `frontend/src/components/WorkspaceToolPages.tsx`
- `frontend/src/components/WorkspaceProvider.tsx`
- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/components/AnalysisResult.tsx`
- `frontend/src/components/ModelAnalysisPanel.tsx`
- `frontend/src/components/FinancialAnalysisPanel.tsx`
- `frontend/src/components/AgentReportPanel.tsx`
- `frontend/src/components/MotionPrimitives.tsx`
- `README.md`
- `PROGRESS.md`

### 新增功能與修正

- 將兩頁結構重建為五頁產品工作區：
  - `/`：真實資料品質、來源、分析進度與建議下一步。
  - `/upload`：多檔上傳、讀取、合併來源選擇與資料探索。
  - `/models`：目標欄位、分析模式、自動或手動模型、AutoML、圖表與程式碼。
  - `/finance`：日期／價格欄位、金融訊號、風險、技術指標與預測。
  - `/reports`：AI 管理摘要、代理執行紀錄與 Word 報告。
- 新增全域資料來源選擇器：
  - 可切換每個成功讀取的檔案與合併資料集。
  - 路由往返時保留檔案、設定、分析結果與程式碼預覽。
- 重構資訊層級：
  - 資料頁用總覽、欄位、缺失值、數值摘要頁籤取代同時顯示全部表格。
  - 模型頁先顯示最佳模型與關鍵 KPI，完整比較表按需展開。
  - 金融頁先顯示趨勢、價格、報酬、波動率與 VaR，再查看完整指標和預測。
  - 報告頁先顯示管理摘要，代理步驟收進可展開紀錄。
  - 程式碼仍可在頁面直接切換 Python / Notebook 預覽，不需先下載。
- 新增真實等待與操作回饋：
  - 多檔讀取、模型訓練、金融分析、AI 代理、報告與程式碼生成都有分段 loading。
  - 結果使用可中斷的小幅淡入，錯誤使用 `role="alert"`，一般通知使用 `role="status"`。
  - 清空工作區改為兩次確認，避免誤刪目前分析。
- UX 與 accessibility 修正：
  - 增加 skip link、語意標題、表格 `scope`、`aria-busy` 與資料完整度 progressbar。
  - 資料和圖表 tabs 支援 Left、Right、Home、End 鍵。
  - 所有互動元素保留清楚 `focus-visible`，手機改為固定底部導覽。
  - 圖表加入尺寸、lazy loading 與不造成版面跳動的 aspect ratio。
  - 支援 `prefers-reduced-motion`，降低或停用持續動畫與載入位移。
- 視覺重建：
  - 深色側欄作為定位層，白色實體工作面承載主要內容。
  - 文字、數據與表格改用高對比語意色，移除會穿過閱讀區的霓虹和透明表面。
  - 品牌色只用在目前位置、主要動作、完成狀態與關鍵結論。
  - 桌機固定側欄，平板與手機使用五項底部導覽。

### 如何啟動

後端：

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev -- --hostname 127.0.0.1 --port 3000
```

### 如何測試

```bash
cd frontend
npm run typecheck
npm run build -- --webpack
```

```bash
cd backend
./.venv/bin/pytest -q
```

人工流程：

1. 在 `/upload` 加入兩個 sample datasets 並執行「讀取全部」。
2. 切換單檔與合併資料來源，確認資料頁籤內容跟著改變。
3. 到 `/models` 執行自動模型分析，確認先顯示最佳模型，圖表可切換，完整比較表可展開。
4. 生成程式碼，確認 Python 與 Notebook 可直接在頁面預覽。
5. 到 `/finance` 選擇股票資料，確認金融訊號、風險、圖表與預測來自後端結果。
6. 到 `/reports` 執行 AI 分析並生成 Word 報告。
7. 回到 `/`，確認分析進度與建議下一步反映目前工作區狀態。
8. 使用鍵盤操作主要導覽、頁籤、details、表單與按鈕。
9. 在 390px、768px、1440px 檢查無水平溢位與文字遮擋。

### 本次驗證結果

- `npm run typecheck`：通過。
- `npm run build -- --webpack`：通過，`/`、`/upload`、`/models`、`/finance`、`/reports` 均成功預渲染。
- `./.venv/bin/pytest -q`：16 passed。
- `git diff --check`：通過。
- Web Interface Guidelines 靜態審查：
  - 修正圖表 tabs 鍵盤操作與 tabpanel 關聯。
  - 修正錯誤通知語意、資料完整度 progressbar 與圖表固有尺寸。
  - 修正深色模式選擇器在淺色環境誤套用的風險。
- Turbopack build 在受限沙盒因內部程序嘗試綁定 port 而失敗；改用 Next.js 官方 webpack build 成功完成 production 驗證。

### 下一階段要做什麼

- 在可啟動 localhost 的環境，以 Browser 實際走完多檔上傳、模型、金融、報告和程式碼預覽。
- 以真實 Chrome、Safari 與手機檢查深色模式、觸控目標與長欄位名稱。
- 若實際使用數據顯示使用者需要跨重新整理保留工作區，再評估 IndexedDB；目前不長期保存本機檔案。

### Known Issues

- 本輪沙盒禁止綁定 localhost port；權限申請又因平台用量限制被拒絕，依系統規則不能繞過，因此沒有新的 Browser 截圖或實際 viewport 數據。
- 專案沒有設定 `npm run lint` script；目前使用 TypeScript、production build、`git diff --check` 與後端測試作為自動化門檻。
- 同一分頁路由往返會保留資料；重新整理或關閉分頁後，瀏覽器不會自動重新取得本機 `File`。
## 2026-06-14：完整專案稽核與優先修正

### 已完成檔案

- `backend/app/main.py`
- `backend/app/services/dataset_analyzer.py`
- `backend/tests/test_api_hardening.py`
- `frontend/src/lib/api.ts`
- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/WorkspaceSource.tsx`
- `frontend/src/components/ModelAnalysisPanel.tsx`
- `frontend/src/components/FinancialAnalysisPanel.tsx`
- `frontend/src/components/AgentReportPanel.tsx`
- `Dockerfile`
- `README.md`
- `docs/superpowers/plans/2026-06-14-project-audit-hardening.md`

### 新增功能與修正

- 多檔上傳新增一致邊界：單檔 25 MB、最多 20 檔、批次總容量 100 MB。
- 前端會在檔案進入佇列前檢查限制，後端所有多檔 API 仍會再次驗證。
- 所有前端 POST API 改用共用 request helper：
  - 資料讀取逾時 90 秒。
  - 模型、金融、AI、程式碼與報告分析逾時 300 秒。
  - 統一處理斷線、非 JSON 錯誤與逾時訊息。
- 500 與資料解析錯誤不再回傳底層例外原文；完整例外保留在伺服器 log。
- API 回應新增 `nosniff`、frame deny、referrer policy、permissions policy 與敏感輸出 `no-store`。
- 補上主要表單欄位的 `name` 與自動填入策略。
- `/upload` 移除會導回同頁的重複「加入資料」動作。
- 修正 Docker 建置複製不存在 `frontend/public` 的問題。
- 新增 4 項安全回歸測試。

### 如何啟動

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm run dev -- --hostname 127.0.0.1 --port 3000
```

### 如何測試

```bash
cd backend
./.venv/bin/pytest -q
```

```bash
cd frontend
npm run typecheck
npm run build -- --webpack
```

### 本次驗證結果

- 後端：20 passed。
- 前端 TypeScript：通過。
- Next.js production build：通過，五個產品頁均成功預渲染。
- Browser：1440px 與 390px 的 `/`、`/upload`、`/models`、`/finance`、`/reports` 均無水平溢位。

### 下一階段

- 將公開輸出改為使用者隔離的私人儲存與限時下載網址。
- 加入登入、API rate limiting、輸出清理期限與背景工作佇列。
- 將巨型模型面板、模型服務與全域 CSS 拆成可獨立測試的模組。
- 加入 API response 執行期 schema 驗證及分析請求的使用者取消控制。

### Known Issues

- `generated_outputs/` 仍是公開靜態路徑，不能用於未經隔離的敏感生產資料。
- 分析工作仍在 Web 程序執行，高併發時可能阻塞其他請求。
- `npm audit` 因目前環境無法連線 npm registry，依賴弱點狀態尚未完成驗證。
- `docker build --check .` 因本機 Docker daemon 未啟動而無法執行；已修正可確定會失敗的 `frontend/public` 複製路徑，完整容器建置仍需在 Docker 可用時補驗。

## 2026-06-14：品牌首頁、產品工作區與真實分析進度完成

### 已完成檔案

- `frontend/src/app/layout.tsx`
- `frontend/src/app/page.tsx`
- `frontend/src/app/app/**`
- `frontend/src/app/en/**`
- `frontend/src/components/MarketingShell.tsx`
- `frontend/src/components/MarketingHome.tsx`
- `frontend/src/components/ProductPreview.tsx`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/WorkspaceDashboard.tsx`
- `frontend/src/components/WorkspaceProvider.tsx`
- `frontend/src/components/WorkspaceToolPages.tsx`
- `frontend/src/components/LocaleProvider.tsx`
- `frontend/src/components/LanguageSwitch.tsx`
- `frontend/src/components/FeedbackProvider.tsx`
- `frontend/src/components/PagePrimitives.tsx`
- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/components/AnalysisResult.tsx`
- `frontend/src/components/ModelAnalysisPanel.tsx`
- `frontend/src/components/FinancialAnalysisPanel.tsx`
- `frontend/src/components/AgentReportPanel.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/workspace-storage.ts`
- `frontend/src/app/globals.css`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/services/analysis_jobs.py`
- `backend/app/services/analysis_progress.py`
- `backend/app/services/model_runner.py`
- `backend/app/services/financial_analyzer.py`
- `backend/app/services/agent_orchestrator.py`
- `backend/app/services/report_generator.py`
- `backend/tests/test_analysis_jobs.py`
- `README.md`
- `docs/superpowers/plans/2026-06-14-product-experience-rebuild.md`

### 新增功能與修正

- 建立成熟 SaaS 資訊架構：
  - `/` 為品牌首頁。
  - `/app` 為分析總覽。
  - `/app/data`、`/app/models`、`/app/finance`、`/app/reports` 為完整工作區。
  - 舊 `/upload`、`/models`、`/finance`、`/reports` 保留 server redirect。
- 建立繁中優先與英文切換：
  - `/en`、`/en/app/*` 對應所有核心頁面。
  - 切換語言保留目前功能路徑並更新 `html lang`。
- 首頁使用核心敘事「把複雜資料，變成清楚的下一步。」：
  - 分析旅程、資料理解、模型選擇、金融洞察、交付成果與真實分析原則皆連到實際功能。
  - 首頁預覽沒有資料時不顯示模擬數字。
- 工作區使用 IndexedDB 保存 File blobs、摘要、結果、程式碼與目前來源：
  - 回首頁、切換路由或重新整理後仍可繼續。
  - 恢復時會清除中斷的 loading / running 暫態旗標。
- 建立真實後端分析工作：
  - `/api/jobs/models`
  - `/api/jobs/finance`
  - `/api/jobs/agents`
  - `/api/jobs/reports`
  - `GET /api/jobs/{job_id}` 查詢真實階段、完成數與耗時。
  - `DELETE /api/jobs/{job_id}` 協作取消目前工作。
- 模型、金融、代理與報告面板顯示後端進度，不再只使用固定輪播文案。
- 程式碼與 Notebook 仍可直接在模型頁內預覽，並保留下載。
- 介面音效預設關閉，可在工作區設定開啟。
- 修正系統深色偏好造成淺色首頁低對比的問題；產品固定使用設計指定的高對比淺色主題。
- 修正英文頁切回繁中後 `html lang` 可能殘留英文的 accessibility 問題。

### 如何啟動

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm run build -- --webpack
npm run start -- --hostname 127.0.0.1 --port 3010
```

開啟 `http://127.0.0.1:3010`。

### 如何測試

```bash
cd backend
./.venv/bin/python -m pytest tests -q
```

```bash
cd frontend
npm run typecheck
npm run build -- --webpack
```

實際流程：

1. 在 `/app/data` 上傳 `sample_datasets/housing_sample.csv` 與 `stock_prices_sample.csv`。
2. 執行多檔讀取，切換單檔與合併來源。
3. 在 `/app/models` 使用自動模式，確認系統依 target 與資料型態選出候選模型。
4. 觀察真實訓練階段、模型完成數與耗時，再查看最佳模型、圖表與頁內程式碼。
5. 在 `/app/finance` 使用股票資料執行金融指標與預測。
6. 在 `/app/reports` 執行代理分析並生成 Word 報告。
7. 回到 `/app` 與 `/`，確認資料和結果仍存在。
8. 切換 `/en`，確認英文導覽、表單、狀態與操作路徑。

### 本次驗證結果

- `npm run typecheck`：通過。
- `npm run build -- --webpack`：通過，18 個路由完成 production prerender。
- `./.venv/bin/python -m pytest tests -q`：23 passed。
- 真實工作 API 整合測試：
  - 上傳 `housing_sample.csv` 到 `/api/jobs/models`。
  - 輪詢取得真實分析階段。
  - 自動判斷為 regression。
  - 回傳多個實際模型結果與 `model_comparison` 圖表。
- Production Browser 驗收：
  - 1280px 首頁、工作區與資料頁無水平溢位，console error / warn 為空。
  - 768px 與 390px 正確隱藏桌面側欄、顯示底部導覽，無水平溢位。
  - 多檔 input 保留 `multiple`，上傳限制文字與空狀態正確。
  - 英文 `/en/app/data` 正確顯示英文介面與 `html lang="en"`。
  - 從前端網域實際呼叫模型 API，`housing_sample.csv` 自動判斷為 regression，執行 Ridge 與 Random Forest 並產生模型比較圖。
- `git diff --check`：通過。

### 下一階段要做什麼

- 在允許綁定 localhost 的執行環境補跑 Browser 視覺驗收：390px、768px、1440px。
- 正式公開上架前加入登入、租戶隔離、限時下載、rate limiting 與獨立工作 worker。

### Known Issues

- 英文模式已完整涵蓋產品導覽、表單、狀態與互動；後端生成的部分模型說明、圖表標題、金融摘要與 Word 報告內容仍以繁中為主。
- 工作佇列目前是單程序記憶體實作；適合本機與單實例驗收，正式多實例部署應改用 Redis / Celery / RQ 等持久化工作系統。
- `generated_outputs/` 尚未做使用者隔離，不應直接處理公開環境的敏感金融資料。

## 2026-06-15：全站文字對比與配色入口修正

### 已完成檔案

- `frontend/src/components/DataLensHero.tsx`
- `frontend/src/components/ThemePicker.tsx`
- `frontend/src/components/MarketingShell.tsx`
- `frontend/src/components/ModelAnalysisPanel.tsx`
- `frontend/src/components/FinancialAnalysisPanel.tsx`
- `frontend/src/components/AgentReportPanel.tsx`
- `frontend/src/app/product-interface.css`
- `frontend/src/components/__tests__/DataLensHero.test.tsx`
- `frontend/src/components/__tests__/ThemePicker.test.tsx`
- `frontend/src/components/__tests__/MarketingShell.test.tsx`
- `frontend/src/components/__tests__/SemanticColorUsage.test.ts`

### 新增功能與修正

- 修正 `text-muted` 誤用背景 token，導致模型、金融與報告頁文字接近白色的問題。
- 為舊版 `bg-white`、`bg-slate-50`、藍綠提示背景與文字類別加入產品主題映射，避免深色配色出現亮字配白底。
- 配色按鈕改為「調色盤圖示 + 配色」文字，並加入首頁導覽列；手機版仍保持可見。
- 首頁標題改為「看懂資料／找到下一步」，移除中英文句號。
- 10 組配色的主要與次要文字皆使用語意化 token；次要文字對表面最低對比為 5.07:1。

### 如何測試

```bash
cd frontend
npm run test:run
npm run typecheck
```

### 本次驗證結果

- 前端測試：36 passed。
- TypeScript 型別檢查：通過。
- `git diff --check`：通過。
- 正式版建置與 Browser 視覺驗收因本次工具執行額度限制無法重新執行，未將其標示為已通過。

### 下一階段要做什麼

- 工具限制解除後補跑 production build。
- 在首頁、模型頁與深色配色下分別補驗 390px、768px、1440px 視覺對比與配色選單位置。

## 2026-06-17：一般人可讀與研究者深挖改善

### 依據文件

- `docs/strategy/2026-06-17-layperson-and-researcher-improvement-plan.md`

### 已完成檔案

- `backend/app/services/metric_glossary.py`
- `backend/app/services/insight_narrative.py`
- `backend/app/services/dataset_analyzer.py`
- `backend/app/services/model_runner.py`
- `backend/app/services/financial_analyzer.py`
- `backend/app/services/agent_orchestrator.py`
- `backend/app/services/report_generator.py`
- `backend/app/schemas.py`
- `backend/tests/test_dataset_analyzer.py`
- `backend/tests/test_model_runner.py`
- `backend/tests/test_financial_analyzer.py`
- `backend/tests/test_agent_report.py`
- `frontend/src/components/InsightExplainers.tsx`
- `frontend/src/components/AnalysisResult.tsx`
- `frontend/src/components/ModelAnalysisPanel.tsx`
- `frontend/src/components/FinancialAnalysisPanel.tsx`
- `frontend/src/components/WorkspaceDashboard.tsx`
- `frontend/src/components/WorkspaceToolPages.tsx`
- `frontend/src/components/PagePrimitives.tsx`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/__tests__/InsightExplainers.test.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/app/globals.css`

### 新增功能

- 建立通用指標字典，涵蓋資料完整度、缺失值、平均數、中位數、標準差、RMSE、MAE、R²、Accuracy、F1-score、Feature importance、Residual、Return、Volatility、Moving Average、RSI、MACD、VaR、Forecast。
- 資料、模型與金融分析 API 新增一致解釋欄位：`plain_summary`、`confidence`、`evidence`、`terms`、`research_details`。
- 模型與金融圖表新增 `chart_stories`，每張圖表提供「這張圖在看什麼、關鍵發現、代表意義、不能證明什麼、建議下一步」。
- 金融分析新增 `forecast_reliability`，把線性預測改以「基準情境估計」呈現，並在低可信或未回測情境顯示明確警告。
- 金融欄位文案從「價格」泛化為「價格/指數/數值」，避免非股價資料被誤導。
- 前端新增閱讀深度控制：`簡明`、`標準`、`研究`，並記住使用者偏好。
- 新增共用解釋元件：`InsightHeadline`、`PlainSummaryGrid`、`ConfidenceBadge`、`MetricExplainer`、`ChartStoryPanel`、`ResearchDetailsDrawer`、`EvidenceList`。
- 結果頁、模型頁與金融頁第一屏先顯示白話摘要、可信度、支撐證據與下一步，而不是直接丟出大量技術指標。
- Word 報告圖表段落加入「不能證明什麼」，降低圖表被過度解讀的風險。

### 如何啟動

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm run build -- --webpack
npm run start -- --hostname 127.0.0.1 --port 3010
```

### 如何測試

```bash
cd backend
./.venv/bin/python -m pytest tests -q
```

```bash
cd frontend
npm run test:run
npm run typecheck
npm run build -- --webpack
```

人工驗收重點：

1. 上傳任一 CSV / Excel / JSON 後，資料結果第一屏應先看到一句話結論、可信度與下一步。
2. 切換閱讀深度為「研究」後，指標卡應顯示技術定義、公式、方法、參數與限制。
3. 模型圖表下方應有圖表解讀，不只顯示圖片。
4. 金融頁的時間序列輸出應標示為「基準情境估計」，並顯示非投資建議與可信度警告。
5. Word 報告中每張圖表都應包含圖表摘要、解讀、限制與建議，而不是只貼圖。

### 本次驗證結果

- `backend/.venv/bin/pytest backend/tests/test_dataset_analyzer.py backend/tests/test_model_runner.py backend/tests/test_financial_analyzer.py backend/tests/test_agent_report.py -q`：14 passed。
- `npm run test:run`：18 個測試檔、66 passed。
- 從 repo 根目錄執行 `backend/.venv/bin/pytest -q` 會因測試匯入路徑找不到 `app` 而失敗；正確方式是從 `backend/` 目錄執行。
- `cd backend && .venv/bin/pytest -q`：40 passed。
- `cd frontend && npm run typecheck`：通過。
- `cd frontend && npm run build -- --webpack`：通過。
- `INTERNAL_API_BASE_URL=http://127.0.0.1:8002 npm run build -- --webpack`：通過，用於 production browser 驗收。
- `git diff --check`：通過。
- API 驗收：
  - `/api/datasets/analyze` 使用 `sample_datasets/housing_sample.csv`，回傳真實列欄統計、缺失值、資料品質、`plain_summary`、`confidence`、`evidence`、`terms`、`research_details`。
  - `/api/models/analyze` 使用 `housing_sample.csv` 與 `price_usd`，自動判斷 regression，執行 baseline 與多個推薦模型，回傳最佳模型摘要、baseline 對照、模型推薦理由、`terms`、`chart_stories`、`research_details`。
  - `/api/finance/analyze` 使用 `stock_prices_sample.csv`，回傳 MA、報酬率、波動率、RSI、MACD、VaR、基準情境估計、`forecast_reliability`、`chart_stories`、非投資建議式限制。
- Browser 驗收：
  - production frontend `http://127.0.0.1:3012` 搭配 backend `http://127.0.0.1:8002` 正常啟動。
  - 1440px 首頁與 `/app` 無水平溢位，品牌首頁、工作區總覽、配色入口與真實資料提示可見。
  - 工作區設定可開啟，確認有「閱讀深度：簡明 / 標準 / 研究」，點選「研究」後按鈕狀態為 selected。
  - 390px `/app` 與 `/app/data` 無水平溢位，底部導覽、上傳文案與資料準備狀態正常。

### 下一階段要做什麼

- 補強報告頁的「一般人報告 / 研究附錄」切換。
- 增加圖表原始資料下載。
- 增加 baseline 對照的更完整視覺化。
- 做非資料背景使用者理解度測試，驗證是否能在 3 分鐘內說出主要結論、限制與下一步。

### Known Issues

- 目前核心白話解釋採規則式模板；未設定 `OPENAI_API_KEY` 時不會假裝呼叫外部 LLM。
- 金融預測目前是基準情境估計，尚未加入 ARIMA / Prophet / LSTM 等正式回測流程，不應解讀為投資建議。
- 研究模式已顯示方法、參數與限制；圖表原始資料下載仍待補強。

## 2026-06-17：圖表工作區顯示真實分析圖表修正

### 已完成檔案

- `frontend/src/components/WorkspaceToolPages.tsx`
- `frontend/src/app/globals.css`
- `frontend/src/components/__tests__/WorkspaceToolPages.test.tsx`
- `PROGRESS.md`

### 新增功能與修正

- 修正圖表工作區固定顯示「先完成分析」空狀態的問題。
- 圖表工作區現在會依目前資料來源讀取 workspace 狀態中的：
  - `${sourceKey}:model:result`
  - `${sourceKey}:finance:result`
- 若模型或金融分析已產生 `charts`，會在 `/app/charts` 集中顯示真實圖表。
- 若後端同時回傳 `chart_stories`，圖表工作區會顯示圖表說明、關鍵發現、代表意義與建議下一步。
- 新增圖表 gallery 樣式，支援多張圖表在同一頁清楚排列。

### 如何啟動

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8002
```

```bash
cd frontend
INTERNAL_API_BASE_URL=http://127.0.0.1:8002 npm run build -- --webpack
INTERNAL_API_BASE_URL=http://127.0.0.1:8002 npm run start -- --hostname 127.0.0.1 --port 3012
```

### 如何測試

```bash
cd frontend
npm run test:run -- WorkspaceToolPages.test.tsx
npm run test:run
npm run typecheck
INTERNAL_API_BASE_URL=http://127.0.0.1:8002 npm run build -- --webpack
```

人工驗收：

1. 到 `/app/data` 上傳資料。
2. 到 `/app/models` 或 `/app/finance` 執行分析。
3. 到 `/app/charts`，應看到剛剛分析產生的真實圖表與解讀。

### 本次驗證結果

- `npm run test:run -- WorkspaceToolPages.test.tsx`：1 個測試檔、3 passed。
- `npm run test:run`：18 個測試檔、67 passed。
- `npm run typecheck`：通過。
- `INTERNAL_API_BASE_URL=http://127.0.0.1:8002 npm run build -- --webpack`：通過。
- Browser 驗收：`http://127.0.0.1:3012/app/charts` 正常載入，無水平溢位。當前瀏覽器 origin 沒有已上傳資料，因此顯示加入資料空狀態；新增測試已覆蓋「有分析結果時必須顯示圖表」。

### 下一階段要做什麼

- 在圖表工作區加入圖表原始資料下載。
- 讓圖表工作區支援篩選模型圖表、金融圖表與報告圖表。

## 2026-06-17：修復大型與非標準資料集讀取失敗

### 已完成檔案

- `backend/app/services/dataset_analyzer.py`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/tests/test_dataset_analyzer.py`
- `backend/tests/test_api_hardening.py`
- `frontend/src/lib/api.ts`
- `frontend/src/components/AnalysisResult.tsx`
- `frontend/next.config.js`
- `PROGRESS.md`

### 新增功能與修正

- 修復 CSV 只支援逗號分隔的問題，現在會自動偵測逗號、分號、Tab 與 pipe 分隔符。
- 擴充 CSV 編碼支援，除了 UTF-8 / Big5，也支援 CP950 與常見 fallback 編碼。
- 對欄位數不齊的 CSV 增加安全降級：可讀資料會保留，格式異常列會略過並回傳 `parser_warnings`，不再直接讓整個讀取失敗。
- 批次上傳中單一檔案若在摘要分析階段失敗，會回傳該檔案的錯誤，不會拖垮整批資料。
- 多檔合併分析若失敗，已成功讀取的單檔結果仍會保留，合併失敗原因會寫入批次備註。
- 大資料品質檢查改成受控輪廓樣本：超過 50,000 列時，保留真實列數與欄位數，但昂貴的唯一值、重複列、類別不平衡、異常值檢查會使用前 50,000 列建立輪廓，避免讀取過久。
- 修復 10MB 前端代理限制根因：本機前端預設直連 FastAPI `http://127.0.0.1:8002`，避免大檔案先經過 Next dev server 被截斷。
- Next rewrites fallback 已設定 `experimental.proxyClientMaxBodySize = 110mb`，降低未設定直連環境時的大檔代理風險。
- FastAPI 預設 CORS 加入本機常用前端 port `3010` 至 `3015`，包含目前使用的 `3012`。
- 前端資料探索區會顯示後端回傳的讀取警告，讓使用者知道哪些資料列被自動降級處理。
- 前端 API 錯誤萃取支援 FastAPI validation error array，不再只顯示泛化錯誤。

### 如何啟動

```bash
cd backend
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8002

cd frontend
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8002 npm run dev -- --hostname 127.0.0.1 --port 3012
```

### 如何測試

```bash
cd backend
.venv/bin/pytest tests/test_dataset_analyzer.py tests/test_api_hardening.py -q
.venv/bin/pytest -q

cd frontend
npm run typecheck
npm run build -- --webpack
```

人工驗收：

1. 到 `/app/data` 上傳 CSV、Excel 或 JSON。
2. 測試分號分隔 CSV 與欄位數不齊的 CSV，應可讀取並顯示讀取警告。
3. 測試約 17MB CSV，應在合理時間內完成資料輪廓建立。

### 本次驗證結果

- `backend/.venv/bin/pytest tests/test_dataset_analyzer.py tests/test_api_hardening.py -q`：9 passed。
- `backend/.venv/bin/pytest -q`：43 passed。
- `frontend/npm run typecheck`：通過。
- `frontend/npm run build -- --webpack`：通過。
- `npm run build` 的 Turbopack 模式在 sandbox 內因「binding to a port / Operation not permitted」失敗，改用 webpack build 驗證通過；此問題與本次程式碼修復無關。
- HTTP API 實測：
  - 分號 CSV：`HTTP 200`，正確解析為 `player`、`score` 兩欄。
  - 欄位數不齊 CSV：`HTTP 200`，保留可讀列並回傳 `parser_warnings`。
  - 17MB CSV：`HTTP 200`，耗時約 `0.24s`，成功讀取 `700,000` 列與 `4` 欄，品質檢查使用 `50,000` 列輪廓樣本。
- 前端與 CORS 實測：
  - `curl -I http://127.0.0.1:3012/app/data`：`HTTP 200`。
  - `OPTIONS /api/datasets/analyze-multiple` 搭配 `Origin: http://127.0.0.1:3012`：`access-control-allow-origin` 正確回傳 `http://127.0.0.1:3012`。
  - 17MB CSV 搭配 `Origin: http://127.0.0.1:3012` 直連 FastAPI：`HTTP 200`，成功讀取 `700,000` 列與 `4` 欄。

### 下一階段要做什麼

- 針對真實使用者上傳失敗案例，收集失敗檔案的格式、編碼、分隔符與錯誤訊息，持續擴充讀取器。
- 在前端上傳佇列加入「讀取警告詳情」展開區，讓使用者更容易看到被略過的格式異常列說明。

## 2026-06-17：圖表頁改為專有名詞解釋

### 已完成檔案

- `frontend/src/components/WorkspaceToolPages.tsx`
- `frontend/src/components/AppShell.tsx`
- `frontend/src/components/WorkspaceDashboard.tsx`
- `frontend/src/app/globals.css`
- `frontend/src/components/__tests__/WorkspaceToolPages.test.tsx`
- `frontend/src/components/__tests__/AppShell.test.tsx`
- `PROGRESS.md`

### 新增功能與修正

- 依使用者回饋，移除 `/app/charts` 集中顯示圖表的設計，避免和模型頁、金融頁的圖表比較區重複。
- `/app/charts` 改成「專有名詞解釋 / 分析字典」頁。
- 工作區導覽文字從「圖表」改為「名詞」，頂部頁名從「圖表工作區」改為「專有名詞」。
- 名詞頁會優先使用目前資料、模型、金融分析回傳的 `terms`，包含白話說明、判讀方式、限制、技術定義與公式。
- 若目前 workspace 是舊資料、沒有 `terms`，會顯示常用模型指標字典，不會冒充分析結果。
- 工作區總覽中原本連到圖表頁的模型/金融圖表入口，已改回連到模型頁與金融頁。
- 圖表區右側解釋文字加大：標題由 11px 提升到 13px，說明文字由 12px 提升到 14px，行距同步提高。

### 如何啟動

```bash
cd frontend
INTERNAL_API_BASE_URL=http://127.0.0.1:8002 npm run build -- --webpack
INTERNAL_API_BASE_URL=http://127.0.0.1:8002 npm run start -- --hostname 127.0.0.1 --port 3012
```

### 如何測試

```bash
cd frontend
npm run test:run -- WorkspaceToolPages.test.tsx AppShell.test.tsx WorkspaceInsightGrid.test.tsx
npm run test:run
npm run typecheck
INTERNAL_API_BASE_URL=http://127.0.0.1:8002 npm run build -- --webpack
```

人工驗收：

1. 開啟 `/app/charts`。
2. 頁面應顯示「專有名詞解釋」，不應顯示「已產生的分析圖表」。
3. 工作區導覽應顯示「名詞」。
4. 模型頁與金融頁的圖表解釋文字應比之前更大、更容易閱讀。

### 本次驗證結果

- `npm run test:run -- WorkspaceToolPages.test.tsx AppShell.test.tsx WorkspaceInsightGrid.test.tsx`：3 個測試檔、8 passed。
- `npm run test:run`：18 個測試檔、67 passed。
- `npm run typecheck`：通過。
- `INTERNAL_API_BASE_URL=http://127.0.0.1:8002 npm run build -- --webpack`：通過。
- Browser 驗收：`http://127.0.0.1:3012/app/charts` 顯示「專有名詞解釋」，導覽為「名詞」，主內容 `img` 數量為 0，無水平溢位。

## 2026-06-19：修復 3MB 以上資料讀取後模型分析逾時

### 已完成檔案

- `backend/app/services/dataset_analyzer.py`
- `backend/app/services/model_runner.py`
- `backend/app/schemas.py`
- `backend/tests/test_dataset_analyzer.py`
- `backend/tests/test_model_runner.py`
- `backend/tests/test_run_governance.py`
- `frontend/src/lib/api.ts`
- `README.md`
- `PROGRESS.md`

### 新增功能與修正

- 修正 JSON Lines / NDJSON 讀取：`.json` 檔若不是標準 JSON 陣列，後端會嘗試逐列解析真實資料。
- 大型模型分析加入固定 random seed 真實抽樣：
  - 自動模式最多使用 2,000 筆真實資料訓練候選模型。
  - 手動模式最多使用 20,000 筆真實資料訓練。
  - 回傳 `source_row_count` 與 `row_count_used`，讓前端可區分原始資料列數與模型實際訓練列數。
- 自動排除模型訓練不適合的欄位：
  - `customer_id`、`order_id`、`source_row_number` 等識別碼欄位。
  - 高基數文字欄位，避免 one-hot 矩陣爆量。
  - 全欄位缺失欄位。
- 類別欄位 one-hot encoder 加入 `max_categories=64`，避免少數高基數欄位造成記憶體與時間暴增。
- 自動模型推薦避開大型資料上的 SVR / SVC / KNN，改用較穩定且可快速完成的樹模型與 boosting 模型。
- 單一模型訓練失敗時會略過該模型並寫入 notes，不會讓整個分析直接中斷；若所有候選模型都失敗才回傳明確錯誤。
- 數值特徵加入標準化，提升線性與距離類模型穩定性。
- 測試 helper 更新為支援 artifact URL encoded token。
- README 補充大型資料與真實分析策略，明確記錄不使用假資料與假圖表。

### 如何啟動

```bash
cd backend
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8002

cd ../frontend
INTERNAL_API_BASE_URL=http://127.0.0.1:8002 npm run dev -- --hostname 127.0.0.1 --port 3012
```

### 如何測試

```bash
PYTHONPATH=backend backend/.venv/bin/pytest backend/tests -q

cd frontend
npm run build
```

人工驗收：

1. 上傳 CSV / Excel / JSON / JSON Lines 檔案。
2. 點選「讀取全部」，確認每個檔案都能顯示真實列數、欄位數、缺失值與摘要。
3. 對 3MB 以上且含高基數欄位的資料執行模型分析，確認不再長時間卡住。
4. 查看模型 notes，確認有標明抽樣列數、排除欄位與自動模型推薦原因。
5. 確認圖表 URL 來自後端 `generated_outputs/charts/`，不是前端假圖。

### 本次驗證結果

- `PYTHONPATH=backend backend/.venv/bin/pytest backend/tests -q`：48 passed。
- `npm run build`：通過。
- FastAPI TestClient 單檔上傳實測：
  - `big5_taiwan_sales.csv`：0.025s，10,000 列、4 欄。
  - `ragged_3mb.csv`：0.025s，100,000 列、3 欄。
  - `records.json`：0.066s，35,000 列、4 欄。
  - `records.xlsx`：0.194s，12,000 列、4 欄。
  - `records_json_lines.json`：0.046s，20,000 列、4 欄。
  - `sales_3mb.csv`：0.065s，70,000 列、8 欄。
  - `semicolon.csv`：0.010s，10,000 列、3 欄。
  - `wide_3mb.csv`：0.176s，3,500 列、180 欄。
- FastAPI TestClient 多檔上傳實測：3 檔全部成功，0.308s。
- `sales_3mb.csv` 模型分析本地 HTTP 實測：0.444s，原始 70,000 列，模型使用真實抽樣 2,000 列，自動模型為 Decision Tree、Random Forest、Extra Trees。
- 追加雲端同步 API 優化：大型自動分析改為 2,000 筆真實抽樣與 Decision Tree、Random Forest、Extra Trees 快速候選模型，以避免 Render / Next proxy 約 30 秒限制。
- 公開 Render 驗證：
  - JSON Lines 單檔讀取：`HTTP 200`，20,000 列、4 欄。
  - 3 檔多檔讀取：`HTTP 200`，`sales_3mb.csv`、`records_json_lines.json`、`records.xlsx` 均成功。
  - `sales_3mb.csv` 同步模型分析：`HTTP 200`，17s，原始 70,000 列，模型使用 2,000 列真實抽樣。
  - 模型比較圖 artifact：`HTTP 200`，PNG，1920 x 1024，49KB。

### Known Issues

- Render 免費方案第一次喚醒可能仍會有冷啟動延遲；這不是資料分析演算法逾時。
- 目前模型訓練為同步執行於單一 Web Service；若未來要支援 100MB 以上資料或更完整 AutoML，應拆成背景 worker 與持久化 job queue。
- LightGBM 在部分測試資料會輸出 feature name warning，但模型結果、圖表與 API 回傳正常。

### 下一階段要做什麼

- 把 `source_row_count` 與 `row_count_used` 顯示在模型結果頁，讓使用者清楚知道模型訓練使用範圍。
- 為大型資料加入使用者可選的「快速 / 平衡 / 全量」模式。
- 若公開測試者提供失敗檔案，新增對應 fixture 與回歸測試。
