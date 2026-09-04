import pandas as pd
from utils.formatters import compact_value

# ==========================================
# DATA QUALITY AGENT
# ==========================================


# ------------------------------------------
# COLUMN TYPE DETECTION
# ------------------------------------------

def detect_column_types(df):

    numerical = []
    categorical = []
    date_columns = []
    id_columns = []
    boolean_columns = []

    for column in df.columns:

        name = column.lower()

        # ------------------------------
        # ID
        # ------------------------------

        if (
            name == "id"
            or name.endswith("_id")
            or "order_id" in name
            or "customer_id" in name
            or "transaction_id" in name
            or "invoice_id" in name
        ):

            id_columns.append(column)

            continue

        # ------------------------------
        # Boolean
        # ------------------------------

        if pd.api.types.is_bool_dtype(
            df[column]
        ):

            boolean_columns.append(column)

            continue

        # ------------------------------
        # Date
        # ------------------------------

        if (
            pd.api.types.is_datetime64_any_dtype(
                df[column]
            )
            or "date" in name
            or "time" in name
        ):

            date_columns.append(column)

            continue

        # ------------------------------
        # Numeric
        # ------------------------------

        if pd.api.types.is_numeric_dtype(
            df[column]
        ):

            numerical.append(column)

            continue

        # ------------------------------
        # Categorical
        # ------------------------------

        categorical.append(column)

    return {
        "numerical": numerical,
        "categorical": categorical,
        "date": date_columns,
        "id": id_columns,
        "boolean": boolean_columns
    }


# ==========================================
# MISSING VALUE CHECK
# ==========================================

def check_missing_values(df):

    missing = df.isnull().sum()

    missing = missing[
        missing > 0
    ]

    total_missing = int(
        missing.sum()
    )

    return {
        "total": total_missing,
        "columns": missing.to_dict()
    }


# ==========================================
# DUPLICATE CHECK
# ==========================================

def check_duplicates(df):

    duplicate_count = int(
        df.duplicated().sum()
    )

    return duplicate_count


# ==========================================
# INVALID DATE CHECK
# ==========================================

def check_invalid_dates(
    df,
    date_columns
):

    invalid_dates = {}

    for column in date_columns:

        converted = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        # Only count values that were originally
        # non-null but became NaT

        invalid = (
            converted.isna()
            &
            df[column].notna()
        )

        count = int(
            invalid.sum()
        )

        if count > 0:

            invalid_dates[column] = count

    return invalid_dates


# ==========================================
# NEGATIVE VALUE CHECK
# ==========================================

def check_negative_values(
    df,
    numerical_columns
):

    negative_values = {}

    for column in numerical_columns:

        count = int(
            (
                pd.to_numeric(
                    df[column],
                    errors="coerce"
                ) < 0
            ).sum()
        )

        if count > 0:

            negative_values[column] = count

    return negative_values


# ==========================================
# CONSTANT COLUMN CHECK
# ==========================================

def check_constant_columns(df):

    constant_columns = []

    for column in df.columns:

        if df[column].nunique(
            dropna=False
        ) <= 1:

            constant_columns.append(
                column
            )

    return constant_columns


# ==========================================
# HIGH CARDINALITY CHECK
# ==========================================

def check_high_cardinality(
    df,
    categorical_columns
):

    high_cardinality = {}

    if len(df) == 0:
        return high_cardinality

    for column in categorical_columns:

        unique_count = df[column].nunique(
            dropna=True
        )

        ratio = (
            unique_count / len(df)
        )

        # More than 90% unique values
        if ratio >= 0.90:

            high_cardinality[column] = (
                unique_count
            )

    return high_cardinality


# ==========================================
# DATA TYPE CHECK
# ==========================================

def check_data_types(df):

    return {
        column: str(df[column].dtype)
        for column in df.columns
    }


# ==========================================
# QUALITY SCORE
# ==========================================

def calculate_quality_score(
    df,
    missing_result,
    duplicate_count,
    invalid_dates,
    negative_values,
    constant_columns
):

    score = 100

    # --------------------------------------
    # Missing values
    # --------------------------------------

    if missing_result["total"] > 0:

        missing_ratio = (
            missing_result["total"]
            /
            (len(df) * len(df.columns))
        )

        if missing_ratio >= 0.20:

            score -= 25

        elif missing_ratio >= 0.10:

            score -= 15

        elif missing_ratio > 0:

            score -= 10

    # --------------------------------------
    # Duplicates
    # --------------------------------------

    if duplicate_count > 0:

        duplicate_ratio = (
            duplicate_count
            /
            len(df)
        )

        if duplicate_ratio >= 0.10:

            score -= 20

        elif duplicate_ratio >= 0.05:

            score -= 15

        else:

            score -= 10

    # --------------------------------------
    # Invalid dates
    # --------------------------------------

    invalid_date_count = sum(
        invalid_dates.values()
    )

    if invalid_date_count > 0:

        score -= 15

    # --------------------------------------
    # Negative values
    # --------------------------------------

    negative_count = sum(
        negative_values.values()
    )

    if negative_count > 0:

        score -= 10

    # --------------------------------------
    # Constant columns
    # --------------------------------------

    if constant_columns:

        score -= min(
            10,
            len(constant_columns) * 2
        )

    # --------------------------------------
    # Keep score between 0 and 100
    # --------------------------------------

    score = max(
        0,
        min(100, score)
    )

    return score


