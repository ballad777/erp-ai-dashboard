"use client";

import { useMemo, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { useLocale } from "@/components/LocaleProvider";

export type AnalysisModelOption = {
  key: string;
  label: string;
  problemType: "regression" | "classification";
  description: string;
};

export function ModelSelectionDrawer({
  open,
  options,
  selected,
  onToggle,
  onClear
}: {
  open: boolean;
  options: AnalysisModelOption[];
  selected: string[];
  onToggle: (key: string) => void;
  onClear: () => void;
}) {
  const { text } = useLocale();
  const reducedMotion = useReducedMotion();
  const [query, setQuery] = useState("");
  const [family, setFamily] = useState<"all" | "regression" | "classification">("all");
  const visibleOptions = useMemo(
    () =>
      options.filter((option) => {
        const matchesFamily = family === "all" || option.problemType === family;
        const normalizedQuery = query.trim().toLocaleLowerCase();
        const matchesQuery =
          !normalizedQuery ||
          option.label.toLocaleLowerCase().includes(normalizedQuery) ||
          option.description.toLocaleLowerCase().includes(normalizedQuery);
        return matchesFamily && matchesQuery;
      }),
    [family, options, query]
  );

  return (
    <AnimatePresence initial={false}>
      {open ? (
        <motion.section
          className="model-selection-drawer"
          initial={false}
          animate={{ opacity: 1, transform: "translate3d(0,0,0)" }}
          exit={{
            opacity: 0,
            transform: reducedMotion ? "none" : "translate3d(0,-4px,0)"
          }}
          transition={{ duration: reducedMotion ? 0 : 0.2 }}
          aria-label={text("手動選擇模型", "Choose models manually")}
        >
          <div className="model-selection-toolbar">
            <label>
              <span className="sr-only">{text("搜尋模型", "Search models")}</span>
              <input
                type="search"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder={text("搜尋模型", "Search models")}
              />
            </label>
            <div role="group" aria-label={text("模型類型", "Model type")}>
              {(["all", "regression", "classification"] as const).map((value) => (
                <button
                  key={value}
                  type="button"
                  aria-pressed={family === value}
                  onClick={() => setFamily(value)}
                >
                  {value === "all"
                    ? text("全部", "All")
                    : value === "regression"
                      ? text("回歸", "Regression")
                      : text("分類", "Classification")}
                </button>
              ))}
            </div>
            <button type="button" onClick={onClear} disabled={selected.length === 0}>
              {text("清除選擇", "Clear selection")}
            </button>
          </div>
          <p className="ui-copy-secondary">
            {text(`已選 ${selected.length} 個模型`, `${selected.length} models selected`)}
          </p>
          <div className="model-selection-options">
            {visibleOptions.map((option) => (
              <label key={option.key}>
                <input
                  type="checkbox"
                  checked={selected.includes(option.key)}
                  onChange={() => onToggle(option.key)}
                />
                <span>
                  <strong>{option.label}</strong>
                  <small className="ui-option-description">{option.description}</small>
                </span>
              </label>
            ))}
          </div>
        </motion.section>
      ) : null}
    </AnimatePresence>
  );
}
