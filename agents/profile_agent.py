import pandas as pd


from utils.formatters import compact_value


# ==========================================
# FIND DATE COLUMNS
# ==========================================

def find_date_columns(df):

    date_columns = []

    for column in df.columns:

        name = column.lower()

        # Already datetime
        if pd.api.types.is_datetime64_any_dtype(
            df[column]
        ):

            date_columns.append(column)

            continue

        # Date-like column names
        if (
            "date" in name
            or "time" in name
        ):

            converted = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            valid_ratio = (
                converted.notna().mean()
            )

            if valid_ratio >= 0.70:

                date_columns.append(column)

    return date_columns


# ==========================================
# FIND ID COLUMNS
# ==========================================

def find_id_columns(df):

    id_columns = []

    for column in df.columns:

        name = column.lower()

        if (
            name == "id"
            or name.endswith("_id")
            or "order_id" in name
            or "customer_id" in name
            or "transaction_id" in name
            or "invoice_id" in name
        ):

            id_columns.append(column)

    return id_columns


# ==========================================
# CLASSIFY COLUMNS
# ==========================================

def classify_columns(df):

    date_columns = find_date_columns(df)

    id_columns = find_id_columns(df)

    numerical = []
    categorical = []
    boolean = []
    location = []

    for column in df.columns:

        name = column.lower()

        # ------------------------------
        # Location columns
        # ------------------------------

        if name in [
            "latitude",
            "longitude",
            "lat",
            "lon",
            "lng"
        ]:

            location.append(column)
            continue

        # ------------------------------
        # Date
        # ------------------------------

        if column in date_columns:
            continue

        # ------------------------------
        # ID
        # ------------------------------

        if column in id_columns:
            continue

        # ------------------------------
        # Boolean
        # ------------------------------

        if pd.api.types.is_bool_dtype(
            df[column]
        ):

            boolean.append(column)

        # ------------------------------
        # Numeric
        # ------------------------------

        elif pd.api.types.is_numeric_dtype(
            df[column]
        ):

            numerical.append(column)

        # ------------------------------
        # Categorical
        # ------------------------------

        else:

            categorical.append(column)

    return {
        "numerical": numerical,
        "categorical": categorical,
        "date": date_columns,
        "id": id_columns,
        "boolean": boolean,
        "location": location
    }


# ==========================================
# NUMERIC SUMMARY
# ==========================================

def numeric_summary(
    df,
    numerical_columns
):

    summary = {}

    for column in numerical_columns:

        values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        if values.dropna().empty:
            continue

        summary[column] = {
            "total": values.sum(),
            "average": values.mean(),
            "minimum": values.min(),
            "maximum": values.max(),
            "median": values.median()
        }

    return summary


# ==========================================
# CATEGORICAL SUMMARY
# ==========================================

def categorical_summary(
    df,
    categorical_columns
):

    summary = {}

    for column in categorical_columns:

        values = df[column].dropna()

        if values.empty:
            continue

        value_counts = (
            values
            .value_counts()
        )

        summary[column] = {
            "unique": int(
                values.nunique()
            ),
            "top": value_counts.index[0],
            "top_count": int(
                value_counts.iloc[0]
            )
        }

    return summary


# ==========================================
# DATE SUMMARY
# ==========================================

def date_summary(
    df,
    date_columns
):

    summary = {}

    for column in date_columns:

        dates = pd.to_datetime(
            df[column],
            errors="coerce"
        ).dropna()

        if dates.empty:
            continue

        summary[column] = {
            "minimum": dates.min(),
            "maximum": dates.max(),
            "days": (
                dates.max()
                -
                dates.min()
            ).days
        }

    return summary


# ==========================================
# FIND IMPORTANT METRICS
# ==========================================

def find_important_metrics(
    df,
    numerical_columns
):

    metrics = []

    # Prefer business-style names
    preferred_keywords = [
        "sales",
        "revenue",
        "profit",
        "income",
        "cost",
        "amount",
        "price",
        "quantity"
    ]

    # --------------------------------------
    # First pass
    # --------------------------------------

    for column in numerical_columns:

        name = column.lower()

        if any(
            keyword in name
            for keyword in preferred_keywords
        ):

            metrics.append(column)

    # --------------------------------------
    # Second pass
    # --------------------------------------

    for column in numerical_columns:

        if column not in metrics:

            metrics.append(column)

    return metrics[:8]


