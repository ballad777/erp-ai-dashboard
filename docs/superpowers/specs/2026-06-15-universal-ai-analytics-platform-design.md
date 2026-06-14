# 通用型 AI 資料分析平台完整設計規格

日期：2026-06-15
產品名稱：智能金融資料分析
狀態：已確認，待建立實作計畫

## 1. 目標

將現有金融與表格分析工具擴充為通用型 AI 資料分析平台。使用者上傳 CSV、Excel 或 JSON 後，系統必須實際讀取資料、理解結構、判斷可行任務、推薦模型、執行訓練、比較結果、產生圖表與報告。

平台同時支援兩種操作方式：

1. 自動模式：系統依資料特徵選擇合適的分析路徑、模型、前處理與評估方式。
2. 手動模式：使用者可調整目標欄位、特徵、模型、超參數、資料切分、前處理及評估指標。

本次帳號、登入與跨裝置記憶功能已明確擱置，不納入這份規格。

## 2. 核心產品原則

- 不使用假資料、固定模型結果或前端模擬分析。
- 畫面上的結果必須能追溯至真實後端任務與產出檔案。
- 系統的「智能」來自可解釋的資料剖析與規則推薦，不宣稱代替使用者決策。
- 自動推薦必須顯示原因、信心、限制、預估時間與資源等級。
- 模型不適用、套件缺失或資源不足時，明確回傳原因。
- 結果先提供重點、限制與下一步，再提供完整指標和細節。
- 長時間分析不得阻塞 FastAPI 請求。
- 首頁與工作區使用一致的品牌、動態與語意配色。
- 繁體中文為預設，英文介面保持功能與資訊對等。

## 3. 資訊架構

### 3.1 品牌首頁

- `/`：繁體中文首頁。
- `/en`：英文首頁。
- 產品價值、運作方式、支援任務、真實分析能力與進入工作區入口。

### 3.2 分析工作區

- `/app`：分析總覽與最近任務。
- `/app/data`：資料上傳、合併、Schema、品質與預覽。
- `/app/models`：任務推薦、模型設定、訓練、比較與解讀。
- `/app/charts`：自動及手動視覺化。
- `/app/finance`：金融與時間序列分析。
- `/app/reports`：程式碼、報告、產出與下載。
- `/en/app/*`：英文對應路由。

現有相容路由可以保留重導向，但主要導覽只呈現 `/app` 架構。

## 4. 視覺方向

### 4.1 品牌首頁：Data Lens

首頁的核心視覺是可互動的資料分析鏡。分析鏡掃過原始資料表時，局部內容轉化為趨勢、異常與洞察，具體表達「看懂資料」。

Hero 標題固定為兩行：

```text
看懂資料。
找到下一步。
```

規則：

- 每一行是不可拆分文字群組。
- 桌面、平板與手機都不得產生第三行。
- 窄螢幕降低字級與容器間距，不拆開「找到下一步。」。
- 首屏只保留一個主要 CTA、一個次要 CTA 與一個互動焦點。
- 首屏不展示完整 Dashboard，也不一次列出所有功能。
- 首頁內容隨捲動依序揭露資料理解、任務推薦、模型比較、報告輸出。

### 4.2 工作區：分析作業系統

工作區參考桌面工具的資訊密度與操作節奏，不複製參考圖片的黑綠配色。

主要結構：

- 左側固定圖示導覽。
- 中央可捲動分析畫布。
- 右側情境設定面板。
- 頂部資料來源、搜尋、配色與匯出控制。
- 分析模組依重要性排列，不使用大量等尺寸卡片。
- 詳細設定、模型資訊和圖表控制使用浮動面板、Popover 或 Drawer。
- 手機版改為底部導覽與全螢幕設定 Drawer，不縮小桌面三欄布局。

### 4.3 結果資訊層級

分析完成後依序顯示：

1. 三項最重要洞察。
2. 推薦的下一步。
3. 最佳模型與可信程度。
4. 主要圖表。
5. 模型比較及完整評估。
6. 資料品質、參數、程式碼與報告。

詳細內容預設收合，避免結果瞬間以密集文字全部出現。

