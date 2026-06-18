import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { AnalysisModeSelector } from "@/components/analysis/AnalysisModeSelector";
import { AnalysisRecommendationPanel } from "@/components/analysis/AnalysisRecommendationPanel";
import { AnalysisStepRail } from "@/components/analysis/AnalysisStepRail";
import { DatasetMetricStrip } from "@/components/analysis/DatasetMetricStrip";
import { ModelSelectionDrawer } from "@/components/analysis/ModelSelectionDrawer";
import { FeedbackProvider } from "@/components/FeedbackProvider";
import { LocaleProvider } from "@/components/LocaleProvider";
import { ModelAnalysisPanel } from "@/components/ModelAnalysisPanel";
import { AnalysisLoadingState } from "@/components/PagePrimitives";
import { WorkspaceProvider } from "@/components/WorkspaceProvider";
import type { DatasetAnalysis } from "@/lib/api";

vi.mock("next/navigation", () => ({
  usePathname: () => "/"
}));

const datasetWithMissingValues: DatasetAnalysis = {
  file_name: "housing.csv",
  row_count: 1284,
  column_count: 5,
  columns: ["price", "district", "age", "income", "sold"],
  data_types: {
    price: "float64",
    district: "object",
    age: "int64",
    income: "float64",
    sold: "bool"
  },
  missing_values: {
    price: 0,
    district: 3,
    age: 0,
    income: 9,
    sold: 0
  },
  numeric_summary: {},
  recommended_target_columns: ["price", "sold"]
};

const modelOptions = [
  {
    key: "ridge",
    label: "Ridge 迴歸",
    problemType: "regression" as const,
    description: "適合共線性較高的中小型資料。"
  },
  {
    key: "random_forest_classifier",
    label: "隨機森林分類",
    problemType: "classification" as const,
    description: "穩健表格資料分類模型。"
  }
];

function renderZh(ui: React.ReactElement) {
  return render(<LocaleProvider locale="zh-Hant">{ui}</LocaleProvider>);
}

function renderModelPanel(dataset = datasetWithMissingValues) {
  return render(
    <LocaleProvider locale="zh-Hant">
      <FeedbackProvider>
        <WorkspaceProvider>
          <ModelAnalysisPanel
            dataset={dataset}
            title="選擇分析方式"
            description="先確認目標與方法，系統再依真實資料選出候選模型。"
          />
        </WorkspaceProvider>
      </FeedbackProvider>
    </LocaleProvider>
  );
}

describe("analysis workspace components", () => {
  it("does not rotate through fabricated loading steps when backend progress is absent", () => {
    vi.useFakeTimers();
    try {
      renderZh(
        <AnalysisLoadingState
          title="正在分析"
          steps={["第一步", "第二步", "第三步"]}
        />
      );

      expect(screen.getByText("第一步")).toBeVisible();
      act(() => {
        vi.advanceTimersByTime(10_000);
      });
      expect(screen.getByText("第一步")).toBeVisible();
      expect(screen.queryByText("第二步")).not.toBeInTheDocument();
    } finally {
      vi.useRealTimers();
    }
  });

  it("shows one active step and exposes status without relying on color", () => {
    renderZh(<AnalysisStepRail current="method" />);

    expect(screen.getByText("選擇方法").closest("li")).toHaveAttribute(
      "aria-current",
      "step"
    );
    expect(screen.getByText("資料理解").closest("li")).toHaveTextContent(
      "完成"
    );
  });

  it("uses real radio controls for analysis modes", async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    renderZh(<AnalysisModeSelector value="auto" onChange={onChange} />);

    await user.click(screen.getByRole("radio", { name: /迴歸分析/ }));

    expect(onChange).toHaveBeenCalledWith("regression");
  });

  it("renders the dataset metric strip as one semantic summary", () => {
    renderZh(<DatasetMetricStrip rows={1284} features={4} models={8} />);

    expect(screen.getAllByRole("term")[0]).toHaveTextContent("資料列");
    expect(screen.getByText("1,284")).toBeVisible();
    expect(screen.getAllByRole("term")[1]).toHaveTextContent("特徵欄位");
    expect(screen.getByText("8")).toBeVisible();
  });

  it("derives recommendation copy from the dataset profile", () => {
    renderZh(
      <AnalysisRecommendationPanel
        dataset={datasetWithMissingValues}
        targetColumn="price"
        analysisMode="auto"
        availableModelCount={8}
      />
    );

    expect(screen.getByText(/連續數值/)).toBeVisible();
    expect(screen.getByText(/缺失/)).toBeVisible();
    expect(screen.getByText(/8 個候選模型/)).toBeVisible();
  });

  it("filters and toggles models inside a progressive drawer", async () => {
    const onToggle = vi.fn();
    const onClear = vi.fn();
    const user = userEvent.setup();
    renderZh(
      <ModelSelectionDrawer
        open
        options={modelOptions}
        selected={["ridge"]}
        onToggle={onToggle}
        onClear={onClear}
      />
    );

    expect(
      screen.getByRole("region", { name: "手動選擇模型" })
    ).toBeVisible();
    await user.type(screen.getByRole("searchbox", { name: "搜尋模型" }), "森林");

    expect(screen.queryByText("Ridge 迴歸")).not.toBeInTheDocument();
    await user.click(screen.getByRole("checkbox", { name: /隨機森林分類/ }));

    expect(onToggle).toHaveBeenCalledWith("random_forest_classifier");
    await user.click(screen.getByRole("button", { name: "清除選擇" }));
    expect(onClear).toHaveBeenCalled();
  });

  it("focuses the model panel on one next decision before showing advanced controls", async () => {
    const user = userEvent.setup();
    renderModelPanel();

    expect(
      screen.getByRole("heading", { name: "選擇分析方式" })
    ).toBeVisible();
    expect(screen.getByText("清楚的下一步")).toBeVisible();
    expect(
      screen.getByRole("button", { name: "執行模型分析" })
    ).toBeVisible();
    expect(screen.getByText("Quick AutoML")).not.toBeVisible();
    expect(
      screen.queryByRole("checkbox", { name: /^Ridge 迴歸/ })
    ).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "手動選擇模型" }));

    await waitFor(() =>
      expect(
        screen.getByRole("region", { name: "手動選擇模型" })
      ).toBeVisible()
    );
    expect(
      screen.getByRole("checkbox", { name: /^Ridge 迴歸/ })
    ).toBeVisible();
  });
});
