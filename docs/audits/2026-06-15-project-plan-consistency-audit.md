# 專案與產品計畫一致性完整稽核報告

日期：2026-06-15  
專案：智能金融資料分析  
分支：`codex/phase-a-product-interface`  
稽核方式：程式碼、文件、測試、production build、桌面與行動版 Browser 驗證  
變更原則：本次只新增稽核報告，不修改產品程式碼

## 1. 結論

目前專案與計畫是「介面方向高度一致，產品基礎明顯不一致」。

- Phase A 產品介面：高度一致，主要元件、配色、雙語、RWD、鍵盤與 reduced motion 已落地。
- Spreadsheet-first 產品入口：大致一致，CSV／Excel、多檔、模型、金融與報告已有真實功能。
- 可驗證 Analysis Run：尚未落地，沒有 Project、Dataset Version、Run Manifest 或 artifact index。
- 正式 Beta P0：大部分未完成，尤其是持久化、權限、私人產物、Worker、資料品質與可信評估。
- 公開部署：目前不符合公開多人或敏感資料使用條件。

因此，現在可定位為：

> 可執行、介面成熟的單人／封閉測試原型，不是可公開處理敏感資料的正式 SaaS。

## 2. 稽核基準

本報告以以下文件作為目前計畫基準：

1. `docs/strategy/2026-06-15-complete-product-recommendation-report.md`
2. `docs/superpowers/specs/2026-06-15-universal-ai-analytics-platform-design.md`
3. `docs/superpowers/plans/2026-06-15-universal-analytics-master-roadmap.md`
4. `docs/superpowers/plans/2026-06-15-phase-a-product-interface.md`

核心策略要求包括：

- 先服務繁中、spreadsheet-first 的中小企業分析團隊。
- 金融是旗艦模板，不是唯一產品邊界。
- 每次分析成為不可變、可重跑、可比較的 Analysis Run。
- 正式 Beta 前完成 PostgreSQL、Redis Worker、私人產物、資料品質與可信評估。
- 完成 Analysis Plan、Plotly、PDF／HTML、分享和連線器後再擴張進階模型。

## 3. 整體一致性評級

| 範圍 | 評級 | 判斷 |
|---|---|---|
| 技術棧 | 高 | Next.js、React、TypeScript、Tailwind、shadcn primitives、Motion、FastAPI 均符合 |
| Phase A 介面 | 高 | Data Lens、十套配色、工作區、詳情面板、RWD 與測試已實作 |
| Spreadsheet-first 入口 | 中高 | CSV／Excel 與多檔流程完整，但缺少 JSON、工作表選擇與範例 Project |
| 產品定位 | 中 | 首頁已稱通用平台，但品牌、metadata、報告仍強烈綁定金融 |
| 可驗證 Analysis Run | 低 | 沒有持久化 domain model、Manifest、版本與 artifact index |
| 資料品質 | 低 | 目前主要是型別、缺失值與數值摘要 |
| 可信模型評估 | 低 | 單次隨機 75／25 切分，缺少完整 CV、時間順序與穩定性 |
| 背景工作架構 | 低 | 單程序記憶體 job，沒有 Redis、Worker、retry 或重啟復原 |
| 報告與視覺化 | 中低 | DOCX、PNG、Python、Notebook 已有；Plotly、PDF、HTML、分享未完成 |
| 安全與公開 Beta | 極低 | 無帳號、owner、tenant isolation、artifact authorization、rate limit |
| 測試與建置 | 中高 | 現有測試、型別與 build 全部通過，但缺少安全、恢復與 E2E 覆蓋 |
| 文件與交付紀律 | 低 | Phase A checkbox 未更新，大量實作未提交，文件狀態互相矛盾 |

## 4. 最高優先問題

### C1. 產物是未授權公開靜態檔案

嚴重度：Critical  
一致性：不一致

證據：

