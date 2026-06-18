"use client";

import { useLocale } from "@/components/LocaleProvider";

export function DatasetMetricStrip({
  rows,
  features,
  models
}: {
  rows: number;
  features: number;
  models: number;
}) {
  const { text } = useLocale();
  const metrics = [
    { label: text("資料列", "Rows"), value: rows },
    { label: text("特徵欄位", "Features"), value: features },
    { label: text("可用模型", "Available models"), value: models }
  ];

  return (
    <dl className="dataset-metric-strip">
      {metrics.map((metric) => (
        <div key={metric.label}>
          <dt className="ui-metric-label">{metric.label}</dt>
          <dd>{metric.value.toLocaleString()}</dd>
        </div>
      ))}
    </dl>
  );
}
