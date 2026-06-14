# Phase A Product Interface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the confirmed Data Lens homepage, desktop-tool workspace, progressive result hierarchy, ten semantic themes, and accessible motion without changing the current real analysis APIs.

**Architecture:** Add a small theme domain (`themes.ts` plus `ThemeProvider`) and focused visual components instead of extending the oversized global stylesheet. Marketing and workspace surfaces share semantic CSS variables, while Motion components own only dynamic, interruptible interactions. Existing upload, model, finance, report, and IndexedDB state remain the source of truth.

**Tech Stack:** Next.js 16 App Router, React 19, TypeScript, Tailwind CSS 3, shadcn/ui primitives, Motion 12, Lucide, Vitest, React Testing Library, jsdom.

---

## File Map

### Create

- `frontend/src/lib/themes.ts`: immutable theme definitions, IDs, labels, and semantic tokens.
- `frontend/src/components/ThemeProvider.tsx`: theme state, local persistence, DOM token application, and preview/apply behavior.
- `frontend/src/components/ThemePicker.tsx`: accessible origin-aware theme popover.
- `frontend/src/components/DataLensHero.tsx`: two-line Hero and pointer-responsive data lens.
- `frontend/src/components/WorkspaceDetailPanel.tsx`: contextual desktop panel and mobile drawer.
- `frontend/src/components/WorkspaceInsightGrid.tsx`: progressive dashboard summary modules.
- `frontend/src/components/ui/popover.tsx`: restyled Radix popover primitive.
- `frontend/src/app/product-themes.css`: semantic token mappings for all ten themes.
- `frontend/src/app/product-interface.css`: Data Lens, workspace shell, dashboard, and responsive styles.
- `frontend/src/app/product-motion.css`: CSS-only ambient, hover, press, reveal, and reduced-motion rules.
- `frontend/src/app/app/charts/page.tsx`: chart workspace route.
- `frontend/src/app/en/app/charts/page.tsx`: English chart workspace route.
- `frontend/src/components/__tests__/DataLensHero.test.tsx`: Hero line and CTA tests.
- `frontend/src/components/__tests__/ThemeProvider.test.tsx`: persistence and DOM token tests.
- `frontend/src/components/__tests__/ThemePicker.test.tsx`: keyboard selection and apply tests.
- `frontend/src/lib/__tests__/themes.test.ts`: completeness and contrast-token tests.
- `frontend/vitest.config.ts`: Vitest configuration.
- `frontend/src/test/setup.ts`: DOM test setup.

### Modify

- `frontend/package.json`: test scripts and UI-test dependencies.
- `frontend/package-lock.json`: resolved dependencies.
- `frontend/src/app/layout.tsx`: install `ThemeProvider` and import focused CSS.
- `frontend/src/components/MarketingHome.tsx`: replace current Hero preview with `DataLensHero`; simplify first viewport.
- `frontend/src/components/MarketingShell.tsx`: theme-safe header and simplified initial navigation.
- `frontend/src/components/AppShell.tsx`: icon rail, charts route, theme picker, contextual panel host.
- `frontend/src/components/WorkspaceDashboard.tsx`: delegate progressive modules to `WorkspaceInsightGrid`.
- `frontend/src/components/MotionPrimitives.tsx`: add reusable shared-element panel and staged-result primitives.
- `frontend/src/components/WorkspaceToolPages.tsx`: export `ChartWorkspace`.
- `frontend/src/app/globals.css`: remove conflicting legacy overrides and import no new large component block.
- `README.md`: Phase A startup, theme, and verification notes.
- `PROGRESS.md`: Phase A completed files, functions, startup, tests, known issues, and Phase B.

## Task 1: Establish Frontend Test Harness

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/package-lock.json`
- Create: `frontend/vitest.config.ts`
- Create: `frontend/src/test/setup.ts`
- Create: `frontend/src/lib/__tests__/smoke.test.ts`

- [ ] **Step 1: Add a failing smoke test**

Create `frontend/src/lib/__tests__/smoke.test.ts`:

```ts
import { describe, expect, it } from "vitest";

describe("frontend test harness", () => {
  it("runs TypeScript tests in jsdom", () => {
    expect(document.documentElement).toBeDefined();
  });
});
```

- [ ] **Step 2: Run the test and verify the script is missing**

Run:

```bash
cd frontend
npm test -- --run
```

Expected: command fails because `test` is not defined.

- [ ] **Step 3: Install the test dependencies**

Run:

```bash
cd frontend
npm install --save-dev vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

Update `frontend/package.json` scripts:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "typecheck": "next typegen && tsc --noEmit --incremental false",
    "test": "vitest",
    "test:run": "vitest run"
  }
}
```

- [ ] **Step 4: Configure Vitest**

Create `frontend/vitest.config.ts`:

```ts
import { defineConfig } from "vitest/config";
import path from "node:path";

export default defineConfig({
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    css: true
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src")
    }
  }
});
```

Create `frontend/src/test/setup.ts`:

```ts
import "@testing-library/jest-dom/vitest";

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => undefined,
    removeListener: () => undefined,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
    dispatchEvent: () => false
  })
});
```

- [ ] **Step 5: Run the harness**

Run:

```bash
cd frontend
npm run test:run
```

Expected: `smoke.test.ts` passes.

- [ ] **Step 6: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/vitest.config.ts frontend/src/test/setup.ts frontend/src/lib/__tests__/smoke.test.ts
git commit -m "test: add frontend component test harness"
```

## Task 2: Define the Ten-Theme Domain

**Files:**
- Create: `frontend/src/lib/themes.ts`
- Create: `frontend/src/lib/__tests__/themes.test.ts`
- Create: `frontend/src/app/product-themes.css`

- [ ] **Step 1: Write failing theme-completeness tests**

Create `frontend/src/lib/__tests__/themes.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { defaultThemeId, themeIds, themes } from "@/lib/themes";

describe("theme registry", () => {
  it("contains ten unique themes and keeps Morning Mist as default", () => {
    expect(themeIds).toHaveLength(10);
    expect(new Set(themeIds).size).toBe(10);
    expect(defaultThemeId).toBe("mist");
  });

  it("defines every semantic token used by the product", () => {
    for (const theme of themes) {
      expect(theme.tokens).toEqual(
        expect.objectContaining({
          background: expect.any(String),
          surface: expect.any(String),
          surfaceElevated: expect.any(String),
          textPrimary: expect.any(String),
          textSecondary: expect.any(String),
          border: expect.any(String),
          accentPrimary: expect.any(String),
          accentSecondary: expect.any(String),
          success: expect.any(String),
          warning: expect.any(String),
          danger: expect.any(String)
        })
      );
      expect(theme.chart).toHaveLength(6);
    }
  });
});
```

- [ ] **Step 2: Run the focused test**

Run:

```bash
cd frontend
npm run test:run -- src/lib/__tests__/themes.test.ts
```

Expected: fails because `@/lib/themes` does not exist.

- [ ] **Step 3: Implement the registry**

Create `frontend/src/lib/themes.ts`:

