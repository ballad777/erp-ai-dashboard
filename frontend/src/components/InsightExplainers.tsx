"use client";

import { useEffect, useMemo, useState } from "react";
import {
  BarChart3,
  BookOpenText,
  ChevronDown,
  CircleAlert,
  ClipboardList,
  Gauge,
  Layers3,
  Microscope,
  ShieldCheck,
  Sparkles
} from "lucide-react";
import { useLocale } from "@/components/LocaleProvider";
import { WorkspaceDetailPanel } from "@/components/WorkspaceDetailPanel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type {
  ChartStory,
  Confidence,
  EvidenceItem,
  PlainSummary,
  ResearchDetails,
  TermDefinition
} from "@/lib/api";

export type ReadingDepth = "simple" | "standard" | "research";

const readingDepthStorageKey = "datapilot-reading-depth";
const readingDepthEventName = "datapilot-reading-depth-change";

function isReadingDepth(value: unknown): value is ReadingDepth {
  return value === "simple" || value === "standard" || value === "research";
}

export function useReadingDepth() {
  const [depth, setDepthState] = useState<ReadingDepth>("simple");

  useEffect(() => {
    const stored = window.localStorage.getItem(readingDepthStorageKey);
    if (isReadingDepth(stored)) {
      setDepthState(stored);
    }

    function handleStorage(event: StorageEvent) {
      if (event.key === readingDepthStorageKey && isReadingDepth(event.newValue)) {
        setDepthState(event.newValue);
      }
    }

    function handleDepthChange(event: Event) {
      const nextDepth = (event as CustomEvent<ReadingDepth>).detail;
      if (isReadingDepth(nextDepth)) {
        setDepthState(nextDepth);
      }
    }

    window.addEventListener("storage", handleStorage);
    window.addEventListener(readingDepthEventName, handleDepthChange);
    return () => {
      window.removeEventListener("storage", handleStorage);
      window.removeEventListener(readingDepthEventName, handleDepthChange);
    };
  }, []);

  function setDepth(nextDepth: ReadingDepth) {
    setDepthState(nextDepth);
    window.localStorage.setItem(readingDepthStorageKey, nextDepth);
    window.dispatchEvent(
      new CustomEvent<ReadingDepth>(readingDepthEventName, {
        detail: nextDepth
      })
    );
  }

  return { depth, setDepth };
}

export function ReadingDepthControl({ compact = false }: { compact?: boolean }) {
  const { text } = useLocale();
  const { depth, setDepth } = useReadingDepth();
  const options: Array<{ value: ReadingDepth; label: string; description: string }> = [
    {
      value: "simple",
      label: text("簡明", "Simple"),
      description: text("先看結論與下一步", "Conclusion and next step")
    },
    {
      value: "standard",
      label: text("標準", "Standard"),
      description: text("加入證據與圖表讀法", "Evidence and chart reading")
    },
    {
      value: "research",
      label: text("研究", "Research"),
      description: text("顯示方法、參數與限制", "Methods, parameters, limits")
    }
  ];

  return (
    <div className={`reading-depth-control ${compact ? "is-compact" : ""}`} role="group" aria-label={text("閱讀深度", "Reading depth")}>
      {!compact ? <span>{text("閱讀深度", "Reading depth")}</span> : null}
      <div>
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            aria-pressed={depth === option.value}
            title={option.description}
            onClick={() => setDepth(option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export function InsightHeadline({
  summary,
  confidence,
  evidence,
  title
}: {
  summary?: PlainSummary;
  confidence?: Confidence;
  evidence?: EvidenceItem[];
  title?: string;
}) {
  const { text } = useLocale();
  const { depth } = useReadingDepth();
  if (!summary?.headline && !summary?.next_action) return null;

  return (
    <section className="insight-headline" aria-labelledby="insight-headline-title">
      <div className="insight-headline-main">
        <span className="insight-headline-icon">
          <Sparkles aria-hidden="true" />
        </span>
        <div>
          <span className="section-kicker">{title ?? text("一句話結論", "One-line conclusion")}</span>
          <h2 id="insight-headline-title">{summary.headline}</h2>
          {summary.next_action ? (
            <p>
              <strong>{text("下一步：", "Next: ")}</strong>
              {summary.next_action}
            </p>
          ) : null}
        </div>
      </div>
      <div className="insight-headline-side">
        <ConfidenceBadge confidence={confidence} />
        {depth !== "simple" && evidence?.length ? (
          <EvidenceList evidence={evidence.slice(0, 3)} compact />
        ) : null}
      </div>
    </section>
  );
}

export function ConfidenceBadge({ confidence }: { confidence?: Confidence }) {
  const { text } = useLocale();
  const level = confidence?.level ?? "medium";
  const label =
    level === "high"
      ? text("可信度高", "High confidence")
      : level === "low"
        ? text("可信度低", "Low confidence")
        : text("可信度中", "Medium confidence");
  return (
    <div className={`confidence-badge is-${level}`}>
      <ShieldCheck aria-hidden="true" />
      <div>
        <strong>{label}</strong>
        {confidence?.reason ? <span>{confidence.reason}</span> : null}
      </div>
    </div>
  );
}

export function PlainSummaryGrid({ summary }: { summary?: PlainSummary }) {
  const { text } = useLocale();
  if (!summary) return null;
  const cards = [
    {
      label: text("發生了什麼", "What happened"),
      value: summary.what_happened,
      icon: ClipboardList
    },
    {
      label: text("為什麼重要", "Why it matters"),
      value: summary.why_it_matters,
      icon: Gauge
    },
    {
      label: text("要小心什麼", "What to watch"),
      value: summary.risk,
      icon: CircleAlert
    },
    {
      label: text("下一步做什麼", "Next action"),
      value: summary.next_action,
      icon: Sparkles
    }
  ].filter((card) => Boolean(card.value));

  if (cards.length === 0) return null;

  return (
    <div className="plain-readable-grid">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <article key={card.label}>
            <span>
              <Icon aria-hidden="true" />
              {card.label}
            </span>
            <p>{card.value}</p>
          </article>
        );
      })}
    </div>
  );
}

