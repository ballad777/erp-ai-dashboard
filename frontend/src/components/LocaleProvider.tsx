"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  type ReactNode
} from "react";
import { usePathname } from "next/navigation";

export type AppLocale = "zh-Hant" | "en";

type LocaleContextValue = {
  locale: AppLocale;
  isEnglish: boolean;
  text: (traditionalChinese: string, english: string) => string;
  path: (pathname: string) => string;
};

const LocaleContext = createContext<LocaleContextValue | null>(null);

export function LocaleProvider({
  locale,
  children
}: {
  locale: AppLocale;
  children: ReactNode;
}) {
  const pathname = usePathname();
  const documentLocale: AppLocale =
    pathname === "/en" || pathname.startsWith("/en/") ? "en" : locale;
  const value = useMemo<LocaleContextValue>(
    () => ({
      locale,
      isEnglish: locale === "en",
      text: (traditionalChinese, english) =>
        locale === "en" ? english : traditionalChinese,
      path: (pathname) => localizePath(pathname, locale)
    }),
    [locale]
  );

  useEffect(() => {
    document.documentElement.lang = documentLocale;
    document.cookie = `finai-locale=${documentLocale}; path=/; max-age=31536000; samesite=lax`;
  }, [documentLocale]);

  return (
    <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>
  );
}

export function useLocale() {
  const context = useContext(LocaleContext);
  if (!context) {
    throw new Error("useLocale 必須在 LocaleProvider 內使用。");
  }
  return context;
}

export function localizePath(pathname: string, locale: AppLocale) {
  if (pathname.startsWith("#")) return pathname;
  const normalized = pathname.startsWith("/") ? pathname : `/${pathname}`;
  const withoutEnglishPrefix =
    normalized === "/en"
      ? "/"
      : normalized.startsWith("/en/")
        ? normalized.slice(3)
        : normalized;

  if (locale === "en") {
    return withoutEnglishPrefix === "/"
      ? "/en"
      : `/en${withoutEnglishPrefix}`;
  }
  return withoutEnglishPrefix;
}

export function useLanguageDestination() {
  const pathname = usePathname();
  const { locale } = useLocale();
  const nextLocale: AppLocale = locale === "en" ? "zh-Hant" : "en";
  return {
    nextLocale,
    destination: localizePath(pathname, nextLocale)
  };
}