- `backend/app/main.py:723-727` 直接將整個 `generated_outputs/` 掛成 StaticFiles。
- `frontend/next.config.js:13-16` 將公開網址直接代理到該靜態目錄。
- 模型、清理後 CSV、圖表、程式碼與報告都回傳可直接存取的 URL。
- 沒有使用者、Project ownership、授權檢查、signed URL 或保存期限。

影響：

- 只要取得或猜到 URL，就能下載其他工作產物。
- 清理後資料集可能仍包含原始敏感欄位。
- UUID 檔名只降低猜測機率，不是授權機制。
- 與計畫要求的 private artifact endpoint 完全不一致。

建議：

1. 正式公開前移除 StaticFiles 直出。
2. 建立 Artifact metadata 與受保護下載 endpoint。
3. 每次下載驗證 user、project、run 與 artifact ownership。
4. 加入刪除、過期和 retention job。

### C2. 部署文件把不安全原型描述為正式部署

嚴重度：Critical  
一致性：不一致

證據：

- `DEPLOYMENT.md:1` 名稱是「正式部署指南」。
- `DEPLOYMENT.md:13` 建議以 Render 作為正式部署方式。
- `render.yaml:1-16` 只有一個 free web service，沒有資料庫、Redis、私有儲存或 worker。
- `DEPLOYMENT.md:71` 已承認服務重啟後產物可能消失。
- 策略報告 `:740-760` 明確要求未有 auth、tenant isolation、artifact authorization 前不得公開處理敏感資料。

影響：

- 使用者容易把可公開展示誤認為可安全上線。
- job、結果和產物會因重啟遺失。
- 多人同時訓練模型會競爭同一 web process 的 CPU 與記憶體。

建議：

- 在安全基礎完成前改名為「展示環境部署」或「封閉測試部署」。
- 頁面與文件明確標示不可上傳敏感資料。
- 正式架構改為 Web、API、Worker、PostgreSQL、Redis、Object Storage。

### C3. 沒有 Project、Dataset Version、Analysis Run 與 Run Manifest

嚴重度：Critical  
一致性：核心不一致

證據：

- 策略要求的生命週期是 Project → Dataset → Dataset Version → Analysis Plan → Analysis Run。
- 後端只有 API、schema 與 service module，沒有 database model、repository、migration 或 artifact index。
- 前端只把目前工作區 snapshot 存在 IndexedDB：`frontend/src/lib/workspace-storage.ts:4-17`。
- job 結果只存在記憶體與本機檔案。

缺少的關鍵資料：

- dataset hash 和版本。
- plan version。
- engine、package 和 model version。
- split、seed、preprocessing 和參數。
- warnings、failure、artifact index。
- immutable run identity。

影響：

- 無法可靠重跑、比較、恢復、稽核、分享、收費或跨裝置使用。
- 首頁「結果可追溯」目前只有檔案 URL，不是計畫定義的可追溯性。

建議：

- 下一個主要工程工作應直接實作 Phase B domain schema 與 Run Manifest，不再新增 UI 主題或模型。

### C4. Job 是單程序記憶體執行，不能支援正式工作負載

嚴重度：Critical  
一致性：不一致

證據：

- `backend/app/services/analysis_jobs.py:37-39` 使用全域 dict，TTL 為四小時。
- `analysis_jobs.py:56` 使用 `asyncio.create_task(asyncio.to_thread(...))`。
- 沒有 Redis、durable queue、concurrency limit、retry、timeout、lease 或 restart recovery。
- `scripts/start-production.sh:17-20` 在同一容器啟動單一 FastAPI process。
- 前端每 450ms polling：`frontend/src/lib/api.ts:623-650`，沒有 SSE。

影響：

- API 重啟後全部 job 狀態消失。
- 多實例部署時不同實例看不到彼此 job。
- 大量同時請求可建立無上限 thread 工作。
- 取消是 cooperative，長步驟無法立即中止。

建議：

