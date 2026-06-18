import { render, screen, within } from "@testing-library/react";
import { hydrateRoot } from "react-dom/client";
import { renderToString } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import { AppShell } from "@/components/AppShell";
import { FeedbackProvider } from "@/components/FeedbackProvider";
import { LocaleProvider } from "@/components/LocaleProvider";
import {
  PageHeader,
  WorkspaceEmptyState
} from "@/components/PagePrimitives";
import { ThemeProvider } from "@/components/ThemeProvider";

vi.mock("next/navigation", () => ({
  usePathname: () => "/app"
}));

vi.mock("@/components/WorkspaceProvider", () => ({
  useWorkspace: () => ({ isHydrated: true })
}));

vi.mock("@/components/WorkspaceSource", () => ({
  useWorkspaceSources: () => ({
    sources: [],
    completedUploads: []
  }),
  WorkspaceSourceSelect: () => <div>source</div>
}));

describe("AppShell", () => {
  it("exposes the complete workspace navigation including terminology", () => {
    render(
      <LocaleProvider locale="zh-Hant">
        <FeedbackProvider>
          <ThemeProvider>
            <AppShell>
              <div>content</div>
            </AppShell>
          </ThemeProvider>
        </FeedbackProvider>
      </LocaleProvider>
    );

    expect(screen.getAllByRole("link", { name: "總覽" })[0]).toHaveAttribute(
      "href",
      "/app"
    );
    expect(screen.getAllByRole("link", { name: "名詞" })[0]).toHaveAttribute(
      "href",
      "/app/charts"
    );
    expect(screen.getAllByRole("link", { name: "報告" })[0]).toHaveAttribute(
      "href",
      "/app/reports"
    );
    expect(screen.getByRole("button", { name: "配色" })).toBeInTheDocument();
  });

  it("mounts one environment notice below the topbar", () => {
    render(
      <LocaleProvider locale="zh-Hant">
        <FeedbackProvider>
          <ThemeProvider>
            <AppShell>
              <WorkspaceEmptyState title="從第一份資料開始" />
            </AppShell>
          </ThemeProvider>
        </FeedbackProvider>
      </LocaleProvider>
    );

    expect(
      screen.getAllByText(
        "目前為封閉測試環境，請勿上傳個資、醫療、財務帳戶或其他敏感資料。"
      )
    ).toHaveLength(1);
  });

  it("keeps one add-data action in the empty workspace", () => {
    render(
      <LocaleProvider locale="zh-Hant">
        <FeedbackProvider>
          <ThemeProvider>
            <AppShell>
              <>
                <PageHeader
                  title="先看重點"
                  description="依目前工作區決定下一步。"
                  suppressActions
                  actions={<a href="/app/data">加入資料</a>}
                />
                <WorkspaceEmptyState title="從第一份資料開始" />
              </>
            </AppShell>
          </ThemeProvider>
        </FeedbackProvider>
      </LocaleProvider>
    );

    const emptyState = screen
      .getByRole("heading", { name: "從第一份資料開始" })
      .closest("section");
    expect(emptyState).not.toBeNull();
    expect(
      within(emptyState as HTMLElement).getByRole("link", {
        name: "加入資料"
      })
    ).toHaveAttribute("href", "/app/data");
    expect(screen.getAllByRole("link", { name: "加入資料" })).toHaveLength(1);
  });

  it("does not report hydration mismatch when a browser extension annotates shell links", async () => {
    const consoleError = vi
      .spyOn(console, "error")
      .mockImplementation(() => undefined);
    const shell = (
      <LocaleProvider locale="zh-Hant">
        <FeedbackProvider>
          <ThemeProvider>
            <AppShell>
              <div>content</div>
            </AppShell>
          </ThemeProvider>
        </FeedbackProvider>
      </LocaleProvider>
    );
    const container = document.createElement("div");
    container.innerHTML = renderToString(shell);
    container
      .querySelectorAll("a")
      .forEach((link) => link.classList.add("keychainify-checked"));
    document.body.append(container);

    const root = hydrateRoot(container, shell);
    await new Promise((resolve) => window.setTimeout(resolve, 0));

    const hydrationErrors = consoleError.mock.calls.filter((call) =>
      call.some((part) =>
        String(part).includes("A tree hydrated but some attributes")
      )
    );

    root.unmount();
    container.remove();
    consoleError.mockRestore();
    expect(hydrationErrors).toHaveLength(0);
  });
});
