import Link from "next/link";
import {
  ArrowRight,
  BrainCircuit,
  ChevronDown,
  CloudUpload,
  Database,
  FileChartColumn,
  Home,
  LineChart,
  ScanSearch,
  ShieldCheck,
  type LucideIcon
} from "lucide-react";
import { AppShell } from "@/components/AppShell";
import {
  PointerSurface,
  ScrollReveal
} from "@/components/MotionPrimitives";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const workflow: Array<{
  title: string;
  body: string;
  icon: LucideIcon;
}> = [
  {
    title: "資料匯入",
    body: "支援 CSV / Excel 多檔上傳，保留每份資料的獨立摘要。",
    icon: Database
  },
  {
    title: "資料探索",
    body: "讀取欄位、型別、缺失值與數值摘要，快速確認資料品質。",
    icon: ScanSearch
  },
  {
    title: "模型分析",
    body: "依資料特性自動推薦模型，也能手動指定模型與圖表。",
    icon: BrainCircuit
  },
  {
    title: "金融分析",
    body: "偵測日期與價格欄位，產生 MA、RSI、MACD 與波動率。",
    icon: LineChart
  },
  {
    title: "報告輸出",
    body: "整理分析圖表、Python 程式碼、Notebook 與 Word 報告。",
    icon: FileChartColumn
  }
];

const previewNavigation: Array<{ label: string; icon: LucideIcon }> = [
  { label: "首頁", icon: Home },
  { label: "資料管理", icon: Database },
  { label: "模型分析", icon: BrainCircuit },
  { label: "金融分析", icon: LineChart },
  { label: "報告中心", icon: FileChartColumn }
];

const engineLayers = [
  {
    title: "資料層",
    body: "多檔讀取、資料摘要、合併輪廓與清理建議。"
  },
  {
    title: "模型層",
    body: "自動判斷回歸或分類，依資料規模與目標欄位挑選模型。"
  },
  {
    title: "金融層",
    body: "針對時間序列價格資料建立技術指標與金融摘要。"
  },
  {
    title: "交付層",
    body: "把圖表、程式碼、Notebook 與報告集中保存。"
  }
];

const previewCapabilities = [
  { label: "資料匯入", value: "多檔" },
  { label: "模型策略", value: "自動 / 手動" },
  { label: "金融模式", value: "偵測後啟用" },
  { label: "輸出方式", value: "頁內預覽" }
];

const decisionSignals = [
  "目標欄位的資料型態與唯一值比例",
  "資料列數、特徵數、缺失比例與數值欄位分布",
  "日期與價格欄位是否形成金融時間序列"
];

