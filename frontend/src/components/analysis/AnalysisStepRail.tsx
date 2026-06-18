"use client";

import { Check } from "lucide-react";
import { useLocale } from "@/components/LocaleProvider";

export type AnalysisWorkspaceStep = "data" | "method" | "running" | "result";

const orderedSteps: Array<{
  id: AnalysisWorkspaceStep;
  zh: string;
  en: string;
}> = [
  { id: "data", zh: "資料理解", en: "Understand data" },
  { id: "method", zh: "選擇方法", en: "Choose method" },
  { id: "running", zh: "執行分析", en: "Run analysis" },
  { id: "result", zh: "整理結果", en: "Review results" }
];

export function AnalysisStepRail({
  current
}: {
  current: AnalysisWorkspaceStep;
}) {
  const { text } = useLocale();
  const activeIndex = Math.max(
    0,
    orderedSteps.findIndex((step) => step.id === current)
  );

  return (
    <ol className="analysis-step-rail" aria-label={text("分析流程", "Analysis flow")}>
      {orderedSteps.map((step, index) => {
        const status =
          index < activeIndex ? "done" : index === activeIndex ? "active" : "pending";
        return (
          <li
            key={step.id}
            className={`is-${status}`}
            aria-current={status === "active" ? "step" : undefined}
          >
            <span className="analysis-step-index" aria-hidden="true">
              {status === "done" ? <Check /> : index + 1}
            </span>
            <span>{text(step.zh, step.en)}</span>
            <span className="sr-only">
              {status === "done"
                ? text("完成", "Complete")
                : status === "active"
                  ? text("目前步驟", "Current step")
                  : text("尚未開始", "Not started")}
            </span>
          </li>
        );
      })}
    </ol>
  );
}
