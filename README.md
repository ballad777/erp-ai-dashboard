# 智能金融資料分析

智能金融資料分析是一個智慧金融與資料分析平台。使用者可以上傳 CSV / Excel / JSON 資料集，逐步完成資料摘要、多模型分析、圖表輸出、程式碼生成、金融分析與完整輸出套件。

目前狀態：除一鍵 ZIP 套件外，計畫書主要功能已補齊可執行版本。前端可整批上傳多個資料集、顯示後端真實摘要、自動建立合併資料集摘要、選擇目標欄位、選擇分析模式、手動或自動選擇模型與圖表，並產出真實 PNG 圖表、可下載程式碼檔案、Notebook、trained model、模型結果 Excel、Word 分析報告與金融指標 CSV。

> 本專案目前僅適合私人展示、封閉測試與非敏感樣本資料。請勿上傳個資、醫療、財務帳戶或其他敏感資料，也不要開放匿名公眾上傳。

上傳限制：CSV / XLSX / XLS / JSON 單檔最多 25 MB，單次最多 20 個檔案，批次總容量最多 100 MB。前端會先檢查，後端仍會再次驗證。

最新現況請先讀 [`CURRENT_STATUS.md`](CURRENT_STATUS.md)。舊稽核與進度文件保留歷史脈絡，但 `CURRENT_STATUS.md` 代表目前可執行能力與尚未完成項目。

## 技術架構

- 前端：Next.js、React、TypeScript、Tailwind CSS、shadcn/ui、Motion
- 後端：FastAPI
- 資料分析：pandas、numpy
- 模型訓練：scikit-learn、XGBoost、LightGBM
- 圖表輸出：matplotlib
- 報告輸出：python-docx
- 本機持久化：SQLite (`.local/finai.sqlite3`)
- 正式資料庫 schema：PostgreSQL DDL (`backend/database/postgres_schema.sql`)
- 輸出資料夾：`generated_outputs/`

## 產品資訊架構

- `/`：品牌首頁，說明產品價值、真實分析原則與完整分析旅程。
- `/app`：分析總覽，依目前真實結果整理重點與建議下一步。
- `/app/data`：CSV / Excel / JSON 多檔上傳、個別讀取、合併摘要、資料品質檢查與資料探索。
- `/app/models`：自動／手動模型選擇、AutoML、模型比較、圖表與程式碼預覽。
- `/app/charts`：集中整理目前資料來源與真實分析產生的圖表；沒有結果時不顯示示範圖。
- `/app/finance`：日期與價格欄位偵測、金融指標、風險、圖表與預測。
- `/app/reports`：代理分析、管理摘要與 Word 報告輸出。
- `/en`、`/en/app/*`：對應的英文介面；使用者檔名、欄位名稱與程式碼維持原文。

首頁與工作區共用同一套設計 tokens。首頁使用固定兩行的 Data Lens Hero；工作區採 icon rail、漸進式洞察層級與脈絡詳情面板，先顯示結論、依據與下一步，再按需展開完整表格。

工作區提供十套語意配色：晨霧藍綠、Atlas、Iris、Clay、Sage、Frost、Graphite、Amber、Deep Sea 與 Midnight。點選配色後會立即套用並保存至 `localStorage` 的 `finai-product-theme-v1`；深色配色也會同步更新既有表格、表單與分析面板。

WorkspaceProvider 會使用 IndexedDB 保存目前瀏覽器中的本機檔案、資料摘要、分析結果、程式碼與資料來源。在同一個瀏覽器中切換 route、返回首頁或重新整理後，工作區會恢復已保存內容；使用「清空工作區」才會刪除。IndexedDB 不會同步到其他瀏覽器、裝置或使用者帳號，也不是伺服器端專案儲存。

分析產物目前使用短效 HMAC capability URL 下載，直接 `/generated_outputs/*` 靜態路徑已移除。當 API 透過 run context 產生 artifact 時，token 會綁定 `artifact_id`、`run_id`、`project_id` 與 `user_id`，下載也會寫入 audit log。這仍只是封閉測試治理層，不等同正式登入、多租戶授權或企業級權限系統。