export default function HomePage() {
  return (
    <AppShell active="home">
      <section className="landing-hero">
        <div className="hero-wave hero-wave-left" />
        <div className="hero-wave hero-wave-right" />

        <div className="landing-hero-grid">
          <div className="landing-copy">
            <p className="hero-kicker">AI 驅動的金融與資料分析平台</p>
            <h1>
              讓資料說話，
              <span>讓決策更智慧。</span>
            </h1>
            <p className="hero-lede">
              上傳資料、選擇分析、取得洞察。系統會從資料理解開始，
              自動完成模型比較、金融指標、圖表輸出與分析報告。
            </p>

            <div className="hero-action-row">
              <Button asChild variant="premium" size="lg" className="hero-primary-action">
                <Link href="/upload">
                  <CloudUpload aria-hidden="true" />
                  上傳資料
                  <ArrowRight aria-hidden="true" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg">
                <Link href="#workflow">查看流程</Link>
              </Button>
            </div>

            <div className="hero-proof-row" aria-label="核心能力">
              <Badge variant="outline">多檔合併分析</Badge>
              <Badge variant="outline">自動模型推薦</Badge>
              <Badge variant="outline">金融指標輸出</Badge>
            </div>
          </div>

          <PointerSurface>
            <ProductPreview />
          </PointerSurface>
        </div>
      </section>

      <ScrollReveal>
        <section id="workflow" className="workflow-section">
          <div className="section-heading">
            <span>完整流程</span>
            <h2>從匯入到報告，一條路徑完成</h2>
            <p>把分析流程拆成五個步驟，使用者不需要猜下一步該做什麼。</p>
          </div>
          <div className="workflow-track">
            {workflow.map((item, index) => {
              const WorkflowIcon = item.icon;
              return (
                <article key={item.title} className="workflow-card">
                  <div className="workflow-icon">
                    <WorkflowIcon aria-hidden="true" className="h-7 w-7" />
                  </div>
                  <span className="workflow-index">{String(index + 1).padStart(2, "0")}</span>
                  <h3>{item.title}</h3>
                  <p>{item.body}</p>
                </article>
              );
            })}
          </div>
        </section>
      </ScrollReveal>

      <ScrollReveal>
        <section className="engine-section">
          <div className="engine-copy">
            <span>分析引擎</span>
            <h2>不是固定套模型，而是先理解資料</h2>
            <p>
              系統會依據欄位型態、目標欄位、資料量、數值比例與金融時間序列訊號，
              決定適合的分析方向。使用者仍可以手動覆寫模型與圖表選項。
            </p>
            <div className="engine-status">
              <strong>所有結果都由後端實際運算產生</strong>
            </div>
            <details className="decision-disclosure">
              <summary>
                <span>查看自動判斷依據</span>
                <ChevronDown aria-hidden="true" className="h-4 w-4" />
              </summary>
              <div className="disclosure-content">
                {decisionSignals.map((signal, index) => (
                  <div key={signal}>
                    <span>{String(index + 1).padStart(2, "0")}</span>
                    <p>{signal}</p>
                  </div>
                ))}
              </div>
            </details>
          </div>
          <div className="engine-grid">
            {engineLayers.map((layer, index) => (
              <article key={layer.title} className="engine-card">
                <div className="engine-card-top">
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <h3>{layer.title}</h3>
                </div>
                <p>{layer.body}</p>
              </article>
            ))}
          </div>
        </section>
      </ScrollReveal>

      <ScrollReveal>
        <section className="handoff-strip">
          <div className="handoff-icon">
            <ShieldCheck aria-hidden="true" className="h-7 w-7" />
          </div>
          <div>
            <h2>清楚、安全、可交付</h2>
            <p>每次分析都能追溯輸入檔案、後端執行結果與生成輸出，不用靠靜態假資料撐畫面。</p>
          </div>
          <Button asChild variant="outline">
            <Link href="/upload">
              進入工作台
              <ArrowRight aria-hidden="true" />
            </Link>
          </Button>
        </section>
      </ScrollReveal>
    </AppShell>
  );
}

function ProductPreview() {
  return (
    <div className="product-preview-frame" aria-label="產品操作預覽">
      <aside className="preview-sidebar">
        <div className="preview-brand">
          <div className="preview-brand-mark">智</div>
          <span>智能金融資料分析</span>
        </div>
        {previewNavigation.map((item, index) => {
          const PreviewIcon = item.icon;
          return (
            <div key={item.label} className={`preview-nav-item ${index === 0 ? "is-active" : ""}`}>
              <PreviewIcon aria-hidden="true" className="h-4 w-4" />
              <span>{item.label}</span>
            </div>
          );
        })}
      </aside>

      <div className="preview-stage">
        <div className="preview-topbar">
          <div>
            <span>分析總覽</span>
            <h2>今天的資料任務</h2>
          </div>
          <span className="preview-session-note">等待資料</span>
        </div>

        <div className="preview-metrics">
          {previewCapabilities.map((signal) => (
            <div key={signal.label}>
              <span>{signal.label}</span>
              <strong>{signal.value}</strong>
            </div>
          ))}
        </div>

        <div className="preview-dashboard-grid">
          <div className="preview-empty-state">
            <div className="preview-upload-icon">
              <CloudUpload aria-hidden="true" className="h-7 w-7" />
            </div>
            <div>
              <div className="preview-card-title">等待資料匯入</div>
              <p>加入 CSV 或 Excel 後，系統才會顯示真實摘要與模型建議。</p>
            </div>
          </div>
          <div className="preview-status-list">
            <div className="preview-card-title">分析流程</div>
            {["資料上傳", "資料讀取", "模型分析", "報告生成"].map((item, index) => (
              <div key={item} className={index === 0 ? "is-current" : ""}>
                <span />
                <strong>{item}</strong>
                <small>{index === 0 ? "等待中" : "尚未開始"}</small>
              </div>
            ))}
          </div>
        </div>

        <div className="preview-flow-mini">
          {workflow.map((item, index) => (
            <div key={item.title}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              {item.title}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
