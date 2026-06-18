"use client";

import {
  BookOpenText,
  BrainCircuit,
  ChartNoAxesCombined,
  FileText
} from "lucide-react";
import { AgentReportPanel } from "@/components/AgentReportPanel";
import { FinancialAnalysisPanel } from "@/components/FinancialAnalysisPanel";
import { useLocale } from "@/components/LocaleProvider";
import { ModelAnalysisPanel } from "@/components/ModelAnalysisPanel";
import { PageHeader, WorkspaceEmptyState } from "@/components/PagePrimitives";
import {
  useWorkspace,
  workspaceSourceKey
} from "@/components/WorkspaceProvider";
import { WorkspaceSourceSelect, useWorkspaceSources } from "@/components/WorkspaceSource";
import { Badge } from "@/components/ui/badge";
import type {
  FinancialAnalysis,
  ModelAnalysis,
  TermDefinition
} from "@/lib/api";

export function ModelWorkspace() {
  const { text } = useLocale();
  const { activeSource } = useWorkspaceSources();
  return (
    <>
      <PageHeader
        eyebrow={text("模型實驗室", "Model lab")}
        title={text("選擇分析方式", "Choose an analysis approach")}
        description={text(
          "先確認目標與方法，系統再依真實資料選出候選模型。",
          "Confirm the target and approach before the system selects candidates from the real dataset."
        )}
        actions={<WorkspaceSourceSelect />}
      />
      {activeSource ? (
        <ToolContext source={activeSource} icon={<BrainCircuit aria-hidden="true" />}>
          <ModelAnalysisPanel
            dataset={activeSource.dataset}
            file={activeSource.file}
            files={activeSource.files}
            isMerged={activeSource.isMerged}
            title={text(
              activeSource.isMerged ? "選擇合併資料分析方式" : "選擇分析方式",
              activeSource.isMerged
                ? "Choose a merged-data analysis approach"
                : "Choose an analysis approach"
            )}
            description={text(
              "先確認目標與方法，系統再依真實資料選出候選模型。",
              "Confirm the target and approach before the system selects candidates from the real dataset."
            )}
          />
        </ToolContext>
      ) : (
        <WorkspaceEmptyState />
      )}
    </>
  );
}

export function FinanceWorkspace() {
  const { text } = useLocale();
  const { activeSource } = useWorkspaceSources();
  return (
    <>
      <PageHeader
        eyebrow={text("金融分析", "Financial analysis")}
        title={text("把時間序列轉成可讀訊號", "Turn time series into readable signals")}
        description={text(
          "系統先判斷日期與價格/指數/數值欄位，再計算趨勢、風險、技術指標與基準情境估計。",
          "The workspace identifies date and price / index / value columns before calculating trends, risk, technical indicators, and baseline scenarios."
        )}
        actions={<WorkspaceSourceSelect />}
      />
      {activeSource ? (
        <ToolContext source={activeSource} icon={<ChartNoAxesCombined aria-hidden="true" />}>
          <FinancialAnalysisPanel
            dataset={activeSource.dataset}
            file={activeSource.file}
            files={activeSource.files}
            isMerged={activeSource.isMerged}
            title={text(
              activeSource.isMerged ? "合併資料金融分析" : "金融分析",
              activeSource.isMerged ? "Merged financial analysis" : "Financial analysis"
            )}
          />
        </ToolContext>
      ) : (
        <WorkspaceEmptyState />
      )}
    </>
  );
}

export function ReportWorkspace() {
  const { text } = useLocale();
  const { activeSource } = useWorkspaceSources();
  return (
    <>
      <PageHeader
        eyebrow={text("報告中心", "Report center")}
        title={text("把分析整理成可以交付的結論", "Package the analysis into a deliverable conclusion")}
        description={text(
          "分析代理會依目前資料完成理解、模型、金融與摘要流程，並輸出 Word 報告。",
          "Analysis agents run data, model, financial, and summary stages against the current dataset and can produce a Word report."
        )}
        actions={<WorkspaceSourceSelect />}
      />
      {activeSource ? (
        <ToolContext source={activeSource} icon={<FileText aria-hidden="true" />}>
          <AgentReportPanel
            dataset={activeSource.dataset}
            file={activeSource.file}
            files={activeSource.files}
            isMerged={activeSource.isMerged}
            title={text(
              activeSource.isMerged ? "合併資料分析與報告" : "分析與報告",
              activeSource.isMerged ? "Merged analysis and report" : "Analysis and report"
            )}
          />
        </ToolContext>
      ) : (
        <WorkspaceEmptyState />
      )}
    </>
  );
}

