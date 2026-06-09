from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import Any
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[3]
MPL_CACHE_DIR = REPO_ROOT / "generated_outputs" / ".matplotlib"
MPL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fastapi import HTTPException, UploadFile
from sklearn.linear_model import LinearRegression

from app.services.dataset_analyzer import merge_dataframes, read_uploaded_dataframe

CHART_DIR = REPO_ROOT / "generated_outputs" / "charts"
DATA_DIR = REPO_ROOT / "generated_outputs" / "data"
DATE_NAME_HINTS = ("date", "datetime", "timestamp", "time", "day", "日期", "時間", "交易日")
PRICE_NAME_HINTS = (
    "close",
    "adj_close",
    "adjusted_close",
    "adjusted close",
    "price",
    "last",
    "settle",
    "nav",
    "收盤",
    "價格",
    "股價",
    "淨值",
)

FINANCIAL_CHART_TITLES = {
    "price_moving_average": "價格與移動平均",
    "return_volatility": "報酬率與波動率",
    "rsi_macd": "RSI 與 MACD",
    "time_series_forecast": "時間序列預測",
}

plt.rcParams["font.sans-serif"] = [
    "Heiti TC",
    "Arial Unicode MS",
    "Hiragino Sans",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False


async def analyze_uploaded_financial_dataset(
    file: UploadFile,
    date_column: str | None = None,
    price_column: str | None = None,
) -> dict[str, Any]:
    df, file_name = await read_uploaded_dataframe(file)
    return run_financial_analysis(
        df=df,
        file_name=file_name,
        date_column=date_column,
        price_column=price_column,
    )


async def analyze_uploaded_merged_financial_dataset(
    files: list[UploadFile],
    date_column: str | None = None,
    price_column: str | None = None,
) -> dict[str, Any]:
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="合併金融分析至少需要 2 個檔案。")

    loaded_datasets: list[tuple[str, pd.DataFrame]] = []
    skipped_files: list[str] = []

    for file in files:
        file_name = file.filename or "未命名檔案"
        try:
            df, parsed_file_name = await read_uploaded_dataframe(file)
            loaded_datasets.append((parsed_file_name, df))
        except HTTPException as exc:
            skipped_files.append(f"{file_name}：{exc.detail}")

    if len(loaded_datasets) < 2:
        detail = "成功讀取的檔案不足 2 個，無法執行合併金融分析。"
        if skipped_files:
            detail += f" 已略過：{'；'.join(skipped_files)}"
        raise HTTPException(status_code=400, detail=detail)

    merged_df, merge_metadata = merge_dataframes(loaded_datasets)
    result = run_financial_analysis(
        df=merged_df,
        file_name="merged_dataset.csv",
        date_column=date_column,
        price_column=price_column,
    )
    result["notes"] = [
        *merge_metadata["merge_notes"],
        *([f"以下檔案無法讀取，已略過：{'；'.join(skipped_files)}"] if skipped_files else []),
        *result["notes"],
    ]
    return result