```ts
export const themeIds = [
  "mist",
  "atlas",
  "iris",
  "clay",
  "sage",
  "frost",
  "graphite",
  "amber",
  "deep-sea",
  "midnight"
] as const;

export type ThemeId = (typeof themeIds)[number];

export type ThemeTokens = {
  background: string;
  surface: string;
  surfaceElevated: string;
  textPrimary: string;
  textSecondary: string;
  border: string;
  accentPrimary: string;
  accentSecondary: string;
  success: string;
  warning: string;
  danger: string;
};

export type ProductTheme = {
  id: ThemeId;
  labelZh: string;
  labelEn: string;
  descriptionZh: string;
  descriptionEn: string;
  appearance: "light" | "dark";
  tokens: ThemeTokens;
  chart: readonly [string, string, string, string, string, string];
};

export const defaultThemeId: ThemeId = "mist";

export const themes: readonly ProductTheme[] = [
  {
    id: "mist",
    labelZh: "晨霧藍綠",
    labelEn: "Morning Mist",
    descriptionZh: "目前品牌預設，清楚而安靜",
    descriptionEn: "The calm, clear brand default",
    appearance: "light",
    tokens: {
      background: "#eef3f5",
      surface: "#ffffff",
      surfaceElevated: "#f7f9fa",
      textPrimary: "#122033",
      textSecondary: "#5f6f82",
      border: "#d7e1e8",
      accentPrimary: "#39777e",
      accentSecondary: "#315f8e",
      success: "#2c806c",
      warning: "#94651f",
      danger: "#ad5158"
    },
    chart: ["#39777e", "#315f8e", "#8b6f47", "#7b668f", "#3f806a", "#b05d62"]
  },
  {
    id: "atlas",
    labelZh: "Atlas 藍",
    labelEn: "Atlas Blue",
    descriptionZh: "理性、專業，適合密集分析",
    descriptionEn: "Focused and professional for dense analysis",
    appearance: "light",
    tokens: {
      background: "#edf2f6",
      surface: "#ffffff",
      surfaceElevated: "#f4f7fa",
      textPrimary: "#142238",
      textSecondary: "#5e6e83",
      border: "#d5e0e8",
      accentPrimary: "#315f8e",
      accentSecondary: "#467f84",
      success: "#347a68",
      warning: "#916323",
      danger: "#aa4f5b"
    },
    chart: ["#315f8e", "#467f84", "#8c7045", "#755f87", "#4d7f64", "#ad5961"]
  },
  {
    id: "iris",
    labelZh: "Iris 灰紫",
    labelEn: "Iris",
    descriptionZh: "柔和、有辨識度但不霓虹",
    descriptionEn: "Distinctive muted violet without neon",
    appearance: "light",
    tokens: {
      background: "#f1f0f4",
      surface: "#ffffff",
      surfaceElevated: "#f6f4f8",
      textPrimary: "#201d2e",
      textSecondary: "#6b6578",
      border: "#ded9e5",
      accentPrimary: "#6b638b",
      accentSecondary: "#4f7281",
      success: "#427866",
      warning: "#93622f",
      danger: "#a84f5d"
    },
    chart: ["#6b638b", "#4f7281", "#967244", "#437868", "#b05d68", "#697d4f"]
  },
  {
    id: "clay",
    labelZh: "Clay 暖灰",
    labelEn: "Clay",
    descriptionZh: "低刺激，適合閱讀長報告",
    descriptionEn: "Low-stimulation reading for long reports",
    appearance: "light",
    tokens: {
      background: "#f3f0ee",
      surface: "#fffdfc",
      surfaceElevated: "#f7f3f1",
      textPrimary: "#29211f",
      textSecondary: "#70645f",
      border: "#e2d9d5",
      accentPrimary: "#7b5f52",
      accentSecondary: "#526f76",
      success: "#4c7865",
      warning: "#8d5f29",
      danger: "#a5524d"
    },
    chart: ["#7b5f52", "#526f76", "#8a733e", "#6d6682", "#4c7865", "#aa5b56"]
  },
  {
    id: "sage",
    labelZh: "Sage 灰綠",
    labelEn: "Sage",
    descriptionZh: "自然沉穩，狀態辨識清楚",
    descriptionEn: "Natural, calm, and status-friendly",
    appearance: "light",
    tokens: {
      background: "#eef2ef",
      surface: "#ffffff",
      surfaceElevated: "#f4f7f5",
      textPrimary: "#17251f",
      textSecondary: "#627269",
      border: "#d7e1da",
      accentPrimary: "#4f6f61",
      accentSecondary: "#4f6682",
      success: "#34705a",
      warning: "#896627",
      danger: "#a34e52"
    },
    chart: ["#4f6f61", "#4f6682", "#967242", "#746184", "#3c7a70", "#a9585e"]
  },
  {
    id: "frost",
    labelZh: "Frost 高亮",
    labelEn: "Frost",
    descriptionZh: "最明亮，適合投影與簡報",
    descriptionEn: "High clarity for projection and presentations",
    appearance: "light",
    tokens: {
      background: "#f7f9fb",
      surface: "#ffffff",
      surfaceElevated: "#f4f7fa",
      textPrimary: "#172235",
      textSecondary: "#5f7085",
      border: "#d9e3eb",
      accentPrimary: "#526b88",
      accentSecondary: "#2f6178",
      success: "#2f7969",
      warning: "#8c6127",
      danger: "#a44d57"
    },
    chart: ["#526b88", "#2f6178", "#88703f", "#70668a", "#3e7763", "#a8525c"]
  },
  {
    id: "graphite",
    labelZh: "Graphite 灰階",
    labelEn: "Graphite",
    descriptionZh: "近單色，專注資料與結構",
    descriptionEn: "Near-monochrome focus on data structure",
    appearance: "light",
    tokens: {
      background: "#eff1f2",
      surface: "#ffffff",
      surfaceElevated: "#f5f6f7",
      textPrimary: "#20242a",
      textSecondary: "#676e77",
      border: "#dadee2",
      accentPrimary: "#666c75",
      accentSecondary: "#3e6571",
      success: "#3e7461",
      warning: "#85602f",
      danger: "#985157"
    },
    chart: ["#515862", "#3e6571", "#857044", "#6d637d", "#47735f", "#9a555b"]
  },
  {
    id: "amber",
    labelZh: "Amber 紙金",
    labelEn: "Amber Paper",
    descriptionZh: "溫和重點色，不使用亮橘",
    descriptionEn: "Warm emphasis without bright orange",
    appearance: "light",
    tokens: {
      background: "#f5f2ec",
      surface: "#fffefa",
      surfaceElevated: "#f8f5ef",
      textPrimary: "#28231b",
      textSecondary: "#70695f",
      border: "#e2ddd2",
      accentPrimary: "#806638",
      accentSecondary: "#526d78",
      success: "#4c7762",
      warning: "#855d1f",
      danger: "#a4534e"
    },
    chart: ["#806638", "#526d78", "#756383", "#477762", "#a35752", "#5e6685"]
  },
  {
    id: "deep-sea",
    labelZh: "Deep Sea 深色",
    labelEn: "Deep Sea",
    descriptionZh: "低眩光深色工作區",
    descriptionEn: "Low-glare dark workspace",
    appearance: "dark",
    tokens: {
      background: "#11171b",
      surface: "#182025",
      surfaceElevated: "#20292e",
      textPrimary: "#ecf2f3",
      textSecondary: "#aab7bd",
      border: "#334047",
      accentPrimary: "#5b9b96",
      accentSecondary: "#8298b7",
      success: "#72b59a",
      warning: "#d0a263",
      danger: "#de8182"
    },
    chart: ["#70b0ab", "#8fa4c3", "#d3aa68", "#a797c3", "#78b995", "#dc8589"]
  },
  {
    id: "midnight",
    labelZh: "Midnight 藍黑",
    labelEn: "Midnight",
    descriptionZh: "夜間分析，維持高可讀性",
    descriptionEn: "High-readability night analysis",
    appearance: "dark",
    tokens: {
      background: "#131720",
      surface: "#1b202b",
      surfaceElevated: "#232a36",
      textPrimary: "#eff2f7",
      textSecondary: "#aeb7c6",
      border: "#364050",
      accentPrimary: "#7085aa",
      accentSecondary: "#65a09a",
      success: "#74b398",
      warning: "#cca166",
      danger: "#da7d87"
    },
    chart: ["#8297bd", "#72aaa4", "#d0aa70", "#a99ac7", "#7db69d", "#de858e"]
  }
];

export function getTheme(id: ThemeId) {
  return themes.find((theme) => theme.id === id) ?? themes[0];
}
```

- [ ] **Step 4: Add semantic theme CSS**

Create `frontend/src/app/product-themes.css` with the root mapping:

