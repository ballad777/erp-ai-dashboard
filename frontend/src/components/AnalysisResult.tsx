"use client";

import { useId, useMemo, useRef, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Columns3,
  ListChecks,
  Sigma
} from "lucide-react";
import {
  EvidenceList,
  InsightHeadline,
  MetricExplainer,
  PlainSummaryGrid,
  ResearchDetailsDrawer,
  useReadingDepth
} from "@/components/InsightExplainers";
import { useLocale } from "@/components/LocaleProvider";
import { InlineNotice } from "@/components/PagePrimitives";
import { Badge } from "@/components/ui/badge";
import type { DatasetAnalysis } from "@/lib/api";

type AnalysisResultProps = {
  result: DatasetAnalysis;
};

type ResultTab = "overview" | "columns" | "missing" | "numeric";

const summaryColumns = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"];
export function AnalysisResult({ result }: AnalysisResultProps) {
  const { text, locale } = useLocale();
  const { depth } = useReadingDepth();
  const tabs: Array<{ id: ResultTab; label: string; icon: typeof ListChecks }> = [
    { id: "overview", label: text("總覽", "Overview"), icon: ListChecks },
    { id: "columns", label: text("欄位", "Columns"), icon: Columns3 },
    { id: "missing", label: text("缺失值", "Missing"), icon: AlertTriangle },
    { id: "numeric", label: text("數值摘要", "Numeric summary"), icon: Sigma }
  ];
  const [activeTab, setActiveTab] = useState<ResultTab>("overview");
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const tabId = useId();
  const numericColumns = Object.entries(result.numeric_summary);
  const missingEntries = Object.entries(result.missing_values);
  const missingColumns = missingEntries
    .filter(([, count]) => count > 0)
    .sort(([, left], [, right]) => right - left);
  const missingTotal = missingEntries.reduce((sum, [, count]) => sum + count, 0);
  const totalCells = result.row_count * Math.max(result.column_count, 1);
  const qualityScore = Math.max(
    0,
    Math.round((1 - missingTotal / Math.max(totalCells, 1)) * 100)
  );

  const typeDistribution = useMemo(() => {
    const counts = new Map<string, number>();
    Object.values(result.data_types).forEach((type) => {
      const family = normalizeType(type, locale);
      counts.set(family, (counts.get(family) ?? 0) + 1);
    });
    return Array.from(counts.entries()).sort(([, left], [, right]) => right - left);
  }, [locale, result.data_types]);

  function handleTabKeyDown(event: React.KeyboardEvent<HTMLButtonElement>, index: number) {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const nextIndex =
      event.key === "Home"
        ? 0
        : event.key === "End"
          ? tabs.length - 1
          : event.key === "ArrowRight"
            ? (index + 1) % tabs.length
            : (index - 1 + tabs.length) % tabs.length;
    setActiveTab(tabs[nextIndex].id);
    tabRefs.current[nextIndex]?.focus();
  }

  return (
    <section className="analysis-result-shell">
      <div className="readable-result-stack">
        <InsightHeadline
          title={text("這份資料可以怎麼用", "How this dataset can be used")}
          summary={result.plain_summary}
          confidence={result.confidence}
          evidence={result.evidence}
        />
        {result.parser_warnings?.length ? (
          <InlineNotice tone="warning" title={text("讀取時已自動修正", "Ingestion adjusted automatically")}>
            {result.parser_warnings.join(" ")}
          </InlineNotice>
        ) : null}
        <PlainSummaryGrid summary={result.plain_summary} />
        {depth !== "simple" ? <EvidenceList evidence={result.evidence} /> : null}
        {depth !== "simple" ? <MetricExplainer terms={result.terms} limit={5} /> : null}
        {depth === "research" ? (
          <ResearchDetailsDrawer
            details={result.research_details}
            title={text("資料研究細節", "Dataset research details")}
          />
        ) : null}
      </div>

      <div className="analysis-result-tabs" role="tablist" aria-label={text("資料探索內容", "Dataset exploration")}>
        {tabs.map((tab, index) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              ref={(node) => { tabRefs.current[index] = node; }}
              id={`${tabId}-${tab.id}-tab`}
              type="button"
              role="tab"
              aria-selected={isActive}
              aria-controls={`${tabId}-${tab.id}-panel`}
              tabIndex={isActive ? 0 : -1}
              className={isActive ? "is-active" : ""}
              onClick={() => setActiveTab(tab.id)}
              onKeyDown={(event) => handleTabKeyDown(event, index)}
            >
              <Icon aria-hidden="true" />
              {tab.label}
              {tab.id === "missing" && missingColumns.length > 0 ? (
                <Badge variant="warning">{missingColumns.length}</Badge>
              ) : null}
            </button>
          );
        })}
      </div>

      <div
        id={`${tabId}-${activeTab}-panel`}
        role="tabpanel"
        aria-labelledby={`${tabId}-${activeTab}-tab`}
        className="analysis-result-panel"
      >
        {activeTab === "overview" ? (
          <OverviewTab
            result={result}
            qualityScore={qualityScore}
            missingTotal={missingTotal}
            missingColumns={missingColumns}
            numericCount={numericColumns.length}
            typeDistribution={typeDistribution}
          />
        ) : null}
        {activeTab === "columns" ? <ColumnsTab result={result} /> : null}
        {activeTab === "missing" ? (
          <MissingTab
            result={result}
            missingEntries={missingEntries}
            missingTotal={missingTotal}
          />
        ) : null}
        {activeTab === "numeric" ? (
          <NumericTab numericColumns={numericColumns} />
        ) : null}
      </div>
    </section>
  );
}

