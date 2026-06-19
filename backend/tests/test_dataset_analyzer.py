import asyncio
from io import BytesIO

import pandas as pd
from fastapi import UploadFile

from app.services import dataset_analyzer
from app.services.dataset_analyzer import (
    analyze_dataframe,
    analyze_multiple_uploaded_datasets,
    merge_dataframes,
    read_uploaded_dataframe,
)


def test_analyze_dataframe_returns_required_summary() -> None:
    df = pd.DataFrame(
        {
            "feature_a": [1, 2, 3],
            "feature_b": [10.5, None, 30.5],
            "category": ["low", "mid", "high"],
        }
    )

    result = analyze_dataframe(df, file_name="unit.csv")

    assert result["file_name"] == "unit.csv"
    assert result["row_count"] == 3
    assert result["column_count"] == 3
    assert result["columns"] == ["feature_a", "feature_b", "category"]
    assert result["missing_values"]["feature_b"] == 1
    assert "feature_a" in result["numeric_summary"]
    assert "feature_b" in result["numeric_summary"]
    assert "category" not in result["numeric_summary"]
    assert "feature_b" in result["recommended_target_columns"]
    assert result["quality_report"]["quality_score"] >= 0
    assert result["schema_fingerprint"]
    assert result["plain_summary"]["headline"]
    assert result["confidence"]["level"] in {"high", "medium", "low"}
    assert result["evidence"]
    assert any(term["term"] == "資料完整度" for term in result["terms"])
    assert result["research_details"]["method"]


def test_merge_dataframes_keeps_union_columns_and_source_metadata() -> None:
    housing_df = pd.DataFrame(
        {
            "area_sqft": [650, 820],
            "price_usd": [325000, 430000],
        }
    )
    stock_df = pd.DataFrame(
        {
            "close": [104.7, 106.1],
            "volume": [1205000, 1380000],
        }
    )

    merged_df, metadata = merge_dataframes(
        [
            ("housing_sample.csv", housing_df),
            ("stock_prices_sample.csv", stock_df),
        ]
    )

    assert merged_df.shape[0] == 4
    assert "area_sqft" in merged_df.columns
    assert "close" in merged_df.columns
    assert metadata["source_file_count"] == 2
    assert metadata["source_file_column"] in merged_df.columns
    assert metadata["source_row_column"] in merged_df.columns
    assert metadata["source_row_counts"]["housing_sample.csv"] == 2
    assert metadata["source_row_counts"]["stock_prices_sample.csv"] == 2
    assert metadata["merge_notes"]
    assert metadata["merge_plan"]["recommended_strategy"] == "separate_analysis"
    assert "separate_analysis" in {
        strategy["key"] for strategy in metadata["merge_plan"]["available_strategies"]
    }


def test_read_uploaded_dataframe_detects_semicolon_csv_delimiter() -> None:
    upload = UploadFile(
        file=BytesIO("player;score\nA;10\nB;12\n".encode("utf-8")),
        filename="semicolon_players.csv",
        size=25,
    )

    df, file_name = asyncio.run(read_uploaded_dataframe(upload))

    assert file_name == "semicolon_players.csv"
    assert df.columns.tolist() == ["player", "score"]
    assert df["score"].tolist() == [10, 12]


def test_read_uploaded_dataframe_accepts_json_lines() -> None:
    payload = (
        '{"date":"2026-01-01","sales":120,"region":"north"}\n'
        '{"date":"2026-01-02","sales":138,"region":"south"}\n'
    ).encode("utf-8")
    upload = UploadFile(
        file=BytesIO(payload),
        filename="records.json",
        size=len(payload),
    )

    df, file_name = asyncio.run(read_uploaded_dataframe(upload))

    assert file_name == "records.json"
    assert df.columns.tolist() == ["date", "sales", "region"]
    assert df["sales"].tolist() == [120, 138]
    assert "JSON Lines" in df.attrs["parser_warnings"][0]


def test_read_uploaded_dataframe_recovers_from_bad_csv_lines_with_warning() -> None:
    upload = UploadFile(
        file=BytesIO(b"player,score\nA,10\nB,12,unexpected\nC,14\n"),
        filename="ragged_players.csv",
        size=43,
    )

    df, _ = asyncio.run(read_uploaded_dataframe(upload))

    assert df["player"].tolist() == ["A", "C"]
    assert df.attrs["parser_warnings"]
    assert "格式異常" in df.attrs["parser_warnings"][0]


def test_analyze_multiple_datasets_isolates_single_file_profile_errors(monkeypatch) -> None:
    upload = UploadFile(
        file=BytesIO(b"player,score\nA,10\n"),
        filename="profile_error.csv",
        size=18,
    )

    def raise_profile_error(_df: pd.DataFrame) -> dict[str, object]:
        raise RuntimeError("unexpected profiling failure")

    monkeypatch.setattr(dataset_analyzer, "_summarize_dataframe", raise_profile_error)

    result = asyncio.run(analyze_multiple_uploaded_datasets([upload]))

    assert result["datasets"][0]["success"] is False
    assert result["datasets"][0]["analysis"] is None
    assert "資料已讀取" in result["datasets"][0]["error"]
