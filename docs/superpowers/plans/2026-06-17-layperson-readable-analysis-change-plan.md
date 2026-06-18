# 一般人可讀、研究者可深挖的完整改動計畫

> **For agentic workers:** REQUIRED SUB-SKILL: Use `premium-ui-workstation` for UI/product changes and `verification-before-completion` before claiming completion. Implement task-by-task with focused verification after each task.

**日期：** 2026-06-17  
**專案：** 智能金融資料分析系統  
**目標：** 讓沒有資料科學背景的一般使用者能讀懂分析結論，同時讓資料科學學生、分析師與研究者可以展開方法、假設、公式、資料品質、回測與原始輸出。  
**核心判斷：** 目前專案方向正確，已開始加入白話摘要、可信度、指標字典與研究細節；但仍需要補齊合約驗收、前端第一屏資訊層級、金融預測防誤解、研究模式可重現性與使用者理解度測試。

---

## 1. 真實使用者檢驗基準

本計畫以一次真實「剛入學資料科學系大學生」測試作為基準。

### 1.1 測試資料

- 資料來源：FRED S&P 500 指數資料
- 來源頁面：https://fred.stlouisfed.org/series/SP500
- CSV URL：https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500
- 資料期間：2016-06-17 到 2026-06-16
- 欄位：`observation_date`、`SP500`
- 總列數：2,608
- 有效金融分析列數：2,513
- 最近一筆：2026-06-16，S&P 500 = 7,511.35

### 1.2 系統輸出觀察

系統已能輸出：

- 資料白話摘要 `plain_summary`
- 可信度 `confidence`
- 證據 `evidence`
- 指標解釋 `terms`
- 研究細節 `research_details`
- 金融預測可信度 `forecast_reliability`
- 圖表故事 `chart_stories`
- RSI、MACD、VaR、波動率、移動平均與預測圖

### 1.3 大一新生視角結論

能讀懂的部分：

- 可以理解這份資料是 S&P 500 指數時間序列。
- 可以理解最新報酬率是 -0.57%，代表最近一期下跌。
- 可以理解系統判斷「短線偏弱」。
- 可以理解預測可信度是「中」，不應直接拿來當投資判斷。
- 可以理解 VaR 約 1.68% 是一種單期下跌風險參考。

仍然難懂的部分：

- RSI 接近 49 為什麼代表中性，不看說明不直覺。
- MACD 與 signal 的差距代表什麼，初學者很難直接理解。
- VaR 的 95%、99% 信心水準需要更白話的風險句子。
- 預測圖的估計值明顯低於最新指數，雖然已有可信度說明，但視覺上仍可能讓一般人誤以為系統預測會大跌。
- 缺失值被列為資料品質問題，但使用者不一定知道金融市場週末與假日沒有交易，這不一定是錯誤資料。

---

## 2. 目前專案與目標一致性檢查

### 2.1 已一致

- 後端已有 `backend/app/services/metric_glossary.py`，開始建立指標字典與指標判讀。
- 後端已有 `backend/app/services/insight_narrative.py`，負責資料、模型、金融、圖表與預測可信度敘事。
- `backend/app/schemas.py` 已加入 `plain_summary`、`confidence`、`evidence`、`terms`、`chart_stories`、`research_details`、`forecast_reliability`。
- `frontend/src/components/InsightExplainers.tsx` 已有閱讀深度、白話摘要、可信度、證據、指標解釋、圖表故事與研究細節抽屜。
- `frontend/src/components/AnalysisResult.tsx`、`ModelAnalysisPanel.tsx`、`FinancialAnalysisPanel.tsx` 已開始接入解釋型元件。
- 金融分析已把部分「價格」文案泛化成「價格/指數/數值」。
- 金融預測已有 `forecast_reliability`，可以提示基準情境估計與可信度。

### 2.2 部分一致

