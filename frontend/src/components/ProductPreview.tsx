"use client";

import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  Check,
  Database,
  FileCode2,
  LineChart,
  Sparkles
} from "lucide-react";
import { useLocale } from "@/components/LocaleProvider";
import {
  useWorkspace,
  workspaceSourceKey
} from "@/components/WorkspaceProvider";
import { useWorkspaceSources } from "@/components/WorkspaceSource";
import { Badge } from "@/components/ui/badge";
import type {
  FinancialAnalysis,
  GeneratedCode,
  ModelAnalysis
} from "@/lib/api";

export function ProductPreview() {
  const { text, path } = useLocale();
  const { panelStates } = useWorkspace();
  const { activeSource } = useWorkspaceSources();
  const sourceKey = activeSource
    ? workspaceSourceKey(
        activeSource.file,
        activeSource.files,
        activeSource.isMerged
      )
    : "";
  const modelResult = findPanelResult<ModelAnalysis>(
    panelStates,
    sourceKey,
    ":model:result"
  );
  const financeResult = findPanelResult<FinancialAnalysis>(
    panelStates,
    sourceKey,
    ":finance:result"
  );
  const generatedCode = findPanelResult<GeneratedCode>(
    panelStates,
    sourceKey,
    ":result",
    ":code:"
  );
  const bestModel = modelResult ? getBestModel(modelResult) : null;
  const chart = financeResult?.charts[0] ?? modelResult?.charts[0] ?? null;

  return (
    <div className="live-product-preview" aria-label={text("工作區即時預覽", "Live workspace preview")}>
      <div className="live-preview-sidebar" aria-hidden="true">
        <span className="live-preview-brand">智</span>
        <span className="is-active"><Sparkles /></span>
        <span><Database /></span>
        <span><BarChart3 /></span>
        <span><LineChart /></span>
        <span><FileCode2 /></span>
      </div>

      <div className="live-preview-stage">
        <div className="live-preview-topbar">
          <div>
            <span>{text("工作區", "Workspace")}</span>
            <strong>{text("清楚的下一步", "A clear next step")}</strong>
          </div>
          <Badge variant={activeSource ? "success" : "outline"}>
            {activeSource
              ? text("資料已連接", "Data connected")
              : text("等待資料", "Waiting for data")}
          </Badge>
        </div>

        {activeSource ? (
          <>
            <section className="live-preview-next">
              <div>
                <span>{text("建議下一步", "Recommended next step")}</span>
                <h3>
                  {modelResult
                    ? text("整理分析成果", "Package the analysis")
                    : text("比較適合的模型", "Compare suitable models")}
                </h3>
                <p>
                  {modelResult
                    ? text(
                        "最佳模型與圖表已完成，可以生成程式碼或報告。",
                        "The best model and charts are ready for code or report generation."
                      )
                    : text(
                        "系統已理解資料輪廓，下一步可依目標欄位推薦模型。",
                        "The dataset profile is ready. Choose a target to get model recommendations."
                      )}
                </p>
              </div>
              <Link href={path(modelResult ? "/app/reports" : "/app/models")}>
                {text("開啟", "Open")}
                <ArrowRight aria-hidden="true" />
              </Link>
            </section>

            <div className="live-preview-grid">
              <section className="live-preview-dataset">
                <div className="preview-section-label">
                  <Database aria-hidden="true" />
                  {text("目前資料", "Current dataset")}
                </div>
                <strong>{activeSource.label}</strong>
                <dl>
                  <div>
                    <dt>{text("資料列", "Rows")}</dt>
                    <dd>{activeSource.dataset.row_count.toLocaleString()}</dd>
                  </div>
                  <div>
                    <dt>{text("欄位", "Columns")}</dt>
                    <dd>{activeSource.dataset.column_count.toLocaleString()}</dd>
                  </div>
                </dl>
              </section>

              <section className="live-preview-result">
                <div className="preview-section-label">
                  <BarChart3 aria-hidden="true" />
                  {text("目前成果", "Current result")}
                </div>
                {bestModel ? (
                  <>
                    <strong>{bestModel.model_name}</strong>
                    <p>
                      {modelResult?.problem_type === "classification"
                        ? `F1 ${formatNumber(bestModel.f1_score)}`
                        : `RMSE ${formatNumber(bestModel.rmse)}`}
                    </p>
                  </>
                ) : (
                  <>
                    <strong>{text("尚未執行模型", "No model run yet")}</strong>
                    <p>{text("結果不使用示範數據", "No demo results are substituted")}</p>
                  </>
                )}
              </section>
            </div>

            {chart ? (
              <figure className="live-preview-chart">
                <figcaption>
                  <span>{chart.title}</span>
                  <Badge variant="outline">{text("真實輸出", "Real output")}</Badge>
                </figcaption>
                <img
                  src={chart.chart_url}
                  alt={chart.title}
                  width={960}
                  height={520}
                />
              </figure>
            ) : (
              <div className="live-preview-output">
                <span><Check aria-hidden="true" /></span>
                <div>
                  <strong>{text("資料輪廓已可用", "Dataset profile is ready")}</strong>
                  <p>
                    {generatedCode
                      ? text("程式碼已在工作區內提供預覽。", "Generated code is available inside the workspace.")
                      : text("執行分析後，圖表會直接顯示在這裡。", "Charts will appear here after a real analysis run.")}
                  </p>
                </div>
              </div>
            )}
          </>
        ) : (
          <section className="live-preview-empty">
            <span><Database aria-hidden="true" /></span>
            <div>
              <strong>{text("從你的資料開始", "Start with your data")}</strong>
              <p>
                {text(
                  "目前沒有連接資料，因此不顯示任何模擬結果。加入 CSV、Excel 或 JSON 後，這裡會顯示真實摘要。",
                  "No dataset is connected, so no simulated result is shown. Add a CSV, Excel, or JSON file to see a real summary here."
                )}
              </p>
              <Link href={path("/app/data")}>
                {text("加入第一份資料", "Add your first dataset")}
                <ArrowRight aria-hidden="true" />
              </Link>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}

function findPanelResult<T>(
  panelStates: Record<string, unknown>,
  sourceKey: string,
  suffix: string,
  includes = ""
) {
  if (!sourceKey) return null;
  const entry = Object.entries(panelStates).find(
    ([key, value]) =>
      key.startsWith(sourceKey) &&
      key.endsWith(suffix) &&
      key.includes(includes) &&
      value !== null &&
      value !== false
  );
  return (entry?.[1] as T | undefined) ?? null;
}

function getBestModel(result: ModelAnalysis) {
  return result.model_results.reduce((best, current) => {
    if (result.problem_type === "classification") {
      return (current.f1_score ?? current.accuracy ?? 0) >
        (best.f1_score ?? best.accuracy ?? 0)
        ? current
        : best;
    }
    return current.rmse < best.rmse ? current : best;
  });
}

function formatNumber(value: number | null) {
  return value === null ? "—" : value.toFixed(3);
}