export function ChartWorkspace() {
  const { text } = useLocale();
  const { activeSource } = useWorkspaceSources();
  const { panelStates } = useWorkspace();
  const terms = activeSource
    ? collectWorkspaceTerms(activeSource, panelStates, {
        dataset: text("資料摘要", "Dataset profile"),
        common: text("常用名詞", "Common terms"),
        model: text("模型分析", "Model analysis"),
        mergedModel: text("合併模型分析", "Merged model analysis"),
        finance: text("金融分析", "Financial analysis"),
        mergedFinance: text("合併金融分析", "Merged financial analysis")
      })
    : [];

  return (
    <>
      <PageHeader
        eyebrow={text("分析字典", "Analysis dictionary")}
        title={text("專有名詞解釋", "Terminology guide")}
        description={text(
          "集中解釋目前資料、模型與金融分析中出現的指標和專有名詞，先看白話再看公式。",
          "Explain the metrics and terminology used by the current data, model, and financial analysis in plain language first."
        )}
        actions={<WorkspaceSourceSelect />}
      />
      {activeSource ? (
        <ToolContext
          source={activeSource}
          icon={<BookOpenText aria-hidden="true" />}
        >
          {terms.length > 0 ? (
            <section className="term-glossary-workspace" aria-labelledby="term-glossary-title">
              <div className="section-title-row">
                <div>
                  <span>{text("白話解釋", "Plain-language guide")}</span>
                  <h2 id="term-glossary-title">
                    {text("目前分析會用到的名詞", "Terms used by this analysis")}
                  </h2>
                </div>
                <Badge variant="outline">
                  {text(`${terms.length} 個`, `${terms.length} terms`)}
                </Badge>
              </div>
              <div className="term-glossary-grid">
                {terms.map((term) => (
                  <article
                    key={term.term}
                    className="term-glossary-card"
                  >
                    <div className="term-glossary-card-header">
                      <strong>{term.term}</strong>
                      <div>
                        {term.sourceLabels.map((label) => (
                          <Badge key={label} variant="secondary">
                            {label}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    {term.plain_explanation ? (
                      <p className="term-glossary-plain">{term.plain_explanation}</p>
                    ) : null}
                    {term.this_result_means ? (
                      <div className="term-glossary-note">
                        <span>{text("這次代表", "This result means")}</span>
                        <p>{term.this_result_means}</p>
                      </div>
                    ) : null}
                    <dl className="term-glossary-read">
                      {term.how_to_read ? (
                        <div>
                          <dt>{text("怎麼看", "How to read")}</dt>
                          <dd>{term.how_to_read}</dd>
                        </div>
                      ) : null}
                      {term.caveat ? (
                        <div>
                          <dt>{text("不要誤解成", "Do not overread")}</dt>
                          <dd>{term.caveat}</dd>
                        </div>
                      ) : null}
                    </dl>
                    {(term.technical_definition || term.formula) ? (
                      <details className="term-glossary-detail">
                        <summary>{text("看技術定義", "Show technical definition")}</summary>
                        <div>
                          {term.technical_definition ? <p>{term.technical_definition}</p> : null}
                          {term.formula ? <code>{term.formula}</code> : null}
                        </div>
                      </details>
                    ) : null}
                  </article>
                ))}
              </div>
            </section>
          ) : (
            <WorkspaceEmptyState
              title={text(
                "目前沒有可解釋的名詞",
                "No terms to explain yet"
              )}
              description={text(
                "重新讀取資料或完成模型、金融分析後，這裡會集中整理指標與專有名詞。",
                "Reload data or run model / financial analysis to collect metrics and terminology here."
              )}
              showAction={false}
            />
          )}
        </ToolContext>
      ) : (
        <WorkspaceEmptyState />
      )}
    </>
  );
}

type GlossaryTerm = TermDefinition & {
  term: string;
  sourceLabels: string[];
};

function collectWorkspaceTerms(
  source: NonNullable<ReturnType<typeof useWorkspaceSources>["activeSource"]>,
  panelStates: Record<string, unknown>,
  labels: {
    dataset: string;
    common: string;
    model: string;
    mergedModel: string;
    finance: string;
    mergedFinance: string;
  }
): GlossaryTerm[] {
  const sourceKey = workspaceSourceKey(source.file, source.files, source.isMerged);
  const modelResult = panelStates[`${sourceKey}:model:result`] as
    | ModelAnalysis
    | null
    | undefined;
  const financeResult = panelStates[`${sourceKey}:finance:result`] as
    | FinancialAnalysis
    | null
    | undefined;

  const terms = new Map<string, GlossaryTerm>();
  addTerms(terms, source.dataset.terms, labels.dataset);
  addTerms(
    terms,
    modelResult?.terms,
    source.isMerged ? labels.mergedModel : labels.model
  );
  addTerms(
    terms,
    financeResult?.terms,
    source.isMerged ? labels.mergedFinance : labels.finance
  );

  if (terms.size === 0) {
    addTerms(terms, defaultGlossaryTerms, labels.common);
  }

  return Array.from(terms.values());
}

function addTerms(
  target: Map<string, GlossaryTerm>,
  terms: TermDefinition[] | undefined,
  sourceLabel: string
) {
  for (const term of terms ?? []) {
    if (!term.term) continue;
    const key = term.term.trim().toLowerCase();
    const existing = target.get(key);
    if (existing) {
      if (!existing.sourceLabels.includes(sourceLabel)) {
        existing.sourceLabels.push(sourceLabel);
      }
      continue;
    }
    target.set(key, {
      ...term,
      term: term.term,
      sourceLabels: [sourceLabel]
    });
  }
}

const defaultGlossaryTerms: TermDefinition[] = [
  {
    term: "RMSE",
    plain_explanation: "模型預測通常會錯多少，而且會更重視大錯誤。",
    technical_definition: "Root Mean Squared Error。",
    formula: "sqrt(mean((y_true - y_pred)^2))",
    how_to_read: "越低越好；要搭配目標欄位單位一起看。",
    caveat: "RMSE 低不代表模型理解原因，也不代表未來資料一定準。"
  },
  {
    term: "MAE",
    plain_explanation: "模型平均大約差多少，通常比 RMSE 更容易用原單位理解。",
    technical_definition: "Mean Absolute Error。",
    formula: "mean(abs(y_true - y_pred))",
    how_to_read: "越低越好；適合拿來向非技術使用者說明平均誤差。",
    caveat: "MAE 不會特別放大大錯誤，因此仍要搭配 RMSE 或殘差圖。"
  },
  {
    term: "R²",
    plain_explanation: "模型大概能解釋目標變化的比例。",
    technical_definition: "Coefficient of determination。",
    formula: "1 - SS_res / SS_tot",
    how_to_read: "越接近 1 通常越好，但仍需看測試集與資料品質。",
    caveat: "R² 高不代表因果關係。"
  },
  {
    term: "Baseline",
    plain_explanation: "一個最低標準模型，用來確認新模型是不是真的有改善。",
    technical_definition: "Dummy baseline model。",
    how_to_read: "正式模型至少應該明顯優於 baseline，否則代表資料訊號可能不足。",
    caveat: "優於 baseline 只是基本門檻，不代表可以直接決策。"
  },
  {
    term: "特徵重要性",
    plain_explanation: "模型認為哪些欄位最影響結果。",
    technical_definition: "Feature importance。",
    how_to_read: "排名越前的欄位越值得優先檢查是否有業務意義。",
    caveat: "重要性不是因果關係；ID 或洩漏欄位排名很高時要小心。"
  },
  {
    term: "殘差",
    plain_explanation: "模型預測錯了多少。",
    technical_definition: "Residual。",
    formula: "實際值 - 預測值",
    how_to_read: "如果殘差呈現規律，表示模型可能漏掉重要因素。",
    caveat: "殘差只能提示問題位置，不能直接說明原因。"
  }
];

function ToolContext({
  source,
  icon,
  children
}: {
  source: NonNullable<ReturnType<typeof useWorkspaceSources>["activeSource"]>;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  const { text } = useLocale();
  return (
    <div className="tool-workspace">
      <div className="tool-context-bar">
        <span className="tool-context-icon">{icon}</span>
        <div>
          <strong>{source.label}</strong>
          <small>{source.detail}</small>
        </div>
        <Badge variant={source.isMerged ? "default" : "outline"}>
          {source.isMerged
            ? text("合併資料", "Merged data")
            : text("單一檔案", "Single file")}
        </Badge>
      </div>
      {children}
    </div>
  );
}
