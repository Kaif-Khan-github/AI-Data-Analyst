import pandas as pd
from agents.anomaly_agent import generate_anomaly_insights

def execute_query(df, intent):

    metric = intent.get("metric")
    group_by = intent.get("group_by")
    query_type = intent.get("type")
    limit = intent.get("limit")

    # --------------------------------
    # FIX PLURALS & SPELLING (EASIEST WAY)
    # --------------------------------
    COLUMN_MAP = {
        "cities": "City",
        "states": "State",
        "regions": "Region",
        "products": "Product",
        "categories": "Category",
        "profits": "Profit",
        "quantities": "Quantity"
    }

    # If the AI captured a plural word, swap it for the real column name
    if group_by and str(group_by).lower() in COLUMN_MAP:
        group_by = COLUMN_MAP[str(group_by).lower()]
        # Update the intent so the visualization agent gets the fixed name too
        intent["group_by"] = group_by 

    if metric and str(metric).lower() in COLUMN_MAP:
        metric = COLUMN_MAP[str(metric).lower()]
        intent["metric"] = metric

    # --------------------------------
    # RELATIONSHIP ANALYSIS (Your existing code starts here...)
    # --------------------------------
    # --------------------------------
    # RELATIONSHIP ANALYSIS
    # --------------------------------

    if query_type == "relationship":

        x_column = intent.get("x_column")
        y_column = intent.get("y_column")

        # Check columns
        if not x_column or not y_column:
            return {
                "error": "relationship_columns_missing"
            }

        if x_column not in df.columns:
            return {
                "error": f"Column '{x_column}' was not found."
            }

        if y_column not in df.columns:
            return {
                "error": f"Column '{y_column}' was not found."
            }

        # Check numeric
        x_numeric = pd.api.types.is_numeric_dtype(
            df[x_column]
        )

        y_numeric = pd.api.types.is_numeric_dtype(
            df[y_column]
        )

        # Non-numeric relationship
        if not x_numeric or not y_numeric:
            return {
                "error": "non_numeric_relationship",
                "x_column": x_column,
                "y_column": y_column,
                "x_numeric": x_numeric,
                "y_numeric": y_numeric
            }

        # Valid relationship data
        result = df[
            [x_column, y_column]
        ].copy()

        # Remove missing values
        result = result.dropna(
            subset=[x_column, y_column]
        )

        return result

    # --------------------------------
    # TREND ANALYSIS
    # --------------------------------

    if query_type == "trend":

        if metric is None or metric not in df.columns:
            return None

        date_columns = [
            col
            for col in df.columns
            if "date" in col.lower()
        ]

        if not date_columns:
            return None

        date_column = date_columns[0]

        df = df.copy()

        df[date_column] = pd.to_datetime(
            df[date_column],
            errors="coerce"
        )

        df = df.dropna(
            subset=[date_column]
        )

        result = (
            df.groupby(
                df[date_column].dt.to_period("M")
            )[metric]
            .sum()
            .sort_index()
        )

        result.index = result.index.astype(str)

        return result


    # --------------------------------
    # DISTRIBUTION ANALYSIS
    # --------------------------------

    if query_type == "distribution":

        if metric is None or metric not in df.columns:
            return {"error": f"Could not find numeric column '{metric}'"}

        # Return just the numeric column as a DataFrame for the histogram
        result = df[[metric]].copy()
        result = result.dropna()
        
        return result

    # --------------------------------
    # ANOMALY ANALYSIS
    # --------------------------------

    if query_type == "anomaly":

        if metric is None or metric not in df.columns:
            return None
        anomaly_results = generate_anomaly_insights(
            df,
            selected_metric=metric
        )

        return anomaly_results


    
    # --------------------------------
    # VALIDATE METRIC
    # --------------------------------

    if metric is None or metric not in df.columns:
        return None

    # --------------------------------
    # SINGLE VALUE
    # --------------------------------

    if group_by is None:

        return df[metric].sum()

    # --------------------------------
    # VALIDATE GROUP
    # --------------------------------

    if group_by not in df.columns:
        return None

    # --------------------------------
    # GROUPED DATA
    # --------------------------------

    grouped = (
        df.groupby(group_by)[metric]
        .sum()
        .sort_values(ascending=False)
    )

    # --------------------------------
    # TOP
    # --------------------------------

    if query_type == "top":

        if limit is None:
            limit = 1

        return grouped.head(limit)

    # --------------------------------
    # BOTTOM
    # --------------------------------

    if query_type == "bottom":

        if limit is None:
            limit = 1

        return grouped.sort_values().head(limit)

    # --------------------------------
    # GROUP
    # --------------------------------

    if query_type == "group":

        return grouped

    # --------------------------------
    # SHARE
    # --------------------------------

    # --------------------------------
    # SHARE
    # --------------------------------
    if query_type == "share":
        # Return the raw numbers (like 2.5M). 
        # Plotly and the Insights tool will calculate the % automatically!
        return grouped

    return None