主要 API 現在會回傳 `run_id`、`dataset_id` 與 `run_manifest`。Manifest 會記錄輸入檔 SHA-256、參數、模型結果與 artifact 清單，用來支撐後續可重現分析、報告與稽核。

模型、金融、代理與報告流程使用後端工作 API。前端顯示的階段、模型完成數與耗時來自真實後端狀態，可在目前步驟完成後協作取消，不是固定時間的假進度。

## 專案結構

```text
.
├── backend/
│   ├── app/
│   │   ├── database/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── services/
│   │       ├── agent_orchestrator.py
│   │       ├── report_generator.py
│   │       ├── dataset_analyzer.py
│   │       ├── financial_analyzer.py
│   │       ├── model_runner.py
│   │       └── code_generator.py
│   ├── tests/
│   │   ├── test_agent_report.py
│   │   ├── test_code_generator.py
│   │   ├── test_dataset_analyzer.py
│   │   ├── test_financial_analyzer.py
│   │   └── test_model_runner.py
│   ├── pytest.ini
│   ├── database/
│   │   └── postgres_schema.sql
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── assets/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   └── MotionPrimitives.tsx
│   │   └── lib/
│   ├── components.json
│   ├── package.json
│   └── tailwind.config.ts
├── sample_datasets/
│   ├── housing_sample.csv
│   └── stock_prices_sample.csv
├── generated_outputs/
│   ├── charts/
│   ├── code/
│   ├── data/
│   ├── models/
│   └── reports/
├── CURRENT_STATUS.md
└── PROGRESS.md
```

## 安裝與啟動

建議版本：

- Python 3.11 以上
- Node.js 22.13.0 以上
- npm 10 以上

### 啟動後端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

macOS 若 XGBoost / LightGBM 因 `libomp.dylib` 無法載入，後端會在啟動時嘗試用 sklearn 內建的 `libomp.dylib` 自動修復套件 dylib 依賴。若環境沒有 `install_name_tool` 或 sklearn 內建 dylib，系統會自動略過 XGBoost / LightGBM，並保留 sklearn 的 Gradient Boosting、Extra Trees、Random Forest 等可執行模型。

後端健康檢查：

```bash
curl http://127.0.0.1:8000/health
```

後端 API 文件：

```text
http://127.0.0.1:8000/docs
```

### 啟動前端

開另一個終端機：

```bash
cd frontend
npm install
npm run dev
```

前端網址：

```text
http://localhost:3000
```

使用已完成的 production build 啟動在 3010 埠：

```bash
cd frontend
npm run build
npm run start -- --hostname 127.0.0.1 --port 3010
```

```text
http://127.0.0.1:3010
```

前端品質檢查：

```bash
cd frontend
npm run test:run
npm run typecheck
npm run build
```

前端預設呼叫同網域 API：

```text
/api/*
```

`frontend/next.config.js` 會把 `/api/*` 與 `/health` 代理到後端，預設後端位址為：

```text
http://127.0.0.1:8000
```

如果要改 Next.js 代理的後端位址，建立 `frontend/.env.local`：

```bash
INTERNAL_API_BASE_URL=http://127.0.0.1:8000
```

如果前端與後端分開部署，也可以讓瀏覽器直接呼叫公開後端：

```bash
NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.example.com
```

分開部署時，後端可用環境變數設定允許的前端來源：

```bash
FRONTEND_ORIGINS=https://your-frontend-domain.example.com
```

### 本機公開分享

目前前端已支援同網域代理，因此本機分享時只需要把前端 port 公開出去，前端會再由 Next.js 代理到本機 FastAPI 後端。

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```bash
cd frontend
npm run dev
```

接著使用可建立公開網址的 tunnel 工具，例如：

```bash
npx --yes localtunnel --port 3000
```

取得的 `https://*.loca.lt` 網址即可分享給其他人測試。這是暫時公開網址，終端機關閉後網址就會失效。

### 封閉測試雲端部署

若要在你電腦關機後繼續進行私人展示或封閉測試，不能只用 GitHub Pages，因為本專案需要執行 FastAPI、Python 模型、檔案上傳與輸出檔案。

目前提供 GitHub + Render 的 Docker 封閉測試設定：

