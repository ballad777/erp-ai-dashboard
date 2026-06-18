"use client";

import Link from "next/link";
import { ArrowRight, BarChart3, Database, Sparkles } from "lucide-react";
import { motion, useReducedMotion } from "motion/react";
import { useLocale } from "@/components/LocaleProvider";

type Metric = {
  label: string;
  value: string;
};

type TrendSummary = {
  title: string;
  detail: string;
  href: string;
};

export function WorkspaceInsightGrid({
  insights,
  nextAction,
  metrics,
  trend
}: {
  insights: string[];
  nextAction: { label: string; href: string };
  metrics: Metric[];
  trend?: TrendSummary | null;
}) {
  const { text } = useLocale();
  const reducedMotion = useReducedMotion();

  return (
    <div className="workspace-insight-grid">
      <motion.section
        className="workspace-priority-module"
        initial={
          reducedMotion
            ? false
            : { opacity: 0, transform: "translate3d(0,8px,0)" }
        }
        animate={{
          opacity: 1,
          transform: "translate3d(0,0,0)"
        }}
        transition={{
          duration: reducedMotion ? 0 : 0.34,
          ease: [0.23, 1, 0.32, 1]
        }}
      >
        <header>
          <span className="workspace-module-icon">
            <Sparkles aria-hidden="true" />
          </span>
          <div>
            <span>{text("優先順序", "Priority")}</span>
            <h2>{text("最重要的發現", "Most important findings")}</h2>
          </div>
        </header>
        {insights.length > 0 ? (
          <ol>
            {insights.slice(0, 3).map((insight, index) => (
              <li key={`${index}-${insight}`}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <p>{insight}</p>
              </li>
            ))}
          </ol>
        ) : (
          <p className="workspace-no-insight">
            {text(
              "尚無可顯示的分析發現",
              "No analysis finding is available yet"
            )}
          </p>
        )}
        <Link href={nextAction.href}>
          {nextAction.label}
          <ArrowRight aria-hidden="true" />
        </Link>
      </motion.section>

      <section className="workspace-metric-module">
        <header>
          <span className="workspace-module-icon">
            <Database aria-hidden="true" />
          </span>
          <div>
            <span>{text("資料狀態", "Data status")}</span>
            <h2>{text("資料概況", "Dataset overview")}</h2>
          </div>
        </header>
        {metrics.length > 0 ? (
          <dl>
            {metrics.map((metric) => (
              <div key={metric.label}>
                <dt>{metric.label}</dt>
                <dd>{metric.value}</dd>
              </div>
            ))}
          </dl>
        ) : (
          <p className="workspace-no-insight">
            {text("尚未連接資料", "No dataset connected")}
          </p>
        )}
      </section>

      <section className="workspace-chart-module">
        <header>
          <span className="workspace-module-icon">
            <BarChart3 aria-hidden="true" />
          </span>
          <div>
            <span>{text("視覺摘要", "Visual summary")}</span>
            <h2>{text("主要趨勢", "Primary trend")}</h2>
          </div>
        </header>
        {trend ? (
          <Link href={trend.href} className="workspace-trend-summary">
            <strong>{trend.title}</strong>
            <span>{trend.detail}</span>
            <ArrowRight aria-hidden="true" />
          </Link>
        ) : (
          <div className="workspace-chart-empty">
            <span aria-hidden="true">
              <i />
              <i />
              <i />
              <i />
            </span>
            <p>
              {text(
                "完成模型或金融分析後顯示真實圖表。",
                "Real charts appear after model or financial analysis."
              )}
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