- PostgreSQL 保存 job/run/event。
- Redis queue 與獨立 worker 執行分析。
- 設定 queue concurrency、timeout、retry 與 interrupted recovery。
- SSE 傳進度，polling 只作 fallback。

## 5. 高優先資料與模型問題

### H1. 多檔合併會自動垂直串接，沒有使用者確認

嚴重度：High  
一致性：不一致

`backend/app/services/dataset_analyzer.py:136-189` 對所有成功讀取的 DataFrame 執行 `pd.concat`，即使沒有共同欄位也會以聯集合併。

優點：

- 同 schema 的月報、分店報表和批次資料可快速 append。
- 會保留來源檔名與來源列號。

缺點：

- 不同粒度、不同實體或應該 join 的檔案會被錯誤堆疊。
- 「沒有共同欄位」仍繼續分析，可能產生大量缺失值與錯誤模型。
- 使用者沒有預覽、join key、型別衝突或取消選項。

應改為：

- 預設先顯示 compatibility preview。
- 明確選擇 Append、Join 或保持分離。
- 無共同 schema 時禁止自動 append。

### H2. 模型評估不足以支持「可信分析」

嚴重度：High  
一致性：不一致

證據：

- `model_runner.py:307-312` 固定使用一次 75／25 random split。
- 分類沒有 `stratify`。
- 時間欄位不會觸發 time-order split。
- Quick AutoML 只在 train set 做 2–3 fold GridSearchCV，但最後仍用同一 test set比較所有模型。
- 選出最佳模型後直接回報該 test set 表現，沒有獨立 final holdout。
- 分類仍計算 R2、RMSE、MAE：`model_runner.py:366-379`。
- 最少五筆資料就允許訓練：`model_runner.py:304-305`。

正面部分：

- preprocessing 在 sklearn Pipeline 中，會跟著 train／CV fit，基本轉換流程比先全資料 fit 安全。
- random seed 固定，可重現同一次切分。

缺口：

- repeated／nested CV。
- class imbalance、ROC-AUC、PR-AUC、confusion matrix、calibration。
- 時間順序、group split、leakage detection。
- 穩定性區間與 baseline。
- 小資料警告和可信度 gate。

### H3. 「資料品質」目前實際上只是缺失率

嚴重度：High  
一致性：部分不一致

後端 profile 只回傳：

- row／column。
- column names 和 pandas dtype。
- missing count。
- numeric describe。
- target 欄位 heuristic。

參考 `backend/app/services/dataset_analyzer.py:233-262`。

前端的品質分數則只用缺失儲存格比例計算：`frontend/src/components/WorkspaceDashboard.tsx:293-302`。

缺少：

- duplicate。
- constant／near constant。
- ID／high cardinality。
- outlier。
- imbalance。
- date frequency／order。
- type conflict。
- leakage。
- 分數組成與可修正動作。

因此首頁 `MarketingHome.tsx:115-116` 的「資料品質」和工作區品質分數比後端能力更廣，應先收斂文案或補齊 profiler。

### H4. 金融預測是未驗證的線性外推

嚴重度：High  
一致性：不一致

`backend/app/services/financial_analyzer.py:505-534` 只以資料索引做 LinearRegression，向後外推五點。

缺少：

- naive baseline 比較。
- backtesting。
- time-series cross-validation。
- MAE／RMSE／MAPE。
- 預測區間。
- seasonality 和頻率驗證。
- ARIMA／SARIMA／Prophet。

這個結果可以作示意趨勢，但不應被描述為具可信度的時間序列預測。金融頁已有「不構成投資建議」，這是優點，但仍應在預測旁直接標示方法與未驗證限制。

### H5. AI Agent 是固定流程，不是 Analysis Plan

嚴重度：High  
一致性：不一致

`agent_orchestrator.py:114-242` 固定執行資料摘要、模型、金融、視覺化和報告摘要。

目前 LLM：

- 只在最後改寫 deterministic summary。
- 沒有把自然語言轉成受約束的 Analysis Plan。
- 沒有 plan validation、tool permission、verification 或可編輯步驟。

