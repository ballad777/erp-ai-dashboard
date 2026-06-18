from __future__ import annotations

from typing import Any


MetricEntry = dict[str, Any]


METRIC_GLOSSARY: dict[str, MetricEntry] = {
    "data_completeness": {
        "term": "資料完整度",
        "plain_explanation": "用來看資料是否有足夠內容可以分析。",
        "technical_definition": "非缺失儲存格占全部儲存格的比例。",
        "formula": "(全部儲存格 - 缺失儲存格) / 全部儲存格",
        "how_to_read": "越接近 100% 越好；低於 80% 時，模型與結論需要更保守解讀。",
        "caveat": "完整不代表正確，仍需確認欄位定義、重複值與異常值。",
    },
    "missing_values": {
        "term": "缺失值",
        "plain_explanation": "資料中沒有填入內容的位置。",
        "technical_definition": "Null、NaN 或空值的計數。",
        "formula": "每欄缺失筆數 / 全部資料列",
        "how_to_read": "缺失越集中在關鍵欄位，越可能影響模型與結論。",
        "caveat": "缺失可能是正常業務現象，也可能是資料收集問題，需要先判斷原因。",
    },
    "mean": {
        "term": "平均數",
        "plain_explanation": "用來快速看一欄數值的大致水準。",
        "technical_definition": "全部數值加總後除以筆數。",
        "formula": "sum(x) / n",
        "how_to_read": "適合看整體水準，但容易被極端值拉動。",
        "caveat": "若資料有很大的極端值，請同時看中位數。",
    },
    "median": {
        "term": "中位數",
        "plain_explanation": "把數值排序後位在中間的位置，較不容易被極端值影響。",
        "technical_definition": "排序後第 50 百分位數。",
        "formula": "P50",
        "how_to_read": "平均數與中位數差很多時，代表資料可能偏斜或有極端值。",
        "caveat": "中位數不反映極端高低點的影響。",
    },
    "std": {
        "term": "標準差",
        "plain_explanation": "用來看數值分散程度。",
        "technical_definition": "資料與平均數距離的平方平均後開根號。",
        "formula": "sqrt(mean((x - mean(x))^2))",
        "how_to_read": "標準差越大，代表資料變動越大。",
        "caveat": "不同單位或尺度的欄位不能直接比較標準差。",
    },
    "rmse": {
        "term": "RMSE",
        "plain_explanation": "模型預測通常會錯多少，且會更重視大錯誤。",
        "technical_definition": "Root Mean Squared Error。",
        "formula": "sqrt(mean((y_true - y_pred)^2))",
        "how_to_read": "越低越好；需和目標欄位單位一起解讀。",
        "caveat": "容易被少數大錯誤放大，應搭配 MAE 與殘差圖。",
    },
    "mae": {
        "term": "MAE",
        "plain_explanation": "模型平均大約差多少，較容易用原單位理解。",
        "technical_definition": "Mean Absolute Error。",
        "formula": "mean(abs(y_true - y_pred))",
        "how_to_read": "越低越好；通常比 RMSE 更容易向非技術使用者說明。",
        "caveat": "不會特別放大大錯誤，因此仍需看 RMSE 或誤差分布。",
    },
    "r2": {
        "term": "R²",
        "plain_explanation": "模型大概能解釋目標變化的比例。",
        "technical_definition": "Coefficient of determination。",
        "formula": "1 - SS_res / SS_tot",
        "how_to_read": "接近 1 通常較好；低於 0.35 代表解釋力有限。",
        "caveat": "R² 高不代表因果關係，也不保證未來仍準確。",
    },
    "accuracy": {
        "term": "Accuracy",
        "plain_explanation": "分類模型猜對的比例。",
        "technical_definition": "正確分類筆數 / 全部筆數。",
        "formula": "(TP + TN) / total",
        "how_to_read": "越高越好，但類別不平衡時可能誤導。",
        "caveat": "若少數類別很重要，應同時看 Precision、Recall 與 F1-score。",
    },
    "f1_score": {
        "term": "F1-score",
        "plain_explanation": "分類模型在抓到目標與避免誤判之間的平衡分數。",
        "technical_definition": "Precision 與 Recall 的調和平均。",
        "formula": "2 * precision * recall / (precision + recall)",
        "how_to_read": "越高越好；適合類別不平衡或錯分成本不同的情境。",
        "caveat": "不同類別的 F1 可能差異很大，正式決策前需看混淆矩陣。",
    },
    "feature_importance": {
        "term": "Feature importance",
        "plain_explanation": "模型認為哪些欄位最影響結果。",
        "technical_definition": "依模型方法估計特徵對預測表現的貢獻度。",
        "formula": "依模型而異，例如樹模型 impurity decrease。",
        "how_to_read": "排名越前越值得優先檢查是否具有業務意義。",
        "caveat": "重要性不是因果關係；ID 或結果欄位排名很高時要小心洩漏。",
    },
    "residual": {
        "term": "Residual",
        "plain_explanation": "模型預測錯了多少。",
        "technical_definition": "y_true - y_pred。",
        "formula": "實際值 - 預測值",
        "how_to_read": "若誤差呈現規律，表示模型可能漏掉重要因素。",
        "caveat": "殘差需要搭配資料分群或欄位內容才能解釋原因。",
    },
    "return": {
        "term": "報酬率",
        "plain_explanation": "這一期相較上一期上升或下降多少百分比。",
        "technical_definition": "Percentage change。",
        "formula": "(目前值 - 前一期值) / 前一期值",
        "how_to_read": "正值代表上升，負值代表下降。",
        "caveat": "單期報酬率容易受短期事件影響，不應單獨推論長期趨勢。",
    },
    "volatility": {
        "term": "波動率",
        "plain_explanation": "一段期間內數值上下變動的幅度。",
        "technical_definition": "報酬率的滾動標準差。",
        "formula": "rolling_std(return)",
        "how_to_read": "越高代表不確定性越高，風險解讀要更保守。",
        "caveat": "波動率高不一定代表方向不好，只代表變動更大。",
    },
    "moving_average": {
        "term": "移動平均 MA",
        "plain_explanation": "用近期平均值平滑短期起伏，看趨勢方向。",
        "technical_definition": "固定窗口內的 rolling mean。",
        "formula": "rolling_mean(value, window)",
        "how_to_read": "短期線高於長期線常表示近期偏強，反之偏弱。",
        "caveat": "MA 是落後指標，轉折發生後才會反映。",
    },
    "rsi": {
        "term": "RSI",
        "plain_explanation": "用來看短期是否偏熱或偏弱的指標。",
        "technical_definition": "Relative Strength Index。",
        "formula": "100 - 100 / (1 + average_gain / average_loss)",
        "how_to_read": "通常低於 30 偏弱，高於 70 偏熱，中間區間偏中性。",
        "caveat": "RSI 不能單獨作為買賣或營運決策依據。",
    },
    "macd": {
        "term": "MACD",
        "plain_explanation": "用短期與長期趨勢差距觀察動能變化。",
        "technical_definition": "Moving Average Convergence Divergence。",
        "formula": "EMA_fast - EMA_slow",
        "how_to_read": "MACD 高於 signal 代表短期動能較強，低於 signal 則偏弱。",
        "caveat": "盤整期間 MACD 容易頻繁翻轉，需搭配趨勢與波動率。",
    },
    "var": {
        "term": "VaR",
        "plain_explanation": "用歷史資料估計正常極端情況下可能出現的下行風險。",
        "technical_definition": "Value at Risk。",
        "formula": "historical quantile of negative returns",
        "how_to_read": "VaR 越高代表單期下行風險越大。",
        "caveat": "VaR 不是最大損失，也不能預測黑天鵝事件。",
    },
    "forecast": {
        "term": "Forecast",
        "plain_explanation": "依目前資料推估接下來可能的基準情境。",
        "technical_definition": "Time-series baseline projection。",
        "formula": "依模型而異；目前金融預測使用簡化線性趨勢基準。",
        "how_to_read": "只能當情境參考，可信度需看資料品質、模型方法與回測。",
        "caveat": "不構成投資建議，也不保證未來會發生。",
    },
}


