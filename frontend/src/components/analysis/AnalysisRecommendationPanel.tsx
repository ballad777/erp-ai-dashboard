"use client";

import { Sparkles } from "lucide-react";
import { useLocale } from "@/components/LocaleProvider";
import type { DatasetAnalysis } from "@/lib/api";
import type { AnalysisMode } from "./AnalysisModeSelector";

export function AnalysisRecommendationPanel({
  dataset,
  targetColumn,
  analysisMode,
  availableModelCount
}: {
  dataset: DatasetAnalysis;
  targetColumn: string;
  analysisMode: AnalysisMode;
  availableModelCount: number;
}) {
  const { text } = useLocale();
  const targetType = dataset.data_types[targetColumn] ?? "";
  const numericTarget = /int|float|double|decimal/i.test(targetType);
  const missingCells = Object.values(dataset.missing_values).reduce(
    (sum, value) => sum + value,
    0
  );
  const reasons = [
    numericTarget
      ? text(
          `目標欄位「${targetColumn}」是連續數值，適合先以迴歸模型比較。`,
          `Target "${targetColumn}" is numeric, so regression comparison is a suitable first pass.`
        )
      : text(
          `目標欄位「${targetColumn}」偏類別或狀態，適合先以分類模型比較。`,
          `Target "${targetColumn}" looks categorical, so classification comparison is a suitable first pass.`
        ),
    missingCells > 0
      ? text(
          `資料含 ${missingCells.toLocaleString()} 個缺失值，後端會先進行可執行的清理流程。`,
          `The dataset contains ${missingCells.toLocaleString()} missing cells; the backend will run an executable cleaning path first.`
        )
      : text(
          "目前缺失值為 0，模型比較可直接從欄位型態與資料列數開始。",
          "No missing cells were detected, so model comparison can start from schema and row count."
        ),
    text(
      `目前可用 ${availableModelCount.toLocaleString()} 個候選模型，系統會依資料型態篩選。`,
      `${availableModelCount.toLocaleString()} candidate models are available and will be filtered by the dataset profile.`
    )
  ];
  const requestedMode =
    analysisMode === "auto"
      ? text("自動選擇", "Automatic")
      : analysisMode === "regression"
        ? text("迴歸分析", "Regression")
        : text("分類分析", "Classification");

  return (
    <aside className="analysis-recommendation-panel">
      <div className="analysis-recommendation-icon">
        <Sparkles aria-hidden="true" />
      </div>
      <div>
        <span>{text("分析建議", "Analysis recommendation")}</span>
        <h3>{text("先確認方法，再執行模型比較", "Confirm the method, then run model comparison")}</h3>
        <p className="ui-copy-secondary">
          {text("目前模式", "Current mode")}：{requestedMode}
        </p>
      </div>
      <ul>
        {reasons.map((reason) => (
          <li key={reason}>{reason}</li>
        ))}
      </ul>
    </aside>
  );
}
