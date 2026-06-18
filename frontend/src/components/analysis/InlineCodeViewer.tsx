"use client";

import { useId, useState } from "react";
import { Check, Copy } from "lucide-react";
import { useLocale } from "@/components/LocaleProvider";

type CodeMode = "python" | "notebook";

export function InlineCodeViewer({
  pythonContent,
  notebookContent,
  pythonPath,
  notebookPath
}: {
  pythonContent: string;
  notebookContent: string;
  pythonPath: string;
  notebookPath: string;
}) {
  const { text } = useLocale();
  const [mode, setMode] = useState<CodeMode>("python");
  const [copied, setCopied] = useState(false);
  const tabId = useId();
  const content = mode === "python" ? pythonContent : notebookContent;
  const path = mode === "python" ? pythonPath : notebookPath;

  async function copyCode() {
    await window.navigator.clipboard.writeText(content);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <section className="inline-code-viewer">
      <div className="inline-code-toolbar">
        <div role="tablist" aria-label={text("程式碼格式", "Code format")}>
          {(["python", "notebook"] as const).map((value) => (
            <button
              key={value}
              id={`${tabId}-${value}-tab`}
              type="button"
              role="tab"
              aria-selected={mode === value}
              aria-controls={`${tabId}-${value}-panel`}
              onClick={() => {
                setMode(value);
                setCopied(false);
              }}
            >
              {value === "python" ? "Python" : "Notebook"}
            </button>
          ))}
        </div>
        <button type="button" onClick={copyCode}>
          {copied ? <Check aria-hidden="true" /> : <Copy aria-hidden="true" />}
          {copied ? text("已複製", "Copied") : text("複製程式碼", "Copy code")}
        </button>
      </div>
      <div className="inline-code-path">{path}</div>
      <pre
        id={`${tabId}-${mode}-panel`}
        role="tabpanel"
        aria-labelledby={`${tabId}-${mode}-tab`}
      >
        <code>
          {content.split("\n").map((line, index) => (
            <span className="inline-code-line" key={`${index}-${line}`}>
              <span aria-hidden="true">{index + 1}</span>
              <span>{line || " "}</span>
            </span>
          ))}
        </code>
      </pre>
    </section>
  );
}
