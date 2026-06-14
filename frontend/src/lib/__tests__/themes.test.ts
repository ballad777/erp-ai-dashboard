import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import {
  defaultThemeId,
  getTheme,
  themeIds,
  themes,
  type ProductTheme,
  type ThemeId,
  type ThemeTokens,
} from "@/lib/themes";

const expectedThemeIds = [
  "mist",
  "atlas",
  "iris",
  "clay",
  "sage",
  "frost",
  "graphite",
  "amber",
  "deep-sea",
  "midnight",
] as const;

const expectedTokenKeys = [
  "accentPrimary",
  "accentSecondary",
  "background",
  "border",
  "danger",
  "success",
  "surface",
  "surfaceElevated",
  "textPrimary",
  "textSecondary",
  "warning",
] as const;

const expectedCoreColors = {
  mist: {
    background: "#eef3f5",
    accentPrimary: "#39777e",
    accentSecondary: "#315f8e",
  },
  atlas: {
    background: "#edf2f6",
    accentPrimary: "#315f8e",
    accentSecondary: "#467f84",
  },
  iris: {
    background: "#f1f0f4",
    accentPrimary: "#6b638b",
    accentSecondary: "#4f7281",
  },
  clay: {
    background: "#f3f0ee",
    accentPrimary: "#7b5f52",
    accentSecondary: "#526f76",
  },
  sage: {
    background: "#eef2ef",
    accentPrimary: "#4f6f61",
    accentSecondary: "#4f6682",
  },
  frost: {
    background: "#f7f9fb",
    accentPrimary: "#526b88",
    accentSecondary: "#2f6178",
  },
  graphite: {
    background: "#eff1f2",
    accentPrimary: "#666c75",
    accentSecondary: "#3e6571",
  },
  amber: {
    background: "#f5f2ec",
    accentPrimary: "#806638",
    accentSecondary: "#526d78",
  },
  "deep-sea": {
    background: "#11171b",
    surface: "#182025",
    accentPrimary: "#5b9b96",
    accentSecondary: "#8298b7",
  },
  midnight: {
    background: "#131720",
    surface: "#1b202b",
    accentPrimary: "#7085aa",
    accentSecondary: "#65a09a",
  },
} satisfies Record<
  ThemeId,
  {
    background: string;
    surface?: string;
    accentPrimary: string;
    accentSecondary: string;
  }
>;

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
  danger: "--product-danger",
} as const satisfies Record<keyof ThemeTokens, `--product-${string}`>;

const hexColorPattern = /^#[0-9a-f]{6}$/i;

type Equal<Left, Right> =
  (<Value>() => Value extends Left ? 1 : 2) extends (
    <Value>() => Value extends Right ? 1 : 2
  )
    ? true
    : false;

type WritableKeys<Value> = {
  [Key in keyof Value]-?: Equal<
    { [Property in Key]: Value[Property] },
    { -readonly [Property in Key]: Value[Property] }
  > extends true
    ? Key
    : never;
}[keyof Value];

type ExpectNever<Value extends never> = Value;
type _ThemeTokensHaveNoWritableKeys = ExpectNever<WritableKeys<ThemeTokens>>;
type _ProductThemeHasNoWritableKeys = ExpectNever<WritableKeys<ProductTheme>>;

function parseCustomProperties(block: string) {
  return Object.fromEntries(
    [...block.matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g)].map(
      ([, name, value]) => [name, value.trim()],
    ),
  );
}

function getExpectedDefaultCssVariables() {
  const defaultTheme = getTheme(defaultThemeId);
  const tokenVariables = Object.fromEntries(
    Object.entries(cssVariableByToken).map(([tokenName, variableName]) => [
      variableName,
      defaultTheme.tokens[tokenName as keyof ThemeTokens],
    ]),
  );
  const chartVariables = Object.fromEntries(
    defaultTheme.chart.map((color, index) => [
      `--product-chart-${index + 1}`,
      color,
    ]),
  );

  return { ...tokenVariables, ...chartVariables };
}

