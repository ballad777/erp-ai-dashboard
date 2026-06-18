# 封閉測試部署指南

本專案需要同時執行 Next.js 前端與 FastAPI / Python 後端，因此不適合只用 GitHub Pages。

> 目前架構不適合公開匿名上傳或敏感資料。部署用途限私人展示、封閉測試與非敏感樣本資料；正式多租戶 SaaS 仍需完成真正登入、PostgreSQL repository、Redis Worker、retention scheduler 與完整權限稽核。

GitHub Pages 只能部署靜態網頁，無法執行：

- FastAPI
- pandas / scikit-learn / XGBoost / LightGBM
- CSV / Excel 檔案上傳
- 模型訓練
- 圖表、報告、程式碼與模型檔輸出

封閉測試部署方式：GitHub + Render Docker Web Service。

## 部署架構

```text
使用者瀏覽器
  ↓
Render 公開網址
  ↓
Next.js 前端
  ↓ 透過 /api/* 與 /api/artifacts/{token} 代理
FastAPI 後端
  ↓
Python 分析、模型訓練、圖表與報告輸出
```

前端與後端會在同一個 Docker 容器內執行。Render 對外只開一個網址，後端由 Next.js 代理轉發，因此不需要額外處理跨網域問題。

## 已提供的部署檔案

- `Dockerfile`：建立封閉測試容器，包含前端 build、後端 Python 環境與模型套件。
- `.dockerignore`：排除本機暫存、venv、node_modules 與大量 generated output。
- `scripts/start-production.sh`：啟動 FastAPI，再啟動 Next.js。
- `render.yaml`：Render Blueprint 設定。

## GitHub 上傳步驟

1. 在 GitHub 建立新的 private repository；若因方案限制必須公開原始碼，請先確認沒有金鑰、敏感資料或測試產物。
2. 將本機專案推上 GitHub：

```bash
git init
git add .
git commit -m "Initial smart finance analysis platform"
git branch -M main
git remote add origin https://github.com/YOUR_ACCOUNT/YOUR_REPO.git
git push -u origin main
```

3. 到 Render Dashboard。
4. 選擇 Blueprints。
5. 連接剛剛的 GitHub repository。
6. Render 會讀取根目錄的 `render.yaml`。
7. 建立 `smart-finance-analysis` web service。
8. 部署完成後，Render 會給一個固定網址，例如：

```text
https://smart-finance-analysis.onrender.com
```

## Render 設定

目前 `render.yaml` 使用 free plan，僅供私人展示與封閉測試。

注意：

- Free plan 可能會有冷啟動。
- 模型分析較耗資源，封閉測試人數或資料量增加時，可能需要升級到 Starter 或更高方案。
- Free plan 的輸出檔案是暫存型；服務重啟後，`generated_outputs/` 內的新圖表與報告可能消失。
- 產物下載使用短效 capability URL；若未設定穩定的 `ARTIFACT_SIGNING_SECRET`，服務重啟後舊 token 會失效。
- 目前 API 有基礎 rate limit middleware，預設每 IP + path 每分鐘 180 次；這不是正式 WAF 或濫用治理。
- 本機預設使用 `.local/finai.sqlite3` 保存 demo project、dataset、run、artifact、job 與 audit log。Render free plan 的檔案系統可能重啟遺失，不可視為正式資料庫。
- `backend/database/postgres_schema.sql` 已提供正式 PostgreSQL schema，但目前執行 repository 仍是 SQLite fallback；公開 SaaS 前必須接上 PostgreSQL driver/repository。
- 固定網址不代表服務已具備公開匿名上傳所需的身份授權、租戶隔離、資料保留政策或完整濫用防護。

## 環境變數

封閉測試的基本啟動不需要額外環境變數。

建議設定穩定的 artifact token secret：

```bash
ARTIFACT_SIGNING_SECRET=請換成至少 32 字元的隨機字串
```

可調整 API rate limit：

```bash
API_RATE_LIMIT_PER_MINUTE=180
```

若要啟用外部 LLM 摘要，可在 Render 加入：

```bash
OPENAI_API_KEY=你的金鑰
```

未設定時，系統會回傳 `local_rule_based`，使用本機規則摘要，不會假裝已呼叫外部 LLM。

## 部署後驗收

封閉測試部署完成後，請測試：

```text
https://你的-render-url/health
```

應回傳：

```json
{"status":"ok","service":"智能金融資料分析 API"}
```

接著在網頁上測試：

1. 打開首頁。
2. 進入「上傳資料」。
3. 上傳 `sample_datasets/housing_sample.csv`。
4. 確認資料摘要來自後端。
5. 選擇 `price_usd` 執行自動模型分析。
6. 確認模型比較表、圖表與程式碼預覽都能產生。
7. 用手機瀏覽器打開同一個公開網址，確認首頁與上傳頁排版正常。
