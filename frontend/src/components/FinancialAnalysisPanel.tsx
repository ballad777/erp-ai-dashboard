"use client";

import { useId, useMemo, useRef, useState } from "react";
import {
  BarChart3,
  ChevronDown,
  Download,
  Play,
  TrendingUp
} from "lucide-react";
import { useFeedback } from "@/components/FeedbackProvider";
import {
  ChartStoryPanel,
  EvidenceList,
  InsightHeadline,
  MetricExplainer,
  PlainSummaryGrid,
  ResearchDetailsDrawer,
  useReadingDepth
} from "@/components/InsightExplainers";
import { useLocale } from "@/components/LocaleProvider";
import {
  AnalysisLoadingState,
  InlineNotice,
  ResultReveal
} from "@/components/PagePrimitives";
import {
  useWorkspacePanelState,
  workspaceSourceKey
} from "@/components/WorkspaceProvider";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import {
  analyzeFinance,
  analyzeMergedFinance,
  cancelAnalysisJob,
  type AnalysisJobProgress,
  type DatasetAnalysis,
  type FinancialAnalysis
} from "@/lib/api";

type FinancialAnalysisPanelProps = {
  dataset: DatasetAnalysis;
  file?: File;
  files?: File[];
  isMerged?: boolean;
  title?: string;
  description?: string;
};

const dateNameHints = ["date", "datetime", "timestamp", "time", "day", "日期", "時間", "交易日"];
const priceNameHints = [
  "close",
  "adj_close",
  "adjusted_close",
  "price",
  "last",
  "settle",
  "nav",
  "收盤",
  "價格",
  "股價",
  "淨值"
];