describe("theme registry", () => {
  it("contains exactly ten unique themes and keeps Morning Mist as default", () => {
    expect(themeIds).toEqual(expectedThemeIds);
    expect(themeIds).toHaveLength(10);
    expect(new Set(themeIds).size).toBe(10);
    expect(defaultThemeId).toBe("mist");
  });

  it("defines every semantic token and six chart colors for each theme", () => {
    expect(themes.map((theme) => theme.id)).toEqual(themeIds);

    for (const theme of themes) {
      expect(theme.labelZh.trim()).not.toBe("");
      expect(theme.labelEn.trim()).not.toBe("");
      expect(theme.descriptionZh.trim()).not.toBe("");
      expect(theme.descriptionEn.trim()).not.toBe("");
      expect(["light", "dark"]).toContain(theme.appearance);
      expect(Object.keys(theme.tokens).sort()).toEqual(expectedTokenKeys);

      for (const color of Object.values(theme.tokens)) {
        expect(color).toMatch(hexColorPattern);
      }

      expect(theme.chart).toHaveLength(6);
      for (const color of theme.chart) {
        expect(color).toMatch(hexColorPattern);
      }
    }
  });

  it("assigns dark appearance only to Deep Sea and Midnight", () => {
    for (const theme of themes) {
      const expectedAppearance =
        theme.id === "deep-sea" || theme.id === "midnight" ? "dark" : "light";

      expect(theme.appearance).toBe(expectedAppearance);
    }
  });

  it("preserves the specified core colors for every theme", () => {
    for (const theme of themes) {
      expect(theme.tokens).toMatchObject(expectedCoreColors[theme.id]);
    }
  });

  it("deep-freezes every registered theme", () => {
    expect(Object.isFrozen(themes)).toBe(true);

    for (const theme of themes) {
      expect(Object.isFrozen(theme)).toBe(true);
      expect(Object.isFrozen(theme.tokens)).toBe(true);
      expect(Object.isFrozen(theme.chart)).toBe(true);
    }

    const defaultTheme = getTheme(defaultThemeId);
    const originalBackground = defaultTheme.tokens.background;

    expect(() => {
      (defaultTheme.tokens as { background: string }).background = "#000000";
    }).toThrow(TypeError);
    expect(defaultTheme.tokens.background).toBe(originalBackground);
  });

  it("returns the requested theme and falls back to Morning Mist", () => {
    expect(getTheme("atlas").id).toBe("atlas");
    expect(getTheme("unknown").id).toBe(defaultThemeId);
    expect(getTheme(null).id).toBe(defaultThemeId);
    expect(getTheme(undefined).id).toBe(defaultThemeId);
  });
});

describe("SSR-safe product theme CSS", () => {
  it("defines default theme root variables and dark color-scheme support", () => {
    const moduleUrl = import.meta.url;
    const cssUrl = new URL("../../app/product-themes.css", moduleUrl);
    const css = readFileSync(
      cssUrl,
      "utf8",
    );
    const rootBlock = css.match(/:root\s*\{([^}]*)\}/)?.[1];
    const rootVariables = parseCustomProperties(rootBlock ?? "");
    const expectedVariables = getExpectedDefaultCssVariables();

    expect(rootBlock).toBeDefined();
    for (const [variableName, color] of Object.entries(expectedVariables)) {
      expect(rootVariables[variableName]).toBe(color);
    }
    expect(
      Object.keys(rootVariables).filter((name) =>
        name.startsWith("--product-chart-"),
      ),
    ).toHaveLength(6);
    expect(
      Object.keys(rootVariables).filter((name) => name.startsWith("--chart-")),
    ).toHaveLength(0);
    expect(css).toMatch(
      /html\[data-product-appearance="dark"\]\s*\{[^}]*color-scheme\s*:\s*dark\s*;?[^}]*\}/,
    );
  });
});
