import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { SystemStatus } from "@/components/SystemStatus";

const capabilities = [
  {
    title: "多模型分析",
    body: "依資料型態自動推薦模型，也能手動指定模型組合。",
    icon: "bars"
  },
  {
    title: "金融指標",
    body: "支援 MA、報酬率、波動率、RSI、MACD 與 VaR。",
    icon: "trend"
  },
  {
    title: "程式碼生成",
    body: "輸出 Python 腳本與 Notebook，方便交付與重跑。",
    icon: "code"
  },
  {
    title: "報告輸出",
    body: "整理模型結果、圖表與摘要，產出正式分析報告。",
    icon: "report"
  }
];

const workflow = ["上傳資料", "資料探索", "模型分析", "結果解讀", "報告輸出"];

const sampleDatasets = [
  {
    name: "金融市場資料集",
    file: "stock_prices_sample.csv",
    tags: ["金融", "時間序列"]
  },
  {
    name: "房價預測資料集",
    file: "housing_sample.csv",
    tags: ["回歸", "結構化"]
  }
];

const productSteps = [
  "資料匯入與清理",
  "自動判斷分析類型",
  "推薦模型與圖表",
  "產生程式碼與報告",
  "交付可下載成果"
];

const analysisLayers = [
  {
    title: "資料層",
    body: "讀取多檔 CSV / Excel，建立欄位摘要、缺失值統計與合併資料輪廓。"
  },
  {
    title: "模型層",
    body: "依目標欄位判斷回歸或分類，推薦適合的模型組合並輸出比較表。"
  },
  {
    title: "金融層",
    body: "偵測日期與價格欄位，計算報酬率、技術指標、VaR 與預測走勢。"
  },
  {
    title: "交付層",
    body: "整理圖表、程式碼、Notebook、模型結果與 Word 報告。"
  }
];

const systemMoments = [
  {
    title: "命令中心",
    body: "把上傳、讀取與清空佇列收進同一個入口，讓常用動作不必來回找。",
    detail: "⌘K"
  },
  {
    title: "工作台狀態",
    body: "即時讀取目前檔案數、成功數、錯誤數與後端健康狀態。",
    detail: "Live"
  },
  {
    title: "頁內程式碼",
    body: "生成 Python 與 Notebook 後直接在介面內檢查內容，再下載交付。",
    detail: "Code"
  }
];

const refinementDetails = [
  "多檔案佇列",
  "合併分析",
  "自動推薦模型",
  "手動模型選擇",
  "圖表類型選擇",
  "金融指標",
  "Word 報告",
  "輸出檔保存"
];