優點：

- 沒有 API key 時明確回傳 `local_rule_based`，不假裝 LLM 已執行。
- 原始資料不會直接整批送給 LLM。

缺點：

- 「AI Agent」名稱容易讓使用者期待自主規劃與驗證。
- 固定流水線仍會執行不必要的金融步驟再 skip。

### H6. 產出的程式碼不等於實際 Run 的完整重現

嚴重度：High  
一致性：不一致

程式碼生成是另一支獨立流程：

- 使用者再次選 model name。
- 不接受實際 run 的 best params。
- 不保存原 run split indices、dataset hash 或 environment。
- 生成程式碼重新建立並訓練多個預設模型：`code_generator.py:521-567`。

因此目前是「可執行範例程式碼」，不是「該次 Analysis Run 的完整重現程式碼」。

### H7. 正式報告與分享能力尚未形成

嚴重度：High  
一致性：P1 未完成

目前已有：

- DOCX。
- PNG。
- Python。
- Notebook。
- CSV／XLSX。
- joblib。

尚缺：

- PDF。
- HTML。
- Plotly 互動圖表。
- chart specification。
- run compare。
- 唯讀分享頁。
- 分享期限和下載權限。

圖表頁目前是既有結果的集中空間，不是計畫中的自動／手動 Plotly builder。

### H8. 公開 Beta 安全最低要求幾乎未完成

嚴重度：High  
一致性：不一致

尚缺：

- 使用者驗證。
- Project ownership。
- tenant isolation。
- dataset／run／artifact authorization。
- malware scan。
- spreadsheet formula injection 防護。
- retention／deletion。
- rate limit／quota。
- secrets manager。
- audit log 和 log redaction policy。
- Privacy Policy／Terms。

目前已有的安全優點：

- 上傳副檔名、單檔、數量與總容量限制。
- API generic 500，不將 stack trace 回傳前端。
- CORS allowlist。
- `nosniff`、`DENY`、Referrer 和 Permissions Policy。
- API／artifact `Cache-Control: no-store`。

這些是必要 hardening，但不能替代身份與授權。

## 6. 中優先產品與工程偏差

### M1. 品牌仍停在金融，與通用 spreadsheet-first 定位不完全一致

證據：

- metadata 和 application name 仍是「智能金融資料分析」：`frontend/src/app/layout.tsx:35-42`。
- FastAPI title／description 仍是金融平台：`backend/app/main.py:77-80`。
- sidebar、footer 和 Word 報告仍使用金融品牌。
- 首頁 eyebrow 已改為「通用型 AI 資料分析平台」。

結果是品牌和產品範圍同時傳達兩個訊息。

建議：

- 決定母品牌為通用工作區，金融作 template。
- 或保留現名，但不要同時宣稱完整通用平台。

### M2. 首頁證據型定位尚未同步

策略建議主標是：

> 看懂資料。留下每一步證據。

目前是：

> 看懂資料。找到下一步。

目前文字符合較早的 Phase A 規格，但不符合最新完整策略報告。由於 Run Manifest 尚未完成，現在其實也不適合先使用「留下每一步證據」。正確順序應是先完成可追溯 run，再更新主標。

### M3. 同一畫面有重複主操作

桌面 `/app` 空狀態同時有：

- topbar「加入資料」。
- next action「加入第一份資料」。
- empty state「前往資料頁」。

`/app/data` 同時有：

- PageHeader「加入檔案」。
- dropzone「選擇檔案」。

兩者功能相同，會削弱主要下一步的層級。保留一個主要 CTA，另一個改為文字提示或移除。

### M4. 前端工作區是本機快照，不是產品持久化

優點：

- 重新整理和切換 route 後可保留目前工作。
- IndexedDB 不可用時仍可用記憶體模式。

缺點：

