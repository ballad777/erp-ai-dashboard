"use client";

import Link from "next/link";
import { useState } from "react";
import {
  ArrowRight,
  BrainCircuit,
  Check,
  ChevronRight,
  Database,
  FileCode2,
  FileText,
  Gauge,
  Layers3,
  LineChart,
  ShieldCheck,
  Sparkles,
  TableProperties
} from "lucide-react";
import { DataLensHero } from "@/components/DataLensHero";
import { MarketingShell } from "@/components/MarketingShell";
import { ScrollReveal } from "@/components/MotionPrimitives";
import { useLocale } from "@/components/LocaleProvider";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const journeyIcons = [Database, TableProperties, BrainCircuit, Sparkles];

export function MarketingHome() {
  const { text, path } = useLocale();
  const [activeJourney, setActiveJourney] = useState(0);
  const journey = [
    {
      title: text("上傳資料", "Upload data"),
      detail: text("CSV、Excel、JSON 與多檔批次都會先分表理解", "CSV, Excel, JSON, and multi-file batches are understood table by table")
    },
    {
      title: text("理解資料", "Understand data"),
      detail: text("辨識資料主題、目標欄位、品質與限制", "Detect dataset topic, targets, quality, and limits")
    },
    {
      title: text("產生洞察", "Generate insight"),
      detail: text("把圖表與模型結果翻譯成一般人看得懂的結論", "Translate charts and model results into readable conclusions")
    },
    {
      title: text("做出決策", "Make a decision"),
      detail: text("整理風險、機會與下一步行動", "Organize risks, opportunities, and next actions")
    }
  ];

  return (
    <MarketingShell>
      <DataLensHero />

      <section id="journey" className="journey-section marketing-section">
        <ScrollReveal>
          <div className="marketing-section-heading">
            <span>{text("分析旅程", "Analysis journey")}</span>
            <h2>{text("從資料到決策，一個工作區完成。", "From data to decisions, in one workspace.")}</h2>
            <p>
              {text(
                "產品會先用人話解釋資料，再讓你進入圖表、模型與報告細節；不用先懂資料科學也能開始。",
                "The product explains data in plain language before charts, models, and reports, so you can start without being a data scientist."
              )}
            </p>
          </div>
        </ScrollReveal>

        <ScrollReveal delay={0.06}>
          <div className="journey-workbench">
            <div className="journey-track" role="tablist" aria-label={text("分析流程", "Analysis process")}>
              {journey.map((step, index) => {
                const Icon = journeyIcons[index];
                return (
                  <button
                    key={step.title}
                    type="button"
                    role="tab"
                    aria-selected={activeJourney === index}
                    className={activeJourney === index ? "is-active" : ""}
                    onClick={() => setActiveJourney(index)}
                  >
                    <span className="journey-index">{String(index + 1).padStart(2, "0")}</span>
                    <span className="journey-icon"><Icon aria-hidden="true" /></span>
                    <strong>{step.title}</strong>
                  </button>
                );
              })}
            </div>
            <div className="journey-detail" role="tabpanel">
              <span>{text("目前階段", "Current stage")}</span>
              <h3>{journey[activeJourney].title}</h3>
              <p>{journey[activeJourney].detail}</p>
              <div className="journey-progress" aria-hidden="true">
                <span style={{ width: `${((activeJourney + 1) / journey.length) * 100}%` }} />
              </div>
              <Link href={path("/app/data")}>
                {text("在工作區開始", "Start in the workspace")}
                <ArrowRight aria-hidden="true" />
              </Link>
            </div>
          </div>
        </ScrollReveal>
      </section>

      <div id="capabilities" className="capability-story">
        <ProductStory
          eyebrow={text("資料理解", "Data understanding")}
          title={text("先理解資料，再選擇方法。", "Understand the data before choosing a method.")}
          body={text(
            "系統會整理欄位型別、缺失值、數值摘要與可能的分析目標，讓你在執行模型前先看見目前資料輪廓。",
            "The workspace summarizes column types, missing values, numeric statistics, and likely targets before you train a model."
          )}
          href={path("/app/data")}
          cta={text("查看資料理解流程", "Explore data understanding")}
          visual={<DataEvidence />}
        />
        <ProductStory
          reverse
          eyebrow={text("模型選擇", "Model selection")}
          title={text("選擇合適模型，而不是執行更多模型。", "Choose suitable models instead of running more models.")}
          body={text(
            "系統依問題類型、資料規模、特徵與缺失情況推薦候選模型；你仍可以手動調整分析模式、模型與圖表。",
            "Recommendations use the problem type, dataset size, feature mix, and missingness. You can still take full manual control."
          )}
          href={path("/app/models")}
          cta={text("查看模型工作區", "Open the model workspace")}
          visual={<ModelEvidence />}
        />
        <ProductStory
          eyebrow={text("金融洞察", "Financial insight")}
          title={text("看見結果背後的依據。", "See the evidence behind the result.")}
          body={text(
            "當資料包含日期與價格/指數/數值欄位，系統會整理趨勢、報酬、波動與技術指標，並清楚標示限制與風險。",
            "When date and price / index / value columns are available, the workspace organizes trend, return, volatility, and technical indicators with explicit limitations."
          )}
          href={path("/app/finance")}
          cta={text("查看金融分析", "Explore financial analysis")}
          visual={<FinanceEvidence />}
        />
        <ProductStory
          reverse
          eyebrow={text("交付成果", "Deliverables")}
          title={text("讓洞察成為下一個動作。", "Turn insight into the next action.")}
          body={text(
            "不只看見結果，也能在頁內檢視 Python 程式碼與 Notebook，並下載報告、模型結果與圖表。",
            "Inspect generated Python and notebook content in the product, then download reports, model results, and charts when needed."
          )}
          href={path("/app/reports")}
          cta={text("查看可交付成果", "View deliverables")}
          visual={<DeliveryEvidence />}
        />
      </div>

      <section id="trust" className="truth-section marketing-section">
        <ScrollReveal>
          <div className="truth-layout">
            <div className="truth-copy">
              <span>{text("真實分析", "Real analysis")}</span>
              <h2>{text("真實分析，清楚交代。", "Real analysis, clearly explained.")}</h2>
              <p>
                {text(
                  "所有結果都由後端針對目前資料重新計算。沒有資料時不顯示模擬數字；未設定外部 LLM 時，也會明確標示本機規則摘要。",
                  "Every result is recalculated by the backend for the current dataset. No connected data means no simulated numbers, and local rule-based summaries are labeled clearly when no external LLM is configured."
                )}
              </p>
            </div>
            <div className="truth-list">
              <TruthItem icon={ShieldCheck} title={text("API 真實執行", "Real API execution")} body={text("資料、模型、圖表與輸出都來自 FastAPI 分析服務。", "Data profiles, models, charts, and exports come from the FastAPI service.")} />
              <TruthItem icon={Layers3} title={text("保留分析控制", "Analysis stays controllable")} body={text("自動推薦之外，仍可指定模式、模型、圖表與 AutoML。", "Automatic recommendations coexist with manual mode, model, chart, and AutoML controls.")} />
              <TruthItem icon={Gauge} title={text("限制寫清楚", "Limits stay visible")} body={text("錯誤、資料限制與金融風險不會藏在下載檔案裡。", "Errors, data limitations, and financial risk notes remain visible in the product.")} />
            </div>
          </div>
        </ScrollReveal>
      </section>

      <section className="marketing-final-cta">
        <ScrollReveal>
          <div>
            <span>{text("下一步", "Next step")}</span>
            <h2>{text("從你的資料開始，找到下一步。", "Start with your data. Find your next step.")}</h2>
            <p>
              {text(
                "上傳第一份資料，先理解結構，再決定最適合的分析方式。",
                "Upload the first dataset, understand its structure, then choose the right analysis."
              )}
            </p>
            <Button asChild variant="premium" size="lg">
              <Link href={path("/app/data")}>
                {text("開始分析資料", "Start analyzing")}
                <ArrowRight aria-hidden="true" />
              </Link>
            </Button>
          </div>
        </ScrollReveal>
      </section>
    </MarketingShell>
  );
}