- `Dockerfile`
- `.dockerignore`
- `scripts/start-production.sh`
- `render.yaml`
- `DEPLOYMENT.md`

將專案推到 GitHub 後，可在 Render 使用 Blueprint 讀取 `render.yaml`，建立單一 Docker Web Service。Render 會提供固定網址，但目前架構不適合公開匿名上傳或任何敏感資料：

```text
https://smart-finance-analysis.onrender.com
```

完整步驟請看：

```text
DEPLOYMENT.md
```

## 介面系統與互動品質

- 產品採用品牌首頁與六頁工作區：`/` 品牌首頁、`/app` 總覽、`/app/data` 資料、`/app/models` 模型、`/app/charts` 圖表、`/app/finance` 金融、`/app/reports` 報告。
- 總覽頁只顯示目前資料品質、分析進度與建議下一步，不使用固定示範數字。
- 全域資料來源選擇器可在單一檔案與合併資料集之間切換，切換路由不會清除目前分頁的分析狀態。
- 使用 CSS variables 統一色彩、間距、陰影、圓角與 160 至 440ms 動態節奏。
- 十套配色使用同一組語意 token，支援點選即時套用、首屏同步初始化與本機持久化。
- 主要操作採用 shadcn/ui primitives，圖示統一使用 Lucide。
- 桌面工作區使用 72px icon rail；主要閱讀區使用實色高對比表面，背景光場不穿過文字區。
- 資料、模型、金融、報告的真實 API 請求都有分段 loading、spinner、成功、警告與錯誤回饋。
- 分析結果採漸進揭露：先顯示最佳模型、金融訊號或管理摘要，再切換圖表，完整表格與代理紀錄按需展開。
- 模型成果可開啟側邊詳情面板；手機會轉為底部抽屜，Escape、背景點擊與焦點回復都有處理。
- 資料與圖表頁籤支援方向鍵、Home、End 與 `focus-visible`。
- 支援 `prefers-reduced-motion`、鍵盤 `focus-visible`、觸控裝置與系統深色模式。
- 桌機使用固定 icon rail；平板與手機切換為底部導覽，表格與圖表保持在可捲動容器內。
- 繁中為預設語言，Header 與工作區設定可切換英文，並保留目前所在功能頁。

### 無障礙與降級

- 所有 icon-only 控制都有可讀名稱，配色選擇器使用 `radiogroup` / `radio` 語意。
- 所有主要操作支援鍵盤、`focus-visible`、Escape 關閉與至少 44px 的手機觸控區。
- `prefers-reduced-motion` 會停用資料透鏡追蹤、面板位移與非必要動畫。
- 圖表工作區只整理真實模型或金融分析輸出；尚未產生圖表時只顯示空狀態，不會製造假圖表。
- 可選介面音效預設關閉，只在長時間工作成功或錯誤時播放簡短回饋。

## 已完成功能

### 第一階段：基礎專案

- 建立 Next.js + React + Tailwind CSS 前端。
- 建立 FastAPI 後端。
- 建立首頁與資料集上傳頁。
- 前端上傳按鈕會呼叫真實後端 API。
- 後端支援 CSV / XLSX / XLS。
- 上傳後回傳並顯示：
  - 欄位名稱
  - 資料筆數
  - 欄位數量
  - 欄位型別
  - 缺失值統計
  - 數值欄位摘要

### 第二階段：模型分析功能

- 使用者可以在上傳分析後選擇目標欄位。
- 後端自動判斷回歸或分類問題。
- 後端不再固定執行同一批模型，會依資料列數、特徵數、欄位型態、缺失比例與問題型態自動推薦模型。
- 使用者也可手動選擇要執行的模型。
- 目前支援模型：
  - 回歸：線性迴歸、Ridge、Lasso、ElasticNet、決策樹、隨機森林、Extra Trees、Gradient Boosting、KNN、SVR
  - 進階回歸：XGBoost、LightGBM
  - 分類：Logistic Regression、決策樹、隨機森林、Extra Trees、Gradient Boosting、KNN、SVC
  - 進階分類：XGBoost、LightGBM
