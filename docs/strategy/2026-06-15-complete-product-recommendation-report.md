# 通用型 AI 資料分析平台完整建議報告

日期：2026-06-15  
適用專案：智能金融資料分析  
報告性質：產品策略、功能優先級、技術架構、商業模式與執行路線建議  

---

## 1. 執行摘要

目前專案已經不是單純的 CSV 上傳工具。現有實作具備真實資料摘要、回歸與分類模型、多模型比較、金融分析、圖表、程式碼、Notebook、模型檔和 DOCX 報告，並開始建立工作狀態、取消、雙語介面與本機工作區保存。

問題不在功能太少，而在產品邊界仍然太寬。若同時正面競爭 ChatGPT、Julius、Power BI、Tableau、Hex、Deepnote、Dataiku、DataRobot、Databricks 與 SageMaker，產品會在每個市場都缺少關鍵能力。

本報告建議採用以下策略：

> **先成為繁中市場中，從 CSV／Excel 到可信分析報告最快的可驗證 AI 分析工作區，再逐步擴充為通用平台。**

第一階段的核心客群應是：

- 依賴 Excel、CSV 進行分析的中小企業分析師。
- 財務、營運、行銷、業務與研究人員。
- 沒有完整資料科學團隊，但需要模型、圖表和正式報告的組織。
- 需要繁體中文說明、可重現程式碼和本機／私有部署的使用者。

第一階段不應將「資料科學家」作為唯一主要客群。專業資料科學家已有 Jupyter、VS Code、Hex、Databricks 和完整 Python 生態，很難因模型數量而遷移。產品應讓分析師先得到結果，再讓資料科學家能審查、重跑與接手。

最重要的五項決策：

1. 將每次分析改造成可追溯的 `Analysis Run`，完整保存資料版本、設定、模型、指標、警告與產物。
2. 將資料品質、洩漏防護和正確評估放在增加模型數量之前。
3. 將 PostgreSQL、Redis Worker、持久化任務和 artifact index 提升為正式產品的必要基礎。
4. 將自然語言定位為「分析計畫建立器」，而不是不透明的聊天回答。
5. 將互動圖表、正式報告與安全分享提前，將 LSTM、GRU 和完整企業治理延後。

---

## 2. 建議的策略選擇

### 方案 A：直接打造通用企業資料科學平台

涵蓋資料連線、ETL、Notebook、AutoML、MLOps、BI、治理、模型部署和 AI agent。

**優點**

- 市場敘事大。
- 理論上可服務最多使用情境。

**缺點**

- 會直接面對 Dataiku、Databricks、SageMaker、Vertex AI 和 Azure ML。
- 需要大量工程、資安、連線器、部署和企業銷售資源。
- 在找到付費客群前就產生高開發與維運成本。

**結論：不建議。**

### 方案 B：維持純金融分析垂直產品

專注股票價格、技術指標、風險、VaR、時間序列和金融報告。

**優點**

- 定位清楚。
- 現有金融功能可直接延伸。
- 容易製作具體模板。

**缺點**

- 容易被理解為投資建議工具，增加法規、資料授權和責任風險。
- 金融專業使用者通常需要即時行情、企業資料和交易生態。
- 會浪費現有通用表格與模型能力。

**結論：可作為旗艦模板，不建議作為唯一產品邊界。**

### 方案 C：以試算表分析為切入點，再擴張到通用平台

先解決 CSV／Excel 的資料品質、任務推薦、模型比較、圖表與報告，再增加資料庫連線、協作和企業治理。

**優點**

- 與現有程式碼最一致。
- 首次價值清楚，使用者不必先建立資料倉庫。
- 可用金融、銷售、房價、流失和營運模板建立差異化。
- 能逐步驗證需求，不必一次完成所有企業能力。

**缺點**

- 必須嚴格控制功能範圍。
- 長期仍需要連線器、權限和協作。

**結論：建議採用。**

---

## 3. 產品定位