- 白話摘要已存在，但仍需確認資料、模型、金融三大流程的第一屏都先呈現「一句話結論、可信度、下一步」，而不是讓圖表或技術指標先出現。
- 指標解釋已存在，但仍需確認 KPI 卡、圖表、報告與研究抽屜都使用同一份字典，避免同一指標在不同頁面有不同說法。
- 研究細節欄位已存在，但目前深度不足，尚未完整包含方法、參數、資料處理、回測、圖表原始資料與可重現資產。
- 前端已有閱讀深度切換，但需要驗證 `simple`、`standard`、`research` 三種模式真的改變資訊密度。
- API 直連最新後端可回傳新欄位，但曾觀察到既有 8000 服務回傳舊格式，表示開發與部署狀態可能不同步。

### 2.3 不一致或高風險

- 金融預測圖仍可能被一般人誤讀為「明確預測未來價格」，尤其當估計線與最新值落差大時。
- 預測點包含週末日期，對金融市場資料不夠嚴謹。
- 缺失值沒有區分「資料真的缺漏」與「市場休市造成沒有交易日」。
- 缺少 API contract tests，無法保證 `/api/finance/analyze`、`/api/jobs/finance` 與其他分析路徑都回傳一致的解釋欄位。
- 缺少使用者理解度驗收，無法證明一般人真的讀懂。
- 報告匯出尚未形成「一般人摘要 + 研究附錄」的雙層結構。
- 缺少版本或 schema freshness guard，容易發生前端期待新欄位、後端仍跑舊版本的情況。

---

## 3. 改動原則

### 3.1 單一分析結果，三層閱讀

不要做兩套產品。每次分析只產生一份結果，再用閱讀層級控制呈現深度。

- `simple`：一般人先看結論、風險、下一步。
- `standard`：補上證據、主要圖表、指標白話翻譯。
- `research`：展開方法、假設、參數、公式、回測、原始輸出與可重現資產。

### 3.2 每個數字都要回答四個問題

- 這是什麼？
- 這次數字代表什麼？
- 我該相信到什麼程度？
- 下一步要做什麼？

### 3.3 預測預設保守呈現

金融與模型預測不能用像「答案」的視覺語言呈現。預測應預設標示為：

- 基準情境估計
- 不是投資建議
- 可信度高/中/低
- 主要限制
- 是否已回測

### 3.4 研究者模式必須可重現

研究模式不能只是多放文字。它要能讓使用者回答：

- 系統怎麼處理資料？
- 使用什麼方法與參數？
- 指標怎麼算？
- 圖表的資料是什麼？
- 模型或預測是否有回測？
- 這次分析能否用 run id、dataset hash、artifact 重新追蹤？

---

## 4. File Map

### 4.1 後端主要修改

- `backend/app/schemas.py`
- `backend/app/main.py`
- `backend/app/services/insight_narrative.py`
- `backend/app/services/metric_glossary.py`
- `backend/app/services/dataset_analyzer.py`
- `backend/app/services/model_runner.py`
- `backend/app/services/financial_analyzer.py`
- `backend/app/services/report_generator.py`
- `backend/app/services/analysis_jobs.py`
- `backend/tests/test_dataset_analyzer.py`
- `backend/tests/test_model_runner.py`
- `backend/tests/test_financial_analyzer.py`
- `backend/tests/test_analysis_jobs.py`
- 新增：`backend/tests/test_explainability_contract.py`
- 新增：`backend/tests/fixtures/fred_sp500_sample.csv`

### 4.2 前端主要修改

