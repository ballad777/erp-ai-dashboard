"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import {
  BookOpenText,
  BrainCircuit,
  ChartNoAxesCombined,
  Database,
  FileText,
  LayoutDashboard,
  Settings2,
  Upload,
  Volume2,
  VolumeX,
  X
} from "lucide-react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { EnvironmentNotice } from "@/components/EnvironmentNotice";
import { useFeedback } from "@/components/FeedbackProvider";
import { ReadingDepthControl } from "@/components/InsightExplainers";
import { LanguageSwitch } from "@/components/LanguageSwitch";
import { useLocale } from "@/components/LocaleProvider";
import { AmbientCanvas, RouteStage } from "@/components/MotionPrimitives";
import { WorkspaceRestoringState } from "@/components/PagePrimitives";
import { ThemePicker } from "@/components/ThemePicker";
import { useWorkspace } from "@/components/WorkspaceProvider";
import {
  useWorkspaceSources,
  WorkspaceSourceSelect
} from "@/components/WorkspaceSource";
import { Button } from "@/components/ui/button";

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { text, path } = useLocale();
  const { isHydrated } = useWorkspace();
  const { completedUploads } = useWorkspaceSources();
  const [settingsOpen, setSettingsOpen] = useState(false);
  const settingsRef = useRef<HTMLDivElement | null>(null);
  const reducedMotion = useReducedMotion();
  const { soundEnabled, setSoundEnabled } = useFeedback();
  const canonicalPath = pathname.startsWith("/en/")
    ? pathname.slice(3)
    : pathname === "/en"
      ? "/"
      : pathname;
  const navItems = [
    { href: "/app", label: text("總覽", "Overview"), icon: LayoutDashboard },
    { href: "/app/data", label: text("資料", "Data"), icon: Database },
    { href: "/app/models", label: text("模型", "Models"), icon: BrainCircuit },
    { href: "/app/charts", label: text("名詞", "Terms"), icon: BookOpenText },
    { href: "/app/finance", label: text("金融", "Finance"), icon: ChartNoAxesCombined },
    { href: "/app/reports", label: text("報告", "Reports"), icon: FileText }
  ];
  const pageTitles: Record<string, string> = {
    "/app": text("分析總覽", "Analysis overview"),
    "/app/data": text("資料工作區", "Data workspace"),
    "/app/models": text("模型實驗室", "Model lab"),
    "/app/charts": text("專有名詞", "Terminology"),
    "/app/finance": text("金融分析", "Financial analysis"),
    "/app/reports": text("報告中心", "Report center")
  };
  const pageTitle = pageTitles[canonicalPath] ?? text("智能金融資料分析", "Intelligent Data Analysis");
  const showTopbarAddData =
    canonicalPath !== "/app/data" && completedUploads.length > 0;

  useEffect(() => {
    if (!settingsOpen) return;
    const handlePointerDown = (event: PointerEvent) => {
      if (!settingsRef.current?.contains(event.target as Node)) {
        setSettingsOpen(false);
      }
    };
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setSettingsOpen(false);
    };
    window.addEventListener("pointerdown", handlePointerDown);
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("pointerdown", handlePointerDown);
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [settingsOpen]);

  return (
    <div className="product-shell">
      <a
        className="skip-link"
        href="#main-content"
        suppressHydrationWarning
      >
        {text("跳至主要內容", "Skip to main content")}
      </a>
      <AmbientCanvas variant="workspace" />

      <aside className="product-sidebar">
        <Link
          href={path("/")}
          className="product-brand"
          aria-label={text("智能金融資料分析首頁", "Product home")}
          suppressHydrationWarning
        >
          <span className="product-brand-mark">智</span>
          <span className="product-brand-copy">
            <strong>{text("智能金融資料分析", "Intelligent Data Analysis")}</strong>
            <small>{text("清楚的下一步", "A clear next step")}</small>
          </span>
        </Link>

        <nav className="product-nav" aria-label={text("主要導覽", "Main navigation")}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = canonicalPath === item.href;
            return (
              <Link
                key={item.href}
                href={path(item.href)}
                aria-current={isActive ? "page" : undefined}
                className={isActive ? "is-active" : ""}
                suppressHydrationWarning
              >
                <Icon aria-hidden="true" />
                <span className="product-nav-label">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      <div className="product-main-column">
        <header className="product-topbar">
          <div className="topbar-title">
            <span>{text("工作區", "Workspace")}</span>
            <strong>{pageTitle}</strong>
          </div>
          <div className="topbar-actions">
            <WorkspaceSourceSelect compact />
            {showTopbarAddData ? (
              <Button asChild variant="outline" size="sm">
                <Link href={path("/app/data")} suppressHydrationWarning>
                  <Upload aria-hidden="true" />
                  {text("加入資料", "Add data")}
                </Link>
              </Button>
            ) : null}
            <ThemePicker />
            <div className="workspace-settings" ref={settingsRef}>
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                aria-label={text("開啟設定", "Open settings")}
                aria-expanded={settingsOpen}
                onClick={() => setSettingsOpen((current) => !current)}
              >
                <Settings2 aria-hidden="true" />
              </Button>
              <AnimatePresence initial={false}>
                {settingsOpen ? (
                  <motion.div
                    className="workspace-settings-popover"
                    role="dialog"
                    aria-label={text("工作區設定", "Workspace settings")}
                    initial={reducedMotion ? false : { opacity: 0, transform: "translate3d(0,-6px,0) scale(.98)" }}
                    animate={{ opacity: 1, transform: "translate3d(0,0,0) scale(1)" }}
                    exit={{ opacity: 0, transform: reducedMotion ? "none" : "translate3d(0,-4px,0) scale(.99)" }}
                    transition={{ duration: reducedMotion ? 0 : 0.18, ease: [0.16, 1, 0.3, 1] }}
                  >
                    <div className="settings-popover-heading">
                      <strong>{text("工作區設定", "Workspace settings")}</strong>
                      <button type="button" onClick={() => setSettingsOpen(false)} aria-label={text("關閉設定", "Close settings")}>
                        <X aria-hidden="true" />
                      </button>
                    </div>
                    <div className="settings-row">
                      <span>{text("介面語言", "Interface language")}</span>
                      <LanguageSwitch />
                    </div>
                    <div className="settings-row is-stacked">
                      <span>{text("閱讀深度", "Reading depth")}</span>
                      <ReadingDepthControl compact />
                    </div>
                    <button
                      type="button"
                      className="settings-row is-button"
                      aria-pressed={soundEnabled}
                      onClick={() => setSoundEnabled(!soundEnabled)}
                    >
                      <span>
                        {soundEnabled ? <Volume2 aria-hidden="true" /> : <VolumeX aria-hidden="true" />}
                        {text("介面音效", "Interface sounds")}
                      </span>
                      <span className={`settings-toggle ${soundEnabled ? "is-on" : ""}`} aria-hidden="true"><i /></span>
                    </button>
                  </motion.div>
                ) : null}
              </AnimatePresence>
            </div>
          </div>
        </header>
        <EnvironmentNotice />

        <main id="main-content" className="product-content">
          {isHydrated ? (
            <RouteStage>{children}</RouteStage>
          ) : (
            <WorkspaceRestoringState />
          )}
        </main>
      </div>

      <nav className="mobile-product-nav" aria-label={text("手機主要導覽", "Mobile navigation")}>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = canonicalPath === item.href;
          return (
            <Link
              key={item.href}
              href={path(item.href)}
              aria-current={isActive ? "page" : undefined}
              className={isActive ? "is-active" : ""}
              suppressHydrationWarning
            >
              <Icon aria-hidden="true" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
