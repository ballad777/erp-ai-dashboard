import type { DatasetAnalysis } from "@/lib/api";

type AnalysisResultProps = {
  result: DatasetAnalysis;
};

const summaryColumns = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"];

export function AnalysisResult({ result }: AnalysisResultProps) {
  const numericColumns = Object.entries(result.numeric_summary);

  return (
    <section className="space-y-7">
      <div className="grid gap-5 md:grid-cols-3">
        <MetricCard label="檔案名稱" value={result.file_name} />
        <MetricCard label="資料筆數" value={result.row_count.toLocaleString()} />
        <MetricCard label="欄位數量" value={result.column_count.toLocaleString()} />
      </div>

      <div className="grid gap-7 xl:grid-cols-[1fr_1fr]">
        <div className="surface-card p-6 sm:p-7">
          <h2 className="text-2xl font-semibold text-ink">欄位清單</h2>
          <div className="mt-4 overflow-hidden rounded-md border border-line">
            <table className="w-full text-left text-base">
              <thead className="bg-slate-50 text-sm uppercase text-muted">
                <tr>
                  <th className="px-5 py-4 font-semibold">欄位名稱</th>
                  <th className="px-5 py-4 font-semibold">資料型別</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {result.columns.map((column) => (
                  <tr key={column}>
                    <td className="px-5 py-4 font-medium text-ink">{column}</td>
                    <td className="px-5 py-4 text-muted">{result.data_types[column]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="surface-card p-6 sm:p-7">
          <h2 className="text-2xl font-semibold text-ink">缺失值統計</h2>
          <div className="mt-4 overflow-hidden rounded-md border border-line">
            <table className="w-full text-left text-base">
              <thead className="bg-slate-50 text-sm uppercase text-muted">
                <tr>
                  <th className="px-5 py-4 font-semibold">欄位名稱</th>
                  <th className="px-5 py-4 font-semibold">缺失數量</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {Object.entries(result.missing_values).map(([column, count]) => (
                  <tr key={column}>
                    <td className="px-5 py-4 font-medium text-ink">{column}</td>
                    <td className="px-5 py-4 text-muted">{count.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="surface-card p-6 sm:p-7">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-2xl font-semibold text-ink">數值欄位摘要</h2>
          <span className="text-base text-muted">
            {numericColumns.length} 個數值欄位
          </span>
        </div>

        {numericColumns.length > 0 ? (
          <div className="mt-4 overflow-x-auto rounded-md border border-line">
            <table className="min-w-[980px] w-full text-left text-base">
              <thead className="bg-slate-50 text-sm uppercase text-muted">
                <tr>
                  <th className="px-5 py-4 font-semibold">欄位名稱</th>
                  {summaryColumns.map((column) => (
                    <th key={column} className="px-5 py-4 font-semibold">
                      {column}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {numericColumns.map(([column, stats]) => (
                  <tr key={column}>
                    <td className="px-5 py-4 font-medium text-ink">{column}</td>
                    {summaryColumns.map((statName) => {
                      const value = stats[statName as keyof typeof stats];
                      return (
                        <td key={statName} className="px-5 py-4 text-muted">
                          {formatStat(value)}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="mt-4 rounded-md border border-line bg-slate-50 p-5 text-base text-muted">
            此資料集中沒有偵測到數值欄位。
          </p>
        )}
      </div>
    </section>
  );
}

function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-blue-100 bg-white/78 p-6 shadow-[0_16px_36px_rgba(15,23,42,0.055)]">
      <div className="text-base font-medium text-muted">{label}</div>
      <div className="mt-2 break-words text-3xl font-semibold text-ink">{value}</div>
    </div>
  );
}

function formatStat(value: number | null): string {
  if (value === null) {
    return "-";
  }

  return Number.isInteger(value)
    ? value.toLocaleString()
    : value.toLocaleString(undefined, { maximumFractionDigits: 4 });
}
