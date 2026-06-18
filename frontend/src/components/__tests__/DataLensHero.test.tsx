import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataLensHero } from "@/components/DataLensHero";
import { LocaleProvider } from "@/components/LocaleProvider";

vi.mock("next/navigation", () => ({
  usePathname: () => "/"
}));

function renderHero() {
  return render(
    <LocaleProvider locale="zh-Hant">
      <DataLensHero />
    </LocaleProvider>
  );
}

describe("DataLensHero", () => {
  it("renders exactly two indivisible headline lines", () => {
    renderHero();

    const headline = screen.getByRole("heading", { level: 1 });
    const lines = headline.querySelectorAll("[data-hero-line]");
    expect(lines).toHaveLength(2);
    expect(lines[0]).toHaveTextContent("看懂資料");
    expect(lines[1]).toHaveTextContent("找到下一步");
    expect(headline).not.toHaveTextContent("。");
    expect(lines[0]).toHaveClass("whitespace-nowrap");
    expect(lines[1]).toHaveClass("whitespace-nowrap");
  });

  it("links both actions to real product destinations", () => {
    renderHero();

    expect(screen.getByRole("link", { name: /開始分析/ })).toHaveAttribute(
      "href",
      "/app/data"
    );
    expect(screen.getByRole("link", { name: /查看運作方式/ })).toHaveAttribute(
      "href",
      "#journey"
    );
  });

  it("presents the analysis illustration as supporting content", () => {
    renderHero();

    expect(
      screen.getByRole("img", { name: "互動式資料分析示意" })
    ).toBeInTheDocument();
    expect(screen.getByText("年度銷售趨勢分析")).toBeInTheDocument();
    expect(screen.queryByText("sales_2026.csv")).not.toBeInTheDocument();
    expect(screen.getByText("發現 3 個關鍵訊號")).toBeInTheDocument();
  });

  it("describes downloadable outputs without claiming result traceability", () => {
    renderHero();

    expect(screen.getByText("結果可下載")).toBeInTheDocument();
    expect(screen.queryByText("結果可追溯")).not.toBeInTheDocument();
  });
});