## 5. 動態與交互

### 5.1 首頁

- Hero 文字以 30–60ms 字組 stagger 顯示，但不延遲 CTA 可操作時間。
- Data Lens 以彈簧插值跟隨游標，移動距離受限。
- 捲動時由資料表逐步轉化為任務、模型與洞察，不產生版面位移。
- 背景使用低透明度網格、柔和材質光帶與輕微 noise。
- 背景週期 16–28 秒，只動畫 `transform` 與 `opacity`。

### 5.2 工作區

- 模型詳情從觸發控制的位置展開，關閉時回到原觸發位置。
- 設定面板根據目前步驟切換內容，使用 180–240ms 可中斷轉場。
- 分析進度由 Worker 真實階段驅動，不使用固定秒數。
- 洞察、模型結果與圖表以 40–70ms stagger 分批出現。
- 卡片 Hover 僅位移 1–2px、改變邊框與陰影，不誇張縮放。
- 按鈕按下縮放至 0.97–0.98。
- 鍵盤快捷操作不播放進出動畫。
- Error、Success、Loading、Selection、Focus 都有視覺回饋。

### 5.3 無障礙與降級

- 支援 `prefers-reduced-motion`。
- Reduced Motion 移除視差、游標追蹤與大幅位移，保留淡入和狀態顏色。
- Touch 裝置不觸發 Hover 動畫。
- 所有控制可使用鍵盤操作，Focus Visible 清楚。
- 文字及狀態對比至少符合 WCAG AA。

## 6. 十套語意配色

每套主題定義完整語意 Token：

- `background`
- `surface`
- `surface-elevated`
- `text-primary`
- `text-secondary`
- `border`
- `accent-primary`
- `accent-secondary`
- `success`
- `warning`
- `danger`
- 六色圖表序列

主題：

1. 晨霧藍綠：目前品牌預設。
2. Atlas 藍：理性、專業。
3. Iris 灰紫：柔和、有辨識度。
4. Clay 暖灰：適合閱讀長報告。
5. Sage 灰綠：自然沉穩。
6. Frost 高亮：適合投影與簡報。
7. Graphite 灰階：聚焦資料結構。
8. Amber 紙金：溫和的暖色重點。
9. Deep Sea 深色：低眩光深色。
10. Midnight 藍黑：夜間分析。

配色選單從頂部工具列展開：

- 即時預覽。
- 使用者按下套用後才保存。
- 保存於本機偏好設定。
- 不提供任意自訂顏色，避免產生低對比組合。
- 主題切換不得改變元件尺寸與版面。

## 7. 系統架構

```text
Next.js App Router
        |
FastAPI API Gateway
        |
PostgreSQL ------- Local File Storage
        |
Redis Task Queue
        |
Analysis Workers
  |-- Dataset Profiler
  |-- Domain Classifier
  |-- Task Recommender
  |-- Model Registry
  |-- AutoML Engine
  |-- Chart Engine
  |-- Report Engine
```

### 7.1 前端

- Next.js App Router
- React
- TypeScript
- Tailwind CSS
- shadcn/ui primitives
- Motion (`motion/react`)
- Plotly 前端互動圖表

### 7.2 API

- FastAPI 負責驗證、任務建立、狀態查詢、能力清單和下載。
- API 不直接執行長時間模型訓練。
- 所有錯誤使用一致的結構化回應。

### 7.3 任務佇列

- Redis 保存佇列與短期狀態。
- Worker 執行資料剖析、模型訓練、圖表及報告。
- 任務支援取消、重新執行、失敗復原與分階段進度。
- Worker 中止或超時後，任務標記為失敗，不永久停留在執行中。

### 7.4 資料庫

PostgreSQL 保存：

- 資料集 Metadata。
- 欄位 Schema 與品質摘要。
- 分析任務及進度事件。
- 推薦結果與理由。
- 模型執行、參數、指標與排名。
- 圖表及報告檔案索引。

不在資料庫保存大型原始檔案內容。
帳號功能擱置期間，主題與純介面偏好只保存在瀏覽器，不寫入共享資料庫。

### 7.5 檔案儲存

初期使用本機目錄：

