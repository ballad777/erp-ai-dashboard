"use client";

import { useMemo } from "react";
import {
  useWorkspacePanelState,
  workspaceSourceKey
} from "@/components/WorkspaceProvider";
import {
  analyzeFinance,
  analyzeMergedFinance,
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
  description = "偵測日期與價格欄位後，產生 MA、報酬率、波動率、RSI、MACD 與金融圖表。"
}: FinancialAnalysisPanelProps) {
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

  const hasFinancialShape = dateCandidates.length > 0 && priceCandidates.length > 0;

  if (!hasFinancialShape) {
    return null;
  }

  async function handleAnalyzeFinance() {
    if (isMerged && files.length < 2) {
      setError("合併金融分析至少需要 2 個成功讀取的檔案。");
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const nextResult = isMerged
        ? await analyzeMergedFinance(files, dateColumn, priceColumn)
        : await analyzeFinance(assertSingleFile(file), dateColumn, priceColumn);
      setResult(nextResult);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "金融分析失敗。");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="surface-card border-brand/40 p-6 sm:p-7">
      <div className="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
        <div className="max-w-4xl">
          <div className="text-base font-semibold text-brand">金融洞察</div>
          <h2 className="mt-2 text-2xl font-semibold text-ink">{title}</h2>
          <p className="mt-3 text-base leading-7 text-muted">{description}</p>
        </div>
        <button
          type="button"
          onClick={handleAnalyzeFinance}
          disabled={isLoading}
          className="glow-button h-12 rounded-xl bg-gradient-to-r from-brand via-sky-500 to-navy px-6 text-base font-semibold text-white transition disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {isLoading ? "金融分析中..." : "執行金融分析"}
        </button>
      </div>

      <div className="mt-7 grid gap-5 2xl:grid-cols-[minmax(260px,340px)_1fr]">
        <div className="grid gap-4">
          <label className="block">
            <span className="text-base font-semibold text-ink">日期欄位</span>
            <select
              value={dateColumn}
              onChange={(event) => {
                setDateColumn(event.target.value);
                setResult(null);
                setError(null);
              }}
              className="mt-2 h-12 w-full rounded-md border border-line bg-white px-4 text-base text-ink outline-none transition focus:border-brand focus:ring-2 focus:ring-teal-100"
            >
              <option value="__auto__">系統自動判斷</option>
              {dataset.columns.map((column) => (
                <option key={column} value={column}>
                  {column}
                </option>
              ))}
            </select>
          </label>

          <label className="block">
            <span className="text-base font-semibold text-ink">價格欄位</span>
            <select
              value={priceColumn}
              onChange={(event) => {
                setPriceColumn(event.target.value);
                setResult(null);
                setError(null);
              }}
              className="mt-2 h-12 w-full rounded-md border border-line bg-white px-4 text-base text-ink outline-none transition focus:border-brand focus:ring-2 focus:ring-teal-100"
            >
              <option value="__auto__">系統自動判斷</option>
              {dataset.columns.map((column) => (
                <option key={column} value={column}>
                  {column}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <MiniMetric label="日期候選" value={dateCandidates.slice(0, 3).join("、")} />
          <MiniMetric label="價格候選" value={priceCandidates.slice(0, 3).join("、")} />
          <MiniMetric label="資料來源" value={isMerged ? `${files.length} 個檔案合併` : "單一檔案"} />
        </div>
      </div>

      {error ? (
        <div className="mt-6 rounded-md border border-red-200 bg-red-50 px-5 py-4 text-base font-medium text-red-700">
          {error}
        </div>
      ) : null}

      {result ? <FinancialResult result={result} /> : null}
    </section>
  );
}

function FinancialResult({ result }: { result: FinancialAnalysis }) {
  return (
    <div className="mt-8 space-y-7">
      <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-6">
        <MiniMetric label="訊號" value={result.trend_label} />
        <MiniMetric label="有效日期" value={result.row_count_used.toLocaleString()} />
        <MiniMetric label="最新價格" value={formatNumber(result.latest_price)} />
        <MiniMetric label="報酬率" value={formatPercent(result.latest_return)} />
        <MiniMetric label="波動率" value={formatPercent(result.latest_volatility)} />
        <MiniMetric label="RSI" value={formatNumber(result.latest_rsi)} />
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <MiniMetric label="VaR 95%" value={formatPercent(result.var_95)} />
        <MiniMetric label="VaR 99%" value={formatPercent(result.var_99)} />
        <MiniMetric
          label="預測期數"
          value={`${result.forecast_points.length.toLocaleString()} 期`}
        />
      </div>

      <div className="rounded-2xl border border-blue-100 bg-slate-50/80 p-5">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
          <div>
            <h3 className="text-xl font-semibold text-ink">金融摘要</h3>
            <ul className="mt-3 space-y-2 text-base leading-7 text-muted">
              {result.summary.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <a
            href={result.indicator_url}
            download
            className="rounded-md border border-line bg-white px-5 py-3 text-base font-semibold text-ink transition hover:border-brand hover:text-brand"
          >
            下載指標 CSV
          </a>
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          <MiniMetric label="日期欄位" value={result.date_column} />
          <MiniMetric label="價格欄位" value={result.price_column} />
          <MiniMetric label="MACD" value={formatNumber(result.latest_macd)} />
        </div>
        {result.forecast_points.length > 0 ? (
          <div className="mt-4 overflow-x-auto rounded-md border border-line bg-white">
            <table className="min-w-[520px] w-full text-left text-base">
              <thead className="bg-slate-50 text-sm text-muted">
                <tr>
                  <th className="px-4 py-3 font-semibold">預測日期</th>
                  <th className="px-4 py-3 font-semibold">預測價格</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {result.forecast_points.map((point) => (
                  <tr key={point.date}>
                    <td className="px-4 py-3 text-ink">{point.date}</td>
                    <td className="px-4 py-3 text-muted">
                      {formatNumber(point.predicted_price)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        {result.charts.map((chart) => (
          <figure
            key={chart.chart_path}
            className="rounded-2xl border border-blue-100 bg-slate-50/80 p-5"
          >
            <figcaption className="mb-4 flex flex-col gap-1">
              <span className="text-lg font-semibold text-ink">{chart.title}</span>
              <span className="break-all text-sm text-muted">{chart.chart_path}</span>
            </figcaption>
            <img
              src={chart.chart_url}
              alt={chart.title}
              className="w-full rounded-md border border-line bg-white"
            />
          </figure>
        ))}
      </div>

      {result.notes.length > 0 ? (
        <div className="rounded-md border border-amber-200 bg-amber-50 p-5">
          <h3 className="text-base font-semibold text-amber-900">金融分析備註</h3>
          <ul className="mt-3 space-y-2 text-base leading-7 text-amber-900">
            {result.notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
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
    <div className="rounded-2xl border border-blue-100 bg-white/78 px-5 py-4 shadow-[0_12px_28px_rgba(15,23,42,0.045)]">
      <div className="text-sm font-semibold text-muted">{label}</div>
      <div className="mt-1 break-words text-xl font-semibold text-ink">{value}</div>
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

function assertSingleFile(file: File | undefined): File {
  if (!file) {
    throw new Error("缺少金融分析需要的檔案。");
  }

  return file;
}
