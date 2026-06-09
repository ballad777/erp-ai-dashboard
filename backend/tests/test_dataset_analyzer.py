import pandas as pd

from app.services.dataset_analyzer import analyze_dataframe, merge_dataframes


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