### 3.1 建議產品類別

`可驗證的 AI 資料分析工作區`

「AI 資料科學平台」過於寬泛；「金融分析工具」又過於狹窄。建議以「可驗證」區隔一般聊天分析，以「工作區」涵蓋持續專案、模型、圖表和報告。

### 3.2 建議價值主張

> 上傳 CSV 或 Excel，在幾分鐘內完成資料品質檢查、分析計畫、模型比較、圖表與正式報告。每一項結論都能追溯、重跑和交接。

### 3.3 建議首頁訊息

主標：

```text
看懂資料。
留下每一步證據。
```

副標：

```text
從 CSV、Excel 到可信分析結果。系統自動檢查資料、推薦方法、比較模型，
並產生可重現程式碼、圖表與正式報告。
```

主要 CTA：

```text
分析第一份資料
```

次要 CTA：

```text
開啟範例專案
```

### 3.4 不應使用的核心訊息

- 「支援最多模型」
- 「完全取代資料科學家」
- 「一鍵保證準確」
- 「AI 自動發現所有洞察」
- 「適用所有產業與所有資料」

這些訊息難以證明，也會提高使用者對黑箱、自動化錯誤和誤導性結論的擔憂。

---

## 4. 目標客群與使用情境

### 4.1 第一優先客群

**Excel-first 分析師與中小型團隊**

典型特徵：

- 資料以 Excel、CSV、Google Sheets 或匯出報表為主。
- 會樞紐分析、公式或基本 SQL，但不一定能建立完整 ML pipeline。
- 每週需要向主管交付圖表、結論與報告。
- 沒有時間自行處理 Python 環境、模型選擇與圖表排版。

主要工作：

1. 快速理解一份陌生資料。
2. 找出品質問題與可用欄位。
3. 預測數值或分類結果。
4. 找出主要影響因素。
5. 比較不同模型並了解限制。
6. 產生可交付的圖表、Excel、Word、PDF 或程式碼。

### 4.2 第二優先客群

**財務、營運與商業決策人員**

主要需求：

- 銷售、營收、成本、風險和趨勢分析。
- 不希望閱讀模型細節，但需要知道資料來源、可信程度和限制。
- 需要正式報告和可分享結果。

### 4.3 審查角色

**資料科學家或技術顧問**

產品不需要取代此角色，而應提供：

- 完整設定與 preprocessing。
- 程式碼和 Notebook。
- 模型版本與指標。
- 資料切分、random seed 和警告。
- 可重跑的 run manifest。

### 4.4 暫不優先客群

- 需要 petabyte 級 Spark 運算的大型企業資料工程團隊。
- 需要即時交易和高頻行情的量化交易團隊。
- 需要完整 Notebook IDE 的研究型資料科學家。
- 需要法規認證醫療模型的臨床機構。
- 只想製作 Dashboard、沒有建模需求的 BI 團隊。

---

## 5. 核心產品模型

建議將產品從「多個功能頁」重新定義為以下生命週期：

```text
Project
  └─ Dataset
      └─ Dataset Version
          └─ Analysis Plan
              └─ Analysis Run
                  ├─ Insight
                  ├─ Model Run
                  ├─ Chart
                  ├─ Report
                  └─ Artifact
```

### 5.1 Project

一個持續分析主題，例如「2026 銷售預測」或「客戶流失分析」。Project 保存資料來源、run、報告與分享設定。

### 5.2 Dataset Version

同一份資料每次更新都建立新版本，保存：

- 檔案 hash。
- 上傳時間。
- row／column count。
- schema。
- 品質摘要。
- 來源與合併方式。

### 5.3 Analysis Plan

在執行前顯示：

- 使用者想回答的問題。
- 推薦任務。
- 目標欄位與特徵。
- 前處理方式。
- 候選模型。
- 評估方法。
- 預估時間與資源。
- 主要風險。

使用者可以接受、修改或取消。

### 5.4 Analysis Run