export function EvidenceList({
  evidence,
  compact = false
}: {
  evidence?: EvidenceItem[];
  compact?: boolean;
}) {
  const { text } = useLocale();
  const items = evidence?.filter((item) => item.label || item.value) ?? [];
  if (!items.length) return null;
  return (
    <section className={`evidence-list ${compact ? "is-compact" : ""}`} aria-label={text("支撐證據", "Supporting evidence")}>
      {!compact ? (
        <div className="section-title-row">
          <div>
            <span>{text("證據", "Evidence")}</span>
            <h3>{text("系統為什麼這樣判斷", "Why the system made this call")}</h3>
          </div>
        </div>
      ) : null}
      <dl>
        {items.map((item, index) => (
          <div key={`${item.label}-${index}`}>
            <dt>{item.label}</dt>
            <dd>{item.value}</dd>
            {item.source ? <small>{item.source}</small> : null}
          </div>
        ))}
      </dl>
    </section>
  );
}

export function MetricExplainer({
  terms,
  limit = 6
}: {
  terms?: TermDefinition[];
  limit?: number;
}) {
  const { text } = useLocale();
  const { depth } = useReadingDepth();
  const visibleTerms = useMemo(() => {
    const clean = terms?.filter((term) => term.term) ?? [];
    return depth === "research" ? clean : clean.slice(0, limit);
  }, [depth, limit, terms]);

  if (!visibleTerms.length) return null;

  return (
    <section className="metric-explainer" aria-labelledby="metric-explainer-title">
      <div className="section-title-row">
        <div>
          <span>{text("指標讀法", "Metric guide")}</span>
          <h3 id="metric-explainer-title">{text("這些數字該怎麼看", "How to read these numbers")}</h3>
        </div>
        <Badge variant="outline">{visibleTerms.length}</Badge>
      </div>
      <div className="metric-explainer-grid">
        {visibleTerms.map((term) => (
          <details key={term.term} className="metric-term-card">
            <summary>
              <span>
                <strong>{term.term}</strong>
                <small>{term.plain_explanation}</small>
              </span>
              <ChevronDown aria-hidden="true" />
            </summary>
            <div>
              {term.this_result_means ? (
                <p>
                  <strong>{text("這次代表", "This result means")}</strong>
                  {term.this_result_means}
                </p>
              ) : null}
              {term.how_to_read ? (
                <p>
                  <strong>{text("判讀方式", "How to read")}</strong>
                  {term.how_to_read}
                </p>
              ) : null}
              {depth === "research" ? (
                <>
                  {term.technical_definition ? (
                    <p>
                      <strong>{text("技術定義", "Technical definition")}</strong>
                      {term.technical_definition}
                    </p>
                  ) : null}
                  {term.formula ? (
                    <p>
                      <strong>{text("公式", "Formula")}</strong>
                      <code>{term.formula}</code>
                    </p>
                  ) : null}
                </>
              ) : null}
              {term.caveat ? (
                <p>
                  <strong>{text("限制", "Caveat")}</strong>
                  {term.caveat}
                </p>
              ) : null}
            </div>
          </details>
        ))}
      </div>
    </section>
  );
}

