import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  InsightHeadline,
  MetricExplainer,
  ReadingDepthControl,
  ResearchDetailsDrawer
} from "@/components/InsightExplainers";
import { LocaleProvider } from "@/components/LocaleProvider";

vi.mock("next/navigation", () => ({
  usePathname: () => "/app/data"
}));

function renderZh(ui: React.ReactElement) {
  return render(<LocaleProvider locale="zh-Hant">{ui}</LocaleProvider>);
}

describe("InsightExplainers", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("persists reading depth selection immediately", async () => {
    const user = userEvent.setup();
    renderZh(<ReadingDepthControl />);

    await user.click(screen.getByRole("button", { name: "研究模式" }));

    expect(window.localStorage.getItem("datapilot-reading-depth")).toBe(
      "research"
    );
    expect(screen.getByRole("button", { name: "研究模式" })).toHaveAttribute(
      "aria-pressed",
      "true"
    );
  });

  it("renders a readable headline with confidence and evidence", () => {
    renderZh(
      <InsightHeadline
        summary={{
          headline: "這份資料可用於銷售預測。",
          next_action: "先確認目標欄位。"
        }}
        confidence={{ level: "medium", reason: "資料品質可接受。" }}
        evidence={[
          { label: "資料規模", value: "100 筆 × 8 欄", source: "資料摘要" }
        ]}
      />
    );

    expect(
      screen.getByRole("heading", { name: "這份資料可用於銷售預測。" })
    ).toBeInTheDocument();
    expect(screen.getByText("可信度中")).toBeInTheDocument();
  });

  it("reveals technical metric details in research mode", async () => {
    const user = userEvent.setup();
    renderZh(
      <>
        <ReadingDepthControl />
        <MetricExplainer
          terms={[
            {
              term: "RMSE",
              plain_explanation: "模型通常會錯多少。",
              technical_definition: "Root Mean Squared Error",
              formula: "sqrt(mean(error^2))",
              how_to_read: "越低越好。",
              caveat: "需搭配 MAE。"
            }
          ]}
        />
      </>
    );

    await user.click(screen.getByRole("button", { name: "研究模式" }));
    await user.click(screen.getByText("RMSE"));

    expect(screen.getByText("Root Mean Squared Error")).toBeInTheDocument();
    expect(screen.getByText("sqrt(mean(error^2))")).toBeInTheDocument();
  });

  it("opens research details in an accessible drawer", async () => {
    const user = userEvent.setup();
    renderZh(
      <ResearchDetailsDrawer
        details={{
          method: "train/test split",
          assumptions: ["固定 random seed"],
          parameters: { seed: 42 },
          limitations: ["尚未交叉驗證"],
          artifacts: ["model_results.xlsx"]
        }}
      />
    );

    await user.click(screen.getByRole("button", { name: "研究細節" }));

    expect(
      screen.getByRole("dialog", { name: "研究細節" })
    ).toBeInTheDocument();
    expect(screen.getByText("train/test split")).toBeInTheDocument();
  });
});