function OverviewTab({
  result,
  qualityScore,
  missingTotal,
  missingColumns,
  numericCount,
  typeDistribution
}: {
  result: DatasetAnalysis;
  qualityScore: number;
  missingTotal: number;
  missingColumns: Array<[string, number]>;
  numericCount: number;
  typeDistribution: Array<[string, number]>;
}) {
  const { text } = useLocale();
  return (
    <div className="data-overview-layout">
      <div className="quality-score-block">
        <span>{text("資料完整度", "Data completeness")}</span>
        <strong>{qualityScore}%</strong>
        <div
          className="quality-track"
          role="progressbar"
          aria-label={text("資料完整度", "Data completeness")}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={qualityScore}
        >
          <span style={{ transform: `scaleX(${qualityScore / 100})` }} />
        </div>
        <p>
          {qualityScore >= 95
            ? text("缺失比例低，可優先進入模型與金融分析。", "Missingness is low, so the dataset can move into model or financial analysis.")
            : text("建議先確認缺失欄位是否會影響目標與關鍵特徵。", "Review whether missing columns affect the target or important features first.")}
        </p>
      </div>

      <dl className="overview-metric-grid">
        <div><dt>{text("資料列", "Rows")}</dt><dd>{result.row_count.toLocaleString()}</dd></div>
        <div><dt>{text("欄位", "Columns")}</dt><dd>{result.column_count.toLocaleString()}</dd></div>
        <div><dt>{text("數值欄位", "Numeric columns")}</dt><dd>{numericCount.toLocaleString()}</dd></div>
        <div><dt>{text("缺失儲存格", "Missing cells")}</dt><dd>{missingTotal.toLocaleString()}</dd></div>
      </dl>

      <div className="overview-insight-grid">
        <section>
          <div className="insight-heading">
            {missingColumns.length > 0 ? (
              <AlertTriangle aria-hidden="true" />
            ) : (
              <CheckCircle2 aria-hidden="true" />
            )}
            <h3>{missingColumns.length > 0 ? text("優先檢查", "Review first") : text("資料完整", "Complete data")}</h3>
          </div>
          {missingColumns.length > 0 ? (
            <ul className="priority-list">
              {missingColumns.slice(0, 5).map(([column, count]) => (
                <li key={column}>
                  <span>{column}</span>
                  <strong>{text(`${count.toLocaleString()} 筆`, `${count.toLocaleString()} rows`)}</strong>
                </li>
              ))}
            </ul>
          ) : (
            <p>{text("所有欄位缺失值皆為 0。", "All columns have zero missing values.")}</p>
          )}
        </section>

        <section>
          <div className="insight-heading">
            <Columns3 aria-hidden="true" />
            <h3>{text("欄位組成", "Column composition")}</h3>
          </div>
          <div className="type-distribution">
            {typeDistribution.map(([type, count]) => (
              <div key={type}>
                <span>{type}</span>
                <strong>{count}</strong>
              </div>
            ))}
          </div>
        </section>

        <section>
          <div className="insight-heading">
            <ListChecks aria-hidden="true" />
            <h3>{text("建議目標欄位", "Suggested targets")}</h3>
          </div>
          {result.recommended_target_columns?.length ? (
            <div className="target-badge-list">
              {result.recommended_target_columns.slice(0, 6).map((column) => (
                <Badge key={column} variant="outline">{column}</Badge>
              ))}
            </div>
          ) : (
            <p>{text("目前沒有明確目標欄位，模型頁仍可手動選擇。", "No clear target was detected, but you can choose one manually in the model workspace.")}</p>
          )}
        </section>
      </div>
    </div>
  );
}