export function ChartStoryPanel({
  story,
  imageUrl,
  imageAlt
}: {
  story: ChartStory;
  imageUrl?: string;
  imageAlt?: string;
}) {
  const { text } = useLocale();
  const { depth } = useReadingDepth();
  return (
    <article className="chart-story-panel">
      {imageUrl ? (
        <figure>
          <img src={imageUrl} alt={imageAlt ?? story.title} loading="lazy" />
        </figure>
      ) : null}
      <div className="chart-story-copy">
        <span className="section-kicker">
          <BarChart3 aria-hidden="true" />
          {story.title}
        </span>
        <StoryBlock label={text("這張圖在看什麼", "What this chart shows")} value={story.explanation} />
        <StoryBlock label={text("關鍵發現", "Key finding")} value={story.key_findings} />
        <StoryBlock label={text("代表意義", "Meaning")} value={story.meaning} />
        <StoryBlock label={text("建議下一步", "Recommended action")} value={story.recommended_action} />
        {depth !== "simple" ? (
          <details className="micro-disclosure">
            <summary>
              {text("看更多判讀與限制", "More interpretation and limits")}
              <ChevronDown aria-hidden="true" />
            </summary>
            <div className="chart-story-extra">
              <StoryBlock label={text("不能證明什麼", "What it cannot prove")} value={story.what_it_cannot_prove} />
              <StoryBlock label={text("趨勢解讀", "Trend interpretation")} value={story.trend_interpretation} />
              <StoryBlock label={text("異常說明", "Anomaly note")} value={story.anomaly_note} />
              <StoryBlock label={text("決策洞察", "Decision insight")} value={story.business_insight} />
            </div>
          </details>
        ) : null}
      </div>
    </article>
  );
}

export function ResearchDetailsDrawer({
  details,
  title
}: {
  details?: ResearchDetails;
  title?: string;
}) {
  const { text } = useLocale();
  if (!details) return null;
  const hasContent =
    details.method ||
    details.assumptions?.length ||
    details.parameters ||
    details.limitations?.length ||
    details.artifacts?.length;
  if (!hasContent) return null;

  return (
    <WorkspaceDetailPanel
      title={title ?? text("研究細節", "Research details")}
      closeLabel={text("關閉研究細節", "Close research details")}
      trigger={
        <Button type="button" variant="outline">
          <Microscope aria-hidden="true" />
          {text("研究細節", "Research details")}
        </Button>
      }
    >
      <div className="research-detail-stack">
        {details.method ? (
          <section>
            <span className="section-kicker">
              <BookOpenText aria-hidden="true" />
              {text("方法", "Method")}
            </span>
            <p>{details.method}</p>
          </section>
        ) : null}
        <ResearchList title={text("假設", "Assumptions")} items={details.assumptions} />
        {details.parameters ? (
          <section>
            <span className="section-kicker">
              <Layers3 aria-hidden="true" />
              {text("參數", "Parameters")}
            </span>
            <pre>{JSON.stringify(details.parameters, null, 2)}</pre>
          </section>
        ) : null}
        <ResearchList title={text("限制", "Limitations")} items={details.limitations} />
        <ResearchList
          title={text("可重現資產", "Reproducible artifacts")}
          items={details.artifacts?.filter((item): item is string => Boolean(item))}
        />
      </div>
    </WorkspaceDetailPanel>
  );
}

function StoryBlock({ label, value }: { label: string; value?: string }) {
  if (!value) return null;
  return (
    <div className="chart-story-block">
      <strong>{label}</strong>
      <p>{value}</p>
    </div>
  );
}

function ResearchList({ title, items }: { title: string; items?: string[] }) {
  if (!items?.length) return null;
  return (
    <section>
      <span className="section-kicker">{title}</span>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}
