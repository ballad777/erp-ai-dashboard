import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { LocaleProvider } from "@/components/LocaleProvider";
import { ThemePicker } from "@/components/ThemePicker";
import { ThemeProvider } from "@/components/ThemeProvider";

vi.mock("next/navigation", () => ({
  usePathname: () => "/"
}));

const themeVariables = [
  "--product-background",
  "--product-surface",
  "--product-surface-elevated",
  "--product-text-primary",
  "--product-text-secondary",
  "--product-border",
  "--product-accent-primary",
  "--product-accent-secondary",
  "--product-success",
  "--product-warning",
  "--product-danger",
  ...Array.from({ length: 6 }, (_, index) => `--product-chart-${index + 1}`)
];

function renderPicker() {
  return render(
    <LocaleProvider locale="zh-Hant">
      <ThemeProvider>
        <ThemePicker />
      </ThemeProvider>
    </LocaleProvider>
  );
}

describe("ThemePicker", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute("data-product-theme");
    document.documentElement.removeAttribute("data-product-appearance");
    themeVariables.forEach((variable) =>
      document.documentElement.style.removeProperty(variable)
    );
  });

  it("shows a visible theme label instead of relying on an icon alone", () => {
    renderPicker();

    expect(screen.getByRole("button", { name: "配色" })).toHaveTextContent(
      "配色"
    );
  });

  it("opens with all themes and no apply or cancel actions", async () => {
    const user = userEvent.setup();
    renderPicker();

    await waitFor(() =>
      expect(document.documentElement.dataset.productTheme).toBe("mist")
    );
    await user.click(screen.getByRole("button", { name: "配色" }));

    expect(screen.getAllByRole("radio")).toHaveLength(10);
    expect(
      screen.queryByRole("button", { name: "套用配色" })
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "取消" })
    ).not.toBeInTheDocument();
  });

  it("saves the clicked theme immediately and closes the picker", async () => {
    const user = userEvent.setup();
    renderPicker();

    await waitFor(() =>
      expect(document.documentElement.dataset.productTheme).toBe("mist")
    );
    await user.click(screen.getByRole("button", { name: "配色" }));

    await user.click(screen.getByRole("radio", { name: /Deep Sea 深色/ }));
    expect(document.documentElement.dataset.productTheme).toBe("deep-sea");
    expect(localStorage.getItem("finai-product-theme-v1")).toBe("deep-sea");
    expect(document.documentElement.dataset.productAppearance).toBe("dark");
    expect(
      screen.queryByRole("radiogroup", { name: "選擇配色" })
    ).not.toBeInTheDocument();
  });

  it("keeps the applied theme when Escape closes the popover", async () => {
    localStorage.setItem("finai-product-theme-v1", "sage");
    const user = userEvent.setup();
    renderPicker();

    await waitFor(() =>
      expect(document.documentElement.dataset.productTheme).toBe("sage")
    );
    await user.click(screen.getByRole("button", { name: "配色" }));
    await user.click(screen.getByRole("radio", { name: /Midnight 藍黑/ }));

    expect(document.documentElement.dataset.productTheme).toBe("midnight");
    expect(localStorage.getItem("finai-product-theme-v1")).toBe("midnight");
    expect(
      screen.queryByRole("radiogroup", { name: "選擇配色" })
    ).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "配色" }));
    await user.keyboard("{Escape}");

    expect(document.documentElement.dataset.productTheme).toBe("midnight");
    expect(localStorage.getItem("finai-product-theme-v1")).toBe("midnight");
    expect(
      screen.queryByRole("radiogroup", { name: "選擇配色" })
    ).not.toBeInTheDocument();
  });

  it("moves focus with arrow keys and saves only when Enter selects the focused theme", async () => {
    const user = userEvent.setup();
    renderPicker();

    await waitFor(() =>
      expect(document.documentElement.dataset.productTheme).toBe("mist")
    );
    await user.click(screen.getByRole("button", { name: "配色" }));
    const mist = screen.getByRole("radio", { name: /晨霧藍綠/ });
    const atlas = screen.getByRole("radio", { name: /Atlas 藍/ });
    act(() => mist.focus());
    await user.keyboard("{ArrowRight}");

    expect(atlas).toHaveFocus();
    expect(document.documentElement.dataset.productTheme).toBe("mist");
    expect(localStorage.getItem("finai-product-theme-v1")).toBeNull();
    expect(mist).toHaveAttribute("aria-checked", "true");
    expect(atlas).toHaveAttribute("aria-checked", "false");

    await user.keyboard("{Enter}");

    expect(document.documentElement.dataset.productTheme).toBe("atlas");
    expect(localStorage.getItem("finai-product-theme-v1")).toBe("atlas");
    expect(
      screen.queryByRole("radiogroup", { name: "選擇配色" })
    ).not.toBeInTheDocument();
  });

  it("saves the focused theme with Space", async () => {
    const user = userEvent.setup();
    renderPicker();

    await waitFor(() =>
      expect(document.documentElement.dataset.productTheme).toBe("mist")
    );
    await user.click(screen.getByRole("button", { name: "配色" }));
    const mist = screen.getByRole("radio", { name: /晨霧藍綠/ });
    act(() => mist.focus());
    await user.keyboard("{ArrowRight} ");

    expect(document.documentElement.dataset.productTheme).toBe("atlas");
    expect(localStorage.getItem("finai-product-theme-v1")).toBe("atlas");
    expect(
      screen.queryByRole("radiogroup", { name: "選擇配色" })
    ).not.toBeInTheDocument();
  });
});
