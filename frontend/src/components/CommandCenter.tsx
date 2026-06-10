"use client";

import { useEffect, useMemo, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { SystemStatus } from "@/components/SystemStatus";

type Command = {
  id: string;
  title: string;
  detail: string;
  keys?: string;
  scope: "全站" | "工作台";
  disabled?: boolean;
  run: () => void;
};

const eventNames = {
  openCommand: "smartfinance:open-command-center",
  openFiles: "smartfinance:open-files",
  analyzeFiles: "smartfinance:analyze-files",
  clearFiles: "smartfinance:clear-files"
};

export function CommandTriggerButton() {
  return (
    <button
      type="button"
      className="hidden h-11 items-center gap-2 rounded-xl border border-sky-200 bg-white/78 px-4 text-sm font-semibold text-ink shadow-[0_12px_28px_rgba(15,23,42,0.05)] transition hover:border-brand hover:text-brand md:inline-flex"
      onClick={() => window.dispatchEvent(new CustomEvent(eventNames.openCommand))}
    >
      快捷
      <span className="keycap">⌘K</span>
    </button>
  );
}

export function CommandCenter() {
  const router = useRouter();
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const isUploadPage = pathname === "/upload";

  const commands = useMemo<Command[]>(
    () => [
      {
        id: "upload",
        title: isUploadPage ? "加入資料檔案" : "前往上傳工作台",
        detail: isUploadPage ? "開啟檔案選擇器" : "進入多檔資料分析流程",
        keys: "⌘ U",
        scope: "全站",
        run: () => {
          if (isUploadPage) {
            window.dispatchEvent(new CustomEvent(eventNames.openFiles));
          } else {
            router.push("/upload");
          }
        }
      },
      {
        id: "analyze",
        title: "讀取全部檔案",
        detail: "執行資料摘要與合併判斷",
        keys: "⌘ ↵",
        scope: "工作台",
        disabled: !isUploadPage,
        run: () => window.dispatchEvent(new CustomEvent(eventNames.analyzeFiles))
      },
      {
        id: "clear",
        title: "清空已加入檔案",
        detail: "重置目前工作台佇列",
        scope: "工作台",
        disabled: !isUploadPage,
        run: () => window.dispatchEvent(new CustomEvent(eventNames.clearFiles))
      },
      {
        id: "home",
        title: "返回首頁",
        detail: "回到產品總覽",
        scope: "全站",
        run: () => router.push("/")
      }
    ],
    [isUploadPage, router]
  );

  const filteredCommands = commands.filter((command) => {
    const target = `${command.title} ${command.detail} ${command.scope}`.toLowerCase();
    return target.includes(query.trim().toLowerCase());
  });

  useEffect(() => {
    function openCommandCenter() {
      setIsOpen(true);
    }

    function isTypingTarget(target: EventTarget | null) {
      if (!(target instanceof HTMLElement)) return false;
      return (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.isContentEditable
      );
    }

    function onKeyDown(event: KeyboardEvent) {
      const commandKey = event.metaKey || event.ctrlKey;

      if (commandKey && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setIsOpen((current) => !current);
        return;
      }

      if (commandKey && event.key.toLowerCase() === "u") {
        event.preventDefault();
        if (isUploadPage) {
          window.dispatchEvent(new CustomEvent(eventNames.openFiles));
        } else {
          router.push("/upload");
        }
        return;
      }

      if (commandKey && event.key === "Enter" && isUploadPage) {
        event.preventDefault();
        window.dispatchEvent(new CustomEvent(eventNames.analyzeFiles));
        return;
      }

      if (event.key === "Escape") {
        setIsOpen(false);
        return;
      }

      if (event.key === "?" && !isTypingTarget(event.target)) {
        event.preventDefault();
        setIsOpen(true);
      }
    }

    window.addEventListener("keydown", onKeyDown);
    window.addEventListener(eventNames.openCommand, openCommandCenter);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener(eventNames.openCommand, openCommandCenter);
    };
  }, [isUploadPage, router]);

  function runCommand(command: Command) {
    if (command.disabled) return;
    command.run();
    setIsOpen(false);
    setQuery("");
  }

  return (
    <>
      <button
        type="button"
        className="command-dock"
        onClick={() => setIsOpen(true)}
        aria-label="開啟快捷指令"
      >
        <span className="command-dock-icon">⌘</span>
        <span className="command-dock-text">快捷指令</span>
        <span className="keycap">K</span>
      </button>

      {isOpen ? (
        <div className="command-overlay" role="dialog" aria-modal="true">
          <button
            type="button"
            className="command-backdrop"
            aria-label="關閉快捷指令"
            onClick={() => setIsOpen(false)}
          />
          <div className="command-panel">
            <div className="command-panel-top">
              <div>
                <div className="command-title">快捷指令</div>
                <div className="command-subtitle">把常用分析動作收在同一個入口</div>
              </div>
              <SystemStatus compact />
            </div>

            <div className="command-search">
              <span>⌕</span>
              <input
                autoFocus
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="搜尋指令"
              />
              <span className="keycap">esc</span>
            </div>

            <div className="command-list">
              {filteredCommands.map((command) => (
                <button
                  key={command.id}
                  type="button"
                  disabled={command.disabled}
                  onClick={() => runCommand(command)}
                  className="command-row"
                >
                  <span>
                    <strong>{command.title}</strong>
                    <small>{command.detail}</small>
                  </span>
                  <span className="command-row-meta">
                    <small>{command.scope}</small>
                    {command.keys ? <span className="keycap">{command.keys}</span> : null}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