- `frontend/src/components/InsightExplainers.tsx`
- `frontend/src/components/AnalysisResult.tsx`
- `frontend/src/components/ModelAnalysisPanel.tsx`
- `frontend/src/components/FinancialAnalysisPanel.tsx`
- `frontend/src/components/WorkspaceToolPages.tsx`
- `frontend/src/components/WorkspaceDashboard.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/app/product-interface.css`
- `frontend/src/app/product-motion.css`
- 新增：`frontend/src/components/analysis/ForecastReliabilityBanner.tsx`
- 新增：`frontend/src/components/analysis/IndicatorKpiCard.tsx`
- 新增：`frontend/src/components/analysis/ResearchRunManifest.tsx`
- 新增：`frontend/src/components/__tests__/InsightExplainers.test.tsx`
- 新增：`frontend/src/components/__tests__/FinancialAnalysisPanel.explainability.test.tsx`
- 新增：`frontend/src/components/__tests__/AnalysisResult.explainability.test.tsx`
- 新增：`frontend/src/components/__tests__/ModelAnalysisPanel.explainability.test.tsx`

### 4.3 文件與驗收主要修改

- `README.md`
- `PROGRESS.md`
- `docs/strategy/2026-06-17-layperson-and-researcher-improvement-plan.md`
- 新增：`docs/testing/layperson-comprehension-test-script.md`
- 新增：`docs/testing/researcher-reproducibility-test-script.md`
- 新增：`docs/testing/fred-sp500-smoke-test.md`

---

## 5. P0 改動：先鎖住分析結果合約

**目的：** 避免 UI 已改、API 服務卻回傳舊格式；也避免不同 endpoint 回傳欄位不一致。

### Task 1：建立 Explainability API Contract Test

**Files:**

- Create: `backend/tests/test_explainability_contract.py`
- Create: `backend/tests/fixtures/fred_sp500_sample.csv`
- Modify: `backend/tests/test_dataset_analyzer.py`
- Modify: `backend/tests/test_model_runner.py`
- Modify: `backend/tests/test_financial_analyzer.py`
- Modify: `backend/tests/test_analysis_jobs.py`

**Steps:**

- [ ] 建立最小 FRED S&P 500 fixture，保留日期、指數值、週末缺口與部分缺失案例。
- [ ] 測試資料分析回應必含 `plain_summary`、`confidence`、`evidence`、`terms`、`research_details`。
- [ ] 測試模型分析回應必含 `plain_summary`、`confidence`、`evidence`、`terms`、`chart_stories`、`research_details`。
- [ ] 測試金融分析回應必含 `plain_summary`、`confidence`、`evidence`、`terms`、`chart_stories`、`forecast_reliability`、`research_details`。
- [ ] 測試 `/api/jobs/finance` 與 `/api/finance/analyze` 的核心回應 shape 一致。
- [ ] 測試缺少新欄位時會 fail，防止回歸成舊格式。

**Acceptance Criteria:**

- 每個分析 endpoint 都能回傳一般人與研究者都需要的欄位。
- 合約測試可在 CI 跑，不依賴外部網路。
- 舊服務或舊 schema 不會被誤認為通過。

### Task 2：加入版本與 Schema Freshness Guard

**Files:**