# ==========================================
# QUALITY LABEL
# ==========================================

def quality_label(score):

    if score >= 90:

        return "Excellent"

    elif score >= 75:

        return "Good"

    elif score >= 60:

        return "Needs Attention"

    else:

        return "Poor"


# ==========================================
# MAIN QUALITY ANALYSIS
# ==========================================

def analyze_data_quality(df):

    if df is None:

        return None

    if df.empty:

        return None

    # --------------------------------------
    # Column types
    # --------------------------------------

    column_types = detect_column_types(
        df
    )

    numerical = column_types[
        "numerical"
    ]

    categorical = column_types[
        "categorical"
    ]

    date_columns = column_types[
        "date"
    ]

    # --------------------------------------
    # Checks
    # --------------------------------------

    missing_result = (
        check_missing_values(df)
    )

    duplicate_count = (
        check_duplicates(df)
    )

    invalid_dates = (
        check_invalid_dates(
            df,
            date_columns
        )
    )

    negative_values = (
        check_negative_values(
            df,
            numerical
        )
    )

    constant_columns = (
        check_constant_columns(df)
    )

    high_cardinality = (
        check_high_cardinality(
            df,
            categorical
        )
    )

    data_types = (
        check_data_types(df)
    )

    # --------------------------------------
    # Score
    # --------------------------------------

    score = calculate_quality_score(
        df,
        missing_result,
        duplicate_count,
        invalid_dates,
        negative_values,
        constant_columns
    )

    return {

        "rows": len(df),

        "columns": len(df.columns),

        "column_types": column_types,

        "missing": missing_result,

        "duplicates": duplicate_count,

        "invalid_dates": invalid_dates,

        "negative_values": negative_values,

        "constant_columns": constant_columns,

        "high_cardinality": high_cardinality,

        "data_types": data_types,

        "score": score,

        "label": quality_label(score)
    }


# ==========================================
# GENERATE HUMAN READABLE REPORT
# ==========================================

def generate_quality_report(
    quality_result
):

    if quality_result is None:

        return []

    report = []

    score = quality_result["score"]

    label = quality_result["label"]

    # --------------------------------------
    # Overall
    # --------------------------------------

    report.append(
        f"📊 Data Quality Score: "
        f"**{score}/100 — {label}**"
    )

    # --------------------------------------
    # Missing
    # --------------------------------------

    missing = quality_result[
        "missing"
    ]

    if missing["total"] == 0:

        report.append(
            "✅ No missing values detected."
        )

    else:

        report.append(
            f"⚠️ **{missing['total']} "
            f"missing values** detected."
        )

        for column, count in (
            missing["columns"].items()
        ):

            report.append(
                f"   • {column}: "
                f"{count} missing"
            )

    # --------------------------------------
    # Duplicates
    # --------------------------------------

    duplicates = quality_result[
        "duplicates"
    ]

    if duplicates == 0:

        report.append(
            "✅ No duplicate rows detected."
        )

    else:

        report.append(
            f"⚠️ **{duplicates} duplicate "
            f"rows** detected."
        )

    # --------------------------------------
    # Invalid dates
    # --------------------------------------

    invalid_dates = quality_result[
        "invalid_dates"
    ]

    if not invalid_dates:

        report.append(
            "✅ No invalid dates detected."
        )

    else:

        for column, count in (
            invalid_dates.items()
        ):

            report.append(
                f"⚠️ **{column}** contains "
                f"{count} invalid dates."
            )

    # --------------------------------------
    # Negative values
    # --------------------------------------

    negative_values = quality_result[
        "negative_values"
    ]

    if not negative_values:

        report.append(
            "✅ No negative numeric values detected."
        )

    else:

        for column, count in (
            negative_values.items()
        ):

            report.append(
                f"⚠️ **{column}** contains "
                f"{count} negative values."
            )

    # --------------------------------------
    # Constant columns
    # --------------------------------------

    constant_columns = quality_result[
        "constant_columns"
    ]

    if not constant_columns:

        report.append(
            "✅ No constant columns detected."
        )

    else:

        report.append(
            "⚠️ Constant columns: "
            + ", ".join(
                constant_columns
            )
        )

    # --------------------------------------
    # High cardinality
    # --------------------------------------

    high_cardinality = quality_result[
        "high_cardinality"
    ]

    if high_cardinality:

        report.append(
            "⚠️ High-cardinality columns: "
            + ", ".join(
                high_cardinality.keys()
            )
        )

    else:

        report.append(
            "✅ No suspicious "
            "high-cardinality columns."
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

    result = analyze_data_quality(
        df
    )

    print(
        "\n=============================="
    )

    print(
        "DATA QUALITY REPORT"
    )

    print(
        "=============================="
    )

    report = generate_quality_report(
        result
    )

    for line in report:

        print(line)