```text
backend/uploads/
generated_outputs/
  charts/
  reports/
  code/
  models/
  data/
```

儲存介面必須抽象化，後續能替換為 S3 相容物件儲存。

## 8. 後端模組邊界

```text
backend/
  app/
    api/
      datasets.py
      analyses.py
      models.py
      charts.py
      reports.py
      capabilities.py
    database/
      session.py
      entities/
      repositories/
      migrations/
    services/
      dataset_service.py
      analysis_service.py
      artifact_service.py
    ml/
      profiling/
      recommendation/
      preprocessing/
      registry/
      runners/
      tuning/
      evaluation/
    reports/
      builders/
      templates/
    workers/
      tasks.py
      progress.py
    utils/
  uploads/
```

既有服務應逐步移入清楚邊界，不一次進行與功能無關的全面重寫。

## 9. 資料讀取與品質分析

### 9.1 格式

- CSV：編碼及分隔符偵測，提供錯誤提示。
- Excel：支援 `.xlsx` 和 `.xls`，可選工作表。
- JSON：支援記錄陣列、NDJSON 及可展平的巢狀記錄。
- 多檔案上傳與逐檔讀取。
- 合併前顯示欄位相容性、Join Key 候選與資料型別衝突。

### 9.2 Schema

- 數值、類別、布林、文字、日期時間、識別碼和可能的目標欄位。
- 日期格式、頻率與排序檢查。
- 高基數類別、常數欄位及近常數欄位。

### 9.3 品質

- 缺失值數量與比例。
- 重複資料。
- IQR、Z-score 或適用方法偵測異常值。
- 類別分布及類別不平衡。
- 數值摘要：平均、中位數、標準差、最小、最大及分位數。
- 欄位間相關性與潛在資料洩漏提醒。

## 10. 領域與任務理解

### 10.1 領域判斷

系統依欄位名稱、資料值、單位、日期結構和欄位關係判斷：

- 金融
- 體育
- 房價
- 醫療
- 商業
- 一般表格

輸出包含：

- 最可能領域。
- 信心分數。
- 判斷依據。
- 其他候選領域。
- 使用者修正控制。

領域判斷只影響推薦，不限制使用者選擇。

### 10.2 任務推薦

- 連續數值目標：Regression。
- 離散或低基數目標：Classification。
- 日期與連續指標：Time Series Forecasting。
- 無目標欄位：EDA、Clustering、Anomaly Detection。
- 高維資料：PCA；t-SNE 和 UMAP 用於探索視覺化。
- 極端值或異常密度：Anomaly Detection。
- 同一資料可同時推薦多條分析路徑。

每條路徑包含原因、前置條件、建議圖表、候選模型與預估成本。

## 11. 模型外掛註冊表

所有模型以統一介面註冊：

```python
class ModelPlugin:
    key: str
    task_types: set[str]
    dependency_group: str
    resource_level: str

    def capability(self) -> CapabilityResult: ...
    def validate(self, dataset_profile, config) -> ValidationResult: ...
    def build_pipeline(self, config): ...
    def default_search_space(self, profile): ...
    def fit(self, train_data, config, progress): ...
    def evaluate(self, test_data, metrics): ...
    def explain(self, fitted_model, feature_names): ...
```

能力 API 必須回傳：

- 是否已安裝。
- 支援任務。
- 不適用原因。
- 預估資源。
- 預設參數與可調參數 Schema。

### 11.1 Regression

- Linear Regression
- Polynomial Regression
- Ridge
- Lasso
- ElasticNet
- Decision Tree Regressor
- Random Forest Regressor
- Gradient Boosting Regressor
- XGBoost Regressor
- LightGBM Regressor
- CatBoost Regressor
- SVR
- KNN Regressor
- AdaBoost Regressor
- Extra Trees Regressor
- MLP Regressor

### 11.2 Classification

- Logistic Regression
- Decision Tree Classifier
- Random Forest Classifier
- Gradient Boosting Classifier
- XGBoost Classifier
- LightGBM Classifier
- CatBoost Classifier
- SVM
- KNN Classifier
- Naive Bayes
- AdaBoost Classifier
- Extra Trees Classifier
- MLP Classifier