def get_metric_terms(keys: list[str] | tuple[str, ...] | None = None) -> list[MetricEntry]:
    if keys is None:
        return [dict(entry) for entry in METRIC_GLOSSARY.values()]
    return [dict(METRIC_GLOSSARY[key]) for key in keys if key in METRIC_GLOSSARY]


def get_metric_entry(key: str) -> MetricEntry | None:
    entry = METRIC_GLOSSARY.get(key)
    return dict(entry) if entry else None


def build_metric_interpretation(
    metric: str,
    value: Any,
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    entry = get_metric_entry(metric) or {
        "term": metric,
        "plain_explanation": "此指標用來輔助理解目前分析結果。",
        "technical_definition": metric,
        "formula": "依分析方法而定",
        "how_to_read": "需搭配資料背景與其他指標一起解讀。",
        "caveat": "單一指標不應作為完整決策依據。",
    }
    return {
        **entry,
        "value": value,
        "this_result_means": _interpret_value(metric, value, context or {}),
    }


def _interpret_value(metric: str, value: Any, context: dict[str, Any]) -> str:
    number = _safe_float(value)
    if metric == "data_completeness" and number is not None:
        if number >= 0.95:
            return "這份資料缺失比例很低，可以先進入分析，但仍要檢查欄位定義。"
        if number >= 0.8:
            return "資料大致可用，但關鍵欄位缺失可能影響模型可信度。"
        return "資料缺失偏多，建議先清理或補齊再做正式結論。"
    if metric == "r2" and number is not None:
        if number >= 0.7:
            return "模型目前具有較高解釋力，可作為初步決策依據。"
        if number >= 0.35:
            return "模型有一定訊號，但仍需要檢查特徵與資料品質。"
        return "模型解釋力偏弱，暫時不適合直接用來做決策。"
    if metric in {"rmse", "mae"} and number is not None:
        target = context.get("target_column") or "目標欄位"
        return f"這代表模型在「{target}」上的典型誤差約為 {number:.4g}，請以原始單位解讀。"
    if metric == "accuracy" and number is not None:
        if number >= 0.8:
            return "分類準確率偏高，但仍需確認各類別是否都有被正確辨識。"
        return "分類準確率仍需改善，請檢查類別不平衡與錯分樣本。"
    if metric == "f1_score" and number is not None:
        if number >= 0.75:
            return "F1-score 表示模型在抓到目標與避免誤判之間已有不錯平衡。"
        return "F1-score 偏低或普通，少數類別可能仍容易被錯分。"
    if metric == "rsi" and number is not None:
        if number >= 70:
            return "RSI 偏高，代表短期可能過熱，應避免只看上升趨勢就下結論。"
        if number <= 30:
            return "RSI 偏低，代表短期可能偏弱或超賣，仍需搭配趨勢確認。"
        return "RSI 接近中性，目前沒有明顯過熱或過弱訊號。"
    if metric == "volatility" and number is not None:
        if number >= 0.05:
            return "近期變動幅度偏高，解讀趨勢與預測時應更保守。"
        if number >= 0.02:
            return "近期變動幅度中等，建議搭配更長期間觀察。"
        return "近期變動幅度偏低，但仍不代表未來風險一定低。"
    if metric == "var" and number is not None:
        return f"以歷史資料估計，正常極端情況下可能有約 {number * 100:.2f}% 等級的單期下行風險。"
    if metric == "forecast":
        return "這是基準情境估計，不應視為確定預測或投資建議。"
    return "這個數字需要搭配資料品質、樣本量與業務背景一起判讀。"


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None
