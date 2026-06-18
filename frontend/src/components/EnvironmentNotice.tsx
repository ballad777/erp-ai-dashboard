"use client";

import { ShieldAlert } from "lucide-react";
import { useLocale } from "@/components/LocaleProvider";

export function EnvironmentNotice() {
  const { text } = useLocale();

  return (
    <div
      className="environment-notice relative z-30 flex min-h-10 items-center justify-center gap-2 border-b border-amber-500/25 bg-amber-50 px-4 py-2 text-center text-sm font-medium text-amber-950 dark:bg-amber-950/40 dark:text-amber-100"
      role="status"
      aria-live="polite"
    >
      <ShieldAlert className="size-4 shrink-0" aria-hidden="true" />
      <span>
        {text(
          "目前為封閉測試環境，請勿上傳個資、醫療、財務帳戶或其他敏感資料。",
          "Closed testing environment. Do not upload personal, medical, financial-account, or other sensitive data."
        )}
      </span>
    </div>
  );
}