- 模型可用性不是寫死清單，後端會依實際 import 結果提供 `/api/models/options`。若 XGBoost / LightGBM 在目前環境不可載入，就不會假裝可用。
- 支援 Quick AutoML 小型參數搜尋，回傳每個模型最佳參數。
- 後端會保存 trained model 到 `generated_outputs/models/`。
- 後端會輸出 `model_results.xlsx` 與 `cleaned_dataset.csv`。
- 前端顯示模型比較表：
  - R2
  - RMSE
  - MAE
  - 訓練時間
- 後端會實際產生模型比較圖，存入：

```text
generated_outputs/charts/
```

- 前端會直接顯示後端產生的圖片。

### 第二階段加強：多檔案、合併分析與分析模式選擇

- 資料集上傳頁可一次或分多次加入多個 CSV / Excel 檔案。
- 前端會整批呼叫後端多檔 API：`POST /api/datasets/analyze-multiple`。
- 每個檔案都會顯示獨立摘要與錯誤狀態。
- 兩個以上檔案成功讀取時，後端會建立合併資料集摘要。
- 合併策略為依欄位名稱垂直合併，保留欄位聯集、來源檔案欄位與來源列號。
- 合併資料集也可以直接執行模型分析：`POST /api/models/analyze-merged`。
- 後端會提供建議目標欄位，前端可一鍵選用。
- 每個檔案都可以各自執行模型分析。
- 模型分析可選擇：
  - 自動選擇
  - 回歸分析
  - 分類分析
- 模型策略可選擇：
  - 系統自動推薦模型
  - 使用者手動多選模型
- 圖表產出可選擇：
  - 系統自動選最適合圖表
  - 使用者手動指定圖表類型

### 第三階段：Colab 式圖表輸出

目前已實作並可實際輸出到 `generated_outputs/charts/`：

- 模型比較圖
- 特徵重要性
- 預測值與實際值
- 殘差圖

前端會讀取後端回傳的真實圖片 URL，直接顯示所有產出的圖表。

依後續需求，目前不產生相關係數熱力圖。

### 第四階段：AI 程式碼生成

- 模型分析完成後，可選擇要生成程式碼的主要模型。
- 後端會依目前資料、目標欄位、分析模式、圖表選擇與主要模型產生：
  - `generated_code.py`
  - `notebook.ipynb`
- 生成的 Python 程式碼包含：
  - 讀取資料
  - 清理資料與缺失值補值
  - train/test split
  - 模型訓練
  - R2、RMSE、MAE 評估
  - 圖表生成
- 後端會把本次使用的資料另存到 `generated_outputs/data/`，讓生成的程式碼可在專案內直接執行。
- 單檔與合併資料都支援程式碼生成。
- 前端會在頁面內以可複製、有行號的程式碼面板顯示本次生成的 Python 程式碼，並可切換 Notebook 預覽；下載功能仍保留。

### 第五階段：金融分析模式

- 新增金融分析 API：
  - `POST /api/finance/analyze`
  - `POST /api/finance/analyze-merged`
- 後端可自動偵測日期欄位與價格欄位，也可接受使用者手動指定欄位。
- 產生金融指標：
  - 移動平均 MA
  - 報酬率
  - 波動率
  - RSI
  - MACD
  - VaR 風險值
  - 時間序列預測
- 實際輸出金融圖表到 `generated_outputs/charts/`：
  - 價格與移動平均
  - 報酬率與波動率
  - RSI 與 MACD
  - 時間序列預測
- 實際輸出金融指標 CSV 到 `generated_outputs/data/`。
- 前端會在資料中偵測到日期與價格候選欄位時顯示金融分析面板。
- 單檔與合併資料都支援金融分析。

### Multi-Agent 與 AI 摘要

- 新增 Multi-Agent API：
  - `POST /api/agents/analyze`
  - `POST /api/agents/analyze-merged`
- Agent 分工：
  - 資料理解代理：資料理解與摘要
  - 模型分析代理：模型訓練、AutoML 與比較
  - 金融分析代理：金融指標、VaR、時間序列預測
  - 視覺化代理：整理後端輸出圖表
  - 報告代理：生成摘要與報告素材