def run_financial_analysis(
    df: pd.DataFrame,
    file_name: str,
    date_column: str | None = None,
    price_column: str | None = None,
) -> dict[str, Any]:
    notes: list[str] = []
    resolved_date_column = _detect_date_column(df, date_column)
    resolved_price_column = _detect_price_column(df, price_column, resolved_date_column)

    parsed_dates = _parse_dates(df[resolved_date_column])
    numeric_prices = pd.to_numeric(df[resolved_price_column], errors="coerce")
    working_df = pd.DataFrame(
        {
            "date": parsed_dates,
            "price": numeric_prices,
        }
    ).dropna(subset=["date", "price"])

    if len(working_df) < 6:
        raise HTTPException(
            status_code=400,
            detail="金融分析至少需要 6 筆有效日期與價格資料。",
        )

    duplicate_count = int(working_df["date"].duplicated().sum())
    if duplicate_count > 0:
        notes.append("偵測到相同日期多筆價格，已依日期取平均值進行金融分析。")

    working_df = (
        working_df.groupby("date", as_index=False)["price"]
        .mean()
        .sort_values("date")
        .reset_index(drop=True)
    )

    if len(working_df) < 6:
        raise HTTPException(
            status_code=400,
            detail="依日期彙整後有效資料不足，金融分析至少需要 6 個日期點。",
        )

    indicator_df = _add_financial_indicators(working_df)
    indicator_path = _save_indicator_dataset(indicator_df)
    forecast_points = _forecast_prices(indicator_df)
    charts = _create_financial_charts(indicator_df, forecast_points)
    metrics = _latest_metrics(indicator_df)
    trend_label = _trend_label(metrics)
    summary = _build_summary(
        metrics=metrics,
        trend_label=trend_label,
        date_column=resolved_date_column,
        price_column=resolved_price_column,
        row_count=len(indicator_df),
    )

    notes.append(f"已自動使用日期欄位「{resolved_date_column}」與價格欄位「{resolved_price_column}」。")
    notes.append("MA 使用 5 期與 10 期；波動率使用 5 期滾動標準差；RSI 依資料長度自動調整週期。")

    return {
        "file_name": file_name,
        "date_column": resolved_date_column,
        "price_column": resolved_price_column,
        "row_count_used": int(len(indicator_df)),
        "latest_price": metrics["latest_price"],
        "latest_return": metrics["latest_return"],
        "latest_volatility": metrics["latest_volatility"],
        "latest_rsi": metrics["latest_rsi"],
        "latest_macd": metrics["latest_macd"],
        "latest_macd_signal": metrics["latest_macd_signal"],
        "var_95": metrics["var_95"],
        "var_99": metrics["var_99"],
        "trend_label": trend_label,
        "summary": summary,
        "forecast_points": forecast_points,
        "charts": charts,
        "indicator_path": str(indicator_path.relative_to(REPO_ROOT)),
        "indicator_url": f"/generated_outputs/data/{indicator_path.name}",
        "notes": notes,
    }


def _detect_date_column(df: pd.DataFrame, requested_column: str | None) -> str:
    if requested_column:
        if requested_column not in df.columns:
            raise HTTPException(status_code=400, detail="指定的日期欄位不存在。")
        parsed = _parse_dates(df[requested_column])
        if float(parsed.notna().mean()) < 0.5:
            raise HTTPException(status_code=400, detail="指定的日期欄位無法有效轉換為日期。")
        return requested_column

    scored_columns: list[tuple[float, str]] = []
    for column in df.columns:
        column_name = str(column)
        lowered = column_name.lower()
        has_hint = any(hint in lowered for hint in DATE_NAME_HINTS)
        is_datetime = pd.api.types.is_datetime64_any_dtype(df[column])
        if pd.api.types.is_numeric_dtype(df[column]) and not has_hint and not is_datetime:
            continue

        parsed = _parse_dates(df[column])
        valid_ratio = float(parsed.notna().mean())
        if valid_ratio < 0.5 and not has_hint:
            continue

        score = valid_ratio * 4
        if has_hint:
            score += 3
        if is_datetime:
            score += 2
        scored_columns.append((score, column_name))

    if not scored_columns:
        raise HTTPException(
            status_code=400,
            detail="無法自動偵測日期欄位，請手動指定日期欄位。",
        )

    return max(scored_columns, key=lambda item: item[0])[1]


def _detect_price_column(
    df: pd.DataFrame,
    requested_column: str | None,
    date_column: str,
) -> str:
    if requested_column:
        if requested_column not in df.columns:
            raise HTTPException(status_code=400, detail="指定的價格欄位不存在。")
        prices = pd.to_numeric(df[requested_column], errors="coerce")
        if prices.notna().sum() < 6 or float(prices.notna().mean()) < 0.5:
            raise HTTPException(status_code=400, detail="指定的價格欄位無法有效轉換為數值。")
        return requested_column

    scored_columns: list[tuple[float, str]] = []
    for column in df.columns:
        column_name = str(column)
        if column_name == date_column:
            continue

        prices = pd.to_numeric(df[column], errors="coerce")
        valid_count = int(prices.notna().sum())
        if valid_count < 6:
            continue

        lowered = column_name.lower()
        has_hint = any(hint in lowered for hint in PRICE_NAME_HINTS)
        valid_ratio = float(prices.notna().mean())
        volatility = float(prices.dropna().std() or 0)
        score = valid_ratio * 3 + min(volatility, 1000) / 1000
        if has_hint:
            score += 5
        if "volume" in lowered or "成交量" in lowered:
            score -= 3
        scored_columns.append((score, column_name))

    if not scored_columns:
        raise HTTPException(
            status_code=400,
            detail="無法自動偵測價格欄位，請手動指定可轉換為數值的價格欄位。",
        )

    return max(scored_columns, key=lambda item: item[0])[1]


