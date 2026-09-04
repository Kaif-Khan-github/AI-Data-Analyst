"""Schema detection for heterogeneous CSV and Excel datasets."""

import re

import pandas as pd


METRIC_ALIASES = {
    "sales": ["sales", "revenue", "revenue amount", "purchase amount", "purchase amount usd", "amount", "price", "income", "value", "saleprice", "sale price", "monthlyincome", "monthly income"],
    "profit": ["profit", "profit amount", "net profit", "earnings"],
    "quantity": ["quantity", "qty", "units", "number of units"],
}
GROUP_ALIASES = {
    "product": ["product name", "product", "item purchased", "item name", "item"],
    "category": ["product category", "category", "type", "segment", "department", "genre", "class", "style", "housestyle", "house style"],
    "region": ["region", "location", "city", "state", "country", "territory", "neighborhood", "area", "address"],
    "customer": ["customer id", "customer", "user id", "user", "client", "member"],
}
DATE_ALIASES = ["order date", "purchase date", "transaction date", "invoice date", "created date", "date", "timestamp", "time"]


def _normalise(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def _parse_ratio(series):
    values = series.dropna()
    if values.empty:
        return 0.0
    cleaned = (values.astype(str).str.replace(r"[₹$£€,]", "", regex=True)
               .str.replace(r"^\((.*)\)$", r"-\1", regex=True).str.strip())
    return float(pd.to_numeric(cleaned, errors="coerce").notna().mean())


def _best_match(columns, aliases, excluded=None):
    excluded = excluded or set()
    candidates = [column for column in columns if column not in excluded]
    names = {column: _normalise(column) for column in candidates}
    for alias in aliases:
        alias = _normalise(alias)
        for column in candidates:
            if names[column] == alias:
                return column
    for alias in aliases:
        alias = _normalise(alias)
        for column in candidates:
            if re.search(rf"(?:^| ){re.escape(alias)}(?:$| )", names[column]):
                return column
    for alias in aliases:
        alias = _normalise(alias)
        for column in candidates:
            if alias and alias in names[column]:
                return column
    return None


def detect_schema(df):
    """Return semantic column metadata without requiring any specific fields."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("detect_schema expects a pandas DataFrame")

    columns = list(df.columns)
    numeric_columns = [c for c in columns if pd.api.types.is_numeric_dtype(df[c])]
    date_columns = [c for c in columns if pd.api.types.is_datetime64_any_dtype(df[c])]

    for column in columns:
        if column in date_columns:
            continue
        name = _normalise(column)
        if any(alias in name for alias in DATE_ALIASES):
            sample = df[column].dropna().head(20)
            if (not pd.api.types.is_numeric_dtype(df[column]) and not sample.empty
                    and pd.to_datetime(sample, errors="coerce").notna().mean() >= 0.7):
                date_columns.append(column)

    id_columns, text_columns = [], []
    for column in columns:
        name = _normalise(column)
        series = df[column]
        unique_ratio = series.nunique(dropna=True) / max(series.notna().sum(), 1)
        if re.search(r"(?:^| )(?:id|identifier|key|code|number)(?:$| )", name):
            id_columns.append(column)
        elif any(word in name for word in ("description", "comment", "review", "text")):
            text_columns.append(column)
        elif pd.api.types.is_object_dtype(series) and unique_ratio > 0.8 and series.astype(str).str.len().mean() > 40:
            text_columns.append(column)

    for column in columns:
        if column not in numeric_columns and _parse_ratio(df[column]) >= 0.9:
            numeric_columns.append(column)

    categorical_columns = [
        c for c in columns
        if c not in date_columns and c not in text_columns and c not in id_columns
        and (pd.api.types.is_object_dtype(df[c]) or pd.api.types.is_string_dtype(df[c])
             or isinstance(df[c].dtype, pd.CategoricalDtype))
    ]

    metrics = {
        key: _best_match(numeric_columns, aliases, set(id_columns))
        for key, aliases in METRIC_ALIASES.items()
    }
    groups = {}
    for key, aliases in GROUP_ALIASES.items():
        candidates = categorical_columns + ([c for c in id_columns] if key == "customer" else [])
        groups[key] = _best_match(candidates, aliases)

    primary_metric = metrics["sales"] or next(
        (c for c in numeric_columns if c not in id_columns and _normalise(c) not in {"year", "month", "quarter"}),
        None,
    )
    date_column = _best_match(date_columns, DATE_ALIASES) if date_columns else None

    return {
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "date_columns": date_columns,
        "id_columns": id_columns,
        "text_columns": text_columns,
        "metrics": metrics,
        "groups": groups,
        "primary_metric": primary_metric,
        "date_column": date_column,
    }
