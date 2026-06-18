import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LocaleProvider } from "@/components/LocaleProvider";
import { WorkspaceInsightGrid } from "@/components/WorkspaceInsightGrid";

vi.mock("next/navigation", () => ({
  usePathname: () => "/app"
}));

describe("WorkspaceInsightGrid", () => {
  it("shows priorities before detailed metrics", () => {
    render(
      <LocaleProvider locale="zh-Hant">
        <WorkspaceInsightGrid
          insights={[
            "營收具有季節性",
            "北區退貨率偏高",
            "價格與轉換率為非線性"
          ]}
          nextAction={{ label: "比較適合模型", href: "/app/models" }}
          metrics={[
            { label: "資料筆數", value: "12,456" },
            { label: "欄位", value: "28" },
            { label: "完整度", value: "96%" }
          ]}
        />
      </LocaleProvider>
    );

    const headings = screen.getAllByRole("heading");
    expect(headings[0]).toHaveTextContent("最重要的發現");
    expect(
      screen.getByRole("link", { name: "比較適合模型" })
    ).toHaveAttribute("href", "/app/models");
    expect(screen.getByText("12,456")).toBeInTheDocument();
  });

  it("does not invent insights when no real finding is available", () => {
    render(
      <LocaleProvider locale="zh-Hant">
        <WorkspaceInsightGrid
          insights={[]}
          nextAction={{ label: "開始模型分析", href: "/app/models" }}
          metrics={[]}
        />
      </LocaleProvider>
    );

    expect(screen.getByText("尚無可顯示的分析發現")).toBeInTheDocument();
    expect(screen.queryByRole("listitem")).not.toBeInTheDocument();
  });
});