每次執行必須是不可變的紀錄，至少包含：

- Dataset version ID。
- Plan version。
- 執行引擎版本。
- 套件和模型版本。
- random seed。
- train／validation／test 方法。
- preprocessing pipeline。
- 模型參數。
- 指標與圖表。
- 警告和失敗紀錄。
- 所有 artifact 索引。

### 5.5 Insight

每一項洞察都應附：

- 結論。
- 證據。
- 使用的資料範圍。
- 信心或穩定性。
- 限制。
- 建議下一步。

---

## 6. 建議的完整使用流程

### 步驟 1：加入資料

支援：

- CSV。
- XLSX／XLS。
- JSON／NDJSON。
- 範例資料。
- 後續加入 Google Sheets 和 PostgreSQL。

輸出：

- 讀取成功／失敗。
- 工作表或 JSON 結構選擇。
- 編碼、分隔符和型別警告。

### 步驟 2：資料健康檢查

顯示：

- 缺失值。
- 重複資料。
- 常數與近常數欄位。
- 高基數類別。
- 疑似 ID。
- 異常值。
- 類別不平衡。
- 日期順序和頻率。
- 潛在 target leakage。
- 品質分數及分數組成。

### 步驟 3：描述分析目的

提供兩種入口：

1. 自然語言：「預測下個月銷售並找出主要驅動因素。」
2. 結構化選擇：EDA、回歸、分類、分群、異常偵測、時間序列或統計檢定。

### 步驟 4：確認分析計畫

系統推薦方法，但使用者保留控制：

- 目標欄位。
- 特徵。
- 排除欄位。
- 切分方式。
- 模型與預算。
- 評估指標。
- 圖表和輸出格式。

### 步驟 5：執行與真實進度

階段來自 Worker：

1. 讀取資料。
2. 建立資料輪廓。
3. 驗證分析計畫。
4. 建立訓練資料。
5. 訓練與評估模型。
6. 產生圖表。
7. 產生洞察和報告。
8. 保存產物。

### 步驟 6：查看結果

依序顯示：

1. 最重要的三項結論。
2. 主要風險與限制。
3. 建議下一步。
4. 最佳模型與選擇原因。
5. 主要互動圖表。
6. 完整模型比較。
7. 資料品質和參數。
8. 程式碼、報告與下載。

### 步驟 7：重跑與分享

- 複製目前 run。
- 修改一項設定後重跑。
- 比較兩次 run。
- 產生唯讀分享頁。
- 設定分享期限和下載權限。
- 匯出正式報告。

---

## 7. 功能優先級

### P0：正式 Beta 前必要

| 能力 | 建議 | 原因 |
|---|---|---|
| Project／Dataset／Run 持久化 | 必做 | 沒有持久化就無法重跑、比較、稽核或分享 |
| Analysis Run Manifest | 必做 | 建立「可驗證」差異化的核心 |
| PostgreSQL＋Redis Worker | 必做 | 目前記憶體 job 無法支援重啟、多人和長任務 |
| Artifact 索引與安全下載 | 必做 | 產物不能只是公開靜態路徑 |
| 進階資料品質 | 必做 | 直接影響模型正確性 |
| Join／Append 預覽 | 必做 | 避免錯誤垂直合併 |
| Leak-safe pipeline | 必做 | 避免不可信的高分模型 |
| Cross-validation 與穩定性 | 必做 | 單次 75／25 切分不足以支持可信結論 |
| 結構化錯誤 | 必做 | 讓使用者能修正而不是重新開始 |
| 範例專案 | 必做 | 降低首次使用門檻並建立產品證據 |

### P1：建立市場差異化