- 若環境有 `OPENAI_API_KEY`，會嘗試呼叫 OpenAI 產生 LLM 摘要。
- 若未設定金鑰，會明確回傳 `local_rule_based`，使用本機規則摘要，不假裝 LLM 已執行。

### 報告輸出

- 新增 Word 報告 API：
  - `POST /api/reports/generate`
  - `POST /api/reports/generate-merged`
- 報告會輸出到 `generated_outputs/reports/`。
- 報告中心與 API 會回傳 `decision_brief`，包含執行摘要、最重要發現、需要注意、成長機會/金融訊號、建議行動、模型推薦原因與逐圖解讀。
- 每張圖表都會附上圖表說明、關鍵發現、代表意義、趨勢解讀、異常說明、商業洞察與決策建議。
- Word 報告升級為顧問式章節：分析目的、分析方法、分析結果、結果解讀、商業意義、建議行動、風險與限制、AI 結論摘要。
- 若未設定 `OPENAI_API_KEY`，報告仍會使用本機規則產生可重現解讀，並明確標示 `local_rule_based`。
- ZIP 套件依使用者要求本階段不實作。

### 介面風格

- 網站已調整為 Linear 風格的高對比 AI SaaS 工作區，優先讓流程與結論一眼可讀。
- 保留原有主色系：`ink`、`brand`、`navy`、`amber`。
- 使用深色定位層、白色工作面與低飽和藍綠狀態色，避免霓虹、過度玻璃與卡片牆。
- 首頁是實際 Dashboard，顯示真實資料品質、來源清單、分析進度與下一步。
- 上傳頁只負責多檔資料管理與探索，不再同頁堆疊模型、金融、報告與程式碼。
- 模型頁改為聚焦流程台：先確認目標欄位、分析模式與模型策略，再執行真實後端模型比較；結果先顯示最佳模型、關鍵指標與建議下一步。
- 金融頁先顯示趨勢與風險；報告頁先顯示管理摘要。
- 完整比較表、預測表、AutoML、圖表設定與代理執行紀錄使用可展開區域。
- 上傳、讀取、移除、清空、分析、程式碼生成與報告生成都有真實狀態回饋。

### 工作階段保留

- WorkspaceProvider 會透過 IndexedDB 保存上傳檔案、資料摘要、模型結果、金融結果、報告與程式碼預覽。
- 在同一個瀏覽器中切換 route、返回首頁或重新整理後，工作區會恢復已保存的檔案與分析狀態。
- IndexedDB 不會同步到其他瀏覽器、裝置或使用者帳號，也不是伺服器端專案儲存。
- 按下工作台的「清空工作區」後，才會刪除這個瀏覽器中已保存的工作區內容。

## 測試流程

### 網頁測試

1. 啟動後端與前端。
2. 打開 `http://localhost:3000`。
3. 點選「上傳資料」。
4. 加入 `sample_datasets/housing_sample.csv` 與 `sample_datasets/stock_prices_sample.csv`。
5. 點選「讀取全部檔案」。
6. 確認資料來源選擇器可切換兩個檔案與合併資料集，資料摘要會跟著改變。
7. 進入 `/models`，選擇建議目標欄位或自行選欄位。
8. 選擇「自動選擇」分析模式與「自動選最適合圖表」。
9. 點選「執行模型分析」。
10. 確認頁面先顯示最佳模型與關鍵指標，可切換後端產生的圖表並展開完整比較表。
11. 在模型策略中切換「自動推薦模型」或「手動選擇模型」，確認模型數量會依選擇改變。
12. 進入 `/finance`，選擇 `stock_prices_sample.csv` 後點選「執行金融分析」。
13. 確認頁面顯示金融摘要、MA / 報酬率 / 波動率 / RSI / MACD / VaR / 時間序列預測圖與指標 CSV 下載。
14. 進入 `/reports`，執行 AI 分析。
15. 點選「生成 Word 報告」，下載 `analysis_report.docx`。
16. 回到 `/models` 的分析結果，在「AI 程式碼生成」選擇主要模型。
17. 點選「生成程式碼」。
18. 直接在頁面內檢查生成的 Python / Notebook 內容，也可下載 `generated_code.py` 與 `notebook.ipynb`。

### 直接測資料摘要 API

