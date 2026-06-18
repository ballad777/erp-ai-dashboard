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
  getThemeRuntimeVariables,
  themeIds,
  type ThemeId
} from "@/lib/themes";

type ThemeContextValue = {
  appliedTheme: ThemeId;
  selectTheme: (theme: ThemeId) => void;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);
const storageKey = "finai-product-theme-v1";

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [appliedTheme, setAppliedTheme] = useState<ThemeId>(defaultThemeId);

  useEffect(() => {
    let restoredTheme = defaultThemeId;

    try {
      restoredTheme = validateStoredTheme(
        window.localStorage.getItem(storageKey)
      );
    } catch {
      // Theme persistence is optional; the in-memory theme remains usable.
    }

    setAppliedTheme(restoredTheme);
    applyThemeToRoot(restoredTheme);
  }, []);

  const selectTheme = useCallback((theme: ThemeId) => {
    const nextTheme = getTheme(theme).id;
    setAppliedTheme(nextTheme);
    applyThemeToRoot(nextTheme);

    try {
      window.localStorage.setItem(storageKey, nextTheme);
    } catch {
      // Applying the theme in memory must not depend on storage availability.
    }
  }, []);

  const value = useMemo(
    () => ({
      appliedTheme,
      selectTheme
    }),
    [appliedTheme, selectTheme]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useProductTheme() {
  const context = useContext(ThemeContext);

  if (!context) {
    throw new Error("useProductTheme must be used inside ThemeProvider.");
  }

  return context;
}

function validateStoredTheme(storedTheme: string | null): ThemeId {
  if (!themeIds.includes(storedTheme as ThemeId)) {
    return defaultThemeId;
  }

  return getTheme(storedTheme).id;
}

function applyThemeToRoot(themeId: ThemeId) {
  const theme = getTheme(themeId);
  const root = document.documentElement;

  root.dataset.productTheme = theme.id;
  root.dataset.productAppearance = theme.appearance;

  for (const [variableName, value] of Object.entries(
    getThemeRuntimeVariables(theme)
  )) {
    root.style.setProperty(variableName, value);
  }
}