### 11.3 Clustering

- K-Means
- Agglomerative Clustering
- DBSCAN
- Gaussian Mixture Model
- Mean Shift
- Spectral Clustering

### 11.4 Dimensionality Reduction

- PCA
- t-SNE
- UMAP

### 11.5 Time Series

- Moving Average
- Exponential Smoothing
- ARIMA
- SARIMA
- Prophet
- TensorFlow LSTM
- TensorFlow GRU
- PyTorch LSTM
- PyTorch GRU

### 11.6 Anomaly Detection

- Isolation Forest
- One-Class SVM
- Local Outlier Factor

### 11.7 Dependency Groups

- `core`: pandas、numpy、scipy、scikit-learn、statsmodels。
- `boosting`: xgboost、lightgbm、catboost。
- `timeseries`: prophet。
- `deep-learning`: tensorflow、pytorch。
- `visualization`: plotly、matplotlib、umap-learn。

開發與正式映像必須提供明確安裝方式。未安裝模型不出現在「可執行」清單，只能出現在能力資訊中並標示缺少套件。

## 12. AutoML

### 12.1 Pipeline

- 所有補值、編碼、縮放和特徵選擇放入 Pipeline，避免資料洩漏。
- 數值欄位與類別欄位分別處理。
- 高基數類別預設使用適合策略，不無限制 One-Hot。
- 時間序列使用時間順序切分，不隨機打亂。
- 分群和異常偵測使用無監督前處理。

### 12.2 搜尋策略

- 快速模式：少量代表模型及固定安全參數。
- 平衡模式：Random Search 與有限交叉驗證。
- 深度模式：擴大候選和搜尋預算。
- 最佳候選可進行第二階段精調。
- 每個任務設定最大模型數、時間、記憶體和交叉驗證折數。
- Grid Search 保留給小型、明確參數空間。

### 12.3 模型推薦

候選集至少覆蓋：

- 一個快速基準。
- 一個線性或簡單模型。
- 一個樹模型。
- 一個進階模型。

系統依資料量、維度、稀疏程度、非線性、類別不平衡、缺失值及資源預算調整候選，不固定執行同一組模型。

## 13. 評估

### 13.1 Regression

- MAE
- MSE
- RMSE
- R²

### 13.2 Classification

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- Confusion Matrix

多類別任務明確標示 Macro、Micro 或 Weighted 平均方式。

### 13.3 Clustering

- Silhouette Score
- Davies-Bouldin Score

### 13.4 Time Series

- MAE
- RMSE
- MAPE

### 13.5 通用規則

- 顯示訓練時間、推論時間及資料切分方式。
- 顯示交叉驗證平均與離散程度。
- 排名依主要指標，但保留其他指標與成本。
- 明確標示過度擬合、資料量不足和不平衡風險。

## 14. 統計分析

- Pearson、Spearman 相關分析。
- T-test。
- ANOVA。
- Chi-square Test。
- A/B Testing。
- Regression Analysis。
- Feature Importance。

每個統計結果顯示假設、樣本條件、檢定方法、統計量、P-value、效果量及限制。系統不得把統計顯著直接描述為因果關係。

## 15. 視覺化

- Line Chart
- Bar Chart
- Pie Chart
- Scatter Plot
- Heatmap
- Correlation Matrix
- Box Plot
- Histogram
- Pair Plot
- Time Series Plot
- Cluster Visualization
- Feature Importance Plot
- Prediction vs Actual Plot
- Residual Plot
- Model Comparison Plot

自動圖表依欄位型別、任務與資料量選擇。大型資料先抽樣或聚合，避免瀏覽器和 Matplotlib 記憶體失控。使用者可手動選擇圖表、X/Y、分組、聚合與篩選條件。

使用者先前取消首頁固定熱力圖要求，不代表平台禁止 Heatmap；Heatmap 僅在使用者選擇或推薦理由充分時產生。

## 16. 報告與程式碼

### 16.1 報告

- PDF
- HTML
- 保留既有 DOCX 能力

內容：