```bash
curl -X POST http://127.0.0.1:8000/api/datasets/analyze \
  -F "file=@sample_datasets/housing_sample.csv"
```

### 直接測多檔摘要與合併摘要 API

```bash
curl -X POST http://127.0.0.1:8000/api/datasets/analyze-multiple \
  -F "files=@sample_datasets/housing_sample.csv" \
  -F "files=@sample_datasets/stock_prices_sample.csv"
```

### 直接測模型分析 API

```bash
curl -X POST http://127.0.0.1:8000/api/models/analyze \
  -F "file=@sample_datasets/housing_sample.csv" \
  -F "target_column=price_usd" \
  -F "analysis_mode=auto" \
  -F "chart_types=auto"
```

### 直接測自動推薦模型 API

```bash
curl -X POST http://127.0.0.1:8000/api/models/analyze \
  -F "file=@sample_datasets/housing_sample.csv" \
  -F "target_column=price_usd" \
  -F "analysis_mode=auto" \
  -F "chart_types=auto" \
  -F "model_selection_mode=auto" \
  -F "selected_models=auto"
```

### 直接測手動模型選擇 API

```bash
curl -X POST http://127.0.0.1:8000/api/models/analyze \
  -F "file=@sample_datasets/housing_sample.csv" \
  -F "target_column=price_usd" \
  -F "analysis_mode=regression" \
  -F "chart_types=model_comparison,feature_importance,predicted_vs_actual,residual_plot" \
  -F "model_selection_mode=custom" \
  -F "selected_models=ridge,random_forest,gradient_boosting_regressor,extra_trees_regressor"
```

### 直接測手動圖表選擇

```bash
curl -X POST http://127.0.0.1:8000/api/models/analyze \
  -F "file=@sample_datasets/housing_sample.csv" \
  -F "target_column=price_usd" \
  -F "analysis_mode=regression" \
  -F "chart_types=model_comparison,feature_importance,predicted_vs_actual,residual_plot"
```

### 直接測合併模型分析 API

```bash
curl -X POST http://127.0.0.1:8000/api/models/analyze-merged \
  -F "files=@sample_datasets/housing_sample.csv" \
  -F "files=@sample_datasets/stock_prices_sample.csv" \
  -F "target_column=price_usd" \
  -F "analysis_mode=auto" \
  -F "chart_types=auto"
```

### 直接測程式碼生成 API

```bash
curl -X POST http://127.0.0.1:8000/api/code/generate \
  -F "file=@sample_datasets/housing_sample.csv" \
  -F "target_column=price_usd" \
  -F "model_name=Ridge 迴歸" \
  -F "analysis_mode=regression" \
  -F "chart_types=model_comparison,feature_importance,predicted_vs_actual,residual_plot"
```

### 直接測合併資料程式碼生成 API

```bash
curl -X POST http://127.0.0.1:8000/api/code/generate-merged \
  -F "files=@sample_datasets/housing_sample.csv" \
  -F "files=@sample_datasets/stock_prices_sample.csv" \
  -F "target_column=price_usd" \
  -F "model_name=隨機森林" \
  -F "analysis_mode=auto" \
  -F "chart_types=auto"
```

### 直接測金融分析 API

```bash
curl -X POST http://127.0.0.1:8000/api/finance/analyze \
  -F "file=@sample_datasets/stock_prices_sample.csv"
```

### 直接測合併金融分析 API

```bash
curl -X POST http://127.0.0.1:8000/api/finance/analyze-merged \
  -F "files=@sample_datasets/stock_prices_sample.csv" \
  -F "files=@sample_datasets/stock_prices_sample.csv" \
  -F "date_column=date" \
  -F "price_column=close"
```

### 直接測 Multi-Agent API

```bash
curl -X POST http://127.0.0.1:8000/api/agents/analyze \
  -F "file=@sample_datasets/stock_prices_sample.csv" \
  -F "target_column=close" \
  -F "analysis_mode=regression" \
  -F "model_selection_mode=custom" \
  -F "selected_models=ridge,random_forest" \
  -F "automl_mode=off"
```

### 直接測 Word 報告 API

