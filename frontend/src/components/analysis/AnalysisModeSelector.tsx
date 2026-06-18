"use client";

import { useLocale } from "@/components/LocaleProvider";

export type AnalysisMode = "auto" | "regression" | "classification";

export function AnalysisModeSelector({
  value,
  onChange
}: {
  value: AnalysisMode;
  onChange: (value: AnalysisMode) => void;
}) {
  const { text } = useLocale();
  const modes = [
    {
      value: "auto" as const,
      label: text("自動選擇", "Automatic"),
      description: text(
        "依目標欄位型態與資料規模選擇候選模型。",
        "Select candidate models from target type and dataset size."
      )
    },
    {
      value: "regression" as const,
      label: text("迴歸分析", "Regression"),
      description: text(
        "預測價格、銷售額或其他連續數值。",
        "Predict prices, sales, or other continuous values."
      )
    },
    {
      value: "classification" as const,
      label: text("分類分析", "Classification"),
      description: text(
        "預測類別、狀態或事件是否發生。",
        "Predict categories, states, or event outcomes."
      )
    }
  ];

  return (
    <fieldset className="analysis-mode-selector">
      <legend>{text("分析模式", "Analysis mode")}</legend>
      <div className="analysis-mode-grid">
        {modes.map((mode) => (
          <label
            key={mode.value}
            className={`${value === mode.value ? "is-selected" : ""} ${
              mode.value === "auto" ? "is-recommended" : ""
            }`}
          >
            <input
              type="radio"
              name="analysis-mode"
              value={mode.value}
              checked={value === mode.value}
              onChange={() => onChange(mode.value)}
            />
            <strong>{mode.label}</strong>
            <span className="ui-option-description">{mode.description}</span>
          </label>
        ))}
      </div>
    </fieldset>
  );
}
