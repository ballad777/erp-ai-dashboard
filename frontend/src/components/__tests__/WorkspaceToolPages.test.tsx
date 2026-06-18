import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { LocaleProvider } from "@/components/LocaleProvider";
import { ChartWorkspace } from "@/components/WorkspaceToolPages";

const workspaceState = vi.hoisted(() => ({
  activeSource: null as null | {
    dataset: {
      terms?: Array<{
        term?: string;
        plain_explanation?: string;
        how_to_read?: string;
        caveat?: string;
        technical_definition?: string;
        formula?: string;
      }>;
    };
    file?: File;
    files: File[];
    label: string;
    detail: string;
    isMerged: boolean;
  },
  panelStates: {} as Record<string, unknown>
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/app/charts"
}));

vi.mock("@/components/WorkspaceSource", () => ({
  useWorkspaceSources: () => ({
    activeSource: workspaceState.activeSource
  }),
  WorkspaceSourceSelect: () => <div>source</div>
}));

vi.mock("@/components/WorkspaceProvider", () => ({
  useWorkspace: () => ({
    panelStates: workspaceState.panelStates
  }),
  workspaceSourceKey: () => "source"
}));

vi.mock("@/components/AgentReportPanel", () => ({
  AgentReportPanel: () => null
}));

vi.mock("@/components/FinancialAnalysisPanel", () => ({
  FinancialAnalysisPanel: () => null
}));

vi.mock("@/components/ModelAnalysisPanel", () => ({
  ModelAnalysisPanel: () => null
}));

function renderChartWorkspace() {
  return render(
    <LocaleProvider locale="zh-Hant">
      <ChartWorkspace />
    </LocaleProvider>
  );
}

afterEach(() => {
  workspaceState.activeSource = null;
  workspaceState.panelStates = {};
});

describe("ChartWorkspace", () => {
  it("hides the add-data action when a source is already available", () => {
    workspaceState.activeSource = {
      dataset: {
        terms: [
          {
            term: "資料完整度",
            plain_explanation: "用來看資料是否有足夠內容可以分析。"
          }
        ]
      },
      file: new File(["a,b\n1,2"], "sales.csv", { type: "text/csv" }),
      files: [],
      label: "sales.csv",
      detail: "100 列 · 8 欄",
      isMerged: false
    };

    renderChartWorkspace();

    expect(
      screen.getByRole("heading", { name: "目前分析會用到的名詞" })
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("link", { name: "加入資料" })
    ).not.toBeInTheDocument();
  });

  it("renders analysis terminology instead of duplicating generated charts", () => {
    workspaceState.activeSource = {
      dataset: {
        terms: []
      },
      file: new File(["a,b\n1,2"], "sales.csv", { type: "text/csv" }),
      files: [],
      label: "sales.csv",
      detail: "100 列 · 8 欄",
      isMerged: false
    };
    workspaceState.panelStates = {
      "source:model:result": {
        terms: [
          {
            term: "RMSE",
            plain_explanation: "模型預測通常會錯多少。",
            how_to_read: "越低越好。",
            caveat: "需要搭配 MAE。",
            technical_definition: "Root Mean Squared Error",
            formula: "sqrt(mean(error^2))"
          }
        ]
      }
    };

    renderChartWorkspace();

    expect(
      screen.getByRole("heading", { name: "目前分析會用到的名詞" })
    ).toBeInTheDocument();
    expect(screen.getByText("模型分析")).toBeInTheDocument();
    expect(screen.getByText("RMSE")).toBeInTheDocument();
    expect(screen.getByText("模型預測通常會錯多少。")).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("keeps one add-data action when no source is available", () => {
    renderChartWorkspace();

    expect(screen.getAllByRole("link", { name: "加入資料" })).toHaveLength(1);
    expect(screen.getByRole("link", { name: "加入資料" })).toHaveAttribute(
      "href",
      "/app/data"
    );
  });
});