| 能力 | 建議 | 原因 |
|---|---|---|
| 自然語言分析計畫 | 優先 | 與 Julius／ChatGPT 競爭首次體驗 |
| Plotly 互動圖表 | 優先 | 支援探索、篩選和分享 |
| Run 比較 | 優先 | 讓 AutoML 和手動控制真正有價值 |
| 結果分享頁 | 優先 | 完成分析師到主管的交付流程 |
| Google Sheets／PostgreSQL | 優先 | 進入真實日常工作 |
| PDF／HTML 報告 | 優先 | 比 DOCX 更適合正式分享與網頁預覽 |
| 模型解釋與警告 | 優先 | 增加信任，不只顯示 feature importance |
| 成本與時間預估 | 建議 | 避免分析工作不可控 |

### P2：找到付費需求後擴張

- 團隊空間、留言、審核和版本。
- SSO、RBAC、SCIM 和 audit log。
- Snowflake、BigQuery、Redshift 和 API 連線器。
- 排程分析與資料更新。
- 模型部署和 prediction API。
- Drift、performance 和資料品質監控。
- 完整 semantic layer。

### 暫不實作

- 完整 Notebook IDE。
- 自建資料倉庫。
- 數十種資料連線器。
- 任意拖拉式 ETL workflow builder。
- LLM 模型訓練平台。
- 高頻金融交易和即時下單。
- 在沒有需求證據前同時支援 TensorFlow 與 PyTorch 的所有深度模型。

---

## 8. 建議調整既有 Roadmap

目前七階段方向合理，但順序需要調整。

### 建議的新順序

#### Phase A：介面與產品敘事

維持目前方向：

- Data Lens 首頁。
- 工作區結構。
- 十套語意主題。
- 雙語、RWD、鍵盤和 reduced motion。

完成後停止新增裝飾性主題與動態，將資源轉向核心分析體驗。

#### Phase B：持久化工作與安全產物

新增明確交付：

- Project、Dataset Version、Analysis Plan、Run、Artifact schema。
- PostgreSQL migration。
- Redis queue 和 Worker。
- SSE、重試、取消、timeout 和重啟復原。
- 私有 artifact download endpoint。
- Run Manifest。

#### Phase C：資料理解與安全分析計畫

維持既定 profiler，並加入：

- target leakage。
- ID 和 high-cardinality 判斷。
- Join／Append 選擇。
- 資料品質分數。
- 可編輯 Analysis Plan。

#### Phase D：傳統 AutoML 與可信評估

優先支援：

- Regression。
- Classification。
- Clustering。
- Anomaly detection。
- PCA。
- Cross-validation。
- class imbalance。
- calibration。
- SHAP 或適當模型解釋。

#### Phase E：互動圖表、報告與分享

建議將原本 Phase F 提前：

- Plotly。
- 圖表規格。
- PDF／HTML／DOCX。
- Run 比較。
- 分享頁。
- 程式碼和 Notebook。

原因：這些能力直接形成使用者交付價值，比深度學習模型更早產生留存與付費可能。

#### Phase F：時間序列與金融模板

先完成：

- Naive baseline。
- Moving average。
- Exponential smoothing。
- ARIMA／SARIMA。
- Prophet。
- Backtesting。
- 時間序列交叉驗證。
- 預測區間。

LSTM／GRU 只有在資料量、需求和 benchmark 證明有價值時加入。

#### Phase G：連線器、協作與正式驗收

- Google Sheets。
- PostgreSQL。
- 依客戶需求選擇 BigQuery 或 Snowflake。
- 唯讀分享。
- 使用量與成本監控。
- 安全、效能、E2E 和正式文件。

---

## 9. 技術架構建議

### 9.1 目標架構

```text
Next.js Web
    |
FastAPI API
    |---------------- PostgreSQL
    |---------------- Object Storage
    |
Redis Queue
    |
Core Worker -------- pandas / Polars / DuckDB / scikit-learn
Heavy Worker ------- Prophet / optional deep learning
    |
Artifact Service --- charts / reports / code / models
```

### 9.2 前端

保留：

- Next.js App Router。
- React＋TypeScript。
- Tailwind。
- shadcn/ui primitives。
- Motion。

新增：

