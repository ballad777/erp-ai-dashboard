"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, Menu, X } from "lucide-react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { EnvironmentNotice } from "@/components/EnvironmentNotice";
import { LanguageSwitch } from "@/components/LanguageSwitch";
import { useLocale } from "@/components/LocaleProvider";
import { AmbientCanvas } from "@/components/MotionPrimitives";
import { ThemePicker } from "@/components/ThemePicker";
import { Button } from "@/components/ui/button";

export function MarketingShell({ children }: { children: React.ReactNode }) {
  const { text, path } = useLocale();
  const [menuOpen, setMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const reducedMotion = useReducedMotion();

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 18);
    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    if (!menuOpen) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMenuOpen(false);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [menuOpen]);

  const navigation = [
    { href: "#journey", label: text("分析流程", "How it works") },
    { href: "#capabilities", label: text("產品能力", "Capabilities") },
    { href: "#trust", label: text("真實分析", "Real analysis") }
  ];

  return (
    <div className="marketing-site">
      <a
        className="skip-link"
        href="#marketing-main"
        suppressHydrationWarning
      >
        {text("跳至主要內容", "Skip to main content")}
      </a>
      <AmbientCanvas variant="marketing" />
      <header
        className={`marketing-header ${isScrolled ? "is-scrolled" : ""}`}
      >
        <div className="marketing-header-inner">
          <Link
            href={path("/")}
            className="marketing-brand"
            aria-label={text("智能金融資料分析首頁", "Product home")}
            suppressHydrationWarning
          >
            <span className="marketing-brand-mark">智</span>
            <span>{text("智能金融資料分析", "Intelligent Data Analysis")}</span>
          </Link>

          <nav className="marketing-nav" aria-label={text("主要導覽", "Main navigation")}>
            {navigation.map((item) => (
              <Link key={item.href} href={item.href} suppressHydrationWarning>
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="marketing-header-actions">
            <LanguageSwitch compact />
            <ThemePicker />
            <Button asChild variant="premium" size="sm">
              <Link href={path("/app")} suppressHydrationWarning>
                {text("開啟工作區", "Open workspace")}
                <ArrowRight aria-hidden="true" />
              </Link>
            </Button>
            <button
              type="button"
              className="marketing-menu-trigger"
              aria-expanded={menuOpen}
              aria-controls="mobile-marketing-menu"
              aria-label={text("開啟選單", "Open menu")}
              onClick={() => setMenuOpen(true)}
            >
              <Menu aria-hidden="true" />
            </button>
          </div>
        </div>
      </header>
      <EnvironmentNotice />

      <AnimatePresence initial={false}>
        {menuOpen ? (
          <motion.div
            className="marketing-mobile-overlay"
            initial={reducedMotion ? false : { opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: reducedMotion ? 0 : 0.18 }}
          >
            <button
              type="button"
              className="marketing-mobile-backdrop"
              aria-label={text("關閉選單", "Close menu")}
              onClick={() => setMenuOpen(false)}
            />
            <motion.div
              id="mobile-marketing-menu"
              className="marketing-mobile-menu"
              role="dialog"
              aria-modal="true"
              aria-label={text("網站選單", "Site menu")}
              initial={
                reducedMotion
                  ? false
                  : { opacity: 0, transform: "translate3d(0,-10px,0) scale(.98)" }
              }
              animate={{
                opacity: 1,
                transform: "translate3d(0,0,0) scale(1)"
              }}
              exit={{
                opacity: 0,
                transform: reducedMotion
                  ? "none"
                  : "translate3d(0,-6px,0) scale(.99)"
              }}
              transition={{
                duration: reducedMotion ? 0 : 0.24,
                ease: [0.16, 1, 0.3, 1]
              }}
            >
              <div className="marketing-mobile-menu-top">
                <strong>{text("導覽", "Navigation")}</strong>
                <button
                  type="button"
                  onClick={() => setMenuOpen(false)}
                  aria-label={text("關閉選單", "Close menu")}
                >
                  <X aria-hidden="true" />
                </button>
              </div>
              <nav>
                {navigation.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMenuOpen(false)}
                    suppressHydrationWarning
                  >
                    {item.label}
                    <ArrowRight aria-hidden="true" />
                  </Link>
                ))}
              </nav>
              <div className="marketing-mobile-menu-actions">
                <LanguageSwitch />
                <Button asChild variant="premium" size="lg">
                  <Link href={path("/app/data")} suppressHydrationWarning>
                    {text("開始分析資料", "Start analyzing")}
                    <ArrowRight aria-hidden="true" />
                  </Link>
                </Button>
              </div>
            </motion.div>
          </motion.div>
        ) : null}
      </AnimatePresence>

      <main id="marketing-main">{children}</main>

      <footer className="marketing-footer">
        <div>
          <Link
            href={path("/")}
            className="marketing-brand"
            suppressHydrationWarning
          >
            <span className="marketing-brand-mark">智</span>
            <span>{text("智能金融資料分析", "Intelligent Data Analysis")}</span>
          </Link>
          <p>
            {text(
              "理解資料、找到重點、看見依據，知道下一步。",
              "Understand the data, find what matters, and move forward with evidence."
            )}
          </p>
        </div>
        <div className="marketing-footer-links">
          <Link href={path("/app/data")} suppressHydrationWarning>{text("資料分析", "Data analysis")}</Link>
          <Link href={path("/app/models")} suppressHydrationWarning>{text("模型比較", "Model comparison")}</Link>
          <Link href={path("/app/finance")} suppressHydrationWarning>{text("金融分析", "Financial analysis")}</Link>
          <Link href={path("/app/reports")} suppressHydrationWarning>{text("報告輸出", "Reports")}</Link>
        </div>
      </footer>
    </div>
  );
}
