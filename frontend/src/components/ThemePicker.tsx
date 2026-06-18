"use client";

import { useState, type KeyboardEvent } from "react";
import { Check, Palette } from "lucide-react";
import { useLocale } from "@/components/LocaleProvider";
import { useProductTheme } from "@/components/ThemeProvider";
import { Button } from "@/components/ui/button";
import {
  Popover,
  PopoverContent,
  PopoverTrigger
} from "@/components/ui/popover";
import { themes } from "@/lib/themes";

export function ThemePicker() {
  const { text } = useLocale();
  const { appliedTheme, selectTheme } = useProductTheme();
  const [open, setOpen] = useState(false);

  function handleRadioKeyDown(
    event: KeyboardEvent<HTMLButtonElement>,
    currentIndex: number
  ) {
    if (!["ArrowRight", "ArrowDown", "ArrowLeft", "ArrowUp"].includes(event.key)) {
      return;
    }

    event.preventDefault();
    const direction =
      event.key === "ArrowRight" || event.key === "ArrowDown" ? 1 : -1;
    const nextIndex =
      (currentIndex + direction + themes.length) % themes.length;
    const nextTheme = themes[nextIndex];
    document
      .querySelector<HTMLButtonElement>(
        `[data-theme-option="${nextTheme.id}"]`
      )
      ?.focus();
  }

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="theme-picker-trigger"
          aria-label={text("配色", "Theme")}
        >
          <Palette aria-hidden="true" />
          <span>{text("配色", "Theme")}</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent
        align="end"
        className="theme-picker"
        aria-label={text("配色設定", "Theme settings")}
      >
        <div className="theme-picker-heading">
          <strong>{text("工作區配色", "Workspace theme")}</strong>
          <span>
            {text("點選後立即套用並保存", "Select to apply and save instantly")}
          </span>
        </div>

        <div
          className="theme-picker-grid"
          role="radiogroup"
          aria-label={text("選擇配色", "Choose theme")}
        >
          {themes.map((theme, index) => {
            const selected = appliedTheme === theme.id;
            return (
              <button
                key={theme.id}
                type="button"
                role="radio"
                aria-checked={selected}
                aria-label={text(theme.labelZh, theme.labelEn)}
                tabIndex={selected ? 0 : -1}
                data-theme-option={theme.id}
                className={selected ? "is-selected" : undefined}
                onClick={() => {
                  selectTheme(theme.id);
                  setOpen(false);
                }}
                onKeyDown={(event) => handleRadioKeyDown(event, index)}
              >
                <span className="theme-swatches" aria-hidden="true">
                  <i style={{ background: theme.tokens.background }} />
                  <i style={{ background: theme.tokens.accentPrimary }} />
                  <i style={{ background: theme.tokens.accentSecondary }} />
                </span>
                <span className="theme-option-copy">
                  <strong>{text(theme.labelZh, theme.labelEn)}</strong>
                  <small>
                    {text(theme.descriptionZh, theme.descriptionEn)}
                  </small>
                </span>
                {selected ? <Check aria-hidden="true" /> : null}
              </button>
            );
          })}
        </div>
      </PopoverContent>
    </Popover>
  );
}