- TanStack Query 或等效 server-state 管理。
- Plotly lazy loading。
- URL-backed project／run state。
- 可恢復的 upload 和 job state。
- 錯誤邊界與大型結果的分段載入。

避免：

- 將大型分析結果全部保存在單一 React context。
- 每次切換頁面重傳完整檔案。
- 把分析規則複製到前端。

### 9.3 API

FastAPI 只負責：

- 驗證。
- 建立資料集與 run。
- 查詢狀態。
- 取消和重試。
- 權限檢查。
- 產物下載。

模型訓練和報告生成必須在 Worker。

### 9.4 資料處理引擎

建議分層：

- pandas：相容性和現有模型 pipeline。
- DuckDB：CSV／Parquet 查詢、聚合和本機大資料處理。
- Polars：大型表格 profiling 和轉換。
- scikit-learn：第一階段傳統模型。

不要立即導入 Spark。當單一資料集、Worker 記憶體和客戶需求真的超出單機能力時再評估。

### 9.5 儲存

PostgreSQL 保存 metadata，不保存大型原始資料內容。

Object storage 保存：

- 原始檔。
- 正規化資料。
- 模型。
- 圖表。
- 報告。
- 程式碼。

本機可使用 MinIO 或 filesystem adapter；正式環境使用 S3 相容儲存。

### 9.6 觀測性

至少收集：

- API latency。
- queue wait time。
- run duration。
- success／failure／cancel rate。
- memory peak。
- artifact size。
- LLM token 和費用。
- 每個模型的訓練時間。
- 每次 run 成本。

---

## 10. AI Agent 設計

### 10.1 原則

LLM 不應直接成為計算引擎。數值、統計、模型和圖表必須由可測試工具執行。

建議流程：

```text
User Intent
   ↓
Plan Agent
   ↓
Validation Rules
   ↓
Deterministic Tools / Workers
   ↓
Verification Agent
   ↓
Explanation and Report
```

### 10.2 Plan Agent

輸出結構化 JSON：

- question。
- task type。
- target。
- features。
- excluded columns。
- preprocessing。
- candidate models。
- metrics。
- charts。
- assumptions。
- risks。

必須通過 schema 驗證和資料規則檢查後才能執行。

### 10.3 Verification Agent

檢查：

- 結論是否能從計算結果支持。
- 是否把相關性誤寫成因果。
- 是否忽略資料量不足或不平衡。
- 是否引用不存在的欄位。
- 是否誤讀指標方向。
- 報告中的數字是否與 artifact 一致。

### 10.4 Provider 策略

- 建立 provider abstraction。
- 支援至少一個主要雲端 LLM。
- 保留本機規則摘要。
- 未設定 LLM 時不得使用「AI 已分析」等誤導文字。
- 敏感資料預設只傳 schema 和聚合摘要，不直接傳完整資料列。

---

## 11. 模型與評估建議

### 11.1 回歸

主要指標：

- MAE。
- RMSE。
- R²。
- Cross-validation mean／std。

必要檢查：

- baseline。
- residual。
- target distribution。
- leakage。
- overfitting gap。

### 11.2 分類

主要指標：

- Accuracy。
- Precision。
- Recall。
- F1。
- ROC-AUC。
- PR-AUC。
- Confusion matrix。
- Calibration。

類別不平衡時不能只以 Accuracy 排名。

### 11.3 時間序列

必要條件：

- 依時間切分。
- rolling／expanding backtest。
- naive baseline。
- 預測區間。
- MAE、RMSE、MAPE 或 sMAPE。

禁止對時間序列使用隨機 train-test split。

### 11.4 模型排名

排名不應只有一個分數。建議計算：

```text
Model Score =
  Predictive Quality
  + Stability
  + Explainability
  + Runtime Efficiency
  - Risk Penalties
```

使用者可選擇：

- 最準確。
- 最穩定。
- 最容易解釋。
- 最快速。

---

## 12. 安全、隱私與法規

### 12.1 目前狀態判斷