def _parse_dates(series: pd.Series) -> pd.Series:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Could not infer format.*", category=UserWarning)
        return pd.to_datetime(series, errors="coerce")


def _add_financial_indicators(price_df: pd.DataFrame) -> pd.DataFrame:
    indicator_df = pd.DataFrame(
        {
            "date": price_df["date"].to_numpy(),
            "price": price_df["price"].to_numpy(dtype=float),
        }
    )
    row_count = len(indicator_df)
    short_window = min(5, max(2, row_count // 2))
    long_window = min(10, max(short_window + 1, row_count))
    rsi_period = min(14, max(5, row_count // 2))
    macd_fast = min(12, max(3, row_count // 3))
    macd_slow = min(26, max(macd_fast + 2, row_count))
    macd_signal = min(9, max(3, row_count // 3))

    indicator_df.loc[:, "ma_short"] = indicator_df["price"].rolling(short_window, min_periods=2).mean()
    indicator_df.loc[:, "ma_long"] = indicator_df["price"].rolling(long_window, min_periods=2).mean()
    indicator_df.loc[:, "return"] = indicator_df["price"].pct_change()
    indicator_df.loc[:, "volatility"] = (
        indicator_df["return"].rolling(short_window, min_periods=2).std() * np.sqrt(short_window)
    )

    price_delta = indicator_df["price"].diff()
    gains = price_delta.clip(lower=0)
    losses = -price_delta.clip(upper=0)
    average_gain = gains.rolling(rsi_period, min_periods=2).mean()
    average_loss = losses.rolling(rsi_period, min_periods=2).mean()
    relative_strength = average_gain / average_loss.replace(0, np.nan)
    indicator_df.loc[:, "rsi"] = 100 - (100 / (1 + relative_strength))
    indicator_df.loc[(average_loss == 0) & (average_gain > 0), "rsi"] = 100
    indicator_df.loc[(average_loss == 0) & (average_gain == 0), "rsi"] = 50

    ema_fast = indicator_df["price"].ewm(span=macd_fast, adjust=False).mean()
    ema_slow = indicator_df["price"].ewm(span=macd_slow, adjust=False).mean()
    indicator_df.loc[:, "macd"] = ema_fast - ema_slow
    indicator_df.loc[:, "macd_signal"] = indicator_df["macd"].ewm(span=macd_signal, adjust=False).mean()
    indicator_df.loc[:, "macd_histogram"] = indicator_df["macd"] - indicator_df["macd_signal"]

    return indicator_df


def _save_indicator_dataset(indicator_df: pd.DataFrame) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    indicator_path = DATA_DIR / f"financial_indicators_{uuid4().hex}.csv"
    indicator_df.to_csv(indicator_path, index=False)
    return indicator_path


def _create_financial_charts(
    indicator_df: pd.DataFrame,
    forecast_points: list[dict[str, float | str | None]],
) -> list[dict[str, str]]:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    return [
        _financial_chart_payload("price_moving_average", _create_price_ma_chart(indicator_df)),
        _financial_chart_payload("return_volatility", _create_return_volatility_chart(indicator_df)),
        _financial_chart_payload("rsi_macd", _create_rsi_macd_chart(indicator_df)),
        _financial_chart_payload(
            "time_series_forecast",
            _create_time_series_forecast_chart(indicator_df, forecast_points),
        ),
    ]


def _financial_chart_payload(chart_type: str, chart_path: Path) -> dict[str, str]:
    return {
        "chart_type": chart_type,
        "title": FINANCIAL_CHART_TITLES[chart_type],
        "chart_path": str(chart_path.relative_to(REPO_ROOT)),
        "chart_url": f"/generated_outputs/charts/{chart_path.name}",
    }


def _create_price_ma_chart(indicator_df: pd.DataFrame) -> Path:
    chart_path = CHART_DIR / f"financial_price_ma_{uuid4().hex}.png"
    fig, ax = plt.subplots(figsize=(12, 6.6))
    ax.plot(indicator_df["date"], indicator_df["price"], label="價格", color="#1d4ed8", linewidth=2.5)
    ax.plot(indicator_df["date"], indicator_df["ma_short"], label="MA 短期", color="#0f766e", linewidth=2)
    ax.plot(indicator_df["date"], indicator_df["ma_long"], label="MA 長期", color="#b7791f", linewidth=2)
    ax.set_title("價格與移動平均", fontsize=18)
    ax.set_xlabel("日期", fontsize=13)
    ax.set_ylabel("價格", fontsize=13)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=12)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)
    return chart_path


def _create_return_volatility_chart(indicator_df: pd.DataFrame) -> Path:
    chart_path = CHART_DIR / f"financial_return_volatility_{uuid4().hex}.png"
    fig, ax = plt.subplots(figsize=(12, 6.6))
    ax.plot(
        indicator_df["date"],
        indicator_df["return"] * 100,
        label="單期報酬率 %",
        color="#0f766e",
        linewidth=2,
    )
    ax.plot(
        indicator_df["date"],
        indicator_df["volatility"] * 100,
        label="滾動波動率 %",
        color="#b7791f",
        linewidth=2,
    )
    ax.axhline(0, color="#1d4ed8", linestyle="--", alpha=0.55)
    ax.set_title("報酬率與波動率", fontsize=18)
    ax.set_xlabel("日期", fontsize=13)
    ax.set_ylabel("百分比", fontsize=13)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=12)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)
    return chart_path


def _create_rsi_macd_chart(indicator_df: pd.DataFrame) -> Path:
    chart_path = CHART_DIR / f"financial_rsi_macd_{uuid4().hex}.png"
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    axes[0].plot(indicator_df["date"], indicator_df["rsi"], color="#0f766e", linewidth=2.2)
    axes[0].axhline(70, color="#b7791f", linestyle="--", alpha=0.75)
    axes[0].axhline(30, color="#1d4ed8", linestyle="--", alpha=0.75)
    axes[0].set_title("RSI", fontsize=16)
    axes[0].set_ylabel("RSI", fontsize=12)
    axes[0].grid(alpha=0.25)

    axes[1].plot(indicator_df["date"], indicator_df["macd"], label="MACD", color="#1d4ed8", linewidth=2)
    axes[1].plot(
        indicator_df["date"],
        indicator_df["macd_signal"],
        label="Signal",
        color="#b7791f",
        linewidth=2,
    )
    axes[1].bar(
        indicator_df["date"],
        indicator_df["macd_histogram"],
        label="Histogram",
        color="#0f766e",
        alpha=0.45,
    )
    axes[1].axhline(0, color="#111827", linestyle="--", alpha=0.55)
    axes[1].set_title("MACD", fontsize=16)
    axes[1].set_xlabel("日期", fontsize=12)
    axes[1].set_ylabel("MACD", fontsize=12)
    axes[1].grid(alpha=0.25)
    axes[1].legend(fontsize=11)

    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)
    return chart_path


def _create_time_series_forecast_chart(
    indicator_df: pd.DataFrame,
    forecast_points: list[dict[str, float | str | None]],
) -> Path:
    chart_path = CHART_DIR / f"financial_forecast_{uuid4().hex}.png"
    forecast_df = pd.DataFrame(forecast_points)
    fig, ax = plt.subplots(figsize=(12, 6.6))
    ax.plot(indicator_df["date"], indicator_df["price"], label="歷史價格", color="#1d4ed8", linewidth=2.5)
    if not forecast_df.empty:
        forecast_dates = pd.to_datetime(forecast_df["date"], errors="coerce")
        ax.plot(
            forecast_dates,
            forecast_df["predicted_price"],
            label="線性時間序列預測",
            color="#b7791f",
            linewidth=2.2,
            linestyle="--",
            marker="o",
        )
    ax.set_title("時間序列預測", fontsize=18)
    ax.set_xlabel("日期", fontsize=13)
    ax.set_ylabel("價格", fontsize=13)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=12)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)
    return chart_path


def _forecast_prices(
    indicator_df: pd.DataFrame,
    horizon: int = 5,
) -> list[dict[str, float | str | None]]:
    if len(indicator_df) < 6:
        return []

    x_values = np.arange(len(indicator_df)).reshape(-1, 1)
    y_values = indicator_df["price"].to_numpy(dtype=float)
    model = LinearRegression()
    model.fit(x_values, y_values)

    date_diffs = indicator_df["date"].diff().dropna()
    step = date_diffs.median() if not date_diffs.empty else pd.Timedelta(days=1)
    if pd.isna(step) or step <= pd.Timedelta(0):
        step = pd.Timedelta(days=1)

    future_points: list[dict[str, float | str | None]] = []
    last_date = indicator_df["date"].iloc[-1]
    for offset in range(1, horizon + 1):
        future_index = len(indicator_df) + offset - 1
        predicted_price = float(model.predict(np.array([[future_index]]))[0])
        future_date = last_date + step * offset
        future_points.append(
            {
                "date": future_date.date().isoformat(),
                "predicted_price": round(predicted_price, 6),
            }
        )
    return future_points


def _latest_metrics(indicator_df: pd.DataFrame) -> dict[str, float | None]:
    latest_row = indicator_df.iloc[-1]
    returns = indicator_df["return"].dropna()
    var_95 = _safe_float(max(0.0, -float(returns.quantile(0.05)))) if not returns.empty else None
    var_99 = _safe_float(max(0.0, -float(returns.quantile(0.01)))) if not returns.empty else None
    return {
        "latest_price": _safe_float(latest_row.get("price")),
        "latest_return": _last_valid_float(indicator_df["return"]),
        "latest_volatility": _last_valid_float(indicator_df["volatility"]),
        "latest_rsi": _last_valid_float(indicator_df["rsi"]),
        "latest_macd": _last_valid_float(indicator_df["macd"]),
        "latest_macd_signal": _last_valid_float(indicator_df["macd_signal"]),
        "var_95": var_95,
        "var_99": var_99,
    }


def _last_valid_float(series: pd.Series) -> float | None:
    valid = series.dropna()
    if valid.empty:
        return None
    return _safe_float(valid.iloc[-1])


def _safe_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    return round(float(value), 6)


def _trend_label(metrics: dict[str, float | None]) -> str:
    latest_return = metrics["latest_return"]
    latest_rsi = metrics["latest_rsi"]
    latest_macd = metrics["latest_macd"]
    latest_macd_signal = metrics["latest_macd_signal"]

    if latest_rsi is not None and latest_rsi >= 70:
        return "偏強但可能過熱"
    if latest_rsi is not None and latest_rsi <= 30:
        return "偏弱但可能超賣"
    if (
        latest_return is not None
        and latest_return > 0
        and latest_macd is not None
        and latest_macd_signal is not None
        and latest_macd >= latest_macd_signal
    ):
        return "短線偏多"
    if (
        latest_return is not None
        and latest_return < 0
        and latest_macd is not None
        and latest_macd_signal is not None
        and latest_macd < latest_macd_signal
    ):
        return "短線偏弱"
    return "盤整觀察"


def _build_summary(
    metrics: dict[str, float | None],
    trend_label: str,
    date_column: str,
    price_column: str,
    row_count: int,
) -> list[str]:
    latest_return = _format_percent(metrics["latest_return"])
    latest_volatility = _format_percent(metrics["latest_volatility"])
    latest_rsi = _format_number(metrics["latest_rsi"])
    latest_macd = _format_number(metrics["latest_macd"])
    var_95 = _format_percent(metrics["var_95"])
    var_99 = _format_percent(metrics["var_99"])

    return [
        f"已使用「{date_column}」作為日期欄位、「{price_column}」作為價格欄位，共分析 {row_count} 個有效日期點。",
        f"最新價格為 {_format_number(metrics['latest_price'])}，最新報酬率 {latest_return}，滾動波動率 {latest_volatility}。",
        f"RSI 為 {latest_rsi}，MACD 為 {latest_macd}，目前訊號判斷為「{trend_label}」。",
        f"歷史法 VaR 估計：95% 信心水準約 {var_95}，99% 信心水準約 {var_99}。",
    ]


def _format_number(value: float | None) -> str:
    if value is None:
        return "無法計算"
    return f"{value:,.4f}".rstrip("0").rstrip(".")


def _format_percent(value: float | None) -> str:
    if value is None:
        return "無法計算"
    return f"{value * 100:.2f}%"