function ProductStory({
  eyebrow,
  title,
  body,
  href,
  cta,
  visual,
  reverse = false
}: {
  eyebrow: string;
  title: string;
  body: string;
  href: string;
  cta: string;
  visual: React.ReactNode;
  reverse?: boolean;
}) {
  return (
    <section className={`product-story marketing-section ${reverse ? "is-reverse" : ""}`}>
      <ScrollReveal className="product-story-copy">
        <span>{eyebrow}</span>
        <h2>{title}</h2>
        <p>{body}</p>
        <Link href={href}>
          {cta}
          <ArrowRight aria-hidden="true" />
        </Link>
      </ScrollReveal>
      <ScrollReveal className="product-story-visual" delay={0.08}>
        {visual}
      </ScrollReveal>
    </section>
  );
}

function DataEvidence() {
  const { text } = useLocale();
  const rows = [
    [text("欄位型別", "Column types"), text("自動辨識", "Detected")],
    [text("缺失值", "Missing values"), text("逐欄統計", "Per-column")],
    [text("建議目標", "Suggested target"), text("依資料推薦", "Data-driven")]
  ];
  return (
    <div className="evidence-window">
      <div className="evidence-window-top"><span /><span /><span /></div>
      <div className="evidence-summary-line">
        <Database aria-hidden="true" />
        <div>
          <strong>{text("資料輪廓", "Dataset profile")}</strong>
          <small>{text("讀取完成後顯示真實結果", "Real results appear after ingestion")}</small>
        </div>
      </div>
      <div className="evidence-table">
        {rows.map(([label, value]) => (
          <div key={label}><span>{label}</span><strong>{value}</strong></div>
        ))}
      </div>
    </div>
  );
}

