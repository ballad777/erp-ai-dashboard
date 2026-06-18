from app.services.insight_narrative import build_dataset_brief


def _summary(columns: list[str], numeric_columns: list[str]) -> dict[str, object]:
    return {
        "row_count": 892,
        "column_count": len(columns),
        "columns": columns,
        "numeric_summary": {column: {"mean": 1} for column in numeric_columns},
        "recommended_target_columns": ["Price"] if "Price" in columns else [],
        "quality_report": {
            "quality_score": 81,
            "issues": [],
            "missing": {"total_cells": 0, "columns": []},
            "date_frequency": [],
        },
    }


def test_car_sales_dataset_is_not_labeled_as_real_estate() -> None:
    brief = build_dataset_brief(
        _summary(
            ["name", "company", "year", "Price", "kms_driven", "fuel_type"],
            ["year", "Price", "kms_driven"],
        )
    )

    headline = str(brief["plain_summary"]["headline"])

    assert "汽車銷售資料" in headline
    assert "房價" not in headline
    assert "不動產" not in headline


def test_generic_price_dataset_stays_conservative_without_real_estate_evidence() -> None:
    brief = build_dataset_brief(
        _summary(
            ["item", "category", "Price", "quantity"],
            ["Price", "quantity"],
        )
    )

    headline = str(brief["plain_summary"]["headline"])

    assert "房價" not in headline
    assert "不動產" not in headline