function ColumnsTab({ result }: { result: DatasetAnalysis }) {
  const { text } = useLocale();
  return (
    <div className="data-table-shell">
      <div className="table-context">
        <strong>{text(`${result.column_count.toLocaleString()} 個欄位`, `${result.column_count.toLocaleString()} columns`)}</strong>
        <span>{text("依原始資料順序排列", "Shown in source order")}</span>
      </div>
      <table>
        <thead>
          <tr>
            <th scope="col">{text("欄位名稱", "Column")}</th>
            <th scope="col">{text("資料型別", "Data type")}</th>
            <th scope="col">{text("角色", "Role")}</th>
          </tr>
        </thead>
        <tbody>
          {result.columns.map((column) => (
            <tr key={column}>
              <th scope="row">{column}</th>
              <td><code>{result.data_types[column]}</code></td>
              <td>
                {result.numeric_summary[column] ? (
                  <Badge variant="default">{text("數值", "Numeric")}</Badge>
                ) : (
                  <Badge variant="secondary">{text("文字／類別", "Text / category")}</Badge>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function MissingTab({
  result,
  missingEntries,
  missingTotal
}: {
  result: DatasetAnalysis;
  missingEntries: Array<[string, number]>;
  missingTotal: number;
}) {
  const { text } = useLocale();
  return (
    <div className="data-table-shell">
      <div className="table-context">
        <strong>{text(`${missingTotal.toLocaleString()} 個缺失值`, `${missingTotal.toLocaleString()} missing values`)}</strong>
        <span>{text(`比例以 ${result.row_count.toLocaleString()} 列為基準`, `Ratios use ${result.row_count.toLocaleString()} rows as the baseline`)}</span>
      </div>
      <table>
        <thead>
          <tr>
            <th scope="col">{text("欄位名稱", "Column")}</th>
            <th scope="col">{text("缺失數量", "Missing count")}</th>
            <th scope="col">{text("缺失比例", "Missing ratio")}</th>
            <th scope="col">{text("狀態", "Status")}</th>
          </tr>
        </thead>
        <tbody>
          {missingEntries.map(([column, count]) => {
            const ratio = result.row_count > 0 ? count / result.row_count : 0;
            return (
              <tr key={column}>
                <th scope="row">{column}</th>
                <td className="tabular">{count.toLocaleString()}</td>
                <td className="tabular">{formatPercent(ratio)}</td>
                <td>
                  <Badge variant={count > 0 ? "warning" : "success"}>
                    {count > 0 ? text("需確認", "Review") : text("完整", "Complete")}
                  </Badge>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function NumericTab({
  numericColumns
}: {
  numericColumns: Array<[string, DatasetAnalysis["numeric_summary"][string]]>;
}) {
  const { text } = useLocale();
  if (numericColumns.length === 0) {
    return <p className="tab-empty-state">{text("此資料集沒有偵測到數值欄位。", "No numeric columns were detected in this dataset.")}</p>;
  }

  return (
    <div className="data-table-shell is-wide">
      <div className="table-context">
        <strong>{text(`${numericColumns.length.toLocaleString()} 個數值欄位`, `${numericColumns.length.toLocaleString()} numeric columns`)}</strong>
        <span>{text("統計值最多顯示 4 位小數", "Statistics show up to four decimal places")}</span>
      </div>
      <table>
        <thead>
          <tr>
            <th scope="col">{text("欄位名稱", "Column")}</th>
            {summaryColumns.map((column) => (
              <th scope="col" key={column}>{column}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {numericColumns.map(([column, stats]) => (
            <tr key={column}>
              <th scope="row">{column}</th>
              {summaryColumns.map((statName) => (
                <td key={statName} className="tabular">
                  {formatStat(stats[statName as keyof typeof stats])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function normalizeType(type: string, locale: "zh-Hant" | "en") {
  const lowered = type.toLowerCase();
  if (lowered.includes("int") || lowered.includes("float") || lowered.includes("decimal")) {
    return locale === "en" ? "Numeric" : "數值";
  }
  if (lowered.includes("date") || lowered.includes("time")) return locale === "en" ? "Date / time" : "日期時間";
  if (lowered.includes("bool")) return locale === "en" ? "Boolean" : "布林";
  return locale === "en" ? "Text / category" : "文字／類別";
}

function formatStat(value: number | null): string {
  if (value === null) return "-";
  return Number.isInteger(value)
    ? value.toLocaleString()
    : value.toLocaleString(undefined, { maximumFractionDigits: 4 });
}

function formatPercent(value: number) {
  return `${(value * 100).toLocaleString(undefined, { maximumFractionDigits: 2 })}%`;
}
