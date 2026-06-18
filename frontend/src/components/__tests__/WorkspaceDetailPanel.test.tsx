import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { WorkspaceDetailPanel } from "@/components/WorkspaceDetailPanel";

describe("WorkspaceDetailPanel", () => {
  it("opens from a trigger, closes with Escape, and restores focus", async () => {
    const user = userEvent.setup();
    render(
      <WorkspaceDetailPanel
        title="模型詳情"
        closeLabel="關閉詳情"
        trigger={<button type="button">開啟詳情</button>}
      >
        <p>Gradient Boosting</p>
        <button type="button">開啟模型工作區</button>
      </WorkspaceDetailPanel>
    );

    const trigger = screen.getByRole("button", { name: "開啟詳情" });
    await user.click(trigger);

    expect(
      screen.getByRole("dialog", { name: "模型詳情" })
    ).toBeInTheDocument();
    expect(screen.getByText("Gradient Boosting")).toBeInTheDocument();
    const closeButton = screen.getByRole("button", { name: "關閉詳情" });
    const actionButton = screen.getByRole("button", {
      name: "開啟模型工作區"
    });
    await waitFor(() => expect(closeButton).toHaveFocus());
    await user.keyboard("{Shift>}{Tab}{/Shift}");
    expect(actionButton).toHaveFocus();
    await user.keyboard("{Tab}");
    expect(closeButton).toHaveFocus();

    await user.keyboard("{Escape}");
    await waitFor(() =>
      expect(
        screen.queryByRole("dialog", { name: "模型詳情" })
      ).not.toBeInTheDocument()
    );
    expect(trigger).toHaveFocus();
  });

  it("closes when the backdrop is pressed", async () => {
    const user = userEvent.setup();
    render(
      <WorkspaceDetailPanel
        title="資料詳情"
        closeLabel="關閉詳情"
        trigger={<button type="button">查看</button>}
      >
        <p>內容</p>
      </WorkspaceDetailPanel>
    );

    await user.click(screen.getByRole("button", { name: "查看" }));
    await user.click(
      screen.getByRole("button", { name: "關閉詳情（背景）" })
    );
    await waitFor(() =>
      expect(
        screen.queryByRole("dialog", { name: "資料詳情" })
      ).not.toBeInTheDocument()
    );
  });
});
