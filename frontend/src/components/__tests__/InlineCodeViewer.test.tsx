import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { InlineCodeViewer } from "@/components/analysis/InlineCodeViewer";
import { LocaleProvider } from "@/components/LocaleProvider";

vi.mock("next/navigation", () => ({
  usePathname: () => "/"
}));

function renderViewer() {
  return render(
    <LocaleProvider locale="zh-Hant">
      <InlineCodeViewer
        pythonContent={"a = 1\nprint(a)"}
        notebookContent={'{"cells":[]}'}
        pythonPath="generated_code.py"
        notebookPath="notebook.ipynb"
      />
    </LocaleProvider>
  );
}

function mockClipboard(writeText: ReturnType<typeof vi.fn>) {
  Object.defineProperty(window.navigator, "clipboard", {
    configurable: true,
    value: { writeText }
  });
}

afterEach(() => {
  Reflect.deleteProperty(window.navigator, "clipboard");
});

describe("InlineCodeViewer", () => {
  it("shows generated code with line numbers and copies the active content", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    mockClipboard(writeText);

    renderViewer();

    expect(screen.getByText("1")).toBeVisible();
    expect(screen.getByText("2")).toBeVisible();
    expect(screen.getByText("generated_code.py")).toBeVisible();

    fireEvent.click(screen.getByRole("button", { name: "複製程式碼" }));

    expect(writeText).toHaveBeenCalledWith("a = 1\nprint(a)");
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "已複製" })).toBeVisible()
    );
  });

  it("switches to notebook content before copying", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    mockClipboard(writeText);

    renderViewer();
    fireEvent.click(screen.getByRole("tab", { name: "Notebook" }));
    fireEvent.click(screen.getByRole("button", { name: "複製程式碼" }));

    expect(screen.getByText("notebook.ipynb")).toBeVisible();
    expect(writeText).toHaveBeenCalledWith('{"cells":[]}');
  });
});
