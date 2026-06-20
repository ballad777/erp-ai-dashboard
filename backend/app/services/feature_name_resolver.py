from __future__ import annotations

from typing import Any

from sklearn.pipeline import Pipeline


class FeatureNameResolver:
    """Resolve model feature names back to human-readable source columns."""

    def resolve_pipeline(self, model: Pipeline) -> list[str]:
        preprocessor = model.named_steps.get("preprocess")
        if preprocessor is None:
            return []
        return self.resolve_preprocessor(preprocessor)

    def resolve_preprocessor(self, preprocessor: Any) -> list[str]:
        names: list[str] = []
        transformers = getattr(preprocessor, "transformers_", None)
        if not transformers:
            return self._safe_get_feature_names(preprocessor, [])

        for transformer_name, transformer, columns in transformers:
            if transformer == "drop":
                continue
            source_columns = self._normalize_columns(columns)
            if transformer == "passthrough":
                names.extend(source_columns)
                continue
            raw_names = self._safe_get_feature_names(transformer, source_columns)
            if raw_names:
                names.extend(self._clean_name(name, source_columns) for name in raw_names)
            else:
                names.extend(source_columns)

        return [name for name in names if name and not self._looks_unresolved(name)]

    @staticmethod
    def _normalize_columns(columns: Any) -> list[str]:
        if columns is None:
            return []
        if isinstance(columns, slice):
            return []
        if isinstance(columns, (str, int)):
            return [str(columns)]
        try:
            return [str(column) for column in list(columns)]
        except TypeError:
            return [str(columns)]

    @staticmethod
    def _safe_get_feature_names(transformer: Any, source_columns: list[str]) -> list[str]:
        try:
            if source_columns:
                return [str(name) for name in transformer.get_feature_names_out(source_columns)]
            return [str(name) for name in transformer.get_feature_names_out()]
        except Exception:  # noqa: BLE001 - resolver must fail closed so charts can be skipped.
            return []

    def _clean_name(self, raw_name: str, source_columns: list[str]) -> str:
        name = raw_name.split("__", 1)[-1]
        if name in source_columns:
            return name

        for column in sorted(source_columns, key=len, reverse=True):
            prefix = f"{column}_"
            if name.startswith(prefix):
                value = name[len(prefix):]
                return f"{column}={self._humanize_category(value)}"

        return name

    @staticmethod
    def _humanize_category(value: str) -> str:
        if value == "infrequent_sklearn":
            return "其他低頻類別"
        return value

    @staticmethod
    def _looks_unresolved(name: str) -> bool:
        lowered = name.strip().lower()
        if lowered.startswith("feature_") and lowered.removeprefix("feature_").isdigit():
            return True
        if lowered.startswith("column_") and lowered.removeprefix("column_").isdigit():
            return True
        if lowered.startswith("x") and lowered[1:].isdigit():
            return True
        if lowered.startswith("欄位") and lowered.replace("欄位", "").strip().isdigit():
            return True
        return False