```bash
curl -X POST http://127.0.0.1:8000/api/reports/generate \
  -F "file=@sample_datasets/stock_prices_sample.csv" \
  -F "target_column=close" \
  -F "analysis_mode=regression" \
  -F "model_selection_mode=custom" \
  -F "selected_models=ridge,random_forest" \
  -F "automl_mode=off"
```

## 自動化驗證

後端：

```bash
cd backend
source .venv/bin/activate
pytest
```

前端：

```bash
cd frontend
npm run typecheck
npm run build
npm audit --audit-level=moderate
```

若在沙盒環境遇到 Turbopack `binding to a port` 權限錯誤，可改用 `npm run build -- --webpack` 驗證 production build。

## AI 智能判斷驗證

本專案目前的「AI 智能分析」包含本機機器學習判斷、AutoML 推薦、多代理工作流與可選 LLM 摘要。若未設定 `OPENAI_API_KEY`，系統會明確回傳 `local_rule_based`，不會假裝已呼叫外部 LLM。

2026-06-14 重新以後端自動化測試與 FastAPI TestClient 對真實 sample datasets 完成稽核：

- `housing_sample.csv`，target=`price_usd`：自動判斷為回歸，推薦並執行 `ridge`、`lasso`、`elastic_net`、`random_forest`、`gradient_boosting_regressor`、`xgboost_regressor`、`knn_regressor`。
- `housing_sample.csv`，target=`near_mrt`：自動判斷為分類，推薦並執行 `logistic_regression`、`decision_tree_classifier`、`random_forest_classifier`、`gradient_boosting_classifier`、`xgboost_classifier`、`knn_classifier`。
- `stock_prices_sample.csv`：金融分析產生 MA、報酬率、波動率、RSI、MACD、VaR 與時間序列預測摘要。
- 程式碼生成 API 回傳內容包含 `train_test_split` 與 `.fit(...)`，並同步產出 Python 與 Notebook 檔案。
- Multi-Agent API 回傳代理步驟：資料理解代理、模型分析代理、金融分析代理、視覺化代理、報告代理。

這代表目前模型不是固定四種硬跑，也不是前端假資料；結果會根據資料欄位、target 類型、列數、特徵數、缺失比例與使用者選項重新判斷。

## 一般人可讀與研究者深挖模式

本專案依據 `docs/strategy/2026-06-17-layperson-and-researcher-improvement-plan.md` 增加雙層分析體驗。核心原則是：同一份真實分析結果，同時提供「一般人看得懂的結論」與「研究者可追溯的細節」。

### 閱讀深度

工作區設定提供三種閱讀深度：

- `簡明`：優先顯示一句話結論、發生了什麼、風險與下一步。
- `標準`：加入支撐證據、圖表讀法與主要限制。
- `研究`：顯示技術定義、公式、方法、參數、假設、限制與可重現資產。

閱讀深度會存在瀏覽器本機，重新整理後仍會保留偏好。

### API 新增解釋欄位

資料、模型與金融分析結果會回傳一致的解釋欄位：

- `plain_summary`：一句話結論、發生什麼、為什麼重要、風險、下一步。
- `confidence`：可信度等級、原因與阻礙因素。
- `evidence`：系統做出判斷的支撐證據。
- `terms`：指標白話說明、技術定義、公式、判讀方式與限制。
- `research_details`：方法、假設、參數、限制與可重現資產。
- `chart_stories`：每張圖表的說明、關鍵發現、代表意義、不能證明什麼與建議行動。

金融分析另外回傳：

- `forecast_reliability`：時間序列基準情境估計的可信度、原因、建議行動與警告旗標。

### 指標字典

後端 `backend/app/services/metric_glossary.py` 維護第一批指標讀法，包含：

- 資料完整度、缺失值、平均數、中位數、標準差
- RMSE、MAE、R²、Accuracy、F1-score
- Feature importance、Residual
- Return、Volatility、Moving Average、RSI、MACD、VaR、Forecast

這些說明不只是 tooltip，而會直接出現在分析結果、模型頁、金融頁與報告內容中，讓使用者不需要先懂統計學也能理解數字代表什麼。

### 金融預測防護