在沒有帳號、tenant isolation 和 artifact authorization 前，產品只能安全地定位為：

- 本機單人使用。
- 私有測試環境。
- 不含敏感資料的封閉 Beta。

**不建議直接開放公開多人上傳敏感資料。**

### 12.2 公開 Beta 前最低要求

- 使用者驗證。
- Project ownership。
- 每個 dataset、run 和 artifact 的授權檢查。
- Signed download URL 或受保護下載 endpoint。
- 資料刪除和保存期限。
- 上傳 malware／formula injection 防護。
- Encryption in transit。
- Secrets manager。
- 日誌脫敏。
- Rate limit 和 quota。
- Privacy Policy 和 Terms。

### 12.3 金融功能

金融報告必須標示：

- 不構成投資建議。
- 資料可能延遲或不完整。
- 歷史績效不代表未來結果。
- 模型與指標只是決策輔助。

若未取得市場資料授權，不應內建或重新散布受限制的即時金融資料。

---

## 13. 商業模式建議

### 13.1 收費原則

不要只按「模型數」收費。使用者更容易理解：

- 每月 analysis runs。
- 儲存容量。
- 檔案大小。
- Worker 資源。
- 團隊席位。
- 分享和連線器。

### 13.2 初步方案假設

價格是驗證假設，不是最終定價。

| 方案 | 建議內容 | 初步價格區間 |
|---|---|---|
| Free | 範例專案、少量 run、10 MB 檔案、短期保存、基本報告 | 免費 |
| Pro | 25–100 MB、較多 run、完整模型、PDF／DOCX、程式碼、較長保存 | NT$790–1,290／月 |
| Team | 共享 Project、唯讀分享、權限、連線器、集中用量 | NT$3,990–9,900／月起 |
| Private | 私有部署、SSO、audit、客製保存與支援 | 年約或專案報價 |

### 13.3 成本控制

每個 run 應設定：

- 最大資料量。
- 最大模型數。
- 最大執行時間。
- CPU／memory 限制。
- LLM token 預算。
- artifact 保存期限。

平台必須能計算每個 run 的實際成本，否則無法可靠定價。

### 13.4 不建議的模式

- 無限制使用的低價方案。
- 免費提供重型 GPU 模型。
- 所有資料永久保存。
- 依模糊的「AI credits」收費而不解釋使用量。

---

## 14. Go-to-Market 建議

### 14.1 市場切入訊息

不要先宣傳 AutoML。先宣傳具體成果：

- 「把 Excel 變成可交付的分析報告。」
- 「五分鐘找出資料問題與可用模型。」
- 「不用先學 Python，也能得到可檢查的 Python。」
- 「繁中分析、圖表、模型與正式報告一次完成。」

### 14.2 建議的四個示範模板

1. 銷售預測與營收驅動因素。
2. 客戶流失分類。
3. 房價或成本預測。
4. 金融價格、風險和趨勢。

每個模板都應有：

- 真實可下載資料。
- 明確問題。
- 資料品質警告。
- 分析計畫。
- 模型結果。
- 可分享報告。

### 14.3 獲客渠道

- 繁中 SEO：Excel 分析、CSV 分析、AutoML、銷售預測、客戶流失。
- YouTube／短影片：從檔案到報告的完整流程。
- 會計、管理顧問和資料顧問合作。
- 大學商管、財金與資料分析課程。
- 中小企業社群和產業協會。
- 可自行執行的公開範例。

### 14.4 Beta 計畫

第一批 10–20 名使用者，要求他們帶真實但可匿名化的工作：

- 5 名財務／營運分析者。
- 5 名商業或行銷分析者。
- 3–5 名資料科學或技術審查者。
- 2–5 名主管型報告閱讀者。

每週觀察：

- 上傳到結論需要多久。
- 哪些警告看不懂。
- 推薦計畫修改了什麼。
- 是否下載或分享產物。
- 是否會再次使用同一 Project。

---

## 15. 產品 KPI

### 15.1 North Star