- 資料摘要
- 品質與缺失值
- 異常值
- 特徵分析
- 推薦任務與理由
- 模型比較與評估
- 圖表
- 重要洞察、限制與下一步

### 16.2 程式碼

- Python `.py`
- Jupyter Notebook `.ipynb`
- 在工作區直接預覽，不要求先下載
- 程式碼與實際執行 Pipeline、模型和參數一致

### 16.3 其他產出

- 清理後 CSV
- 模型結果 XLSX
- PNG 圖表
- 訓練模型檔案

ZIP 整包下載不在本次新增範圍，維持先前擱置決定。

## 17. API

### 17.1 Dataset

- `POST /api/datasets/upload`
- `POST /api/datasets/upload/multiple`
- `GET /api/datasets/{dataset_id}`
- `GET /api/datasets/{dataset_id}/preview`
- `GET /api/datasets/{dataset_id}/schema`
- `GET /api/datasets/{dataset_id}/profile`
- `POST /api/datasets/merge/preview`
- `POST /api/datasets/merge`

### 17.2 Recommendation

- `POST /api/analyses/recommend`
- `GET /api/models/capabilities`
- `GET /api/models/{model_key}/parameters`

### 17.3 Analysis Jobs

- `POST /api/analyses`
- `GET /api/analyses/{job_id}`
- `GET /api/analyses/{job_id}/events`
- `POST /api/analyses/{job_id}/cancel`
- `POST /api/analyses/{job_id}/retry`
- `GET /api/analyses/{job_id}/results`

### 17.4 Charts and Reports

- `POST /api/analyses/{job_id}/charts`
- `GET /api/analyses/{job_id}/charts`
- `POST /api/analyses/{job_id}/reports`
- `GET /api/analyses/{job_id}/artifacts`
- `GET /api/artifacts/{artifact_id}/download`

前端進度可使用 Server-Sent Events；斷線後改以狀態輪詢恢復。

## 18. 錯誤處理

統一錯誤格式：

```json
{
  "error": {
    "code": "MODEL_NOT_AVAILABLE",
    "message": "此模型尚未安裝必要套件。",
    "details": {},
    "suggested_action": "改用可用模型或安裝 deep-learning 依賴群組。"
  }
}
```

錯誤類型至少包含：

- 檔案格式或編碼錯誤。
- Schema 不相容。
- 目標欄位無效。
- 模型不適用。
- 套件缺失。
- 資料量不足。
- 記憶體或執行時間超限。
- 任務取消。
- Worker 中斷。
- 報告或檔案輸出失敗。

前端保留使用者輸入與選擇，提供修正、重試或切換模型，不清空整個工作區。

## 19. 資料庫實體

主要資料表：

- `datasets`
- `dataset_files`
- `dataset_columns`
- `dataset_profiles`
- `analysis_jobs`
- `analysis_events`
- `analysis_recommendations`
- `model_runs`
- `model_metrics`
- `artifacts`

所有實體使用 UUID、建立／更新時間及明確狀態欄位。刪除資料集時同步清理關聯檔案和產出。

## 20. 安全與資源控制

- 僅接受允許的副檔名、MIME 類型和檔案大小。
- 檔名正規化，不直接使用使用者路徑。
- 上傳與輸出限制在指定根目錄。
- JSON 與試算表公式內容不可直接注入 HTML。
- 報告模板轉義使用者資料。
- API 設定請求大小、模型時間、記憶體及併發上限。
- 模型檔案不使用來自使用者的任意 Pickle。
- 正式環境限制 CORS。
- 日誌不記錄完整資料列或敏感欄位值。

帳號系統擱置期間，平台不宣稱提供多人資料隔離；正式公開多人使用前必須補上驗證與租戶隔離。

## 21. 本機與部署

提供 Docker Compose：

- `frontend`
- `api`
- `worker-core`
- `worker-heavy`
- `postgres`
- `redis`

`worker-core` 處理一般分析；`worker-heavy` 處理 Prophet、TensorFlow、PyTorch 等重型任務。

本機開發可以選擇只啟動 Core 能力，但 UI 必須依能力 API 隱藏不可執行模型。完整驗收環境必須啟動全部服務。

