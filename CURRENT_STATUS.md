# 智能金融資料分析目前狀態

最後更新：2026-06-17

## 可執行狀態

- 前端：Next.js / React / TypeScript / Tailwind CSS / Motion。
- 後端：FastAPI / pandas / numpy / scikit-learn / XGBoost / LightGBM / matplotlib。
- 本機資料庫：預設自動建立 `.local/finai.sqlite3`。
- 正式資料庫 schema：`backend/database/postgres_schema.sql` 已定義 PostgreSQL 版 User、Project、Dataset、AnalysisRun、Artifact、ModelResult、Job、AuditLog。
- 上傳格式：CSV、XLSX、XLS、JSON。
- 輸出：PNG 圖表、Excel 模型結果、CSV 清理資料、Python、Notebook、Word 報告、trained model。

## 本輪已補齊的計畫缺口

- 新增 Dataset / AnalysisRun / Artifact / ModelResult / Job / AuditLog 的持久化資料模型。
- 每次主要 API 執行都會建立 `run_id`、`dataset_id` 與 `run_manifest`。
- Run Manifest 會記錄輸入檔名、大小、SHA-256、參數、模型結果與 artifact 清單。
- Artifact token 在 run context 內會綁定 `artifact_id`、`run_id`、`project_id` 與 `user_id`。
- Job 狀態會寫入資料庫；記憶體仍保留作為執行中取消控制。
- 新增 demo session endpoint：`GET /api/auth/session`。
- 新增 API rate limit middleware，預設每 IP + path 每分鐘 180 次。
- 資料摘要新增品質報告：缺失值、重複列、常數欄位、高基數欄位、ID-like 欄位、IQR 異常值、類別不平衡、日期頻率、疑似 leakage 欄位。
- 多檔分析新增合併策略建議、Join key 候選與 schema conflict 檢查。
- 模型分析新增 baseline model，分類任務可行時使用 stratified split。
- 類別特徵會在 OneHotEncoder 前明確轉成字串，可處理同欄位混合數字與文字的資料。

## 仍未完成，不可宣稱已完成

- 尚未接入正式登入、OAuth、密碼驗證或多租戶權限系統。
- 尚未接入真正 PostgreSQL repository/driver；目前正式 PostgreSQL 僅提供 schema，執行層預設 SQLite。
- 尚未接入 Redis / Celery / RQ / Arq worker；目前仍由 API process 內的 thread 執行長任務。
- 尚未提供 SSE；前端仍使用 polling 查 job 狀態。
- 尚未完成 artifact revoke UI、retention scheduler 與完整 audit 查詢介面。
- 尚未完成 Prophet / ARIMA / ETS、正式 backtesting、預測區間與時間序列驗證。
- 尚未完成完整互動式 Plotly dashboard / chart builder。
- 尚未完成 PDF 報告與一鍵 ZIP 套件。

## 啟動

後端：

```bash
cd backend
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

前端 production preview：

```bash
cd frontend
npm run build
npm run start -- --hostname 127.0.0.1 --port 3010
```

測試網址：

```text
http://localhost:3010
```

## 驗證命令

後端：

```bash
cd backend
.venv/bin/pytest -q
```

前端：

```bash
cd frontend
npm run test:run
npm run typecheck
npm run build -- --webpack
```