- 沒有 server-side source of truth。
- 不能跨裝置、跨瀏覽器或多人協作。
- browser storage 清除後資料與分析狀態消失。
- 大型 File、結果和 panel state 都放在同一 snapshot/context，與目標架構避免大型 context 的原則不一致。

### M5. API response 只靠 TypeScript assertion

`frontend/src/lib/api.ts:203-229` 將 JSON 直接 cast 為泛型 T，沒有 Zod 或其他 runtime schema。

後端 response 漂移時，錯誤會延後到元件存取欄位時才發生。正式產品應由 OpenAPI 產生 client 或加入 runtime validation。

### M6. Docker Node 版本和專案要求不一致

- `frontend/package.json:5-7` 要求 Node `>=22.13.0`。
- `Dockerfile:1` 和 `:15` 使用 Node 20。

目前本機 build 通過，不代表 Docker image 與 declared engine 一致。應統一使用 Node 22，或把 package engine 改成實際支援範圍並驗證。

### M7. 路線圖引用的 Phase B–G plan 檔案不存在

Master Roadmap 列出：

- `2026-06-15-phase-b-job-infrastructure.md`
- `2026-06-15-phase-c-dataset-understanding.md`
- Phase D–G 對應檔案

目前目錄只有 master roadmap 和 Phase A plan。這代表有 phase 定義，但沒有可逐步執行的後續 implementation plan。

### M8. Phase A 文件追蹤已失真

- Phase A plan 的所有 checkbox 仍是未完成。
- `PROGRESS.md` 宣稱 Phase A 完成。
- Git 只有 test harness 和 theme domain 兩個 Phase A commit。
- 目前有 61 個 status entry、62 個 untracked file，diff 約 7,999 insertions／1,615 deletions。
- `PROGRESS.md` 記錄 30 個 frontend test，但本次實際是 36 個。

影響：

- 無法從 commit history 判斷哪些 task 已驗證。
- 大量功能與文件混在同一工作樹，review 和 rollback 風險高。

### M9. 測試通過，但缺少正式產品風險測試

本次通過：

- Backend：23 tests。
- Frontend：36 tests。
- TypeScript typecheck。
- Next.js production build。
- Desktop／mobile Browser render。
- Browser console 無 error／warn。

主要缺口：

- 沒有 auth／tenant／artifact access 測試。
- 沒有 restart recovery、multi-instance、retry、timeout、queue saturation。
- 沒有 merge preview 和錯誤 join 測試。
- 沒有 leakage、time split、imbalanced classification、stability benchmark。
- 沒有完整 browser file upload E2E。
- 沒有 production Docker build 的最新完成證據。
- Python 3.14 仍有 FastAPI／Starlette deprecation warnings。

### M10. 輸入格式和連線器落後於計畫

已有：

- CSV。
- XLSX／XLS。
- Big5／UTF-8 fallback。
- 多檔。

尚缺：

- JSON／NDJSON。
- Excel multi-sheet selection。
- nested JSON flattening。
- Google Sheets。
- PostgreSQL。
- sample Project。

## 7. 完整計畫差距矩陣

### 7.1 產品與介面

| 計畫項目 | 現況 | 狀態 |
|---|---|---|
| Spreadsheet-first 繁中入口 | CSV／Excel、繁中預設 | 一致 |
| 金融作旗艦模板 | 品牌與報告仍以金融為母體 | 部分 |
| Data Lens Hero | 已實作 | 一致 |
| 固定兩行 Hero | 已實作 | 一致 |
| 十套語意主題 | 已實作並測試 | 一致 |
| Desktop icon rail | 已實作 | 一致 |
| Mobile bottom navigation | 已實作 | 一致 |
| Progressive result hierarchy | 已實作 | 一致 |
| Contextual detail panel | 已實作 | 一致 |
| 雙語 | 主要介面已完成，後端產物部分仍繁中 | 部分 |
| Keyboard／reduced motion | 元件和 CSS 已支援 | 一致 |
| 一個清楚主操作 | 多處重複 CTA | 不一致 |
| 證據型主標 | 尚未使用，且底層能力也未完成 | 未完成 |