- Modify: `backend/app/main.py`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/components/EnvironmentNotice.tsx` 或產品 shell

**Steps:**

- [ ] 後端新增 `/api/health/schema` 或擴充 health endpoint，回傳 `api_version`、`schema_version`、`build_time`、`git_sha`。
- [ ] 前端啟動時讀取 schema version，若低於 UI 需要版本，顯示「後端版本過舊」警示。
- [ ] 在開發文件加入重啟後端與確認版本的檢查步驟。

**Acceptance Criteria:**

- 當後端仍是舊版本時，前端不會安靜地缺少白話摘要。
- 開發者能在 30 秒內確認目前跑的是不是最新 schema。

---

## 6. P0 改動：第一屏讓一般人先讀懂

**目的：** 使用者上傳資料後，第一眼看到的是「結論與怎麼讀」，不是一堆不知意義的指標。

### Task 3：統一三大分析頁第一屏

**Files:**

- Modify: `frontend/src/components/AnalysisResult.tsx`
- Modify: `frontend/src/components/ModelAnalysisPanel.tsx`
- Modify: `frontend/src/components/FinancialAnalysisPanel.tsx`
- Modify: `frontend/src/components/InsightExplainers.tsx`
- Create: `frontend/src/components/__tests__/AnalysisResult.explainability.test.tsx`
- Create: `frontend/src/components/__tests__/ModelAnalysisPanel.explainability.test.tsx`
- Create: `frontend/src/components/__tests__/FinancialAnalysisPanel.explainability.test.tsx`

**Required First-Screen Order:**

1. 分析狀態與資料來源
2. 一句話結論 `plain_summary.headline`
3. 可信度 `confidence.level`
4. 四格白話摘要：發生什麼、為什麼重要、風險、下一步
5. 主要證據 2 到 4 個
6. 技術指標與圖表
7. 研究細節

**Steps:**

- [ ] 資料分析頁：確認 `InsightHeadline` 與 `PlainSummaryGrid` 在資料品質表格之前。
- [ ] 模型分析頁：確認模型分數前先出現模型是否可相信、為什麼、下一步。
- [ ] 金融分析頁：確認預測可信度與風險提示在預測圖與 KPI 前。
- [ ] 三頁都放置閱讀深度控制，且 `simple` 模式不顯示過量技術細節。
- [ ] 為每頁補測試，驗證 DOM 順序與可見文案。

**Acceptance Criteria:**

- 一般使用者不需要展開抽屜，就能知道這次分析最重要結論。
- 第一屏不會先用 RSI、MACD、RMSE、VaR 等詞作為主要入口。
- `simple` 模式下仍保留風險提示，不因簡化而隱藏限制。

### Task 4：KPI 卡加上「這次代表什麼」

**Files:**

- Create: `frontend/src/components/analysis/IndicatorKpiCard.tsx`
- Modify: `frontend/src/components/FinancialAnalysisPanel.tsx`
- Modify: `frontend/src/components/ModelAnalysisPanel.tsx`
- Modify: `frontend/src/components/InsightExplainers.tsx`
- Modify: `backend/app/services/metric_glossary.py`

**Steps:**

- [ ] KPI 卡不只顯示數字，必須顯示 `plain_meaning` 或 `this_run_interpretation`。
- [ ] RSI 顯示「接近 50，偏中性」這類本次解讀。
- [ ] MACD 顯示「MACD 低於 signal，短線偏弱」這類本次解讀。
- [ ] VaR 顯示「依過去資料，單期下跌超過約 X% 的情境約落在最差 5%」。
- [ ] 模型指標如 RMSE、MAE、R2、Accuracy、F1 都要有同樣處理。

**Acceptance Criteria:**

- 每張 KPI 卡至少包含：標籤、數值、白話解釋、可信度或注意事項。
- 一般人可以只看 KPI 卡就知道數字方向是好、壞、中性或需要保守。

---

## 7. P0 改動：金融預測防誤解

**目的：** 防止一般人把系統預測圖當成投資建議或確定事件。

### Task 5：強化 Forecast Reliability Banner

**Files:**

- Create: `frontend/src/components/analysis/ForecastReliabilityBanner.tsx`
- Modify: `frontend/src/components/FinancialAnalysisPanel.tsx`
- Modify: `backend/app/services/insight_narrative.py`
- Modify: `backend/app/services/financial_analyzer.py`
- Create: `frontend/src/components/__tests__/FinancialAnalysisPanel.explainability.test.tsx`

**Steps:**

- [ ] 將 `forecast_reliability` 警示放在預測圖之前。
- [ ] 文案固定包含「基準情境估計」、「不是投資建議」、「可信度」、「主要限制」。
- [ ] 當 `should_show_warning` 為 true，使用更高視覺權重，不能只放在小字說明。
- [ ] 當預測值與最新值偏離過大，圖表標題與 legend 改為「基準情境估計」，避免使用「預測價格」。
- [ ] 研究模式顯示偏離率、方法、資料視窗、是否回測。

**Acceptance Criteria:**

- 使用者在看到預測線前，已經看到可信度與限制。
- 圖表不再暗示這是一個確定價格預測。
- 螢幕閱讀器也能讀到風險提示。

### Task 6：金融時間序列改用交易日邏輯

**Files:**

- Modify: `backend/app/services/financial_analyzer.py`
- Modify: `backend/tests/test_financial_analyzer.py`

**Steps:**

- [ ] 預測日期預設跳過週末。
- [ ] 若資料頻率是日資料且市場資料有休市缺口，缺失值說明要區分「休市」與「資料品質問題」。
- [ ] 在 `research_details` 加入資料頻率判斷與日期處理規則。
- [ ] 加測 FRED S&P 500 fixture，確認預測點不落在週六、週日。

**Acceptance Criteria:**

- 金融資料不會產生週末預測點作為主要顯示結果。
- 缺失值不會一律被說成資料壞掉。

---

## 8. P1 改動：研究者模式可重現

**目的：** 讓想深入研究的人能檢查方法、重現結果、下載中間資料。

### Task 7：補完整 Research Run Manifest

**Files:**

- Create: `frontend/src/components/analysis/ResearchRunManifest.tsx`
- Modify: `backend/app/services/insight_narrative.py`
- Modify: `backend/app/services/dataset_analyzer.py`
- Modify: `backend/app/services/model_runner.py`
- Modify: `backend/app/services/financial_analyzer.py`
- Modify: `frontend/src/components/InsightExplainers.tsx`

**Required Fields:**

- `run_id`
- `dataset_hash`
- `source_filename`
- `row_count`
- `column_count`
- `detected_date_column`
- `detected_target_or_price_column`
- `cleaning_steps`
- `dropped_rows`
- `missing_value_policy`
- `method`
- `parameters`
- `assumptions`
- `limitations`
- `artifacts`
- `created_at`

**Steps:**

- [ ] 後端三種分析都回傳一致的 run manifest。
- [ ] 研究抽屜用表格與可複製 JSON 顯示 manifest。
- [ ] 下載連結使用現有 artifact access 機制，不直接公開靜態路徑。
- [ ] 文件說明 manifest 如何用於重現分析。

**Acceptance Criteria:**

- 研究者能根據 UI 中的 manifest 解釋這次結果如何產生。
- 每張圖表都能追到原始資料或產物。

### Task 8：補上金融回測與預測誤差

**Files:**

- Modify: `backend/app/services/financial_analyzer.py`
- Modify: `backend/app/services/insight_narrative.py`
- Modify: `backend/tests/test_financial_analyzer.py`
- Modify: `frontend/src/components/FinancialAnalysisPanel.tsx`

**Steps:**

- [ ] 對時間序列預測做簡單 holdout backtest。
- [ ] 回傳 MAE、MAPE 或其他適合的誤差指標。
- [ ] 若資料不足以回測，明確顯示「未回測，不適合作為決策依據」。
- [ ] `forecast_reliability.level` 納入回測誤差，而不只看偏離率。

**Acceptance Criteria:**

- 金融預測不再只有估計線，還有「過去測試準不準」。
- 使用者可以知道這次預測是高、中、低可信度的原因。

### Task 9：圖表故事與圖表資料下載

**Files:**

- Modify: `backend/app/services/financial_analyzer.py`
- Modify: `backend/app/services/model_runner.py`
- Modify: `backend/app/services/report_generator.py`
- Modify: `frontend/src/components/InsightExplainers.tsx`
- Modify: `frontend/src/components/FinancialAnalysisPanel.tsx`
- Modify: `frontend/src/components/ModelAnalysisPanel.tsx`

**Steps:**

- [ ] 每張圖表都回傳 `chart_story`：看什麼、這次重點、不能證明什麼、下一步。
- [ ] 每張圖表都回傳 plotted data artifact。
- [ ] 前端圖表下方顯示簡短故事，研究模式顯示下載。
- [ ] 報告匯出使用同一份 chart story，不另寫一套文案。

**Acceptance Criteria:**

- 一般人看得懂圖表重點。
- 研究者能拿到圖表背後資料。

---

## 9. P1 改動：報告改成雙層輸出

**目的：** 報告可以給主管或老師看，也可以給研究者檢查。

### Task 10：建立雙層報告結構

**Files:**

- Modify: `backend/app/services/report_generator.py`
- Modify: `frontend/src/app/reports/page.tsx`
- Modify: `frontend/src/components/AgentReportPanel.tsx`
- Modify: `README.md`

**Required Report Sections:**

1. 一頁式摘要
2. 主要結論
3. 可信度與限制
4. 指標白話翻譯
5. 圖表解讀
6. 建議下一步
7. 研究附錄
8. 資料來源與引用
9. 方法與參數
10. 原始產物清單

**Steps:**

- [ ] 報告前半部使用一般人語言。
- [ ] 報告後半部加入研究附錄。
- [ ] 金融資料必須顯示資料來源與非投資建議。
- [ ] 報告中的指標解釋與 UI 共用後端字典。

**Acceptance Criteria:**

- 報告可直接交給非資料科學背景讀者。
- 研究者能從附錄查到方法與限制。

---

## 10. P2 改動：使用者理解度與產品品質驗收

**目的：** 不能只用單元測試證明功能存在，還要證明目標使用者真的讀懂。

### Task 11：一般人理解度測試

**Files:**

- Create: `docs/testing/layperson-comprehension-test-script.md`
- Modify: `PROGRESS.md`

**Test Design:**

- 招募 5 位非資料科學背景使用者。
- 任務：上傳 FRED S&P 500 或類似金融資料。
- 觀察：他們能否在 3 分鐘內說出分析結論、風險、可信度與下一步。
- 禁止引導：測試者不能解釋 RSI、MACD、VaR。

**Pass Criteria:**

- 至少 4/5 位能正確說出「這不是投資建議」。
- 至少 4/5 位能正確說出「短線偏弱」與「可信度中或需保守」。
- 至少 4/5 位能分辨「歷史風險指標」與「未來預測」。

### Task 12：研究者可重現性測試

**Files:**

- Create: `docs/testing/researcher-reproducibility-test-script.md`
- Modify: `PROGRESS.md`

**Test Design:**

- 招募 3 位資料科學學生或分析師。
- 任務：根據研究模式資訊，重現一次金融分析或模型分析。
- 觀察：是否能找到資料處理、方法、參數、圖表資料與限制。

**Pass Criteria:**

- 至少 2/3 位能根據 manifest 重現核心指標。
- 至少 2/3 位能指出模型或預測限制。
- 至少 2/3 位認為研究模式資訊足以進一步分析。

### Task 13：瀏覽器與可及性驗收

**Files:**

- Modify: frontend component tests
- Modify: `frontend/src/app/product-interface.css`
- Modify: `frontend/src/app/product-motion.css`

**Steps:**

- [ ] 桌面寬度測試資料、模型、金融、報告流程。
- [ ] 手機寬度測試第一屏摘要、閱讀深度控制、研究抽屜。
- [ ] 鍵盤操作可切換閱讀深度與展開研究細節。
- [ ] Reduced motion 模式不依賴動畫理解內容。
- [ ] 警示文字顏色符合可讀性要求。

**Acceptance Criteria:**

- 一般人摘要在手機上仍是第一優先。
- 研究模式在手機上不破版。
- 沒有只能靠滑鼠 hover 才能讀到的重要資訊。

---

## 11. 建議執行順序

### Sprint 1：合約與第一屏

1. Task 1：Explainability API contract tests
2. Task 2：Schema freshness guard
3. Task 3：三大分析頁第一屏統一
4. Task 4：KPI 卡本次解讀

**完成定義：** 所有主要分析路徑都能保證回傳解釋欄位，前端第一屏能讓一般人讀懂。

### Sprint 2：金融預測與研究模式

1. Task 5：Forecast reliability banner
2. Task 6：交易日邏輯
3. Task 7：Research run manifest
4. Task 8：金融回測與預測誤差

**完成定義：** 金融分析不再容易被誤讀，研究者能追溯方法與產物。

### Sprint 3：報告與驗收

1. Task 9：圖表故事與圖表資料下載
2. Task 10：雙層報告
3. Task 11：一般人理解度測試
4. Task 12：研究者可重現性測試
5. Task 13：瀏覽器與可及性驗收

**完成定義：** 系統不只功能可用，也能證明不同背景使用者真的能讀懂或深挖。

---

## 12. 優缺點分析

### 12.1 目前系統優點

- 已有真實資料上傳與分析能力，不是純展示產品。
- 後端已開始建立白話摘要、可信度與指標字典，方向正確。
- 前端已有閱讀深度控制與解釋型元件，具備逐層揭露的基礎。
- 金融分析涵蓋常見指標與圖表，對資料科學入門學習有價值。
- 報告功能已具備延伸成「交付成果」的基礎。

### 12.2 目前系統缺點

- 使用者理解度尚未被測試，不能只靠開發者判斷「應該看得懂」。
- 金融預測仍有誤讀風險，尤其視覺上看起來像確定預測。
- 研究模式資料尚未完整到可重現。
- 部分 API 或服務可能仍跑舊格式，需要版本檢查。
- 缺失值、休市、資料品質等概念需要更精準說明。

### 12.3 改動後優點

- 一般人可以先讀結論，不會被技術名詞擋住。
- 深度研究者可以展開方法與原始資料，不會被過度簡化限制。
- API 合約固定後，前後端不容易不同步。
- 金融預測風險更清楚，產品責任邊界更安全。
- 使用者測試會讓產品判斷從主觀感覺變成可驗收標準。

### 12.4 改動後代價

- 後端 schema 與測試會變多，開發初期速度會稍慢。
- 前端需要更嚴格控制資訊層級，不能隨意堆卡片。
- 研究模式需要維護 artifact、manifest、回測與文件。
- 使用者測試需要時間，但這是確認產品是否真的可讀的必要成本。

---

## 13. 驗證命令

### 後端

```bash
cd backend
pytest
pytest tests/test_explainability_contract.py
pytest tests/test_financial_analyzer.py
```

### 前端

```bash
cd frontend
npm run typecheck
npm run test:run
npm run build
```

### 真實資料煙霧測試

```bash
curl -L "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500" -o /tmp/fred_sp500.csv
curl -X POST "http://127.0.0.1:8000/api/finance/analyze" -F "file=@/tmp/fred_sp500.csv"
```

回應必須包含：

- `plain_summary`
- `confidence`
- `evidence`
- `terms`
- `chart_stories`
- `forecast_reliability`
- `research_details`

---

## 14. 完成定義

本計畫完成時，系統必須滿足以下條件：

- 一般人能在第一屏讀到結論、可信度、風險與下一步。
- 每個主要技術指標都有白話解釋與本次數字解讀。
- 金融預測明確標示為基準情境估計，且不被視覺誤導成確定投資預測。
- 研究者能找到資料處理、方法、參數、限制、回測、原始圖表資料與 run manifest。
- API contract tests 能防止白話欄位或研究欄位消失。
- 真實 FRED S&P 500 資料煙霧測試可通過。
- 5 位非資料科學背景測試者中至少 4 位能正確說出分析結論、主要風險、可信度與下一步。
- 3 位研究者中至少 2 位能根據研究模式重現核心指標或指出方法限制。

