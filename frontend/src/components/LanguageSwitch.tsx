"use client";

import Link from "next/link";
import { Languages } from "lucide-react";
import { useLanguageDestination, useLocale } from "@/components/LocaleProvider";
import { cn } from "@/lib/utils";

export function LanguageSwitch({
  compact = false,
  className
}: {
  compact?: boolean;
  className?: string;
}) {
  const { locale, text } = useLocale();
  const { destination } = useLanguageDestination();

  return (
    <Link
      href={destination}
      className={cn("language-switch", compact && "is-compact", className)}
      aria-label={text("切換為英文", "Switch to Traditional Chinese")}
      title={text("切換為英文", "Switch to Traditional Chinese")}
      suppressHydrationWarning
    >
      <Languages aria-hidden="true" />
      <span>{locale === "en" ? "繁中" : "EN"}</span>
    </Link>
  );
}
