import pandas as pd
from utils.formatters import compact_value



# ==========================================
# FIND DATE COLUMN
# ==========================================

def find_date_column(df):

    # First check columns containing "date"
    for col in df.columns:

        if "date" in col.lower():

            return col

    # Then check actual datetime columns
    for col in df.columns:

        if pd.api.types.is_datetime64_any_dtype(
            df[col]
        ):

            return col

    return None


# ==========================================
# CHECK IF COLUMN IS AN ID
# ==========================================

def is_id_column(column):

    name = column.lower()

    id_keywords = [
        "id",
        "_id",
        "order_id",
        "customer_id",
        "product_id",
        "transaction_id",
        "invoice_id"
    ]

    for keyword in id_keywords:

        if (
            name == keyword
            or name.endswith(keyword)
            or keyword in name
        ):
            return True

    return False


# ==========================================
# CHECK IF COLUMN IS LOCATION
# ==========================================

def is_location_column(column):

    name = column.lower()

    location_keywords = [
        "latitude",
        "longitude",
        "lat",
        "lon",
        "lng"
    ]

    return any(
        keyword in name
        for keyword in location_keywords
    )


# ==========================================
# FIND BUSINESS NUMERIC COLUMNS
# ==========================================

def find_business_numeric_columns(df):

    columns = []

    for col in df.columns:

        # Ignore IDs
        if is_id_column(col):
            continue

        # Ignore latitude / longitude
        if is_location_column(col):
            continue

        # Only numeric columns
        if pd.api.types.is_numeric_dtype(
            df[col]
        ):

            columns.append(col)

    return columns


# ==========================================
# DETECT MONTHLY ANOMALIES
# ==========================================

def detect_monthly_anomalies(
    df,
    metric,
    date_column
):

    if metric not in df.columns:
        return None

    if date_column not in df.columns:
        return None

    data = df.copy()

    # --------------------------------------
    # Convert date
    # --------------------------------------

    data[date_column] = pd.to_datetime(
        data[date_column],
        errors="coerce"
    )

    # --------------------------------------
    # Convert metric
    # --------------------------------------

    data[metric] = pd.to_numeric(
        data[metric],
        errors="coerce"
    )

    data = data.dropna(
        subset=[
            date_column,
            metric
        ]
    )

    if data.empty:
        return None

    # --------------------------------------
    # Monthly aggregation
    # --------------------------------------

    monthly = (
        data.groupby(
            data[date_column].dt.to_period("M")
        )[metric]
        .sum()
        .sort_index()
    )

    # Need enough months
    if len(monthly) < 4:
        return None

    # --------------------------------------
    # IQR
    # --------------------------------------

    q1 = monthly.quantile(0.25)
    q3 = monthly.quantile(0.75)

    iqr = q3 - q1

    if iqr == 0:
        return None

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # --------------------------------------
    # Find anomalies
    # --------------------------------------

    anomalies = monthly[
        (monthly < lower_bound)
        |
        (monthly > upper_bound)
    ]

    if anomalies.empty:
        return None

    return {
        "metric": metric,
        "monthly_data": monthly,
        "anomalies": anomalies,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound
    }


# ==========================================
# GENERATE ANOMALY INSIGHTS
# ==========================================

def generate_anomaly_insights(
    df,
    selected_metric=None
):

    if df is None:
        return []

    if df.empty:
        return []

    # --------------------------------------
    # Find date
    # --------------------------------------

    date_column = find_date_column(df)

    if date_column is None:
        return []

    # --------------------------------------
    # Determine metrics
    # --------------------------------------

    if selected_metric:

        if selected_metric not in df.columns:
            return []

        metrics = [selected_metric]

    else:

        metrics = (
            find_business_numeric_columns(df)
        )

    insights = []

    # --------------------------------------
    # Analyze metrics
    # --------------------------------------

    for metric in metrics:

        result = detect_monthly_anomalies(
            df,
            metric,
            date_column
        )

        if result is None:
            continue

        monthly = result["monthly_data"]
        anomalies = result["anomalies"]

        average = monthly.mean()

        for period, value in anomalies.items():

            difference = value - average

            if average != 0:

                difference_percentage = (
                    difference /
                    abs(average)
                ) * 100

            else:

                difference_percentage = 0

            if value > result["upper_bound"]:

                anomaly_type = "high"

            else:

                anomaly_type = "low"

            insights.append(
                {
                    "metric": metric,
                    "period": str(period),
                    "value": value,
                    "value_formatted":
                        compact_value(value),
                    "average": average,
                    "average_formatted":
                        compact_value(average),
                    "difference_percentage":
                        difference_percentage,
                    "type": anomaly_type
                }
            )

    return insights


# ==========================================
# FORMAT ANOMALIES
# ==========================================

def format_anomaly_insights(
    anomaly_results
):

    formatted = []

    if not anomaly_results:
        return formatted

    for anomaly in anomaly_results:

        metric = anomaly["metric"]
        period = anomaly["period"]
        value = anomaly["value_formatted"]
        average = anomaly["average_formatted"]

        percentage = abs(
            anomaly["difference_percentage"]
        )

        if anomaly["type"] == "high":

            formatted.append(
                f"🚨 **{metric} anomaly detected** — "
                f"{period} recorded **{value}**, "
                f"which was significantly higher "
                f"than the normal average of "
                f"**{average}** "
                f"({percentage:.1f}% difference)."
            )

        else:

            formatted.append(
                f"📉 **{metric} anomaly detected** — "
                f"{period} recorded **{value}**, "
                f"which was significantly lower "
                f"than the normal average of "
                f"**{average}** "
                f"({percentage:.1f}% difference)."
            )

    return formatted