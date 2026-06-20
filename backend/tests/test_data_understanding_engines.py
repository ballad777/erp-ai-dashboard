import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.services.data_understanding import build_dataset_understanding
from app.services.dataset_analyzer import analyze_dataframe
from app.services.feature_name_resolver import FeatureNameResolver


def _iris_frame() -> pd.DataFrame:
    species = ["Iris-setosa"] * 50 + ["Iris-versicolor"] * 50 + ["Iris-virginica"] * 50
    rows = []
    for index, label in enumerate(species):
        group = index // 50
        rows.append(
            {
                "SepalLengthCm": 5.0 + group * 0.7 + (index % 10) * 0.03,
                "SepalWidthCm": 3.5 - group * 0.25 + (index % 7) * 0.02,
                "PetalLengthCm": 1.4 + group * 1.8 + (index % 8) * 0.04,
                "PetalWidthCm": 0.2 + group * 0.75 + (index % 6) * 0.02,
                "Species": label,
            }
        )
    return pd.DataFrame(rows)


def test_iris_dataset_understanding_and_top_targets() -> None:
    understanding = build_dataset_understanding(_iris_frame(), file_name="Iris.csv")

    assert understanding["primary_domain"]["key"] == "iris_classification"
    assert understanding["primary_domain"]["label"] == "鳶尾花分類資料集"
    assert understanding["target_recommendations"][0]["column"] == "Species"
    assert understanding["target_recommendations"][0]["task_type"] == "classification"
    assert understanding["target_recommendations"][0]["confidence_score"] == 98
    assert [item["column"] for item in understanding["target_recommendations"][:3]] == [
        "Species",
        "PetalLengthCm",
        "PetalWidthCm",
    ]
    assert len(understanding["target_recommendations"]) == 5
    assert understanding["confidence_breakdown"]["components"][0]["label"] == "資料完整度"
    assert "金融分析" in " ".join(understanding["dataset_story"]["cannot_answer"])


def test_iris_analysis_uses_readable_story_not_general_table() -> None:
    summary = analyze_dataframe(_iris_frame(), file_name="Iris.csv")

    assert summary["dataset_type"]["label"] == "鳶尾花分類資料集"
    assert summary["recommended_target_columns"][0] == "Species"
    assert "一般表格資料" not in summary["plain_summary"]["headline"]
    assert "鳶尾花" in summary["plain_summary"]["what_happened"]
    assert summary["confidence_breakdown"]["formula"]


def test_feature_name_resolver_preserves_one_hot_names() -> None:
    df = pd.DataFrame(
        {
            "Amount": [10, 20, 30, 40],
            "Country": ["USA", "Taiwan", "Japan", "USA"],
        }
    )
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", Pipeline([("scaler", StandardScaler())]), ["Amount"]),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), ["Country"]),
        ]
    )
    preprocessor.fit(df)

    names = FeatureNameResolver().resolve_preprocessor(preprocessor)

    assert "Amount" in names
    assert "Country=USA" in names
    assert "Country=Taiwan" in names
    assert not any(name.startswith(("feature_", "column_", "欄位")) for name in names)
