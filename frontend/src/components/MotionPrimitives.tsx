"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";
import {
  motion,
  useMotionTemplate,
  useMotionValue,
  useReducedMotion,
  useSpring
} from "motion/react";
import { cn } from "@/lib/utils";

const ambientEase = [0.45, 0, 0.2, 1] as const;

export function AmbientCanvas({
  variant = "workspace"
}: {
  variant?: "marketing" | "workspace";
}) {
  const reducedMotion = useReducedMotion();
  const pointerX = useMotionValue(-240);
  const pointerY = useMotionValue(-240);
  const springX = useSpring(pointerX, { stiffness: 48, damping: 22, mass: 0.9 });
  const springY = useSpring(pointerY, { stiffness: 48, damping: 22, mass: 0.9 });
  const pointerTransform = useMotionTemplate`translate3d(${springX}px, ${springY}px, 0) translate3d(-50%, -50%, 0)`;
  const frameRef = useRef<number | null>(null);

  useEffect(() => {
    const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");
    if (reducedMotion || !finePointer.matches) return;

    function handlePointerMove(event: PointerEvent) {
      if (frameRef.current !== null) cancelAnimationFrame(frameRef.current);
      frameRef.current = requestAnimationFrame(() => {
        pointerX.set(event.clientX);
        pointerY.set(event.clientY);
      });
    }

    window.addEventListener("pointermove", handlePointerMove, { passive: true });
    return () => {
      window.removeEventListener("pointermove", handlePointerMove);
      if (frameRef.current !== null) cancelAnimationFrame(frameRef.current);
    };
  }, [pointerX, pointerY, reducedMotion]);

  return (
    <div className={`ambient-canvas is-${variant}`} aria-hidden="true">
      <motion.div
        className="ambient-field ambient-field-one"
        initial={false}
        animate={
          reducedMotion
            ? undefined
            : {
                transform: [
                  "translate3d(0, 0, 0) scale(1)",
                  "translate3d(18px, 10px, 0) scale(1.025)",
                  "translate3d(-8px, 18px, 0) scale(1.01)",
                  "translate3d(0, 0, 0) scale(1)"
                ],
                opacity: [0.42, 0.5, 0.44, 0.42]
              }
        }
        transition={{ duration: 24, repeat: Infinity, ease: ambientEase }}
      />
      <motion.div
        className="ambient-field ambient-field-two"
        initial={false}
        animate={
          reducedMotion
            ? undefined
            : {
                transform: [
                  "translate3d(0, 0, 0) scale(1)",
                  "translate3d(-16px, 14px, 0) scale(1.02)",
                  "translate3d(10px, -8px, 0) scale(1.01)",
                  "translate3d(0, 0, 0) scale(1)"
                ],
                opacity: [0.34, 0.42, 0.36, 0.34]
              }
        }
        transition={{ duration: 29, repeat: Infinity, ease: ambientEase }}
      />
      <motion.div
        className="ambient-cursor"
        style={reducedMotion ? undefined : { transform: pointerTransform }}
      />
      <div className="ambient-grain" />
    </div>
  );
}

export function RouteStage({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const reducedMotion = useReducedMotion();

  return (
    <motion.div
      key={pathname}
      className="route-stage"
      initial={reducedMotion ? false : { opacity: 0, transform: "translate3d(0, 3px, 0)" }}
      animate={{ opacity: 1, transform: "translate3d(0, 0, 0)" }}
      transition={{ duration: reducedMotion ? 0 : 0.18, ease: ambientEase }}
    >
      {children}
    </motion.div>
  );
}

export function ScrollReveal({
  children,
  className,
  delay = 0
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}) {
  const reducedMotion = useReducedMotion();

  return (
    <motion.div
      className={className}
      initial={reducedMotion ? false : { opacity: 0, transform: "translate3d(0, 12px, 0)" }}
      whileInView={{ opacity: 1, transform: "translate3d(0, 0, 0)" }}
      viewport={{ once: true, amount: 0.16 }}
      transition={{
        duration: reducedMotion ? 0 : 0.44,
        delay: reducedMotion ? 0 : delay,
        ease: ambientEase
      }}
    >
      {children}
    </motion.div>
  );
}

export function PointerSurface({
  children,
  className
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const reducedMotion = useReducedMotion();
  const x = useMotionValue(-320);
  const y = useMotionValue(-320);
  const springX = useSpring(x, { stiffness: 120, damping: 28, mass: 0.55 });
  const springY = useSpring(y, { stiffness: 120, damping: 28, mass: 0.55 });
  const glowTransform = useMotionTemplate`translate3d(${springX}px, ${springY}px, 0) translate3d(-50%, -50%, 0)`;

  function handlePointerMove(event: React.PointerEvent<HTMLDivElement>) {
    if (reducedMotion || event.pointerType === "touch") return;
    const bounds = event.currentTarget.getBoundingClientRect();
    x.set(event.clientX - bounds.left);
    y.set(event.clientY - bounds.top);
  }

  function handlePointerLeave() {
    x.set(-320);
    y.set(-320);
  }

  return (
    <div
      className={cn("pointer-surface", className)}
      onPointerMove={handlePointerMove}
      onPointerLeave={handlePointerLeave}
    >
      <motion.span
        className="pointer-surface-glow"
        style={reducedMotion ? undefined : { transform: glowTransform }}
      />
      <div className="pointer-surface-content">{children}</div>
    </div>
  );
}

export function SharedPanel({
  open,
  layoutId,
  children
}: {
  open: boolean;
  layoutId: string;
  children: React.ReactNode;
}) {
  const reducedMotion = useReducedMotion();

  if (!open) return null;

  return (
    <motion.div
      className="shared-panel-motion"
      layoutId={reducedMotion ? undefined : layoutId}
      initial={
        reducedMotion
          ? false
          : {
              opacity: 0,
              transform: "translate3d(12px,0,0) scale(.99)"
            }
      }
      animate={{
        opacity: 1,
        transform: "translate3d(0,0,0) scale(1)"
      }}
      exit={{
        opacity: 0,
        transform: reducedMotion
          ? "none"
          : "translate3d(8px,0,0) scale(.995)"
      }}
      transition={{
        duration: reducedMotion ? 0 : 0.22,
        ease: [0.23, 1, 0.32, 1]
      }}
    >
      {children}
    </motion.div>
  );
}