### 7.2 核心 domain 與工作基礎

| 計畫項目 | 現況 | 狀態 |
|---|---|---|
| Project | 無 | 未完成 |
| Dataset entity | 只有前端 snapshot 與即時 payload | 未完成 |
| Dataset Version | 無 hash／version | 未完成 |
| Analysis Plan | 無可編輯 plan | 未完成 |
| Analysis Run | job 不等於 immutable run | 未完成 |
| Run Manifest | 無 | 未完成 |
| Artifact index | 只有檔案 URL | 未完成 |
| Run compare | 無 | 未完成 |
| PostgreSQL | 無 | 未完成 |
| Migration | 無 | 未完成 |
| Redis queue | 無 | 未完成 |
| Worker | 無獨立 worker | 未完成 |
| SSE | 前端 450ms polling | 未完成 |
| Retry／recovery | 無 | 未完成 |
| Cooperative cancel | 已有 | 部分一致 |
| 真實 progress | 已有 backend stage | 一致 |

### 7.3 資料理解

| 計畫項目 | 現況 | 狀態 |
|---|---|---|
| CSV／Excel | 已有 | 一致 |
| JSON／NDJSON | 無 | 未完成 |
| Multi-sheet | 無 | 未完成 |
| Missing profile | 已有 | 一致 |
| Numeric summary | 已有 | 一致 |
| Duplicate | 無 | 未完成 |
| Constant／near constant | 無 | 未完成 |
| ID detection | 只有 target 推薦時略過常見 ID 名稱 | 部分 |
| High cardinality | 無 | 未完成 |
| Outlier | 無 | 未完成 |
| Imbalance | 無 | 未完成 |
| Date frequency／order | 無通用 profile | 未完成 |
| Leakage warning | 無 | 未完成 |
| Domain classification | 無 | 未完成 |
| Quality score composition | 前端只計 missing ratio | 不一致 |
| Join／Append preview | 無，自動 append | 未完成 |
| Type conflict warning | 無 | 未完成 |

### 7.4 模型與可信評估

| 計畫項目 | 現況 | 狀態 |
|---|---|---|
| Regression | 已有多模型 | 一致 |
| Classification | 已有多模型 | 一致 |
| Clustering | 無 | 未完成 |
| Anomaly detection | 無 | 未完成 |
| PCA | 無 | 未完成 |
| Plugin registry | 只有單檔 catalog | 部分 |
| Capability API | 可依 import 結果列出模型 | 部分一致 |
| Leak-safe preprocessing | sklearn Pipeline | 部分一致 |
| Target leakage detection | 無 | 未完成 |
| Fast／balanced／deep budget | 只有 off／quick | 未完成 |
| Manual model selection | 已有 | 一致 |
| Manual parameters | 無 | 未完成 |
| Split controls | 無 | 未完成 |
| Seed controls | 固定 42，使用者不可調 | 部分 |
| Cross-validation | 只有 quick tuning 內部 2–3 folds | 部分 |
| Stability | 無 | 未完成 |
| Explainability | feature importance／coef | 部分 |
| SHAP | 無 | 未完成 |
| Baseline benchmark | 無正式 gate | 未完成 |

### 7.5 時間序列、圖表與報告

| 計畫項目 | 現況 | 狀態 |
|---|---|---|
| 金融指標 | MA、RSI、MACD、VaR 已有 | 一致 |
| Naive baseline | 無 | 未完成 |
| Exponential smoothing | 無 | 未完成 |
| ARIMA／SARIMA | 無 | 未完成 |
| Prophet | 無 | 未完成 |
| Backtesting | 無 | 未完成 |
| Forecast interval | 無 | 未完成 |
| Matplotlib PNG | 已有 | 一致 |
| Plotly | 無 | 未完成 |
| Manual chart builder | 無 | 未完成 |
| DOCX | 已有 | 一致 |
| PDF／HTML | 無 | 未完成 |
| Python／Notebook | 已有 | 一致 |
| Trained model | 已有 | 一致 |
| Exact run reproduction | 無 Manifest／params linkage | 未完成 |
| Read-only share | 無 | 未完成 |

