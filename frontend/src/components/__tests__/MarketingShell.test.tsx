import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LocaleProvider } from "@/components/LocaleProvider";
import { MarketingShell } from "@/components/MarketingShell";
import { ThemeProvider } from "@/components/ThemeProvider";

vi.mock("next/navigation", () => ({
  usePathname: () => "/"
}));

describe("MarketingShell", () => {
  it("exposes the theme picker in the primary header", () => {
    render(
      <LocaleProvider locale="zh-Hant">
        <ThemeProvider>
          <MarketingShell>
            <div>內容</div>
          </MarketingShell>
        </ThemeProvider>
      </LocaleProvider>
    );

    expect(screen.getByRole("button", { name: "配色" })).toBeVisible();
  });

  it("mounts the closed-testing notice once directly below the header", () => {
    render(
      <LocaleProvider locale="zh-Hant">
        <ThemeProvider>
          <MarketingShell>
            <div>內容</div>
          </MarketingShell>
        </ThemeProvider>
      </LocaleProvider>
    );

    const notice = screen.getByRole("status");
    expect(notice).toHaveTextContent(
      "目前為封閉測試環境，請勿上傳個資、醫療、財務帳戶或其他敏感資料。"
    );
    expect(
      screen.getByRole("banner").nextElementSibling
    ).toBe(notice);
    expect(
      screen.getAllByText(
        "目前為封閉測試環境，請勿上傳個資、醫療、財務帳戶或其他敏感資料。"
      )
    ).toHaveLength(1);
  });
});