**Weekly Trusted Analysis Runs**

定義：每週完成、沒有未處理重大警告，且被使用者查看、下載、分享或重跑的分析 run 數。

只計算「按下執行」會鼓勵低品質工作，必須加入完成和使用條件。

### 15.2 啟用指標

- 首次成功上傳率。
- 首次成功 profile 率。
- Time to first trusted insight。
- 首次 run 完成率。
- 範例轉自有資料率。

### 15.3 品質指標

- Run success rate。
- Warning resolution rate。
- Recommendation acceptance rate。
- Report consistency error rate。
- Model failure rate。
- Retry recovery rate。

### 15.4 留存與價值

- 7 日 Project return rate。
- 30 日 active project rate。
- Re-run rate。
- Artifact download／share rate。
- Connector reuse rate。
- Free-to-paid conversion。

### 15.5 建議初始目標

| 指標 | Beta 目標 |
|---|---|
| 首次成功上傳率 | ≥ 95% |
| 首次 run 完成率 | ≥ 80% |
| Time to first trusted insight | 中位數 ≤ 5 分鐘 |
| 重大警告可理解率 | ≥ 85% |
| 7 日回訪率 | ≥ 30% |
| Artifact 使用率 | ≥ 40% |

---

## 16. 團隊與資源

### 16.1 最小正式團隊

- 1 名產品／全端工程師。
- 1 名後端／資料平台工程師。
- 1 名 ML／資料科學工程師。
- 1 名產品設計或前端工程師。
- 兼任 DevOps／Security。
- 兼任財務或營運領域顧問。

### 16.2 若由單人開發

必須依序執行：

1. 持久化與安全。
2. 資料品質。
3. 評估正確性。
4. 報告與分享。
5. 自然語言計畫。
6. 連線器。
7. 進階模型。

不要平行開發所有 Phase。

### 16.3 基礎設施成本估計

以下只是容量規劃區間，需以實際 run 成本修正：

- 封閉 Beta：每月約 US$100–400。
- 約 100 名月活躍使用者：每月約 US$500–2,000。
- 重型模型、長期儲存和大量 LLM 使用會顯著提高成本。

---

## 17. 主要風險

| 風險 | 可能影響 | 緩解措施 |
|---|---|---|
| 產品範圍失控 | 延遲交付、每項功能都不完整 | 以 spreadsheet-first ICP 和 P0 清單限制範圍 |
| AI 結論錯誤 | 使用者失去信任 | deterministic tools、verification、證據與限制 |
| 模型洩漏或評估錯誤 | 產生虛高分數 | leak-safe pipeline、CV、time-order rules |
| 敏感資料外洩 | 法律和品牌損害 | auth、tenant isolation、private artifacts、retention |
| 運算成本不可控 | 無法建立可行定價 | run budget、quota、成本追蹤 |
| 與大型平台正面競爭 | 缺少差異化 | 繁中、試算表入口、可信交付和私有部署 |
| 過早投入深度學習 | 高成本、低使用率 | 需求 gate 和 baseline benchmark |
| 金融敘事過強 | 限縮市場並產生投資建議風險 | 金融改為模板，品牌保持通用 |
| 報告看似專業但證據不足 | 誤導決策者 | 每項洞察連回 run、圖表和限制 |

---

## 18. 30／60／90 天執行建議

### 前 30 天：建立可信產品基礎

1. 完成 Phase A 並停止擴充裝飾性 UI。
2. 定義 Project、Dataset Version、Analysis Plan、Run 和 Artifact schema。
3. 建立 Analysis Run Manifest。
4. 加入 duplicate、constant、ID、high-cardinality、imbalance 和 leakage 基礎檢查。
5. 為現有四個示範資料建立完整 benchmark。
6. 建立產品事件與 run 成本紀錄。

**完成條件**

- 每個結果都能指出來自哪份資料、哪次 run 和哪些設定。

### 第 31–60 天：持久化與正確性

