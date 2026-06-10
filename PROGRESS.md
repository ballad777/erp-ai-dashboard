# 智能金融資料分析開發進度

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
