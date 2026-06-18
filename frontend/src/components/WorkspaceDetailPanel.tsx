"use client";

import {
  cloneElement,
  useEffect,
  useId,
  useRef,
  useState,
  type MouseEvent,
  type ReactElement,
  type ReactNode
} from "react";
import { AnimatePresence } from "motion/react";
import { X } from "lucide-react";
import { SharedPanel } from "@/components/MotionPrimitives";

type TriggerProps = {
  onClick?: (event: MouseEvent<HTMLElement>) => void;
  "aria-expanded"?: boolean;
  "aria-controls"?: string;
};

export function WorkspaceDetailPanel({
  title,
  closeLabel,
  trigger,
  children
}: {
  title: string;
  closeLabel: string;
  trigger: ReactElement<TriggerProps>;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const panelId = useId();
  const triggerRef = useRef<HTMLElement | null>(null);
  const panelRef = useRef<HTMLElement | null>(null);
  const closeRef = useRef<HTMLButtonElement | null>(null);

  function closePanel() {
    setOpen(false);
    window.requestAnimationFrame(() => triggerRef.current?.focus());
  }

  useEffect(() => {
    if (!open) return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.requestAnimationFrame(() => closeRef.current?.focus());

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        event.preventDefault();
        closePanel();
        return;
      }

      if (event.key === "Tab" && panelRef.current) {
        const focusable = Array.from(
          panelRef.current.querySelectorAll<HTMLElement>(
            'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
          )
        ).filter((element) => !element.hasAttribute("hidden"));
        const first = focusable[0];
        const last = focusable[focusable.length - 1];

        if (!first || !last) {
          event.preventDefault();
          closeRef.current?.focus();
        } else if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = previousOverflow;
    };
  }, [open]);

  return (
    <>
      {cloneElement(trigger, {
        "aria-expanded": open,
        "aria-controls": panelId,
        onClick: (event) => {
          trigger.props.onClick?.(event);
          triggerRef.current = event.currentTarget;
          setOpen(true);
        }
      })}
      <AnimatePresence>
        {open ? (
          <div className="workspace-detail-layer">
            <button
              type="button"
              className="workspace-detail-backdrop"
              aria-label={`${closeLabel}（背景）`}
              tabIndex={-1}
              onClick={closePanel}
            />
            <SharedPanel open layoutId={`detail-${panelId}`}>
              <section
                ref={panelRef}
                id={panelId}
                className="workspace-detail-panel"
                role="dialog"
                aria-modal="true"
                aria-label={title}
              >
                <header>
                  <strong>{title}</strong>
                  <button
                    ref={closeRef}
                    type="button"
                    onClick={closePanel}
                    aria-label={closeLabel}
                  >
                    <X aria-hidden="true" />
                  </button>
                </header>
                <div className="workspace-detail-content">{children}</div>
              </section>
            </SharedPanel>
          </div>
        ) : null}
      </AnimatePresence>
    </>
  );
}