1. PostgreSQL migration。
2. Redis Worker。
3. SSE 進度、取消、重試和恢復。
4. 私有 artifact service。
5. Cross-validation 與分類完整指標。
6. Join／Append 預覽。
7. 結構化錯誤和修正動作。

**完成條件**

- API 或 Worker 重啟後，run 狀態和結果不會遺失。

### 第 61–90 天：形成可測試的市場產品

1. Analysis Plan UI。
2. 受約束的自然語言計畫入口。
3. Plotly 主要圖表。
4. PDF／HTML 報告。
5. 唯讀分享頁。
6. 四個範例專案。
7. 封閉 Beta 10–20 人。

**完成條件**

- 使用者能從檔案完成分析、分享結果，並在一週內回來重跑同一 Project。

---

## 19. 十二個月建議路線

| 時間 | 目標 |
|---|---|
| 月 1–3 | 可信 run、持久化、資料品質、Beta |
| 月 4–6 | 傳統 AutoML、互動圖表、報告、分享 |
| 月 7–9 | Google Sheets／PostgreSQL、團隊功能、收費實驗 |
| 月 10–12 | 時間序列深化、私有部署、企業安全或特定倉庫連線 |

進入下一階段的條件應是使用者證據，而不是前一階段程式碼寫完。

建議 gate：

- 沒有 30% 七日回訪，不擴充更多模型。
- 沒有穩定 artifact 使用，不開發完整 Dashboard builder。
- 沒有三個以上付費客戶要求，不做 Snowflake／BigQuery 雙線。
- 沒有 baseline 改善證據，不做 LSTM／GRU。
- 沒有多人使用需求，不做複雜 SCIM 和組織層級。

---

## 20. 最終建議

本專案的機會不在於重建整個資料科學生態，而在於消除現有工具之間的斷層：

```text
Excel / CSV
    ↓
資料品質
    ↓
正確的分析計畫
    ↓
可信模型與統計
    ↓
可理解的結論
    ↓
可重現程式碼與正式報告
```

建議保留現有通用分析方向，但做出三項收斂：

1. **客群收斂**：先服務 spreadsheet-first 的繁中分析團隊。
2. **價值收斂**：先交付可信、可重現、可分享的分析結果。
3. **技術收斂**：先完成持久化、資料品質和傳統模型，再擴張重型能力。

若只能選擇下一項工作，應先做：

> **持久化的 Analysis Run 與 Run Manifest，而不是新增模型。**

這項能力會同時支撐可重現性、工作恢復、比較、報告、分享、權限、收費與未來的 AI agent，是從功能原型走向正式產品的真正分界。

---

## 21. 參考資料

本報告使用既有市場研究、現況程式碼與產品規格，主要外部來源包括：

- [Hex Notebooks](https://hex.tech/product/notebooks/)
- [Deepnote](https://deepnote.com/)
- [Julius AI](https://julius.ai/)
- [ChatGPT Data Analysis](https://help.openai.com/en/articles/8437071-advanced-data-analysis)
- [Dataiku Platform](https://www.dataiku.com/product)
- [KNIME Pricing and Capabilities](https://www.knime.com/knime-hub-pricing)
- [H2O AutoML](https://docs.h2o.ai/h2o/latest-stable/h2o-docs/automl.html)
- [ThoughtSpot Agents](https://www.thoughtspot.com/product/agents)
- [Microsoft Power BI](https://www.microsoft.com/en-us/power-platform/products/power-bi)
- [Tableau AI](https://www.tableau.com/products/artificial-intelligence)
- [Streamlit](https://streamlit.io/)
- [Apache Superset](https://superset.apache.org/)
- [Amazon SageMaker](https://aws.amazon.com/sagemaker/)
- [Google Vertex AI](https://docs.cloud.google.com/vertex-ai/docs/start/introduction-unified-platform)

價格、雲端成本和競品功能會變動。本報告中的定價和成本是產品驗證假設，不是供應商正式報價。
