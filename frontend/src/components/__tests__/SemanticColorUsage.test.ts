import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const productPanels = [
  "../ModelAnalysisPanel.tsx",
  "../FinancialAnalysisPanel.tsx",
  "../AgentReportPanel.tsx"
];

const semanticTextRules = [
  { selector: ".ui-copy-primary", token: "--product-text-primary" },
  { selector: ".ui-copy-secondary", token: "--product-text-secondary" },
  { selector: ".ui-copy-tertiary", token: "--product-text-secondary" },
  { selector: ".ui-metric-label", token: "--product-text-secondary" },
  { selector: ".ui-option-description", token: "--product-text-secondary" }
];

function readPanel(relativePath: string) {
  return readFileSync(new URL(relativePath, import.meta.url), "utf8");
}

function escapeRegExp(value: string) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

describe("semantic text color usage", () => {
  it.each(productPanels)(
    "does not use the muted background token as a text color in %s",
    (relativePath) => {
      const source = readPanel(relativePath);

      expect(source).not.toMatch(/\btext-muted\b(?!-foreground)/);
    }
  );

  it.each(productPanels)(
    "does not rely on unsupported transparent white utilities in %s",
    (relativePath) => {
      expect(readPanel(relativePath)).not.toContain("bg-white/78");
    }
  );

  it("uses semantic copy, metric, option, and output classes in the analysis panels", () => {
    const modelSource = readPanel("../ModelAnalysisPanel.tsx");
    const financialSource = readPanel("../FinancialAnalysisPanel.tsx");
    const agentSource = readPanel("../AgentReportPanel.tsx");

    for (const source of [modelSource, financialSource, agentSource]) {
      expect(source).toContain("ui-copy-secondary");
      expect(source).toContain("analysis-mini-metric");
      expect(source).toContain("ui-metric-label");
      expect(source).toContain("ui-metric-value");
    }

    expect(modelSource).toContain("ui-option-description");
    expect(modelSource).toContain("analysis-surface-card");
    expect(modelSource).toContain("ui-output-label");
    expect(modelSource).toContain("ui-output-value");
    expect(agentSource).toContain("ui-copy-tertiary");
  });

  it("defines semantic text classes as opaque solid theme colors", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/app/product-interface.css"),
      "utf8"
    );

    for (const { selector, token } of semanticTextRules) {
      expect(source).toMatch(
        new RegExp(
          `${escapeRegExp(selector)}\\s*\\{[\\s\\S]*color:\\s*var\\(${escapeRegExp(
            token
          )}\\)[\\s\\S]*opacity:\\s*1\\s*!important`
        )
      );
    }
  });

  it("keeps explicit analysis surfaces aligned with the active product theme", () => {
    const source = readFileSync(
      resolve(process.cwd(), "src/app/product-interface.css"),
      "utf8"
    );

    expect(source).toMatch(
      /\.analysis-mini-metric\s*\{[\s\S]*background:\s*var\(--product-surface\)/
    );
    expect(source).toMatch(
      /\.analysis-surface-card\s*\{[\s\S]*background:\s*var\(--product-surface-elevated\)/
    );

    expect(source).toMatch(
      /\.product-shell \.bg-white[\s\S]*background:\s*var\(--product-surface\)/
    );
    expect(source).toMatch(
      /\.product-shell \.bg-slate-50[\s\S]*background:\s*var\(--product-surface-elevated\)/
    );
    expect(source).toMatch(
      /\.product-shell \.text-muted-foreground[\s\S]*color:\s*var\(--product-text-secondary\)/
    );
  });
});