金融頁不再把線性外推直接稱為確定預測，而是顯示為「基準情境估計」。若資料量不足、預測與最新值落差過大，或尚未完成回測，系統會降低可信度並顯示警告。所有金融分析都應視為資料理解輔助，不構成投資建議。

## 開發階段路線圖

### 第一階段：基礎專案

狀態：已完成。

### 第二階段：模型分析功能

狀態：已完成，並已加入多檔整批上傳、合併分析、建議目標欄位、分析模式、圖表選擇、自動推薦模型與手動多模型選擇。

### 第三階段：Colab 式圖表輸出

狀態：已完成目前需求版本。

- 已完成模型比較圖、特徵重要性、預測值與實際值圖、殘差圖。
- 圖片會實際儲存在 `generated_outputs/charts/`。
- 依使用者需求已移除熱力圖。
- 待加強：更多圖表排列與輸出套件整合。

### 第四階段：程式碼生成

狀態：已完成。

- 已完成 `generated_code.py`。
- 已完成 `notebook.ipynb`。
- 前端已提供頁內預覽與下載功能。
- 待加強：第六階段會把程式碼、圖表、資料與報告整合進 ZIP 輸出套件。

### 第五階段：金融分析模式

狀態：已完成主要可執行版本。

- 已完成日期與價格欄位偵測。
- 已完成移動平均、報酬率、波動率、RSI、MACD。
- 已完成金融分析圖表與摘要。
- 已完成金融指標 CSV 輸出。

### 第六階段：完整輸出套件

依使用者最新要求，ZIP 本階段不實作。

- 已完成分析報告 Word 輸出。
- 已完成程式碼與 Notebook 輸出。
- 已完成清理後資料集輸出。
- 已完成模型結果試算表輸出。
- 已完成圖表資料夾輸出。
- 已完成訓練模型資料夾輸出。
- 尚未完成一鍵下載 ZIP。

### 第七階段：整理與驗收

狀態：已完成本次全面檢查，ZIP 套件依使用者要求仍不實作。

- 已完成後端完整測試。
- 已完成前端 TypeScript 與 production build 檢查。
- 已完成多檔上傳、合併摘要、模型分析、金融分析、Multi-Agent、Word 報告的真實 API 稽核。
- 已確認前端頁面結果來自後端 API，非靜態假資料。
- 已修正 `manual` 模型選擇模式相容與 Agent 名稱繁中化。
- 已修正 macOS XGBoost / LightGBM OpenMP 載入問題，並加入後端自動修復 fallback。

## 已知限制

- 一鍵 ZIP 套件依使用者最新要求尚未實作。
- 分類問題會先將目標欄位轉成數值標籤；目前已額外回傳 Accuracy 與 F1，仍保留 R2、RMSE、MAE 以符合原驗收欄位。
- 目前報告輸出為 Word `.docx`；PDF 尚未實作。
- LLM 摘要需要設定 `OPENAI_API_KEY`，未設定時會使用本機規則摘要並在 API 回傳中註明。
- `generated_outputs/` 不再由公開靜態路徑直接提供下載，後端會回傳短效 capability URL。這仍不等同使用者登入、tenant authorization、租戶隔離與完整清理期限；不得用於公開匿名上傳或敏感資料。
- 目前沒有 API rate limiting；正式公開服務應在反向代理或應用層加入使用者與 IP 配額。
- pandas、scikit-learn 與繪圖工作目前仍在 Web 服務程序中執行；高併發部署應移至工作佇列與獨立 worker。
- 前端目前使用 TypeScript 型別描述 API，尚未加入 Zod 等執行期 response schema 驗證。
- `npm audit` 在 2026-06-14 因執行環境無法連線 npm registry 而未完成，不能據此宣稱依賴沒有已知弱點。
- 2026-06-14 已完成 `npm run typecheck`、`npm run build -- --webpack`、`git diff --check` 與 23 項後端測試，包含真實 `/api/jobs/models` 上傳、輪詢與輸出整合測試。另以 production server 完成 1280px、768px、390px Browser 驗收，首頁、工作區、資料頁與英文頁均無水平溢位或 console 錯誤。
- Excel 上傳依賴 `openpyxl` / `xlrd`，請依照 `backend/requirements.txt` 安裝。