### 7.6 安全、營運與商業基礎

| 計畫項目 | 現況 | 狀態 |
|---|---|---|
| Auth | 無 | 未完成 |
| Project ownership | 無 | 未完成 |
| Tenant isolation | 無 | 未完成 |
| Private artifacts | 公開靜態 URL | 不一致 |
| Retention／deletion | 無 | 未完成 |
| Malware protection | 無 | 未完成 |
| Formula injection protection | 無明確輸出防護 | 未完成 |
| Rate limit／quota | 無 | 未完成 |
| Secrets manager | 環境變數 | 未完成 |
| Log redaction | 無 policy | 未完成 |
| Privacy／Terms | 無 | 未完成 |
| Usage／cost tracking | 只有單模型 training time | 未完成 |
| Billing | 無 | 未完成 |
| Product analytics | 無 | 未完成 |
| Observability | 基本 logging／health only | 部分 |

## 8. 現況優點

### 產品優點

- 使用真實 FastAPI 分析，不以假數字填滿空狀態。
- CSV／Excel 到模型、圖表、金融與報告的流程已能完成。
- 繁中優先與英文路由形成明確區隔。
- 自動推薦之外仍保留模型、模式和圖表控制。
- 沒有 LLM key 時誠實標示 rule-based fallback。
- 金融頁已有不構成投資建議的限制文字。

### 介面優點

- Phase A 的整體視覺品質高，桌面和行動版資訊層級清楚。
- 390×844 行動版可正常操作，底部導覽、Header 和內容沒有明顯破版。
- Data Lens Hero 有清楚產品記憶點。
- 十套主題使用 semantic token，不是逐頁硬編碼。
- 有 skip link、focus-visible、keyboard、Escape、focus restore 和 reduced motion。
- 圖表未產生時不顯示假圖。

### 工程優點

- 現有 frontend stack 符合計畫。
- 模型 preprocessing 使用 sklearn Pipeline。
- XGBoost／LightGBM 無法 import 時不會假裝可用。
- API 有 upload limit、CORS、security headers、generic errors。
- job 有真實 stage、elapsed time 和 cooperative cancel。
- 本次 backend 23 tests、frontend 36 tests、typecheck、production build 全部通過。
- Browser console 沒有 error 或 warning。

## 9. 現況缺點

- 產品最核心的「可驗證」價值尚未由 Run Manifest 支撐。
- 公開靜態 artifact 與無身份授權是直接的資料外洩風險。
- 單程序 in-memory job 不能承受重啟、多人或多實例。
- 自動 append、多數品質缺口與單次 split 會影響分析正確性。
- 金融預測呈現形式比方法可信度成熟。
- 介面完成度遠高於資料、模型和基礎設施完成度，容易造成能力錯覺。
- 品牌同時是「智能金融」和「通用 AI 平台」，定位尚未收斂。
- 大量未提交變更與未更新 plan checklist，降低 review 和交付可信度。

## 10. 上線判斷

| 使用情境 | 判斷 | 條件 |
|---|---|---|
| 本機單人使用 | 可以 | 使用者理解資料保存在本機與瀏覽器 |
| 私有展示 | 可以 | 不上傳敏感資料，限制少量使用者 |
| 封閉 Beta | 有條件 | 單 tenant、非敏感資料、明確免責與人工監控 |
| 公開匿名上傳 | 不可以 | 缺少 auth、artifact authorization、rate limit、retention |
| 公開敏感資料 | 不可以 | 有直接資料外洩和責任風險 |
| 正式多租戶 SaaS | 不可以 | 缺少完整 Phase B、安全、治理與營運基礎 |