function ModelEvidence() {
  const { text } = useLocale();
  return (
    <div className="evidence-window model-evidence">
      <div className="evidence-window-top"><span /><span /><span /></div>
      <div className="model-recommendation">
        <BrainCircuit aria-hidden="true" />
        <div>
          <span>{text("推薦邏輯", "Recommendation logic")}</span>
          <strong>{text("先判斷問題，再選候選模型", "Detect the problem before selecting candidates")}</strong>
        </div>
      </div>
      <div className="model-evidence-steps">
        {[text("問題類型", "Problem type"), text("資料規模", "Dataset size"), text("特徵組成", "Feature mix")].map((item, index) => (
          <div key={item}><span>{index + 1}</span><strong>{item}</strong><ChevronRight /></div>
        ))}
      </div>
    </div>
  );
}

function FinanceEvidence() {
  const { text } = useLocale();
  return (
    <div className="evidence-window finance-evidence">
      <div className="evidence-window-top"><span /><span /><span /></div>
      <div className="finance-evidence-header">
        <div><LineChart /><strong>{text("金融訊號", "Financial signals")}</strong></div>
        <Badge variant="outline">{text("條件式啟用", "Conditional")}</Badge>
      </div>
      <div className="finance-line-visual" aria-hidden="true">
        <span /><span /><span /><span /><span /><span /><span />
      </div>
      <div className="finance-evidence-labels">
        <span>MA</span><span>RSI</span><span>MACD</span><span>VaR</span>
      </div>
    </div>
  );
}

function DeliveryEvidence() {
  const { text } = useLocale();
  return (
    <div className="evidence-window delivery-evidence">
      <div className="evidence-window-top"><span /><span /><span /></div>
      <div className="delivery-tabs">
        <span className="is-active">Python</span><span>Notebook</span><span>Word</span>
      </div>
      <pre aria-label={text("程式碼預覽示意", "Code preview illustration")}>
        <code>{`model.fit(X_train, y_train)\nmetrics = evaluate(model, X_test)\nreport.add_chart(results)`}</code>
      </pre>
      <div className="delivery-file-row">
        <FileCode2 /><span>generated_code.py</span><Check />
      </div>
    </div>
  );
}

function TruthItem({
  icon: Icon,
  title,
  body
}: {
  icon: typeof ShieldCheck;
  title: string;
  body: string;
}) {
  return (
    <div className="truth-item">
      <span><Icon aria-hidden="true" /></span>
      <div><strong>{title}</strong><p>{body}</p></div>
    </div>
  );
}