export function FinancialAnalysisPanel({
  dataset,
  file,
  files = [],
  isMerged = false,
  title = "金融分析模式",
  description = "偵測日期與價格/指數/數值欄位後，產生 MA、報酬率、波動率、RSI、MACD 與金融圖表。"
}: FinancialAnalysisPanelProps) {
  const { isEnglish, text } = useLocale();
  const { playError, playSuccess } = useFeedback();
  const dateCandidates = useMemo(() => rankDateColumns(dataset), [dataset]);
  const priceCandidates = useMemo(() => rankPriceColumns(dataset), [dataset]);
  const sourceKey = workspaceSourceKey(file, files, isMerged);
  const [dateColumn, setDateColumn] = useWorkspacePanelState(
    `${sourceKey}:finance:date-column`,
    "__auto__"
  );
  const [priceColumn, setPriceColumn] = useWorkspacePanelState(
    `${sourceKey}:finance:price-column`,
    "__auto__"
  );
  const [result, setResult] =
    useWorkspacePanelState<FinancialAnalysis | null>(
      `${sourceKey}:finance:result`,
      null
    );
  const [error, setError] = useWorkspacePanelState<string | null>(
    `${sourceKey}:finance:error`,
    null
  );
  const [isLoading, setIsLoading] = useWorkspacePanelState(
    `${sourceKey}:finance:loading`,
    false
  );
  const [jobProgress, setJobProgress] = useState<AnalysisJobProgress | null>(null);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [isCancelling, setIsCancelling] = useState(false);

  const hasFinancialShape = dateCandidates.length > 0 && priceCandidates.length > 0;

  if (!hasFinancialShape) {
    return (
      <section className="analysis-tool-panel finance-unavailable">
        <span className="empty-state-icon">
          <TrendingUp aria-hidden="true" />
        </span>
        <div>
          <h2>{isEnglish && title === "金融分析模式" ? "Financial analysis mode" : title}</h2>
          <p>
            {text(
              "目前資料沒有同時偵測到日期與價格/指數/數值欄位，因此尚不能計算金融指標。可回到資料頁確認欄位名稱與型別，或改用模型分析。",
              "The dataset does not contain both a detectable date column and numeric price / index / value column. Review column names and types, or use model analysis instead."
            )}
          </p>
        </div>
        <dl>
          <div><dt>{text("日期候選", "Date candidates")}</dt><dd>{dateCandidates.length}</dd></div>
          <div><dt>{text("價格候選", "Price candidates")}</dt><dd>{priceCandidates.length}</dd></div>
        </dl>
      </section>
    );
  }

  async function handleAnalyzeFinance() {
    if (isMerged && files.length < 2) {
      setError(text("合併金融分析至少需要 2 個成功讀取的檔案。", "Merged financial analysis needs at least two successfully ingested files."));
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);
    setJobProgress(null);
    setActiveJobId(null);
    const startedAt = performance.now();

    try {
      const nextResult = isMerged
        ? await analyzeMergedFinance(files, dateColumn, priceColumn, {
            onProgress: setJobProgress,
            onJobCreated: setActiveJobId
          })
        : await analyzeFinance(assertSingleFile(file), dateColumn, priceColumn, {
            onProgress: setJobProgress,
            onJobCreated: setActiveJobId
          });
      setResult(nextResult);
      if (performance.now() - startedAt >= 3000) playSuccess();
    } catch (caughtError) {
      const message = caughtError instanceof Error ? caughtError.message : text("金融分析失敗。", "Financial analysis failed.");
      setError(message);
      if (!isCancellationMessage(message)) playError();
    } finally {
      setIsLoading(false);
      setActiveJobId(null);
    }
  }

  async function handleCancelAnalysis() {
    if (!activeJobId) return;
    setIsCancelling(true);
    try {
      await cancelAnalysisJob(activeJobId);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : text("無法取消目前分析。", "Unable to cancel the current analysis.")
      );
    } finally {
      setIsCancelling(false);
    }
  }

  return (
    <section className="analysis-tool-panel" aria-busy={isLoading}>
      <div className="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
        <div className="max-w-4xl">
          <div className="text-base font-semibold text-brand">{text("金融洞察", "Financial insight")}</div>
          <h2 className="mt-2 text-2xl font-semibold text-ink">{isEnglish && title === "金融分析模式" ? "Financial analysis mode" : title}</h2>
          <p className="ui-copy-secondary mt-3 text-base leading-7">
            {isEnglish && description.startsWith("偵測日期")
              ? "Detect date and price / index / value columns, then calculate moving averages, returns, volatility, RSI, MACD, and financial charts."
              : description}
          </p>
        </div>
        <Button
          type="button"
          onClick={handleAnalyzeFinance}
          disabled={isLoading}
          variant="premium"
          size="lg"
        >
          {isLoading ? <Spinner /> : <Play aria-hidden="true" />}
          {isLoading ? text("金融分析中", "Analyzing finance") : text("執行金融分析", "Run financial analysis")}
        </Button>
      </div>

      <div className="mt-7 grid gap-5 2xl:grid-cols-[minmax(260px,340px)_1fr]">
        <div className="grid gap-4">
          <label className="block">
            <span className="text-base font-semibold text-ink">{text("日期欄位", "Date column")}</span>
            <select
              name="financial-date-column"
              autoComplete="off"
              value={dateColumn}
              onChange={(event) => {
                setDateColumn(event.target.value);
                setResult(null);
                setError(null);
              }}
              className="mt-2 h-12 w-full rounded-md border border-line bg-white px-4 text-base text-ink outline-none transition focus:border-brand focus:ring-2 focus:ring-teal-100"
            >
              <option value="__auto__">{text("系統自動判斷", "Detect automatically")}</option>
              {dataset.columns.map((column) => (
                <option key={column} value={column}>
                  {column}
                </option>
              ))}
            </select>
          </label>

          <label className="block">
            <span className="text-base font-semibold text-ink">{text("價格/指數/數值欄位", "Price / index / value column")}</span>
            <select
              name="financial-price-column"
              autoComplete="off"
              value={priceColumn}
              onChange={(event) => {
                setPriceColumn(event.target.value);
                setResult(null);
                setError(null);
              }}
              className="mt-2 h-12 w-full rounded-md border border-line bg-white px-4 text-base text-ink outline-none transition focus:border-brand focus:ring-2 focus:ring-teal-100"
            >
              <option value="__auto__">{text("系統自動判斷", "Detect automatically")}</option>
              {dataset.columns.map((column) => (
                <option key={column} value={column}>
                  {column}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <MiniMetric label={text("日期候選", "Date candidates")} value={dateCandidates.slice(0, 3).join("、")} />
          <MiniMetric label={text("價格候選", "Price candidates")} value={priceCandidates.slice(0, 3).join("、")} />
          <MiniMetric label={text("資料來源", "Data source")} value={isMerged ? text(`${files.length} 個檔案合併`, `${files.length} merged files`) : text("單一檔案", "Single file")} />
        </div>
      </div>

      {error ? (
        <InlineNotice tone="error" title={text("金融分析無法執行", "Financial analysis cannot run")}>
          {error}
        </InlineNotice>
      ) : null}

      {isLoading ? (
        <AnalysisLoadingState
          title={text("正在計算金融訊號", "Calculating financial signals")}
          steps={[
            text("排序時間序列與處理價格/指數/數值", "Sorting the time series and preparing values"),
            text("計算報酬、風險與技術指標", "Calculating returns, risk, and technical indicators"),
            text("建立趨勢圖與預測結果", "Building trend charts and forecast results")
          ]}
          progress={jobProgress}
          onCancel={activeJobId ? handleCancelAnalysis : undefined}
          isCancelling={isCancelling}
        />
      ) : null}

      {result ? (
        <ResultReveal>
          <FinancialResult result={result} />
        </ResultReveal>
      ) : null}
    </section>
  );
}

function FinancialResult({ result }: { result: FinancialAnalysis }) {
  const { text } = useLocale();
  const { depth } = useReadingDepth();
  const [activeChart, setActiveChart] = useState(result.charts[0]?.chart_path ?? "");
  const chartTabId = useId();
  const chartTabRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const visibleChart =
    result.charts.find((chart) => chart.chart_path === activeChart) ??
    result.charts[0];
  const visibleChartStory =
    result.chart_stories?.find((story) => story.chart_path === visibleChart?.chart_path) ??
    result.chart_stories?.find((story) => story.chart_type === visibleChart?.chart_type) ??
    result.chart_stories?.[0];

  function handleChartKeyDown(
    event: React.KeyboardEvent<HTMLButtonElement>,
    index: number
  ) {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const nextIndex =
      event.key === "Home"
        ? 0
        : event.key === "End"
          ? result.charts.length - 1
          : event.key === "ArrowRight"
            ? (index + 1) % result.charts.length
            : (index - 1 + result.charts.length) % result.charts.length;
    setActiveChart(result.charts[nextIndex].chart_path);
    chartTabRefs.current[nextIndex]?.focus();
  }

  return (
    <div className="analysis-result-stack">
      <section className="finance-signal">
        <div className="finance-signal-icon">
          <TrendingUp aria-hidden="true" />
        </div>
        <div>
          <span>{text("目前市場訊號", "Current market signal")}</span>
          <h3>{result.trend_label}</h3>
          <p>{result.summary[0] ?? text("金融指標已完成計算。", "Financial indicators have been calculated.")}</p>
        </div>
        <Button asChild variant="outline">
          <a href={result.indicator_url} download>
            <Download aria-hidden="true" />
            {text("指標 CSV", "Indicator CSV")}
          </a>
        </Button>
      </section>

      <InsightHeadline
        title={text("金融結論", "Financial conclusion")}
        summary={result.plain_summary}
        confidence={result.confidence}
        evidence={result.evidence}
      />

      <PlainSummaryGrid summary={result.plain_summary} />

      {result.forecast_reliability?.should_show_warning ? (
        <ForecastReliabilityNotice result={result} />
      ) : null}

      <dl className="result-kpi-strip is-explained">
        <div>
          <dt>{text("最新價格/指數/數值", "Latest price / index / value")}</dt>
          <dd>{formatNumber(result.latest_price)}</dd>
          <small>{text("目前觀察區間最後一期數值。", "The last value in the current observation window.")}</small>
        </div>
        <div>
          <dt>{text("最新報酬率", "Latest return")}</dt>
          <dd>{formatPercent(result.latest_return)}</dd>
          <small>{result.latest_return !== null && result.latest_return < 0 ? text("最近一期下跌。", "The latest period declined.") : text("最近一期上升或持平。", "The latest period rose or stayed flat.")}</small>
        </div>
        <div>
          <dt>{text("波動率", "Volatility")}</dt>
          <dd>{formatPercent(result.latest_volatility)}</dd>
          <small>{volatilityCopy(result.latest_volatility, text)}</small>
        </div>
        <div>
          <dt>RSI</dt>
          <dd>{formatNumber(result.latest_rsi)}</dd>
          <small>{rsiCopy(result.latest_rsi, text)}</small>
        </div>
        <div>
          <dt>VaR 95%</dt>
          <dd>{formatPercent(result.var_95)}</dd>
          <small>{text("歷史估計的單期下行風險。", "Historical single-period downside risk estimate.")}</small>
        </div>
      </dl>

      {depth !== "simple" ? (
        <>
          <EvidenceList evidence={result.evidence} />
          <MetricExplainer terms={result.terms} />
        </>
      ) : null}

      <section className="result-section">
        <div className="result-section-heading">
          <div>
            <span>{text("視覺訊號", "Visual signals")}</span>
            <h3>{text("金融圖表", "Financial charts")}</h3>
          </div>
          <Badge variant="outline">{text(`${result.charts.length} 張`, `${result.charts.length} charts`)}</Badge>
        </div>
        {result.charts.length > 0 ? (
          <>
            <div className="chart-tablist" role="tablist" aria-label={text("金融圖表", "Financial charts")}>
              {result.charts.map((chart, index) => (
                <button
                  key={chart.chart_path}
                  ref={(node) => { chartTabRefs.current[index] = node; }}
                  id={`${chartTabId}-${index}-tab`}
                  type="button"
                  role="tab"
                  aria-selected={visibleChart?.chart_path === chart.chart_path}
                  aria-controls={`${chartTabId}-chart-panel`}
                  tabIndex={visibleChart?.chart_path === chart.chart_path ? 0 : -1}
                  className={visibleChart?.chart_path === chart.chart_path ? "is-active" : ""}
                  onClick={() => setActiveChart(chart.chart_path)}
                  onKeyDown={(event) => handleChartKeyDown(event, index)}
                >
                  <BarChart3 aria-hidden="true" />
                  {chart.title}
                </button>
              ))}
            </div>
            {visibleChart ? (
              <div
                id={`${chartTabId}-chart-panel`}
                role="tabpanel"
                aria-labelledby={`${chartTabId}-${result.charts.indexOf(visibleChart)}-tab`}
              >
                {visibleChartStory ? (
                  <ChartStoryPanel
                    story={visibleChartStory}
                    imageUrl={visibleChart.chart_url}
                    imageAlt={visibleChart.title}
                  />
                ) : (
                  <figure className="featured-chart">
                    <figcaption>
                      <strong>{visibleChart.title}</strong>
                      <span>{visibleChart.chart_path}</span>
                    </figcaption>
                    <img
                      src={visibleChart.chart_url}
                      alt={visibleChart.title}
                      width={1200}
                      height={760}
                      loading="lazy"
                    />
                  </figure>
                )}
                </div>
            ) : null}
          </>
        ) : (
          <p className="tab-empty-state">{text("本次金融分析沒有產生圖表。", "This financial analysis did not generate charts.")}</p>
        )}
      </section>

      <details className="result-disclosure">
        <summary>
          <span>
            <strong>{text("完整金融指標與預測", "Full indicators and forecast")}</strong>
            <small>{text(`摘要、欄位、風險指標與 ${result.forecast_points.length} 期預測`, `Summary, columns, risk metrics, and ${result.forecast_points.length} forecast periods`)}</small>
          </span>
          <ChevronDown aria-hidden="true" />
        </summary>
        <div className="result-disclosure-content finance-detail-stack">
          <ul className="finance-summary-list">
            {result.summary.map((item) => <li key={item}>{item}</li>)}
          </ul>
          <dl className="overview-metric-grid">
            <div><dt>{text("有效日期", "Valid dates")}</dt><dd>{result.row_count_used.toLocaleString()}</dd></div>
            <div><dt>{text("日期欄位", "Date column")}</dt><dd>{result.date_column}</dd></div>
            <div><dt>{text("價格/指數/數值欄位", "Price / index / value column")}</dt><dd>{result.price_column}</dd></div>
            <div><dt>MACD</dt><dd>{formatNumber(result.latest_macd)}</dd></div>
            <div><dt>VaR 99%</dt><dd>{formatPercent(result.var_99)}</dd></div>
            <div><dt>{text("預測期數", "Forecast periods")}</dt><dd>{result.forecast_points.length}</dd></div>
          </dl>
          {result.forecast_points.length > 0 ? (
            <div className="data-table-shell">
              <table>
                <thead>
                  <tr>
                    <th scope="col">{text("預測日期", "Forecast date")}</th>
                    <th scope="col">{text("基準估計值", "Baseline estimate")}</th>
                  </tr>
                </thead>
                <tbody>
                  {result.forecast_points.map((point) => (
                    <tr key={point.date}>
                      <th scope="row">{point.date}</th>
                      <td className="tabular">{formatNumber(point.predicted_price)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </div>
      </details>

      {result.notes.length > 0 ? (
        <InlineNotice tone="warning" title={text("金融分析備註", "Financial analysis notes")}>
          <ul>
            {result.notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </InlineNotice>
      ) : null}
      {depth === "research" ? (
        <ResearchDetailsDrawer
          details={result.research_details}
          title={text("金融研究細節", "Financial research details")}
        />
      ) : null}
      <InlineNotice tone="warning" title={text("使用限制", "Important limitation")}>
        {text(
          "目前資料顯示的結果僅反映本次觀察區間，不構成投資建議。",
          "These results reflect only the current observation window and do not constitute investment advice."
        )}
      </InlineNotice>
    </div>
  );
}

function ForecastReliabilityNotice({ result }: { result: FinancialAnalysis }) {
  const { text } = useLocale();
  const level = result.forecast_reliability?.level ?? "medium";
  return (
    <InlineNotice
      tone={level === "low" ? "warning" : "info"}
      title={text("預測可信度防護", "Forecast reliability guardrail")}
    >
      <p>{result.forecast_reliability?.reason}</p>
      <p>{result.forecast_reliability?.recommended_action}</p>
    </InlineNotice>
  );
}

function rankDateColumns(dataset: DatasetAnalysis): string[] {
  return dataset.columns
    .map((column) => ({
      column,
      score: scoreDateColumn(column, dataset.data_types[column])
    }))
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .map((item) => item.column);
}

function rankPriceColumns(dataset: DatasetAnalysis): string[] {
  return dataset.columns
    .map((column) => ({
      column,
      score: scorePriceColumn(column, Boolean(dataset.numeric_summary[column]))
    }))
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .map((item) => item.column);
}

function scoreDateColumn(column: string, dataType = ""): number {
  const lowered = column.toLowerCase();
  let score = 0;
  if (dateNameHints.some((hint) => lowered.includes(hint))) score += 5;
  if (dataType.includes("datetime")) score += 4;
  if (lowered.includes("created") || lowered.includes("updated")) score += 1;
  return score;
}

function scorePriceColumn(column: string, isNumeric: boolean): number {
  if (!isNumeric) return 0;
  const lowered = column.toLowerCase();
  let score = 1;
  if (priceNameHints.some((hint) => lowered.includes(hint))) score += 5;
  if (lowered.includes("volume") || lowered.includes("成交量")) score -= 3;
  return Math.max(score, 0);
}

function MiniMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="analysis-mini-metric px-5 py-4">
      <div className="ui-metric-label text-sm font-semibold">{label}</div>
      <div className="ui-metric-value mt-1 break-words text-xl font-semibold">{value}</div>
    </div>
  );
}

function formatNumber(value: number | null): string {
  if (value === null) return "-";
  return value.toLocaleString(undefined, { maximumFractionDigits: 4 });
}

function formatPercent(value: number | null): string {
  if (value === null) return "-";
  return `${(value * 100).toLocaleString(undefined, { maximumFractionDigits: 2 })}%`;
}

function volatilityCopy(
  value: number | null,
  text: (traditionalChinese: string, english: string) => string
) {
  if (value === null) return text("目前無法判讀。", "Unavailable.");
  if (value >= 0.05) return text("近期變動幅度偏高。", "Recent movement is high.");
  if (value >= 0.02) return text("近期變動幅度中等。", "Recent movement is moderate.");
  return text("近期變動幅度偏低。", "Recent movement is low.");
}

function rsiCopy(
  value: number | null,
  text: (traditionalChinese: string, english: string) => string
) {
  if (value === null) return text("目前無法判讀。", "Unavailable.");
  if (value >= 70) return text("偏熱，需避免過度追高解讀。", "Elevated; avoid overreading upside.");
  if (value <= 30) return text("偏弱或可能超賣。", "Weak or potentially oversold.");
  return text("接近中性。", "Near neutral.");
}

function assertSingleFile(file: File | undefined): File {
  if (!file) {
    throw new Error("缺少金融分析需要的檔案。");
  }

  return file;
}

function isCancellationMessage(message: string) {
  return message.includes("已取消") || message.toLowerCase().includes("cancelled");
}