```css
:root {
  --product-background: #eef3f5;
  --product-surface: #ffffff;
  --product-surface-elevated: #f7f9fa;
  --product-text-primary: #122033;
  --product-text-secondary: #5f6f82;
  --product-border: #d7e1e8;
  --product-accent-primary: #39777e;
  --product-accent-secondary: #315f8e;
  --product-success: #2c806c;
  --product-warning: #94651f;
  --product-danger: #ad5158;
  --chart-1: #39777e;
  --chart-2: #315f8e;
  --chart-3: #8b6f47;
  --chart-4: #7b668f;
  --chart-5: #3f806a;
  --chart-6: #b05d62;
}

html[data-product-appearance="dark"] {
  color-scheme: dark;
}
```

The provider in Task 3 writes the selected theme values as inline root variables; this file supplies the SSR-safe default.

- [ ] **Step 5: Run the tests**

Run:

```bash
cd frontend
npm run test:run -- src/lib/__tests__/themes.test.ts
```

Expected: both tests pass.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/lib/themes.ts frontend/src/lib/__tests__/themes.test.ts frontend/src/app/product-themes.css
git commit -m "feat: define semantic product themes"
```

## Task 3: Add Persistent Theme Provider

**Files:**
- Create: `frontend/src/components/ThemeProvider.tsx`
- Create: `frontend/src/components/__tests__/ThemeProvider.test.tsx`
- Modify: `frontend/src/app/layout.tsx`

- [ ] **Step 1: Write failing provider tests**

Create `frontend/src/components/__tests__/ThemeProvider.test.tsx`:

```tsx
import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { ThemeProvider, useProductTheme } from "@/components/ThemeProvider";

describe("ThemeProvider", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute("data-product-theme");
    document.documentElement.removeAttribute("data-product-appearance");
  });

  it("applies and persists a selected theme", async () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <ThemeProvider>{children}</ThemeProvider>
    );
    const { result } = renderHook(() => useProductTheme(), { wrapper });

    await waitFor(() => expect(result.current.appliedTheme).toBe("mist"));
    act(() => result.current.previewTheme("deep-sea"));
    expect(document.documentElement.dataset.productTheme).toBe("deep-sea");
    expect(localStorage.getItem("finai-product-theme-v1")).toBeNull();

    act(() => result.current.applyPreview());
    expect(localStorage.getItem("finai-product-theme-v1")).toBe("deep-sea");
    expect(document.documentElement.dataset.productAppearance).toBe("dark");
  });

  it("restores the applied theme when preview is cancelled", async () => {
    localStorage.setItem("finai-product-theme-v1", "atlas");
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <ThemeProvider>{children}</ThemeProvider>
    );
    const { result } = renderHook(() => useProductTheme(), { wrapper });

    await waitFor(() => expect(result.current.appliedTheme).toBe("atlas"));
    act(() => result.current.previewTheme("iris"));
    act(() => result.current.cancelPreview());

    expect(document.documentElement.dataset.productTheme).toBe("atlas");
  });
});
```

- [ ] **Step 2: Verify the test fails**

Run:

```bash
cd frontend
npm run test:run -- src/components/__tests__/ThemeProvider.test.tsx
```

Expected: fails because `ThemeProvider` does not exist.

- [ ] **Step 3: Implement the provider**

Create `frontend/src/components/ThemeProvider.tsx`:

```tsx
"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode
} from "react";
import {
  defaultThemeId,
  getTheme,
  themeIds,
  type ThemeId
} from "@/lib/themes";

type ThemeContextValue = {
  appliedTheme: ThemeId;
  previewedTheme: ThemeId;
  previewTheme: (theme: ThemeId) => void;
  applyPreview: () => void;
  cancelPreview: () => void;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);
const storageKey = "finai-product-theme-v1";

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [appliedTheme, setAppliedTheme] = useState<ThemeId>(defaultThemeId);
  const [previewedTheme, setPreviewedTheme] = useState<ThemeId>(defaultThemeId);

  useEffect(() => {
    const stored = localStorage.getItem(storageKey);
    const restored = themeIds.includes(stored as ThemeId)
      ? (stored as ThemeId)
      : defaultThemeId;
    setAppliedTheme(restored);
    setPreviewedTheme(restored);
    applyThemeToRoot(restored);
  }, []);

  const previewTheme = useCallback((theme: ThemeId) => {
    setPreviewedTheme(theme);
    applyThemeToRoot(theme);
  }, []);

  const applyPreview = useCallback(() => {
    setAppliedTheme(previewedTheme);
    localStorage.setItem(storageKey, previewedTheme);
  }, [previewedTheme]);

  const cancelPreview = useCallback(() => {
    setPreviewedTheme(appliedTheme);
    applyThemeToRoot(appliedTheme);
  }, [appliedTheme]);

  const value = useMemo(
    () => ({
      appliedTheme,
      previewedTheme,
      previewTheme,
      applyPreview,
      cancelPreview
    }),
    [appliedTheme, applyPreview, cancelPreview, previewTheme, previewedTheme]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useProductTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error("useProductTheme must be used inside ThemeProvider.");
  return context;
}

function applyThemeToRoot(id: ThemeId) {
  const theme = getTheme(id);
  const root = document.documentElement;
  root.dataset.productTheme = id;
  root.dataset.productAppearance = theme.appearance;
  const entries = {
    "--product-background": theme.tokens.background,
    "--product-surface": theme.tokens.surface,
    "--product-surface-elevated": theme.tokens.surfaceElevated,
    "--product-text-primary": theme.tokens.textPrimary,
    "--product-text-secondary": theme.tokens.textSecondary,
    "--product-border": theme.tokens.border,
    "--product-accent-primary": theme.tokens.accentPrimary,
    "--product-accent-secondary": theme.tokens.accentSecondary,
    "--product-success": theme.tokens.success,
    "--product-warning": theme.tokens.warning,
    "--product-danger": theme.tokens.danger
  };
  Object.entries(entries).forEach(([key, value]) => root.style.setProperty(key, value));
  theme.chart.forEach((value, index) => root.style.setProperty(`--chart-${index + 1}`, value));
}
```

- [ ] **Step 4: Install the provider at the root**

Update `frontend/src/app/layout.tsx`:

```tsx
import { ThemeProvider } from "@/components/ThemeProvider";
import "./product-themes.css";
import "./product-interface.css";
import "./product-motion.css";

// Inside <FeedbackProvider>:
<ThemeProvider>
  <WorkspaceProvider>{children}</WorkspaceProvider>
</ThemeProvider>
```

- [ ] **Step 5: Run provider and type tests**

Run:

```bash
cd frontend
npm run test:run -- src/components/__tests__/ThemeProvider.test.tsx
npm run typecheck
```

Expected: tests and typecheck pass.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/ThemeProvider.tsx frontend/src/components/__tests__/ThemeProvider.test.tsx frontend/src/app/layout.tsx
git commit -m "feat: persist product theme selection"
```

## Task 4: Build Accessible Theme Picker

**Files:**
- Modify: `frontend/package.json`
- Modify: `frontend/package-lock.json`
- Create: `frontend/src/components/ui/popover.tsx`
- Create: `frontend/src/components/ThemePicker.tsx`
- Create: `frontend/src/components/__tests__/ThemePicker.test.tsx`

- [ ] **Step 1: Write the failing interaction test**

Create `frontend/src/components/__tests__/ThemePicker.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { ThemePicker } from "@/components/ThemePicker";
import { ThemeProvider } from "@/components/ThemeProvider";
import { LocaleProvider } from "@/components/LocaleProvider";

describe("ThemePicker", () => {
  it("previews a theme and persists only after Apply", async () => {
    const user = userEvent.setup();
    render(
      <LocaleProvider locale="zh-Hant">
        <ThemeProvider>
          <ThemePicker />
        </ThemeProvider>
      </LocaleProvider>
    );

    await user.click(screen.getByRole("button", { name: "配色" }));
    await user.click(screen.getByRole("radio", { name: /Deep Sea 深色/ }));
    expect(document.documentElement.dataset.productTheme).toBe("deep-sea");
    expect(localStorage.getItem("finai-product-theme-v1")).toBeNull();

    await user.click(screen.getByRole("button", { name: "套用配色" }));
    expect(localStorage.getItem("finai-product-theme-v1")).toBe("deep-sea");
  });
});
```