export default function HomePage() {
  return (
    <AppShell active="home">
      <section className="relative isolate overflow-hidden px-0 pb-10 pt-6 lg:pb-14 lg:pt-8">
        <div className="hero-wave hero-wave-left" />
        <div className="hero-wave hero-wave-right" />

        <div className="grid gap-10 2xl:grid-cols-[0.98fr_1.02fr] 2xl:items-center">
          <div className="relative z-10">
            <div className="inline-flex items-center rounded-full border border-sky-200 bg-white/72 px-5 py-2 text-sm font-semibold text-brand shadow-[0_10px_28px_rgba(14,116,144,0.08)] backdrop-blur-xl">
              AI 驅動的金融與資料分析平台
            </div>
            <h1 className="mt-7 max-w-5xl text-5xl font-semibold leading-[1.05] tracking-normal text-ink sm:text-6xl 2xl:text-7xl">
              智能金融
              <span className="block bg-gradient-to-r from-brand via-sky-500 to-navy bg-clip-text text-transparent">
                資料分析
              </span>
            </h1>
            <p className="mt-7 max-w-3xl text-lg leading-9 text-slate-600 sm:text-xl">
              上傳資料、選擇分析、取得洞察。讓 AI 協助你完成模型比較、
              金融指標、圖表輸出與分析報告。
            </p>

            <div className="mt-9 flex flex-col gap-4 sm:flex-row">
              <Link
                href="/upload"
                className="glow-button inline-flex h-14 items-center justify-center gap-3 rounded-xl bg-gradient-to-r from-brand via-sky-500 to-navy px-7 text-base font-semibold text-white shadow-[0_20px_40px_rgba(14,116,144,0.18)] sm:h-16 sm:px-8 sm:text-lg"
              >
                <Icon name="upload" className="h-6 w-6" />
                上傳資料集
                <Icon name="arrow" className="h-5 w-5" />
              </Link>
            </div>

            <div className="mt-12 grid gap-5 sm:grid-cols-2 2xl:grid-cols-4">
              {capabilities.map((item) => (
                <div key={item.title} className="feature-chip">
                  <div className="feature-icon">
                    <Icon name={item.icon} className="h-6 w-6" />
                  </div>
                  <div>
                    <div className="text-base font-semibold text-ink">{item.title}</div>
                    <p className="mt-1 text-sm leading-6 text-slate-600">{item.body}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <ProductPreview />
        </div>
      </section>

      <section className="control-center-band">
        <div className="control-center-copy">
          <h2>像一個真正的分析系統，而不是單次工具</h2>
          <p>
            從進站、上傳、讀取、分析到交付，每個動作都保留明確狀態與下一步，
            讓操作節奏更像熟悉的系統工作流。
          </p>
        </div>
        <div className="control-center-panel">
          <div className="control-center-top">
            <SystemStatus />
            <span className="text-sm font-semibold text-slate-500">智慧工作流</span>
          </div>
          <div className="control-center-grid">
            {systemMoments.map((item) => (
              <div key={item.title} className="control-tile">
                <div className="flex items-center justify-between gap-3">
                  <h3>{item.title}</h3>
                  <span>{item.detail}</span>
                </div>
                <p>{item.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mb-8 grid gap-4 lg:grid-cols-4">
        {analysisLayers.map((layer, index) => (
          <article key={layer.title} className="layer-card">
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-xl font-semibold text-ink">{layer.title}</h2>
              <span className="text-sm font-semibold text-brand">
                {String(index + 1).padStart(2, "0")}
              </span>
            </div>
            <p className="mt-4 text-sm leading-7 text-slate-600">{layer.body}</p>
          </article>
        ))}
      </section>

      <section className="deep-system-section">
        <div className="deep-system-copy">
          <h2>細節會慢慢浮現</h2>
          <p>
            初次使用可以只上傳資料；熟悉後可以切換自動推薦、手動選模型、
            指定圖表、合併多檔，再把結果整理成程式碼與報告。
          </p>
        </div>
        <div className="refinement-grid">
          {refinementDetails.map((item, index) => (
            <div key={item} className="refinement-chip">
              <span>{String(index + 1).padStart(2, "0")}</span>
              {item}
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-7 2xl:grid-cols-[0.95fr_1.05fr_1.05fr]">
        <ProductPanel title="核心能力" action="開始分析">
          <div className="grid gap-4">
            {productSteps.map((step, index) => (
              <div key={step} className="flex items-center gap-4 rounded-lg border border-blue-100 bg-white/72 px-4 py-3 shadow-[0_12px_30px_rgba(15,23,42,0.04)]">
                <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-gradient-to-br from-brand to-indigo-500 text-sm font-semibold text-white">
                  {index + 1}
                </span>
                <span className="text-base font-semibold text-slate-800">{step}</span>
              </div>
            ))}
          </div>
        </ProductPanel>

        <ProductPanel title="範例資料集" action="前往上傳">
          <div className="grid gap-3">
            {sampleDatasets.map((item) => (
              <div key={item.file} className="dataset-row">
                <div className="flex min-w-0 items-center gap-3">
                  <Icon name="file" className="h-6 w-6 shrink-0 text-navy" />
                  <div className="min-w-0">
                    <div className="truncate text-base font-semibold text-slate-900">{item.name}</div>
                    <div className="truncate text-sm text-slate-500">{item.file}</div>
                  </div>
                </div>
                <div className="flex shrink-0 gap-2">
                  {item.tags.map((tag) => (
                    <span key={tag} className="rounded-md bg-blue-50 px-2.5 py-1 text-xs font-semibold text-slate-600">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </ProductPanel>

        <ProductPanel title="分析成果" action="建立報告">
          <div className="space-y-4">
            <OutcomeRow title="模型比較表" body="R2、RMSE、MAE、Accuracy、F1 與訓練時間" />
            <OutcomeRow title="視覺化圖表" body="模型比較、特徵重要性、預測值與實際值、殘差圖" />
            <OutcomeRow title="金融摘要" body="移動平均、報酬率、波動率、RSI、MACD、VaR" />
            <OutcomeRow title="交付檔案" body="Python、Notebook、Word 報告、Excel、CSV、模型檔" />
          </div>
        </ProductPanel>
      </section>

      <section className="mt-12 rounded-2xl border border-blue-100 bg-white/76 px-8 py-7 text-center shadow-soft backdrop-blur-2xl">
        <div className="mx-auto flex max-w-4xl flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <div className="grid h-14 w-14 place-items-center rounded-2xl border border-cyan-200 bg-cyan-50 text-brand">
            <Icon name="shield" className="h-8 w-8" />
          </div>
          <div className="text-left">
            <h2 className="text-2xl font-semibold text-ink">安全、可追溯、可交付</h2>
            <p className="mt-2 text-base leading-7 text-slate-600">
              每一次分析都以實際資料運算，輸出檔案集中保存，讓團隊能檢查、重跑與交付。
            </p>
          </div>
        </div>
      </section>
    </AppShell>
  );
}

function ProductPreview() {
  return (
    <div className="relative z-10">
      <div className="product-preview">
        <aside className="hidden border-r border-blue-100 bg-white/56 p-5 lg:block">
          <div className="mb-6 flex items-center gap-3">
            <div className="h-3 w-3 rounded bg-gradient-to-br from-brand to-indigo-500" />
            <div className="text-sm font-semibold text-slate-900">智能金融資料分析</div>
          </div>
          <div className="space-y-2">
            {["首頁", "資料管理", "模型分析", "金融分析", "程式碼生成", "報告中心", "設定"].map((item, index) => (
              <div
                key={item}
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold ${
                  index === 0 ? "bg-blue-50 text-navy" : "text-slate-600"
                }`}
              >
                <span className={`h-2 w-2 rounded-full ${index === 0 ? "bg-brand" : "bg-blue-200"}`} />
                {item}
              </div>
            ))}
          </div>
        </aside>

        <div className="p-6 lg:p-8">
          <div className="mb-5 flex items-center justify-between gap-4">
            <div>
              <div className="text-xl font-semibold text-ink">快速開始</div>
              <div className="mt-1 text-sm text-slate-500">從資料匯入到報告輸出</div>
            </div>
            <span className="rounded-full border border-cyan-200 bg-cyan-50 px-4 py-1.5 text-sm font-semibold text-brand">
              產品流程
            </span>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <PreviewTile icon="upload" title="上傳資料" body="CSV / Excel 多檔匯入" />
            <PreviewTile icon="brain" title="自動分析" body="AI 推薦模型與圖表" />
            <PreviewTile icon="trend" title="洞察報告" body="圖表、摘要與交付檔" />
          </div>

          <div className="mt-6 rounded-xl border border-blue-100 bg-white/72 p-5 shadow-[0_18px_42px_rgba(15,23,42,0.05)]">
            <div className="mb-5 text-lg font-semibold text-ink">分析流程</div>
            <div className="flex flex-col gap-4 md:flex-row md:items-center">
              {workflow.map((item, index) => (
                <div key={item} className="flex flex-1 items-center gap-3">
                  <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-gradient-to-br from-brand to-indigo-500 text-sm font-semibold text-white">
                    {index + 1}
                  </div>
                  <div className="min-w-0 text-sm font-semibold text-slate-600">{item}</div>
                  {index < workflow.length - 1 ? (
                    <div className="hidden h-px flex-1 bg-gradient-to-r from-brand to-blue-200 md:block" />
                  ) : null}
                </div>
              ))}
            </div>
            <div className="mt-5 rounded-lg border border-cyan-200 bg-cyan-50/80 px-4 py-3 text-sm font-semibold text-brand">
              已準備好開始你的資料分析流程
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function PreviewTile({ icon, title, body }: { icon: string; title: string; body: string }) {
  return (
    <div className="rounded-xl border border-blue-100 bg-white/76 p-5 text-center shadow-[0_18px_42px_rgba(15,23,42,0.05)]">
      <div className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-gradient-to-br from-cyan-50 to-blue-50 text-brand">
        <Icon name={icon} className="h-8 w-8" />
      </div>
      <div className="mt-4 text-base font-semibold text-ink">{title}</div>
      <p className="mt-2 text-sm leading-6 text-slate-500">{body}</p>
    </div>
  );
}

function ProductPanel({
  title,
  action,
  children
}: {
  title: string;
  action: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-2xl border border-blue-100 bg-white/76 p-7 shadow-soft backdrop-blur-2xl">
      <div className="mb-6 flex items-center justify-between gap-4">
        <h2 className="text-2xl font-semibold text-ink">{title}</h2>
        <Link href="/upload" className="inline-flex items-center gap-2 text-sm font-semibold text-brand transition hover:text-navy">
          {action}
          <Icon name="arrow" className="h-4 w-4" />
        </Link>
      </div>
      {children}
    </section>
  );
}

function OutcomeRow({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-lg border border-blue-100 bg-white/72 px-4 py-3 shadow-[0_12px_30px_rgba(15,23,42,0.04)]">
      <div className="text-base font-semibold text-slate-900">{title}</div>
      <div className="mt-1 text-sm leading-6 text-slate-500">{body}</div>
    </div>
  );
}

function Icon({ name, className = "" }: { name: string; className?: string }) {
  const common = "none";
  if (name === "upload") {
    return (
      <svg viewBox="0 0 24 24" className={className} fill={common} stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 16V7" />
        <path d="m8 11 4-4 4 4" />
        <path d="M7 18.5H6.5a4.5 4.5 0 0 1-.4-8.98A6 6 0 0 1 17.7 8.4 4.75 4.75 0 0 1 18 18.5h-.8" />
      </svg>
    );
  }
  if (name === "arrow") {
    return (
      <svg viewBox="0 0 24 24" className={className} fill={common} stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M5 12h14" />
        <path d="m13 6 6 6-6 6" />
      </svg>
    );
  }
  if (name === "bars") {
    return (
      <svg viewBox="0 0 24 24" className={className} fill={common} stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M5 19V9" />
        <path d="M12 19V5" />
        <path d="M19 19v-7" />
      </svg>
    );
  }
  if (name === "trend") {
    return (
      <svg viewBox="0 0 24 24" className={className} fill={common} stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M4 18h16" />
        <path d="M6 15 11 10l3 3 6-7" />
        <path d="M16 6h4v4" />
      </svg>
    );
  }
  if (name === "code") {
    return (
      <svg viewBox="0 0 24 24" className={className} fill={common} stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="m8 9-4 3 4 3" />
        <path d="m16 9 4 3-4 3" />
        <path d="m14 5-4 14" />
      </svg>
    );
  }
  if (name === "report" || name === "file") {
    return (
      <svg viewBox="0 0 24 24" className={className} fill={common} stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M7 3h7l5 5v13H7z" />
        <path d="M14 3v5h5" />
        <path d="M10 13h6" />
        <path d="M10 17h4" />
      </svg>
    );
  }
  if (name === "brain") {
    return (
      <svg viewBox="0 0 24 24" className={className} fill={common} stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9 4.5a3 3 0 0 0-3 3v.4a3.2 3.2 0 0 0-2 3v.4a3.2 3.2 0 0 0 2 3V16a3.5 3.5 0 0 0 6 2.45V6.4A3.5 3.5 0 0 0 9 4.5Z" />
        <path d="M15 4.5a3 3 0 0 1 3 3v.4a3.2 3.2 0 0 1 2 3v.4a3.2 3.2 0 0 1-2 3V16a3.5 3.5 0 0 1-6 2.45V6.4A3.5 3.5 0 0 1 15 4.5Z" />
        <path d="M8 10h4" />
        <path d="M12 13h4" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 24 24" className={className} fill={common} stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3 19 6v5c0 4.5-2.7 8-7 10-4.3-2-7-5.5-7-10V6z" />
      <path d="m9 12 2 2 4-5" />
    </svg>
  );
}