## 11. 修正優先順序

### 立即：0–3 天

1. 停止把目前 Render 設定稱為正式 production。
2. 在 README、DEPLOYMENT 和產品入口標示「封閉測試／不可上傳敏感資料」。
3. 移除或收斂「結果可追溯」「資料品質」等超過實際能力的文案。
4. 將 Docker Node 改為與 package engine 一致。
5. 整理 Phase A：更新 checklist、切分 commits、確認 36 tests 與 Browser 結果。
6. 不再增加裝飾性 UI、主題或模型種類。

### 第一優先：第 1–4 週

1. 定義 Project、Dataset、Dataset Version、Analysis Plan、Run、Artifact schema。
2. 建立 PostgreSQL migration。
3. 實作 Analysis Run Manifest。
4. 將 artifact 改成 metadata + private download endpoint。
5. 建立 Redis queue 與獨立 Core Worker。
6. 建立 retry、timeout、cancel、restart recovery 和 SSE。
7. 加入基礎 auth、Project ownership 和授權測試。
8. 建立 run event、耗時、資源與成本紀錄。

### 第二優先：第 5–8 週

1. duplicate、constant、ID、high cardinality、outlier、imbalance、leakage。
2. Join／Append preview、join key 和 type conflict。
3. stratified split、time-order split、group split。
4. cross-validation、stability、baseline 和完整分類指標。
5. 對小資料、失衡與不可信結果建立 blocking warning。
6. 建立四個完整 sample Project benchmark。

### 第三優先：第 9–12 週

1. 可編輯 Analysis Plan。
2. 受約束的自然語言 plan builder。
3. Plotly 自動／手動圖表。
4. PDF／HTML 報告。
5. Run compare。
6. 唯讀分享頁與期限／下載權限。
7. 再評估 Google Sheets／PostgreSQL connector。

## 12. 建議的下一個實作主題

下一個主題應是：

> Phase B：Persistent Analysis Run、Run Manifest、私人 Artifact 與 Redis Worker。

不建議下一步做：

- 更多深度學習模型。
- 更多配色或動態。
- 完整 Dashboard builder。
- 更多金融指標。
- 對外公開匿名上傳。

原因是 Phase B 同時解決：

- 可追溯。
- 重跑與比較。
- 工作恢復。
- 安全下載。
- 分享。
- 權限。
- 成本紀錄。
- 未來收費與 AI agent。

## 13. 驗證紀錄

本次實際執行：

- Backend：`pytest -q`，23 passed。
- Frontend：`npm run test:run`，36 passed。
- Frontend：`npm run typecheck`，通過。
- Frontend：`npm run build -- --webpack`，通過。
- Browser desktop：首頁、工作區、資料頁、圖表頁。
- Browser mobile：390×844 首頁與資料頁。
- Browser console：0 error、0 warning。
- `git diff --check`：通過。

已知驗證限制：

- 未透過 Browser 完成真實 file chooser 上傳 E2E。
- 未重建 Docker image。
- 未做 dependency vulnerability network audit。
- 未做負載、併發、重啟恢復或滲透測試。

## 14. 第一批修正追蹤

- C1：部分緩解。公開 StaticFiles 已移除，改為短效 capability URL；尚未完成 user/project ownership。
- C2：已修正。部署文件與產品入口改為封閉測試定位。
- M3：已修正。重複主要 CTA 已收斂。
- M6：已修正。Docker 與 package engine 統一 Node 22。
- 可讀性與工作區：已依 A 聚焦流程台完成；配色即時套用，分析面板改用語意實色文字。
- 進度與程式碼預覽：已修正。沒有後端 progress 時不輪播假步驟，生成程式碼可在頁內切換、複製與下載。
- 未完成：PostgreSQL、Analysis Run Manifest、auth/project ownership、Redis Worker、SSE、正式 artifact authorization 與 rate limit 仍屬 Phase B。
