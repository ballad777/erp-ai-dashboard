# 智能金融資料分析

智能金融資料分析是一個智慧金融與資料分析平台。使用者可以上傳 CSV / Excel 資料集，逐步完成資料摘要、多模型分析、圖表輸出、程式碼生成、金融分析與完整輸出套件。

目前狀態：除一鍵 ZIP 套件外，計畫書主要功能已補齊可執行版本。前端可整批上傳多個資料集、顯示後端真實摘要、自動建立合併資料集摘要、選擇目標欄位、選擇分析模式、手動或自動選擇模型與圖表，並產出真實 PNG 圖表、可下載程式碼檔案、Notebook、trained model、模型結果 Excel、Word 分析報告與金融指標 CSV。

## 技術架構

- 前端：Next.js、React、Tailwind CSS
- 後端：FastAPI
- 資料分析：pandas、numpy
- 模型訓練：scikit-learn、XGBoost、LightGBM
- 圖表輸出：matplotlib
- 報告輸出：python-docx
- 輸出資料夾：`generated_outputs/`

## 專案結構

```text
.
├── backend/
│   ├── app/
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
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── assets/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
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
└── PROGRESS.md
```

## 安裝與啟動

建議版本：

- Python 3.11 以上
- Node.js 20.9.0 以上
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

前端預設呼叫同網域 API：

```text
/api/*
```

`frontend/next.config.js` 會把 `/api/*`、`/generated_outputs/*` 與 `/health` 代理到後端，預設後端位址為：

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

### 正式雲端部署

若要讓使用者在你電腦關機後仍可使用，不能只用 GitHub Pages，因為本專案需要執行 FastAPI、Python 模型、檔案上傳與輸出檔案。

目前已提供 GitHub + Render 的 Docker 部署設定：

- `Dockerfile`
- `.dockerignore`
- `scripts/start-production.sh`
- `render.yaml`
- `DEPLOYMENT.md`

將專案推到 GitHub 後，可在 Render 使用 Blueprint 讀取 `render.yaml`，建立單一 Docker Web Service。部署完成後，Render 會提供固定公開網址，例如：

```text
https://smart-finance-analysis.onrender.com
```

完整步驟請看：

```text
DEPLOYMENT.md
```

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
- 前端會在頁面內直接顯示本次生成的 Python 程式碼，並可切換 Notebook 預覽；下載功能仍保留。

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
- 報告內容包含資料摘要、Agent 執行紀錄、模型比較、金融分析與圖表。
- ZIP 套件依使用者要求本階段不實作。

### 介面風格

- 網站已調整為淺色科技新創風格。
- 保留原有主色系：`ink`、`brand`、`navy`、`amber`。
- 使用玻璃感面板、藍綠漸層光帶、清晰字體與 hover glow 按鈕。
- 新增 Apple / iOS 風格的產品層次：
  - 全站 Command Center 快捷指令。
  - 真實後端健康狀態顯示。
  - 上傳工作台狀態列與準備度。
  - 更細緻的玻璃面板、焦點狀態、hover 狀態與手機排版。

### 快捷指令

目前支援：

- `⌘ / Ctrl + K`：開啟快捷指令。
- `⌘ / Ctrl + U`：在上傳頁開啟檔案選擇；其他頁面前往上傳工作台。
- `⌘ / Ctrl + Enter`：在上傳頁讀取全部檔案。
- `?`：開啟快捷指令。
- `Esc`：關閉快捷指令。

快捷指令只會觸發既有真實功能，例如前往上傳頁、加入檔案、讀取全部檔案與清空佇列，不會顯示無法執行的假功能。

## 測試流程

### 網頁測試

1. 啟動後端與前端。
2. 打開 `http://localhost:3000`。
3. 點選「上傳資料集」。
4. 加入 `sample_datasets/housing_sample.csv` 與 `sample_datasets/stock_prices_sample.csv`。
5. 點選「讀取全部檔案」。
6. 確認頁面顯示兩個檔案的獨立摘要，以及「智慧合併分析」區塊。
7. 在「合併資料模型分析」選擇建議目標欄位或自行選欄位。
8. 選擇「自動選擇」分析模式與「自動選最適合圖表」。
9. 點選「執行模型分析」。
10. 確認頁面顯示模型比較表與多張後端產生的圖表。
11. 在模型策略中切換「自動推薦模型」或「手動選擇模型」，確認模型數量會依選擇改變。
12. 在 `stock_prices_sample.csv` 或合併資料區塊點選「執行金融分析」。
13. 確認頁面顯示金融摘要、MA / 報酬率 / 波動率 / RSI / MACD / VaR / 時間序列預測圖與指標 CSV 下載。
14. 在「AI 協作分析與報告」執行 AI 分析。
15. 點選「生成 Word 報告」，下載 `analysis_report.docx`。
16. 在「AI 程式碼生成」選擇主要模型。
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

2026-06-10 以 FastAPI TestClient 對真實 sample datasets 做過一次稽核：

- `housing_sample.csv`，target=`price_usd`：自動判斷為回歸，推薦並執行 `ridge`、`lasso`、`elastic_net`、`random_forest`、`gradient_boosting_regressor`、`xgboost_regressor`、`knn_regressor`。
- `housing_sample.csv`，target=`near_mrt`：自動判斷為分類，推薦並執行 `logistic_regression`、`decision_tree_classifier`、`random_forest_classifier`、`gradient_boosting_classifier`、`xgboost_classifier`、`knn_classifier`。
- `stock_prices_sample.csv`：金融分析產生 MA、報酬率、波動率、RSI、MACD、VaR 與時間序列預測摘要。
- 程式碼生成 API 回傳內容包含 `train_test_split` 與 `.fit(...)`，並同步產出 Python 與 Notebook 檔案。
- Multi-Agent API 回傳代理步驟：資料理解代理、模型分析代理、金融分析代理、視覺化代理、報告代理。

這代表目前模型不是固定四種硬跑，也不是前端假資料；結果會根據資料欄位、target 類型、列數、特徵數、缺失比例與使用者選項重新判斷。

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
- Browser 工具在本 session 對 `localhost:3000` 的開啟動作被安全政策拒絕，因此本次前端驗證以 `npm run typecheck`、`npm run build -- --webpack`、本機健康檢查與後端 TestClient 測試為主。
- Excel 上傳依賴 `openpyxl` / `xlrd`，請依照 `backend/requirements.txt` 安裝。
