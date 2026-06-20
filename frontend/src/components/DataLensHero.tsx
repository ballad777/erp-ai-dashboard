"use client";

import Link from "next/link";
import { ArrowRight, ScanSearch } from "lucide-react";
import {
  motion,
  useMotionTemplate,
  useMotionValue,
  useReducedMotion,
  useSpring
} from "motion/react";
import { useLocale } from "@/components/LocaleProvider";
import { Button } from "@/components/ui/button";

const cells = Array.from({ length: 32 }, (_, index) => index);

export function DataLensHero() {
  const { text, path } = useLocale();
  const reducedMotion = useReducedMotion();
  const pointerX = useMotionValue(330);
  const pointerY = useMotionValue(210);
  const springX = useSpring(pointerX, {
    stiffness: 105,
    damping: 24,
    mass: 0.55
  });
  const springY = useSpring(pointerY, {
    stiffness: 105,
    damping: 24,
    mass: 0.55
  });
  const lensTransform = useMotionTemplate`translate3d(${springX}px, ${springY}px, 0) translate3d(-50%, -50%, 0)`;

  return (
    <section className="data-lens-hero">
      <div className="data-lens-hero-inner">
        <div className="data-lens-copy">
          <span className="data-lens-eyebrow">
            {text(
              "給一般人使用的 AI 分析工作區",
              "An AI analysis workspace for everyone"
            )}
          </span>
          <h1>
            <span data-hero-line className="whitespace-nowrap">
              {text("從資料到決策", "From data to decisions")}
            </span>
            <span data-hero-line className="whitespace-nowrap">
              {text("一個工作區完成", "In one workspace")}
            </span>
          </h1>
          <p>
            {text(
              "上傳資料，系統先理解資料、解釋重點，再把圖表、模型與報告整理成清楚的下一步。",
              "Upload data, let the system understand it, explain what matters, then turn charts, models, and reports into the next step."
            )}
          </p>
          <div className="data-lens-actions">
            <Button asChild variant="premium" size="lg">
              <Link href={path("/app/data")}>
                {text("開始分析", "Start analyzing")}
                <ArrowRight aria-hidden="true" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="#journey">
                {text("查看運作方式", "See how it works")}
              </Link>
            </Button>
          </div>
          <div className="data-lens-proof">
            <span>{text("真實 Python 分析", "Real Python analysis")}</span>
            <span>{text("先解釋再建模", "Explain before modeling")}</span>
            <span>{text("報告可直接閱讀", "Readable reports")}</span>
          </div>
        </div>

        <div
          className="data-lens-board"
          role="img"
          aria-label={text(
            "互動式資料分析示意",
            "Interactive data analysis illustration"
          )}
          onPointerMove={(event) => {
            if (reducedMotion || event.pointerType === "touch") return;
            const bounds = event.currentTarget.getBoundingClientRect();
            pointerX.set(event.clientX - bounds.left);
            pointerY.set(event.clientY - bounds.top);
          }}
          onPointerLeave={() => {
            pointerX.set(330);
            pointerY.set(210);
          }}
        >
          <div className="data-lens-toolbar" aria-hidden="true">
            <span className="data-lens-file">
              <i />
              {text("年度銷售趨勢分析", "Annual sales trend analysis")}
            </span>
            <span>{text("12,456 筆 × 28 欄", "12,456 rows × 28 columns")}</span>
          </div>
          <div className="data-lens-table" aria-hidden="true">
            {cells.map((cell) => (
              <i
                key={cell}
                className={
                  cell === 5 || cell === 16 || cell === 26 ? "is-signal" : ""
                }
              />
            ))}
          </div>
          <motion.div
            className="data-lens-orb"
            style={reducedMotion ? undefined : { transform: lensTransform }}
            aria-hidden="true"
          >
            <span>
              <ScanSearch />
            </span>
          </motion.div>
          <motion.div
            className="data-lens-insight"
            initial={
              reducedMotion
                ? false
                : {
                    opacity: 0,
                    transform: "translate3d(0,8px,0) scale(.98)"
                  }
            }
            animate={{
              opacity: 1,
              transform: "translate3d(0,0,0) scale(1)"
            }}
            transition={{
              duration: reducedMotion ? 0 : 0.42,
              delay: reducedMotion ? 0 : 0.3
            }}
          >
            <span>{text("分析完成", "Analysis complete")}</span>
            <strong>
              {text("發現 3 個關鍵訊號", "3 key signals found")}
            </strong>
            <small>
              {text(
                "季節性 · 退貨異常 · 非線性關係",
                "Seasonality · Return anomaly · Nonlinear relationship"
              )}
            </small>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