# ==========================================
# GENERATE PROFILE
# ==========================================

def generate_profile(df):

    if df is None:
        return None

    if df.empty:
        return None

    column_types = classify_columns(
        df
    )

    numerical = column_types[
        "numerical"
    ]

    categorical = column_types[
        "categorical"
    ]

    dates = column_types[
        "date"
    ]

    ids = column_types[
        "id"
    ]

    boolean = column_types[
        "boolean"
    ]

    return {

        "rows": len(df),

        "columns": len(df.columns),

        "column_names": list(
            df.columns
        ),

        "column_types": column_types,

        "numeric_summary":
            numeric_summary(
                df,
                numerical
            ),

        "categorical_summary":
            categorical_summary(
                df,
                categorical
            ),

        "date_summary":
            date_summary(
                df,
                dates
            ),

        "important_metrics":
            find_important_metrics(
                df,
                numerical
            )
    }


# ==========================================
# GENERATE HUMAN READABLE REPORT
# ==========================================

def generate_profile_report(
    profile
):

    if profile is None:
        return []

    report = []

    # ======================================
    # DATASET SIZE
    # ======================================

    report.append(
        f"📋 **Dataset Overview**"
    )

    report.append(
        f"Rows: **{profile['rows']:,}**"
    )

    report.append(
        f"Columns: **{profile['columns']}**"
    )

    # ======================================
    # COLUMN TYPES
    # ======================================

    types = profile[
        "column_types"
    ]

    report.append(
        "\n📊 **Column Types**"
    )

    report.append(
        f"• Numerical: "
        f"{len(types['numerical'])}"
    )

    report.append(
        f"• Categorical: "
        f"{len(types['categorical'])}"
    )

    report.append(
        f"• Date: "
        f"{len(types['date'])}"
    )

    report.append(
        f"• ID: "
        f"{len(types['id'])}"
    )

    report.append(
        f"• Boolean: "
        f"{len(types['boolean'])}"
    )

    # ======================================
    # IMPORTANT METRICS
    # ======================================

    metrics = profile[
        "important_metrics"
    ]

    if metrics:

        report.append(
            "\n💰 **Important Metrics**"
        )

        for metric in metrics:

            report.append(
                f"• {metric}"
            )

    # ======================================
    # NUMERIC SUMMARY
    # ======================================

    numeric = profile[
        "numeric_summary"
    ]

    if numeric:

        report.append(
            "\n📈 **Numeric Summary**"
        )

        for column, data in numeric.items():

            report.append(
                f"• **{column}** — "
                f"Total: "
                f"{compact_value(data['total'])}, "
                f"Average: "
                f"{compact_value(data['average'])}"
            )

    # ======================================
    # CATEGORICAL SUMMARY
    # ======================================

    categorical = profile[
        "categorical_summary"
    ]

    if categorical:

        report.append(
            "\n🏷️ **Categorical Summary**"
        )

        for column, data in (
            categorical.items()
        ):

            report.append(
                f"• **{column}** — "
                f"{data['unique']} unique values, "
                f"most common: "
                f"{data['top']}"
            )

    # ======================================
    # DATE SUMMARY
    # ======================================

    dates = profile[
        "date_summary"
    ]

    if dates:

        report.append(
            "\n📅 **Date Range**"
        )

        for column, data in dates.items():

            start = data[
                "minimum"
            ].strftime(
                "%b %Y"
            )

            end = data[
                "maximum"
            ].strftime(
                "%b %Y"
            )

            report.append(
                f"• **{column}** — "
                f"{start} → {end}"
            )

    return report


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    from analysis.data_loader import (
        load_dataset
    )

    df = load_dataset(
        "data/processed/cleaned_sales.csv"
    )

    profile = generate_profile(
        df
    )

    print(
        "\n=============================="
    )

    print(
        "DATASET PROFILE"
    )

    print(
        "=============================="
    )

    report = generate_profile_report(
        profile
    )

    for line in report:

        print(line)