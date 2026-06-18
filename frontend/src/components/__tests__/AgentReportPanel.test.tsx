import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AgentWorkflowResult } from "@/components/AgentReportPanel";
import { LocaleProvider } from "@/components/LocaleProvider";
import type { AgentWorkflow } from "@/lib/api";

vi.mock("next/navigation", () => ({
  usePathname: () => "/app/reports"
}));

const workflow: AgentWorkflow = {
  file_name: "sample.csv",
  target_column: "sales",
  agent_steps: [
    {
      agent_name: "報告代理",
      status: "completed",
      summary: "已產生決策摘要。",
      outputs: {}
    }
  ],
  executive_summary: ["本次分析完成。"],
  decision_brief: {
    summary_title: "把分析結果翻譯成下一步",
    plain_language_summary: {
      what_happened: "讀取 100 筆資料。",
      why_it_matters: "最佳模型已有可用表現。",
      risks: "資料品質仍需確認。",
      opportunities: "可優先追蹤重要欄位。",
      next_step: "先檢查特徵重要性。"
    },
    executive_summary: [
      "本次分析共讀取 100 筆資料。",
      "最佳模型為 Random Forest。",
      "建議下一步：先檢查特徵重要性。"
    ],
    priority_findings: [
      {
        level: "most_important",
        label: "最重要發現",
        title: "最佳模型目前是 Random Forest",
        summary: "RMSE 明顯低於 baseline。",
        evidence: "RMSE 1.2；MAE 0.8。",
        recommended_action: "先用此模型作為基準。"
      }
    ],
    model_guidance: {
      problem_type_label: "回歸",
      target_column: "sales",
      selection_logic: "系統依資料型態推薦模型。",
      baseline_summary: "Baseline：RMSE 2.0。",
      best_model_summary: "Random Forest：RMSE 1.2。",
      recommended_models: [
        {
          model_key: "random_forest",
          model_name: "隨機森林",
          purpose: "處理非線性表格資料。",
          suitable_data_types: ["一般表格資料"],
          difficulty: "中級",
          use_cases: ["銷售預測"],
          why_recommended: "資料含多個欄位且可能有非線性關係。",
          expected_output: "預測 sales 並找出重要欄位。",
          recommendation_score: "4/5",
          evaluation_summary: "RMSE 1.2。"
        }
      ]
    },
    chart_interpretations: [
      {
        chart_type: "model_comparison",
        title: "模型比較圖",
        explanation: "這張圖比較模型表現。",
        key_findings: "Random Forest 表現最佳。",
        meaning: "代表資料存在可學習訊號。",
        trend_interpretation: "模型排序可作為適配程度。",
        anomaly_note: "未發現立即警訊。",
        business_insight: "可支援預測基準。",
        recommended_action: "採用最佳模型作為基準。"
      }
    ],
    risk_and_limitations: ["正式決策前應補交叉驗證。"],
    ai_conclusion: "目前可作為初步分析。"
  },
  llm_provider: "local_rule_based",
  dataset_summary: {},
  model_analysis: {
    file_name: "sample.csv",
    target_column: "sales",
    analysis_mode: "auto",
    problem_type: "regression",
    row_count_used: 100,
    feature_count_used: 5,
    model_results: [],
    model_selection_mode: "auto",
    automl_mode: "quick",
    selected_model_keys: [],
    available_models: [],
    recommended_models: [],
    model_results_path: "",
    model_results_url: "",
    cleaned_dataset_path: "",
    cleaned_dataset_url: "",
    chart_path: "",
    chart_url: "",
    charts: [],
    selected_chart_types: [],
    notes: []
  },
  financial_analysis: null,
  notes: []
};

describe("AgentWorkflowResult", () => {
  it("renders advisor-style report priorities, model guidance, and chart interpretation", () => {
    render(
      <LocaleProvider locale="zh-Hant">
        <AgentWorkflowResult workflow={workflow} />
      </LocaleProvider>
    );

    expect(screen.getByRole("heading", { name: "把分析結果翻譯成下一步" })).toBeInTheDocument();
    expect(screen.getByText("分析結果優先級")).toBeInTheDocument();
    expect(screen.getByText("模型推薦不是讓你猜")).toBeInTheDocument();
    expect(screen.getByText("逐圖解讀")).toBeInTheDocument();
    expect(screen.getByText("為什麼推薦")).toBeInTheDocument();
    expect(screen.getByText("圖表說明")).toBeInTheDocument();
  });
});
