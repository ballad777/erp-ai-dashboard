import { act, renderHook, waitFor } from "@testing-library/react";
import { renderToString } from "react-dom/server";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  ThemeProvider,
  useProductTheme
} from "@/components/ThemeProvider";
import { getTheme, type ThemeId, type ThemeTokens } from "@/lib/themes";

const storageKey = "finai-product-theme-v1";

const cssVariableByToken = {
  background: "--product-background",
  surface: "--product-surface",
  surfaceElevated: "--product-surface-elevated",
  textPrimary: "--product-text-primary",
  textSecondary: "--product-text-secondary",
  border: "--product-border",
  accentPrimary: "--product-accent-primary",
  accentSecondary: "--product-accent-secondary",
  success: "--product-success",
  warning: "--product-warning",
  danger: "--product-danger"
} as const satisfies Record<keyof ThemeTokens, `--product-${string}`>;

const productVariables = [
  ...Object.values(cssVariableByToken),
  ...Array.from(
    { length: 6 },
    (_, index) => `--product-chart-${index + 1}`
  )
];
const legacyVariables = [
  "--color-background",
  "--color-foreground",
  "--color-card",
  "--color-card-foreground",
  "--color-popover",
  "--color-popover-foreground",
  "--color-primary",
  "--color-primary-deep",
  "--color-primary-foreground",
  "--color-secondary",
  "--color-secondary-foreground",
  "--color-muted",
  "--color-muted-foreground",
  "--color-accent",
  "--color-accent-foreground",
  "--color-destructive",
  "--color-border",
  "--color-input",
  "--color-ring",
  "--accent",
  "--accent-blue",
  "--accent-soft",
  "--surface",
  "--surface-solid",
  "--border-soft"
];

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <ThemeProvider>{children}</ThemeProvider>
);

type SelectableThemeContext = ReturnType<typeof useProductTheme> & {
  selectTheme: (theme: ThemeId) => void;
};

function ThemeState() {
  const { appliedTheme } = useProductTheme();

  return <span>{appliedTheme}</span>;
}

function resetRootTheme() {
  const root = document.documentElement;
  root.removeAttribute("data-product-theme");
  root.removeAttribute("data-product-appearance");
  for (const variableName of [...productVariables, ...legacyVariables]) {
    root.style.removeProperty(variableName);
  }
}

function expectRootTheme(themeId: Parameters<typeof getTheme>[0]) {
  const theme = getTheme(themeId);
  const root = document.documentElement;

  expect(root.dataset.productTheme).toBe(theme.id);
  expect(root.dataset.productAppearance).toBe(theme.appearance);

  for (const [tokenName, variableName] of Object.entries(
    cssVariableByToken
  )) {
    expect(root.style.getPropertyValue(variableName)).toBe(
      theme.tokens[tokenName as keyof ThemeTokens]
    );
  }

  theme.chart.forEach((color, index) => {
    expect(
      root.style.getPropertyValue(`--product-chart-${index + 1}`)
    ).toBe(color);
  });
}

describe("ThemeProvider", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    window.localStorage.clear();
    resetRootTheme();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    window.localStorage.clear();
    resetRootTheme();
  });

  it("uses mist for the SSR context state", () => {
    window.localStorage.setItem(storageKey, "atlas");

    expect(
      renderToString(
        <ThemeProvider>
          <ThemeState />
        </ThemeProvider>
      )
    ).toContain("mist");
  });

  it("restores a valid stored theme after hydration", async () => {
    window.localStorage.setItem(storageKey, "atlas");
    const { result } = renderHook(() => useProductTheme(), { wrapper });

    await waitFor(() => {
      expect(result.current.appliedTheme).toBe("atlas");
      expectRootTheme("atlas");
    });
  });

  it("selects Deep Sea immediately and updates state, root variables, appearance, and storage", async () => {
    const { result } = renderHook(() => useProductTheme(), { wrapper });

    await waitFor(() => expectRootTheme("mist"));
    act(() =>
      (result.current as SelectableThemeContext).selectTheme("deep-sea")
    );

    expect(result.current.appliedTheme).toBe("deep-sea");
    expect(window.localStorage.getItem(storageKey)).toBe("deep-sea");
    expectRootTheme("deep-sea");
    expect(document.documentElement.dataset.productAppearance).toBe("dark");
    expect(
      document.documentElement.style.getPropertyValue("--color-background")
    ).toBe("17 23 27");
    expect(
      document.documentElement.style.getPropertyValue("--color-foreground")
    ).toBe("236 242 243");
    expect(
      document.documentElement.style.getPropertyValue("--color-card")
    ).toBe("24 32 37");
    expect(
      document.documentElement.style.getPropertyValue("--color-border")
    ).toBe("51 64 71");
  });

  it("falls back to mist when the stored theme is invalid", async () => {
    window.localStorage.setItem(storageKey, "not-a-theme");
    const { result } = renderHook(() => useProductTheme(), { wrapper });

    await waitFor(() => {
      expect(result.current.appliedTheme).toBe("mist");
      expectRootTheme("mist");
    });
  });

  it("falls back to mist when storage reads throw", async () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("storage read failed");
    });

    const { result } = renderHook(() => useProductTheme(), { wrapper });

    await waitFor(() => {
      expect(result.current.appliedTheme).toBe("mist");
      expectRootTheme("mist");
    });
  });

  it("keeps DOM and state updates when storage writes throw", async () => {
    const { result } = renderHook(() => useProductTheme(), { wrapper });
    await waitFor(() => expectRootTheme("mist"));
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("storage write failed");
    });

    expect(() => {
      act(() =>
        (result.current as SelectableThemeContext).selectTheme("deep-sea")
      );
    }).not.toThrow();
    expect(result.current.appliedTheme).toBe("deep-sea");
    expectRootTheme("deep-sea");
  });
});