- [ ] **Step 2: Verify failure**

Run:

```bash
cd frontend
npm run test:run -- src/components/__tests__/ThemePicker.test.tsx
```

Expected: fails because `ThemePicker` does not exist.

- [ ] **Step 3: Add the Radix dependency**

Run:

```bash
cd frontend
npm install @radix-ui/react-popover
```

- [ ] **Step 4: Add the popover primitive**

Create `frontend/src/components/ui/popover.tsx`:

```tsx
"use client";

import * as React from "react";
import * as PopoverPrimitive from "@radix-ui/react-popover";
import { cn } from "@/lib/utils";

export const Popover = PopoverPrimitive.Root;
export const PopoverTrigger = PopoverPrimitive.Trigger;
export const PopoverClose = PopoverPrimitive.Close;

export function PopoverContent({
  className,
  sideOffset = 8,
  ...props
}: React.ComponentProps<typeof PopoverPrimitive.Content>) {
  return (
    <PopoverPrimitive.Portal>
      <PopoverPrimitive.Content
        sideOffset={sideOffset}
        className={cn("product-popover", className)}
        {...props}
      />
    </PopoverPrimitive.Portal>
  );
}
```

- [ ] **Step 5: Implement the picker**

Create `frontend/src/components/ThemePicker.tsx`:

```tsx
"use client";

import { Check, Palette } from "lucide-react";
import { useLocale } from "@/components/LocaleProvider";
import { useProductTheme } from "@/components/ThemeProvider";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverClose,
  PopoverContent,
  PopoverTrigger
} from "@/components/ui/popover";
import { themes } from "@/lib/themes";

export function ThemePicker() {
  const { text } = useLocale();
  const {
    appliedTheme,
    previewedTheme,
    previewTheme,
    applyPreview,
    cancelPreview
  } = useProductTheme();

  return (
    <Popover onOpenChange={(open) => { if (!open) cancelPreview(); }}>
      <PopoverTrigger asChild>
        <Button type="button" variant="ghost" size="icon-sm" aria-label={text("配色", "Theme")}>
          <Palette aria-hidden="true" />
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" aria-label={text("選擇配色", "Choose theme")}>
        <div className="theme-picker-heading">
          <strong>{text("工作區配色", "Workspace theme")}</strong>
          <span>{text("即時預覽，套用後保存", "Preview now, save on apply")}</span>
        </div>
        <div className="theme-picker-grid" role="radiogroup">
          {themes.map((theme) => (
            <button
              key={theme.id}
              type="button"
              role="radio"
              aria-checked={previewedTheme === theme.id}
              aria-label={`${theme.labelZh} ${theme.appearance === "dark" ? "深色" : "淺色"}`}
              className={previewedTheme === theme.id ? "is-selected" : ""}
              onClick={() => previewTheme(theme.id)}
            >
              <span className="theme-swatches">
                <i style={{ background: theme.tokens.background }} />
                <i style={{ background: theme.tokens.accentPrimary }} />
                <i style={{ background: theme.tokens.accentSecondary }} />
              </span>
              <span>
                <strong>{text(theme.labelZh, theme.labelEn)}</strong>
                <small>{text(theme.descriptionZh, theme.descriptionEn)}</small>
              </span>
              {previewedTheme === theme.id ? <Check aria-hidden="true" /> : null}
            </button>
          ))}
        </div>
        <div className="theme-picker-actions">
          <PopoverClose asChild>
            <Button type="button" variant="ghost" onClick={cancelPreview}>
              {text("取消", "Cancel")}
            </Button>
          </PopoverClose>
          <PopoverClose asChild>
            <Button type="button" onClick={applyPreview} aria-label={text("套用配色", "Apply theme")}>
              {text("套用", "Apply")}
            </Button>
          </PopoverClose>
        </div>
        <span className="sr-only">{appliedTheme}</span>
      </PopoverContent>
    </Popover>
  );
}
```

- [ ] **Step 6: Run tests**

Run:

```bash
cd frontend
npm run test:run -- src/components/__tests__/ThemePicker.test.tsx
npm run typecheck
```

Expected: interaction test and typecheck pass.

- [ ] **Step 7: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/src/components/ui/popover.tsx frontend/src/components/ThemePicker.tsx frontend/src/components/__tests__/ThemePicker.test.tsx
git commit -m "feat: add accessible theme picker"
```

## Task 5: Implement the Two-Line Data Lens Hero

**Files:**
- Create: `frontend/src/components/DataLensHero.tsx`
- Create: `frontend/src/components/__tests__/DataLensHero.test.tsx`
- Modify: `frontend/src/components/MarketingHome.tsx`
- Modify: `frontend/src/components/MarketingShell.tsx`
- Create: `frontend/src/app/product-interface.css`
- Create: `frontend/src/app/product-motion.css`

- [ ] **Step 1: Write the failing Hero contract test**

Create `frontend/src/components/__tests__/DataLensHero.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DataLensHero } from "@/components/DataLensHero";
import { LocaleProvider } from "@/components/LocaleProvider";

describe("DataLensHero", () => {
  it("renders exactly two indivisible headline lines", () => {
    render(<LocaleProvider locale="zh-Hant"><DataLensHero /></LocaleProvider>);
    const headline = screen.getByRole("heading", { level: 1 });
    const lines = headline.querySelectorAll("[data-hero-line]");
    expect(lines).toHaveLength(2);
    expect(lines[0]).toHaveTextContent("看懂資料。");
    expect(lines[1]).toHaveTextContent("找到下一步。");
    expect(lines[1]).toHaveClass("whitespace-nowrap");
  });

  it("links the primary action to the real data workspace", () => {
    render(<LocaleProvider locale="zh-Hant"><DataLensHero /></LocaleProvider>);
    expect(screen.getByRole("link", { name: /開始分析/ })).toHaveAttribute("href", "/app/data");
  });
});
```

- [ ] **Step 2: Verify failure**

Run:

```bash
cd frontend
npm run test:run -- src/components/__tests__/DataLensHero.test.tsx
```

Expected: fails because `DataLensHero` does not exist.

- [ ] **Step 3: Implement the interactive Hero**

Create `frontend/src/components/DataLensHero.tsx`:

```tsx
"use client";

import Link from "next/link";
import { ArrowRight, ScanSearch } from "lucide-react";
import {
  motion,
  useMotionTemplate,
  useMotionValue,
  useReducedMotion,
  useSpring
} from "motion/react";
import { useLocale } from "@/components/LocaleProvider";
import { Button } from "@/components/ui/button";

const rows = Array.from({ length: 8 }, (_, row) =>
  Array.from({ length: 4 }, (_, column) => `${row}-${column}`)
);

