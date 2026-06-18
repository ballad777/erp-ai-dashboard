import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EnvironmentNotice } from "@/components/EnvironmentNotice";
import { LocaleProvider } from "@/components/LocaleProvider";

vi.mock("next/navigation", () => ({
  usePathname: () => "/"
}));

describe("EnvironmentNotice", () => {
  it("states in Traditional Chinese that closed testing rejects sensitive data", () => {
    render(
      <LocaleProvider locale="zh-Hant">
        <EnvironmentNotice />
      </LocaleProvider>
    );

    const notice = screen.getByRole("status");
    expect(notice).toHaveTextContent(
      "目前為封閉測試環境，請勿上傳個資、醫療、財務帳戶或其他敏感資料。"
    );
    expect(
      notice.querySelector('svg[aria-hidden="true"]')
    ).toBeInTheDocument();
  });

  it("provides the corresponding English warning", () => {
    render(
      <LocaleProvider locale="en">
        <EnvironmentNotice />
      </LocaleProvider>
    );

    expect(screen.getByRole("status")).toHaveTextContent(
      "Closed testing environment. Do not upload personal, medical, financial-account, or other sensitive data."
    );
  });
});