## 22. 測試

### 22.1 後端

- 每種檔案格式讀取測試。
- Schema、日期、缺失、異常與重複偵測。
- 領域與任務推薦規則。
- 每個模型外掛的能力與輸入驗證。
- 各任務至少一個真實訓練整合測試。
- Pipeline 資料洩漏防護。
- Worker 取消、超時、失敗及重試。
- 報告與產出檔案存在且可開啟。
- API 錯誤格式與路徑安全。

### 22.2 前端

- 上傳、預覽、合併及錯誤流程。
- 自動與手動模型模式。
- 真實進度、取消及重試。
- 結果分層與程式碼預覽。
- 十套主題切換及保存。
- 中文與英文路由。
- 鍵盤、Focus、Reduced Motion。
- Mobile、Tablet、Desktop RWD。

### 22.3 端到端

至少使用以下資料：

- 金融時間序列。
- 房價迴歸。
- 醫療或客戶分類。
- 體育或商業分群。
- 含異常值與缺失值的一般表格。
- JSON 巢狀資料。

每組測試必須驗證後端真實執行、結果檔案、圖表、模型排名和報告。

## 23. 分階段交付

雖然最終交付是完整平台，仍分成可驗收階段，避免同時改動所有系統而無法定位問題。

### 階段 A：設計系統與工作區重構

- Data Lens 首頁。
- 兩行 Hero。
- 新工作區框架、結果層級、浮動面板。
- 十套主題。
- RWD、Accessibility、Motion。

### 階段 B：資料層與任務基礎建設

- PostgreSQL、Redis、Worker、Migration。
- CSV、Excel、JSON。
- Dataset/Profile API。
- 真實進度與任務恢復。

### 階段 C：通用資料理解

- 品質分析。
- 領域判斷。
- 任務推薦。
- 合併預覽與執行。

### 階段 D：模型註冊表與傳統 AutoML

- Regression、Classification、Clustering、Anomaly Detection、PCA。
- 統一 Pipeline、搜尋、評估和模型排名。
- 手動參數介面。

### 階段 E：時間序列與重型模型

- Statsmodels、Prophet。
- LSTM、GRU。
- TensorFlow、PyTorch Worker 能力。

### 階段 F：圖表、統計、報告與產出

- 自動及手動圖表。
- 統計分析。
- PDF、HTML、DOCX、PY、IPYNB、CSV、XLSX、PNG、模型檔。

### 階段 G：完整驗收

- 全模型能力稽核。
- Production Build。
- 後端及端到端測試。
- 桌面、平板、手機瀏覽器驗證。
- README、PROGRESS、Known Issues。

每一階段完成後記錄：

- 已完成檔案。
- 新增功能。
- 啟動方式。
- 測試方式。
- 已知問題。
- 下一階段。

## 24. 驗收標準

- Hero 在所有支援尺寸固定兩行。
- CSV、Excel、JSON 均能真實讀取。
- 多檔案逐檔讀取與合併功能可用。
- 系統依不同資料推薦不同任務與模型。
- 自動模式不固定執行同一組模型。
- 使用者可切換手動模式和參數。
- 長任務由 Worker 執行，前端顯示真實進度。
- 所有顯示中的模型都能執行，或清楚標示不可用原因。
- 模型比較、圖表和報告來自真實結果。
- 程式碼可在頁面中預覽並下載。
- 十套主題在桌面與手機均維持可讀性。
- 所有主要控制具 Loading、Success、Error、Focus 和 Disabled 狀態。
- Production Build、後端測試與 E2E 流程通過。
- README 能讓新手用 Docker Compose 啟動完整環境。

## 25. 已確認與擱置事項

已確認：

- Data Lens 視覺方向。
- Hero 固定兩行。
- 首頁與工作區都具有豐富但有目的的動態。
- 十套完整語意配色。
- 模型外掛註冊表。
- Redis 背景 Worker。
- PostgreSQL 任務與結果資料。
- 本機檔案儲存。
- 完整通用分析與 AutoML 方向。

擱置：

- 帳號登入。
- 跨裝置記憶。
- 多租戶資料隔離。
- ZIP 整包下載。