export function DataLensHero() {
  const { text, path } = useLocale();
  const reducedMotion = useReducedMotion();
  const pointerX = useMotionValue(280);
  const pointerY = useMotionValue(160);
  const springX = useSpring(pointerX, { stiffness: 105, damping: 24, mass: 0.55 });
  const springY = useSpring(pointerY, { stiffness: 105, damping: 24, mass: 0.55 });
  const lensTransform = useMotionTemplate`translate3d(${springX}px, ${springY}px, 0) translate3d(-50%, -50%, 0)`;

  return (
    <section className="data-lens-hero">
      <div className="data-lens-hero-inner">
        <div className="data-lens-copy">
          <span className="data-lens-eyebrow">
            {text("通用型 AI 資料分析平台", "Universal AI analytics platform")}
          </span>
          <h1>
            <span data-hero-line className="whitespace-nowrap">{text("看懂資料。", "Understand data.")}</span>
            <span data-hero-line className="whitespace-nowrap">{text("找到下一步。", "Find the next step.")}</span>
          </h1>
          <p>
            {text(
              "上傳資料，讓系統理解結構、推薦方法，並把重點整理成可繼續操作的分析結果。",
              "Upload data, understand its structure, choose suitable methods, and turn results into clear next actions."
            )}
          </p>
          <div className="data-lens-actions">
            <Button asChild variant="premium" size="lg">
              <Link href={path("/app/data")}>
                {text("開始分析", "Start analyzing")}
                <ArrowRight aria-hidden="true" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="#journey">{text("查看運作方式", "See how it works")}</Link>
            </Button>
          </div>
        </div>

        <div
          className="data-lens-board"
          onPointerMove={(event) => {
            if (reducedMotion || event.pointerType === "touch") return;
            const bounds = event.currentTarget.getBoundingClientRect();
            pointerX.set(event.clientX - bounds.left);
            pointerY.set(event.clientY - bounds.top);
          }}
        >
          <div className="data-lens-toolbar">
            <span>sales_2026.csv</span>
            <span>{text("12,456 筆 × 28 欄", "12,456 rows × 28 columns")}</span>
          </div>
          <div className="data-lens-table" aria-hidden="true">
            {rows.flatMap((row) => row).map((cell, index) => (
              <i key={cell} className={index % 7 === 0 ? "is-signal" : ""} />
            ))}
          </div>
          <motion.div
            className="data-lens-orb"
            style={reducedMotion ? undefined : { transform: lensTransform }}
            aria-hidden="true"
          >
            <ScanSearch />
          </motion.div>
          <motion.div
            className="data-lens-insight"
            initial={reducedMotion ? false : { opacity: 0, transform: "translate3d(0,8px,0) scale(.98)" }}
            animate={{ opacity: 1, transform: "translate3d(0,0,0) scale(1)" }}
            transition={{ duration: reducedMotion ? 0 : 0.42, delay: reducedMotion ? 0 : 0.3 }}
          >
            <strong>{text("發現 3 個關鍵訊號", "3 key signals found")}</strong>
            <span>{text("季節性、退貨異常、非線性關係", "Seasonality, return anomaly, nonlinear relationship")}</span>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
```

- [ ] **Step 4: Replace only the current Hero block**

In `frontend/src/components/MarketingHome.tsx`:

- Import `DataLensHero`.
- Replace the existing `<section className="marketing-hero">...</section>` with `<DataLensHero />`.
- Remove `ProductPreview` and `PointerSurface` imports if no longer used.
- Keep journey, capability, trust, and final CTA sections intact.

In `frontend/src/components/MarketingShell.tsx`:

- Keep the current real navigation and language switch.
- Use semantic theme variables for header text, border, and background.
- Do not add login controls.

- [ ] **Step 5: Add focused interface and motion CSS**

Create `frontend/src/app/product-interface.css` with:

```css
.marketing-site,
.product-shell {
  color: var(--product-text-primary);
  background: var(--product-background);
}

.data-lens-hero {
  min-height: min(760px, calc(100dvh - 68px));
  padding: clamp(52px, 7vw, 96px) var(--space-page);
}

.data-lens-hero-inner {
  display: grid;
  grid-template-columns: minmax(360px, .82fr) minmax(520px, 1.18fr);
  gap: clamp(42px, 6vw, 92px);
  align-items: center;
  width: min(1380px, 100%);
  margin-inline: auto;
}

.data-lens-copy h1 {
  margin: 18px 0 0;
  font-size: clamp(3rem, 5vw, 4.8rem);
  font-weight: 720;
  line-height: 1.02;
  letter-spacing: 0;
}

.data-lens-copy h1 > span {
  display: block;
  width: max-content;
  max-width: 100%;
}

.data-lens-copy h1 > span:last-child {
  color: var(--product-accent-primary);
}

.data-lens-board {
  position: relative;
  min-height: 390px;
  overflow: hidden;
  border: 1px solid var(--product-border);
  border-radius: 18px;
  background: color-mix(in srgb, var(--product-surface) 94%, transparent);
  box-shadow: 0 30px 72px rgb(20 38 58 / 14%);
}

.data-lens-table {
  display: grid;
  grid-template-columns: 1.5fr repeat(3, .75fr);
  gap: 0 12px;
  padding: 15px 18px;
}

.data-lens-table i {
  height: 34px;
  border-bottom: 1px solid var(--product-border);
}

.data-lens-table i::after {
  display: block;
  width: 72%;
  height: 6px;
  margin-top: 14px;
  border-radius: 999px;
  content: "";
  background: color-mix(in srgb, var(--product-text-secondary) 22%, transparent);
}

.data-lens-table i.is-signal::after {
  background: var(--product-accent-primary);
}

.data-lens-orb {
  position: absolute;
  top: 0;
  left: 0;
  display: grid;
  width: 132px;
  height: 132px;
  place-items: center;
  border: 1px solid color-mix(in srgb, var(--product-accent-primary) 48%, transparent);
  border-radius: 50%;
  color: var(--product-accent-primary);
  background: color-mix(in srgb, var(--product-surface) 94%, transparent);
  box-shadow: 0 18px 44px rgb(30 65 82 / 20%), 0 0 0 9px rgb(255 255 255 / 62%);
}

@media (max-width: 1080px) {
  .data-lens-hero-inner { grid-template-columns: 1fr; }
  .data-lens-copy { max-width: 760px; }
}

@media (max-width: 620px) {
  .data-lens-hero { padding-inline: 18px; }
  .data-lens-copy h1 { font-size: clamp(2.45rem, 11vw, 3.4rem); }
  .data-lens-board { min-height: 300px; }
}
```

Create `frontend/src/app/product-motion.css`:

```css
:root {
  --product-ease-out: cubic-bezier(.23, 1, .32, 1);
  --product-ease-in-out: cubic-bezier(.77, 0, .175, 1);
}

@media (hover: hover) and (pointer: fine) {
  .data-lens-board {
    transition: transform 220ms var(--product-ease-out), box-shadow 220ms ease;
  }
  .data-lens-board:hover {
    transform: translateY(-2px);
    box-shadow: 0 36px 84px rgb(20 38 58 / 17%);
  }
}

@media (prefers-reduced-motion: reduce) {
  .data-lens-board,
  .data-lens-orb,
  .data-lens-insight {
    animation: none !important;
    transition-duration: 1ms !important;
    transform: none !important;
  }
}
```

- [ ] **Step 6: Run focused tests and build**

Run:

```bash
cd frontend
npm run test:run -- src/components/__tests__/DataLensHero.test.tsx
npm run typecheck
npm run build
```

Expected: tests, typecheck, and production build pass.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/components/DataLensHero.tsx frontend/src/components/__tests__/DataLensHero.test.tsx frontend/src/components/MarketingHome.tsx frontend/src/components/MarketingShell.tsx frontend/src/app/product-interface.css frontend/src/app/product-motion.css
git commit -m "feat: add two-line interactive data lens hero"
```

## Task 6: Rebuild the Workspace Shell and Add Charts Route

**Files:**
- Modify: `frontend/src/components/AppShell.tsx`
- Modify: `frontend/src/components/WorkspaceToolPages.tsx`
- Create: `frontend/src/app/app/charts/page.tsx`
- Create: `frontend/src/app/en/app/charts/page.tsx`
- Modify: `frontend/src/app/product-interface.css`
- Modify: `frontend/src/app/product-motion.css`
- Create: `frontend/src/components/__tests__/AppShell.test.tsx`

- [ ] **Step 1: Write the failing navigation test**

Create `frontend/src/components/__tests__/AppShell.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppShell } from "@/components/AppShell";
import { FeedbackProvider } from "@/components/FeedbackProvider";
import { LocaleProvider } from "@/components/LocaleProvider";
import { ThemeProvider } from "@/components/ThemeProvider";

vi.mock("next/navigation", () => ({ usePathname: () => "/app" }));
vi.mock("@/components/WorkspaceProvider", () => ({
  useWorkspace: () => ({ isHydrated: true })
}));
vi.mock("@/components/WorkspaceSource", () => ({
  useWorkspaceSources: () => ({ sources: [], completedUploads: [] }),
  WorkspaceSourceSelect: () => <div>source</div>
}));

describe("AppShell", () => {
  it("exposes the complete workspace navigation including charts", () => {
    render(
      <LocaleProvider locale="zh-Hant">
        <FeedbackProvider>
          <ThemeProvider>
            <AppShell><div>content</div></AppShell>
          </ThemeProvider>
        </FeedbackProvider>
      </LocaleProvider>
    );
    expect(screen.getByRole("link", { name: "總覽" })).toHaveAttribute("href", "/app");
    expect(screen.getByRole("link", { name: "圖表" })).toHaveAttribute("href", "/app/charts");
    expect(screen.getByRole("link", { name: "報告" })).toHaveAttribute("href", "/app/reports");
  });
});
```

- [ ] **Step 2: Verify failure**

Run:

```bash
cd frontend
npm run test:run -- src/components/__tests__/AppShell.test.tsx
```

Expected: fails because Charts is absent.

- [ ] **Step 3: Update the shell**

In `frontend/src/components/AppShell.tsx`:

- Add `BarChart3` and `Palette`-driven `ThemePicker`.
- Add `{ href: "/app/charts", label: text("圖表", "Charts"), icon: BarChart3 }`.
- Convert `.product-sidebar` to a 72px icon rail on desktop.
- Use tooltips or `aria-label` for icons while keeping visible labels in an expandable navigation panel on pointer hover/focus.
- Remove the sidebar status card; status belongs in the topbar and dashboard.
- Keep source selection, language, sound, and real data state.
- Add `ThemePicker` directly in the topbar.
- On screens below 860px, retain bottom navigation with five primary destinations and move Finance/Reports into More only if all six labels do not fit.

- [ ] **Step 4: Add the chart route**

Append to `frontend/src/components/WorkspaceToolPages.tsx`:

```tsx
export function ChartWorkspace() {
  const { text } = useLocale();
  const { activeSource } = useWorkspaceSources();

  return (
    <>
      <PageHeader
        eyebrow={text("視覺化", "Visualization")}
        title={text("圖表工作區", "Chart workspace")}
        description={text(
          "依目前資料與分析結果選擇圖表。完整自動圖表引擎將在後端圖表階段接入。",
          "Choose charts for the current data and results. The full automatic chart engine connects in the visualization backend phase."
        )}
        actions={<WorkspaceSourceSelect />}
      />
      {activeSource ? (
        <WorkspaceEmptyState
          title={text("圖表設定將在這裡展開", "Chart controls will open here")}
          description={text(
            "目前保留真實資料來源，不顯示模擬圖表。",
            "The real data source is retained; no simulated chart is shown."
          )}
        />
      ) : (
        <WorkspaceEmptyState />
      )}
    </>
  );
}
```

Create both route files:

```tsx
import { AppShell } from "@/components/AppShell";
import { ChartWorkspace } from "@/components/WorkspaceToolPages";

export default function ChartWorkspacePage() {
  return <AppShell><ChartWorkspace /></AppShell>;
}
```

The English route uses the same component under the English layout.

- [ ] **Step 5: Add shell CSS**

In `frontend/src/app/product-interface.css`, define:

```css
:root {
  --workspace-rail-width: 72px;
  --workspace-topbar-height: 64px;
}

.product-sidebar {
  width: var(--workspace-rail-width);
  padding: 14px 10px;
  color: var(--product-text-secondary);
  background: var(--product-surface);
  border-right: 1px solid var(--product-border);
}

.product-main-column {
  margin-left: var(--workspace-rail-width);
  background: var(--product-background);
}

.product-nav a {
  width: 48px;
  height: 44px;
  justify-content: center;
  border-radius: 10px;
}

.product-nav a.is-active {
  color: #fff;
  background: var(--product-accent-secondary);
}

.product-topbar {
  background: color-mix(in srgb, var(--product-surface) 94%, transparent);
  border-color: var(--product-border);
}
```

Remove or override the old dark 236px sidebar rules so only the new rail is visible.

- [ ] **Step 6: Run tests and build**

Run:

```bash
cd frontend
npm run test:run -- src/components/__tests__/AppShell.test.tsx
npm run typecheck
npm run build
```

Expected: navigation test and all build steps pass; route output contains `/app/charts` and `/en/app/charts`.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/components/AppShell.tsx frontend/src/components/WorkspaceToolPages.tsx frontend/src/app/app/charts/page.tsx frontend/src/app/en/app/charts/page.tsx frontend/src/app/product-interface.css frontend/src/app/product-motion.css frontend/src/components/__tests__/AppShell.test.tsx
git commit -m "feat: rebuild workspace shell and add chart route"
```

## Task 7: Add Contextual Detail Panel and Shared Motion

**Files:**
- Create: `frontend/src/components/WorkspaceDetailPanel.tsx`
- Modify: `frontend/src/components/MotionPrimitives.tsx`
- Modify: `frontend/src/app/product-interface.css`
- Modify: `frontend/src/app/product-motion.css`
- Create: `frontend/src/components/__tests__/WorkspaceDetailPanel.test.tsx`

- [ ] **Step 1: Write the failing panel test**

Create `frontend/src/components/__tests__/WorkspaceDetailPanel.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { WorkspaceDetailPanel } from "@/components/WorkspaceDetailPanel";

describe("WorkspaceDetailPanel", () => {
  it("opens from a trigger and closes with Escape", async () => {
    const user = userEvent.setup();
    render(
      <WorkspaceDetailPanel
        title="模型詳情"
        trigger={<button type="button">開啟詳情</button>}
      >
        <p>Gradient Boosting</p>
      </WorkspaceDetailPanel>
    );

    await user.click(screen.getByRole("button", { name: "開啟詳情" }));
    expect(screen.getByRole("dialog", { name: "模型詳情" })).toBeVisible();
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog", { name: "模型詳情" })).not.toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Verify failure**

Run:

```bash
cd frontend
npm run test:run -- src/components/__tests__/WorkspaceDetailPanel.test.tsx
```

Expected: fails because the component does not exist.

- [ ] **Step 3: Add reusable panel motion**

Append to `frontend/src/components/MotionPrimitives.tsx`:

```tsx
export function SharedPanel({
  open,
  layoutId,
  children
}: {
  open: boolean;
  layoutId: string;
  children: React.ReactNode;
}) {
  const reducedMotion = useReducedMotion();
  if (!open) return null;
  return (
    <motion.div
      layoutId={reducedMotion ? undefined : layoutId}
      initial={reducedMotion ? false : { opacity: 0, transform: "translate3d(0,8px,0) scale(.98)" }}
      animate={{ opacity: 1, transform: "translate3d(0,0,0) scale(1)" }}
      exit={{ opacity: 0, transform: reducedMotion ? "none" : "translate3d(0,4px,0) scale(.99)" }}
      transition={{ duration: reducedMotion ? 0 : 0.22, ease: [0.23, 1, 0.32, 1] }}
    >
      {children}
    </motion.div>
  );
}
```

- [ ] **Step 4: Implement the panel**

Create `frontend/src/components/WorkspaceDetailPanel.tsx`:

```tsx
"use client";

import { cloneElement, useEffect, useId, useState, type ReactElement, type ReactNode } from "react";
import { AnimatePresence } from "motion/react";
import { X } from "lucide-react";
import { SharedPanel } from "@/components/MotionPrimitives";

export function WorkspaceDetailPanel({
  title,
  trigger,
  children
}: {
  title: string;
  trigger: ReactElement<{ onClick?: () => void; "aria-expanded"?: boolean }>;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const id = useId();

  useEffect(() => {
    if (!open) return;
    const close = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [open]);

  return (
    <>
      {cloneElement(trigger, {
        "aria-expanded": open,
        onClick: () => setOpen(true)
      })}
      <AnimatePresence>
        {open ? (
          <div className="workspace-detail-layer">
            <button
              type="button"
              className="workspace-detail-backdrop"
              aria-label="關閉詳情"
              onClick={() => setOpen(false)}
            />
            <SharedPanel open layoutId={`detail-${id}`}>
              <section className="workspace-detail-panel" role="dialog" aria-modal="true" aria-label={title}>
                <header>
                  <strong>{title}</strong>
                  <button type="button" onClick={() => setOpen(false)} aria-label="關閉詳情">
                    <X aria-hidden="true" />
                  </button>
                </header>
                <div>{children}</div>
              </section>
            </SharedPanel>
          </div>
        ) : null}
      </AnimatePresence>
    </>
  );
}
```

- [ ] **Step 5: Add desktop-panel and mobile-drawer styles**

Add to `frontend/src/app/product-interface.css`:

```css
.workspace-detail-layer {
  position: fixed;
  inset: 0;
  z-index: 70;
  display: grid;
  justify-items: end;
}

.workspace-detail-backdrop {
  position: absolute;
  inset: 0;
  border: 0;
  background: rgb(15 23 42 / 16%);
}

.workspace-detail-panel {
  position: relative;
  width: min(420px, calc(100vw - 24px));
  height: 100dvh;
  overflow: auto;
  border-left: 1px solid var(--product-border);
  background: var(--product-surface);
  box-shadow: -24px 0 64px rgb(15 23 42 / 16%);
}

@media (max-width: 620px) {
  .workspace-detail-layer { align-items: end; justify-items: stretch; }
  .workspace-detail-panel {
    width: 100%;
    height: min(78dvh, 720px);
    border-top: 1px solid var(--product-border);
    border-left: 0;
    border-radius: 16px 16px 0 0;
  }
}
```

- [ ] **Step 6: Run tests**

Run:

```bash
cd frontend
npm run test:run -- src/components/__tests__/WorkspaceDetailPanel.test.tsx
npm run typecheck
```

Expected: panel test and typecheck pass.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/components/WorkspaceDetailPanel.tsx frontend/src/components/MotionPrimitives.tsx frontend/src/app/product-interface.css frontend/src/app/product-motion.css frontend/src/components/__tests__/WorkspaceDetailPanel.test.tsx
git commit -m "feat: add contextual workspace detail panels"
```

## Task 8: Build Progressive Workspace Insight Grid

**Files:**
- Create: `frontend/src/components/WorkspaceInsightGrid.tsx`
- Modify: `frontend/src/components/WorkspaceDashboard.tsx`
- Modify: `frontend/src/app/product-interface.css`
- Create: `frontend/src/components/__tests__/WorkspaceInsightGrid.test.tsx`

- [ ] **Step 1: Write the failing hierarchy test**

Create `frontend/src/components/__tests__/WorkspaceInsightGrid.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WorkspaceInsightGrid } from "@/components/WorkspaceInsightGrid";

describe("WorkspaceInsightGrid", () => {
  it("shows priorities before detailed metrics", () => {
    render(
      <WorkspaceInsightGrid
        insights={["營收具有季節性", "北區退貨率偏高", "價格與轉換率為非線性"]}
        nextAction={{ label: "比較適合模型", href: "/app/models" }}
        metrics={[
          { label: "資料筆數", value: "12,456" },
          { label: "欄位", value: "28" },
          { label: "完整度", value: "96%" }
        ]}
      />
    );
    const headings = screen.getAllByRole("heading");
    expect(headings[0]).toHaveTextContent("最重要的發現");
    expect(screen.getByRole("link", { name: "比較適合模型" })).toHaveAttribute("href", "/app/models");
  });
});
```

- [ ] **Step 2: Verify failure**

Run:

```bash
cd frontend
npm run test:run -- src/components/__tests__/WorkspaceInsightGrid.test.tsx
```

Expected: fails because `WorkspaceInsightGrid` does not exist.

- [ ] **Step 3: Implement the result hierarchy**

Create `frontend/src/components/WorkspaceInsightGrid.tsx`:

```tsx
"use client";

import Link from "next/link";
import { ArrowRight, BarChart3, Database, Sparkles } from "lucide-react";
import { motion, useReducedMotion } from "motion/react";

type Metric = { label: string; value: string };

export function WorkspaceInsightGrid({
  insights,
  nextAction,
  metrics
}: {
  insights: string[];
  nextAction: { label: string; href: string };
  metrics: Metric[];
}) {
  const reducedMotion = useReducedMotion();
  return (
    <div className="workspace-insight-grid">
      <motion.section
        className="workspace-priority-module"
        initial={reducedMotion ? false : { opacity: 0, transform: "translate3d(0,8px,0)" }}
        animate={{ opacity: 1, transform: "translate3d(0,0,0)" }}
      >
        <header><Sparkles aria-hidden="true" /><h2>最重要的發現</h2></header>
        <ol>{insights.slice(0, 3).map((insight) => <li key={insight}>{insight}</li>)}</ol>
        <Link href={nextAction.href}>{nextAction.label}<ArrowRight aria-hidden="true" /></Link>
      </motion.section>
      <section className="workspace-metric-module">
        <header><Database aria-hidden="true" /><h2>資料概況</h2></header>
        <dl>{metrics.map((metric) => <div key={metric.label}><dt>{metric.label}</dt><dd>{metric.value}</dd></div>)}</dl>
      </section>
      <section className="workspace-chart-module">
        <header><BarChart3 aria-hidden="true" /><h2>主要趨勢</h2></header>
        <div className="workspace-chart-placeholder" aria-label="等待真實分析圖表" />
      </section>
    </div>
  );
}
```

- [ ] **Step 4: Integrate real dashboard data**

In `frontend/src/components/WorkspaceDashboard.tsx`:

- Keep all existing `panelStates`, `activeSource`, model, finance, report, and code lookups.
- Derive up to three insights only from existing real results:
  - model result recommendation or metric summary;
  - finance result summary;
  - missing-value or quality finding from the active dataset.
- If fewer than three real insights exist, show only the available items; do not fill with demo copy.
- Render `WorkspaceInsightGrid` before detailed analysis routes and source ledger.
- Wrap model outcome details in `WorkspaceDetailPanel`.
- Keep empty state when no dataset is connected.

Use:

```tsx
const insights = [
  ...(financeResult?.summary ?? []),
  ...(modelResult?.recommended_models.map((model) => model.description) ?? []),
  ...(modelResult?.notes ?? []),
  ...getDatasetQualityInsights(activeSource.dataset, text)
].filter(Boolean).slice(0, 3);
```

Add this exact helper beside the existing dashboard helpers:

```tsx
function getDatasetQualityInsights(
  dataset: WorkspaceSource["dataset"],
  text: ReturnType<typeof useLocale>["text"]
) {
  const missing = Object.entries(dataset.missing_values)
    .filter(([, count]) => count > 0)
    .sort(([, left], [, right]) => right - left);
  if (missing.length === 0) {
    return [text("目前未偵測到缺失值。", "No missing values were detected.")];
  }
  const [column, count] = missing[0];
  return [
    text(
      `${column} 有 ${count.toLocaleString()} 筆缺失值，應先確認處理方式。`,
      `${column} has ${count.toLocaleString()} missing values and should be reviewed first.`
    )
  ];
}
```

- [ ] **Step 5: Add grid styles**

Add to `frontend/src/app/product-interface.css`:

```css
.workspace-insight-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(280px, .85fr);
  gap: 14px;
}

.workspace-priority-module,
.workspace-metric-module,
.workspace-chart-module {
  border: 1px solid var(--product-border);
  border-radius: 12px;
  background: var(--product-surface);
  box-shadow: 0 10px 26px rgb(28 47 68 / 6%);
}

.workspace-priority-module {
  grid-row: span 2;
  padding: 20px;
}

.workspace-metric-module,
.workspace-chart-module {
  padding: 16px;
}

@media (max-width: 900px) {
  .workspace-insight-grid { grid-template-columns: 1fr; }
  .workspace-priority-module { grid-row: auto; }
}
```

- [ ] **Step 6: Run focused and full tests**

Run:

```bash
cd frontend
npm run test:run -- src/components/__tests__/WorkspaceInsightGrid.test.tsx
npm run test:run
npm run typecheck
```

Expected: all frontend tests and typecheck pass.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/components/WorkspaceInsightGrid.tsx frontend/src/components/WorkspaceDashboard.tsx frontend/src/app/product-interface.css frontend/src/components/__tests__/WorkspaceInsightGrid.test.tsx
git commit -m "feat: prioritize workspace insights and next actions"
```

## Task 9: Remove Legacy Conflicts and Complete Responsive States

**Files:**
- Modify: `frontend/src/app/globals.css`
- Modify: `frontend/src/app/product-interface.css`
- Modify: `frontend/src/app/product-motion.css`

- [ ] **Step 1: Audit conflicting selectors**

Run:

```bash
cd frontend
rg -n "marketing-hero|live-product-preview|product-sidebar|product-main-column|product-nav|product-topbar|workspace-outcome|next-action-band" src/app/globals.css
```

Expected: list of legacy selectors that overlap the new focused CSS.

- [ ] **Step 2: Remove obsolete Hero and preview rules**

Delete the old `.marketing-hero*`, `.marketing-preview-surface`, and `.live-product-preview*` blocks that no longer have rendered components. Keep journey, capability, trust, footer, upload, model, finance, and report styles.

- [ ] **Step 3: Remove obsolete 236px dark-sidebar rules**

Delete the previous `.product-sidebar`, `.product-brand`, `.product-nav`, `.sidebar-evidence`, `.product-main-column`, and their conflicting responsive rules from `globals.css`. The new definitions live in `product-interface.css`.

- [ ] **Step 4: Add stable responsive dimensions**

In `product-interface.css`, guarantee:

```css
html { background: var(--product-background); }
body { color: var(--product-text-primary); background: var(--product-background); }

.product-content {
  width: min(100%, 1560px);
  min-width: 0;
}

@media (max-width: 860px) {
  .product-sidebar { display: none; }
  .product-main-column { margin-left: 0; padding-bottom: 70px; }
  .mobile-product-nav { display: grid; }
  .product-topbar { min-width: 0; }
}

@media (max-width: 620px) {
  .product-content { padding-inline: 14px; }
  .topbar-actions { min-width: 0; }
  .source-select.is-compact { min-width: 0; max-width: 150px; }
}
```

- [ ] **Step 5: Add complete state feedback**

Use exact properties, not `transition: all`:

```css
[data-slot="button"],
.theme-picker-grid button,
.workspace-priority-module a {
  transition:
    color 180ms ease,
    background-color 180ms ease,
    border-color 180ms ease,
    box-shadow 180ms ease,
    transform 140ms var(--product-ease-out);
}

[data-slot="button"]:active,
.theme-picker-grid button:active,
.workspace-priority-module a:active {
  transform: scale(.98);
}

:focus-visible {
  outline: 2px solid var(--product-accent-secondary);
  outline-offset: 3px;
}
```

- [ ] **Step 6: Run CSS and build checks**

Run:

```bash
cd frontend
rg -n "transition:\\s*all|scale\\(0\\)|ease-in[;,)]" src/app src/components
npm run test:run
npm run typecheck
npm run build
```

Expected:

- The `rg` command produces no newly introduced violations in Phase A files.
- Tests, typecheck, and build pass.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/app/globals.css frontend/src/app/product-interface.css frontend/src/app/product-motion.css
git commit -m "refactor: remove legacy interface conflicts"
```

## Task 10: Browser Verification at Desktop, Tablet, and Mobile

**Files:**
- Modify only if defects are found: Phase A frontend files.

- [ ] **Step 1: Start the production server**

Run:

```bash
cd frontend
npm run build
npm run start -- --hostname 0.0.0.0 --port 3010
```

Expected: Next.js production server listens on port 3010.

- [ ] **Step 2: Verify the homepage at 1440×900**

Open `http://127.0.0.1:3010`.

Verify:

- H1 contains exactly two visible lines.
- `找到下一步。` remains one line.
- Data Lens follows the pointer smoothly.
- Primary CTA opens `/app/data`.
- No horizontal overflow.
- Header and body text meet contrast requirements.

- [ ] **Step 3: Verify workspace at 1440×900**

Open `http://127.0.0.1:3010/app`.

Verify:

- Icon rail is fixed and does not cover content.
- Charts route is present.
- Theme picker previews and applies all ten themes.
- Opening detail panel does not shift the layout.
- Escape closes popovers and panels.
- Existing workspace data remains available after returning from the homepage.

- [ ] **Step 4: Verify tablet at 834×1112**

Verify homepage and `/app/data`:

- Hero remains two lines.
- Board stacks below copy.
- Topbar controls fit without overlap.
- Workspace content does not sit beneath navigation.

- [ ] **Step 5: Verify mobile at 390×844**

Verify homepage and all primary workspace routes:

- No horizontal overflow.
- Hero remains exactly two lines.
- Bottom navigation remains readable and touch targets are at least 44px.
- Detail panel becomes a bottom drawer.
- Theme picker is usable without clipped text.
- Long filenames wrap or truncate without resizing controls.

- [ ] **Step 6: Verify reduced motion and keyboard**

Enable reduced motion and verify:

- Lens no longer tracks the pointer.
- Route, panel, and result transitions become fade-only or instant.
- Tab order follows visual order.
- Focus is visible on navigation, CTA, theme options, and panel close buttons.

- [ ] **Step 7: Inspect console and fix any issue**

Expected:

- No hydration mismatch.
- No React key or accessibility warnings.
- No failed resource requests.

- [ ] **Step 8: Run final Phase A commands**

```bash
cd frontend
npm run test:run
npm run typecheck
npm run build
```

Expected: all pass.

- [ ] **Step 9: Commit verification fixes**

```bash
git add frontend
git commit -m "fix: complete responsive interface verification"
```

Only stage Phase A files; do not stage unrelated backend or documentation changes.

## Task 11: Document Phase A

**Files:**
- Modify: `README.md`
- Modify: `PROGRESS.md`

- [ ] **Step 1: Update README**

Add:

- New homepage and workspace route map.
- Theme picker behavior and local persistence key.
- `npm run test:run`, `npm run typecheck`, and `npm run build`.
- Accessibility and reduced-motion behavior.
- Clear note that charts route does not fabricate outputs before the real chart engine phase.

- [ ] **Step 2: Update PROGRESS**

Add a dated Phase A section with:

```markdown
## 2026-06-15：通用分析平台階段 A

### 已完成檔案
- ...

### 新增功能
- Data Lens 兩行 Hero
- 十套語意配色
- 桌面工具式工作區
- 漸進式結果層級

### 如何啟動
...

### 如何測試
...

### Known Issues
- 圖表工作區目前只呈現真實資料狀態；完整圖表生成將在 Phase F 接入。
- Worker 真實進度將在 Phase B 接入。

### 下一階段
- PostgreSQL、Redis、背景 Worker 與持久化分析任務。
```

- [ ] **Step 3: Verify documentation commands**

Run every command copied into README and confirm it matches the actual package scripts.

- [ ] **Step 4: Commit**

```bash
git add README.md PROGRESS.md
git commit -m "docs: record product interface phase"
```

## Phase A Completion Check

Run:

```bash
cd frontend
npm run test:run
npm run typecheck
npm run build
```

Then verify the real upload, model, finance, report, and code-preview flows still call their existing FastAPI endpoints. Phase A is complete only when visual redesign and existing real analysis behavior both pass.
