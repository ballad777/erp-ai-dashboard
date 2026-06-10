import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { SystemStatus } from "@/components/SystemStatus";

const workflow = [
  {
    title: "資料匯入",
    body: "支援 CSV / Excel 多檔上傳，保留每份資料的獨立摘要。",
    icon: "database"
  },
  {
    title: "資料探索",
    body: "讀取欄位、型別、缺失值與數值摘要，快速確認資料品質。",
    icon: "scan"
  },
  {
    title: "模型分析",
    body: "依資料特性自動推薦模型，也能手動指定模型與圖表。",
    icon: "brain"
  },
  {
    title: "金融分析",
    body: "偵測日期與價格欄位，產生 MA、RSI、MACD 與波動率。",
    icon: "trend"
  },
  {
    title: "報告輸出",
    body: "整理分析圖表、Python 程式碼、Notebook 與 Word 報告。",
    icon: "report"
  }
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

const liveSignals = [
  { label: "資料集", value: "12" },
  { label: "模型執行", value: "28" },
  { label: "圖表輸出", value: "9" },
  { label: "節省時間", value: "68h" }
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
              <Link href="/upload" className="primary-action glow-button">
                <Icon name="upload" className="h-6 w-6" />
                上傳資料
                <Icon name="arrow" className="h-5 w-5" />
              </Link>
              <Link href="#workflow" className="secondary-action">
                查看流程
              </Link>
            </div>

            <div className="hero-proof-row" aria-label="核心能力">
              <span>多檔合併分析</span>
              <span>自動模型推薦</span>
              <span>金融指標輸出</span>
            </div>
          </div>

          <ProductPreview />
        </div>
      </section>

      <section id="workflow" className="workflow-section">
        <div className="section-heading">
          <span>完整流程</span>
          <h2>從匯入到報告，一條路徑完成</h2>
          <p>把分析流程拆成五個步驟，使用者不需要猜下一步該做什麼。</p>
        </div>
        <div className="workflow-track">
          {workflow.map((item, index) => (
            <article key={item.title} className="workflow-card">
              <div className="workflow-icon">
                <Icon name={item.icon} className="h-7 w-7" />
              </div>
              <span className="workflow-index">{String(index + 1).padStart(2, "0")}</span>
              <h3>{item.title}</h3>
              <p>{item.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="engine-section">
        <div className="engine-copy">
          <span>分析引擎</span>
          <h2>不是固定套模型，而是先理解資料</h2>
          <p>
            系統會依據欄位型態、目標欄位、資料量、數值比例與金融時間序列訊號，
            決定適合的分析方向。使用者仍可以手動覆寫模型與圖表選項。
          </p>
          <div className="engine-status">
            <SystemStatus />
            <strong>所有結果都由後端實際運算產生</strong>
          </div>
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

      <section className="handoff-strip">
        <div className="handoff-icon">
          <Icon name="shield" className="h-7 w-7" />
        </div>
        <div>
          <h2>清楚、安全、可交付</h2>
          <p>每次分析都能追溯輸入檔案、後端執行結果與生成輸出，不用靠靜態假資料撐畫面。</p>
        </div>
        <Link href="/upload" className="handoff-link">
          進入工作台
          <Icon name="arrow" className="h-4 w-4" />
        </Link>
      </section>
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
        {["首頁", "資料管理", "模型分析", "金融分析", "報告中心"].map((item, index) => (
          <div key={item} className={`preview-nav-item ${index === 0 ? "is-active" : ""}`}>
            <Icon name={index === 0 ? "home" : workflow[Math.min(index, workflow.length - 1)].icon} className="h-4 w-4" />
            <span>{item}</span>
          </div>
        ))}
      </aside>

      <div className="preview-stage">
        <div className="preview-topbar">
          <div>
            <span>分析總覽</span>
            <h2>今天的資料任務</h2>
          </div>
          <SystemStatus compact />
        </div>

        <div className="preview-metrics">
          {liveSignals.map((signal) => (
            <div key={signal.label}>
              <span>{signal.label}</span>
              <strong>{signal.value}</strong>
            </div>
          ))}
        </div>

        <div className="preview-dashboard-grid">
          <div className="preview-chart">
            <div className="preview-card-title">模型表現趨勢</div>
            <div className="chart-lines" aria-hidden="true">
              <span />
              <span />
              <span />
            </div>
          </div>
          <div className="preview-donut">
            <div className="donut-ring">
              <strong>65%</strong>
              <small>最佳模型</small>
            </div>
            <ul>
              <li>資料品質</li>
              <li>模型比較</li>
              <li>報告輸出</li>
            </ul>
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

function Icon({ name, className = "" }: { name: string; className?: string }) {
  const commonProps = {
    className,
    fill: "none",
    stroke: "currentColor",
    strokeWidth: "2.2",
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    viewBox: "0 0 24 24"
  };

  if (name === "upload") {
    return (
      <svg {...commonProps}>
        <path d="M12 16V7" />
        <path d="m8 11 4-4 4 4" />
        <path d="M7 18.5H6.5a4.5 4.5 0 0 1-.4-8.98A6 6 0 0 1 17.7 8.4 4.75 4.75 0 0 1 18 18.5h-.8" />
      </svg>
    );
  }

  if (name === "arrow") {
    return (
      <svg {...commonProps}>
        <path d="M5 12h14" />
        <path d="m13 6 6 6-6 6" />
      </svg>
    );
  }

  if (name === "database") {
    return (
      <svg {...commonProps}>
        <ellipse cx="12" cy="5" rx="7" ry="3" />
        <path d="M5 5v7c0 1.7 3.1 3 7 3s7-1.3 7-3V5" />
        <path d="M5 12v7c0 1.7 3.1 3 7 3s7-1.3 7-3v-7" />
      </svg>
    );
  }

  if (name === "scan") {
    return (
      <svg {...commonProps}>
        <path d="M7 3H5a2 2 0 0 0-2 2v2" />
        <path d="M17 3h2a2 2 0 0 1 2 2v2" />
        <path d="M7 21H5a2 2 0 0 1-2-2v-2" />
        <path d="M17 21h2a2 2 0 0 0 2-2v-2" />
        <path d="M7 12h10" />
        <path d="M9 8h6" />
        <path d="M10 16h4" />
      </svg>
    );
  }

  if (name === "brain") {
    return (
      <svg {...commonProps}>
        <path d="M9 4.5a3 3 0 0 0-3 3v.4a3.2 3.2 0 0 0-2 3v.4a3.2 3.2 0 0 0 2 3V16a3.5 3.5 0 0 0 6 2.45V6.4A3.5 3.5 0 0 0 9 4.5Z" />
        <path d="M15 4.5a3 3 0 0 1 3 3v.4a3.2 3.2 0 0 1 2 3v.4a3.2 3.2 0 0 1-2 3V16a3.5 3.5 0 0 1-6 2.45V6.4A3.5 3.5 0 0 1 15 4.5Z" />
        <path d="M8 10h4" />
        <path d="M12 13h4" />
      </svg>
    );
  }

  if (name === "trend") {
    return (
      <svg {...commonProps}>
        <path d="M4 18h16" />
        <path d="M6 15 11 10l3 3 6-7" />
        <path d="M16 6h4v4" />
      </svg>
    );
  }

  if (name === "report") {
    return (
      <svg {...commonProps}>
        <path d="M7 3h7l5 5v13H7z" />
        <path d="M14 3v5h5" />
        <path d="M10 13h6" />
        <path d="M10 17h4" />
      </svg>
    );
  }

  if (name === "home") {
    return (
      <svg {...commonProps}>
        <path d="m4 11 8-7 8 7" />
        <path d="M6 10v10h12V10" />
        <path d="M10 20v-6h4v6" />
      </svg>
    );
  }

  return (
    <svg {...commonProps}>
      <path d="M12 3 19 6v5c0 4.5-2.7 8-7 10-4.3-2-7-5.5-7-10V6z" />
      <path d="m9 12 2 2 4-5" />
    </svg>
  );
}
