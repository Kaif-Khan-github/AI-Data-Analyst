def understand_query(query, default_metric=None):

    query = query.lower().strip()

    intent = {
        "type": "unknown",
        "metric": None,
        "group_by": None,
        "limit": None,
        "time_based": False,
        "share": False
    }



# -----------------------------
# Detect chart type
# -----------------------------

    intent["chart_type"] = None
    intent["x_column"] = None
    intent["y_column"] = None


# --------------------------------
# Detect relationship / scatter
# --------------------------------

    relationship_words = [
        "relationship",
        "relation",
        "correlation",
        "versus",
        "vs",
        "against",
        "compare"
    ]

    if any(word in query for word in relationship_words):

    # Sales vs Profit
        if "sales" in query and "profit" in query:

            intent["chart_type"] = "scatter"
            intent["x_column"] = "Sales"
            intent["y_column"] = "Profit"

    # Sales vs Quantity
        elif (
            "sales" in query
            and "quantity" in query
        ):

            intent["chart_type"] = "scatter"
            intent["x_column"] = "Sales"
            intent["y_column"] = "Quantity"

    # Profit vs Quantity
        elif (
            "profit" in query
            and "quantity" in query
        ):

            intent["chart_type"] = "scatter"
            intent["x_column"] = "Profit"
            intent["y_column"] = "Quantity"
    # -----------------------------
    # Detect metric
    # -----------------------------

    if (
        "sales" in query
        or "revenue" in query
        or "sold" in query
        or "selling" in query
    ):
        intent["metric"] = "Sales"

    elif (
        "profit" in query
        or "profits" in query
        or "earning" in query
        or "earnings" in query
    ):
        intent["metric"] = "Profit"

    elif (
        "quantity" in query
        or "units" in query
        or "volume" in query
        or "items" in query
    ):
        intent["metric"] = "Quantity"

    # Use default metric if user didn't specify one
    if intent["metric"] is None:
        intent["metric"] = default_metric

    # -----------------------------
    # Detect group
    # -----------------------------

    if (
        "product" in query
        or "products" in query
        or "item" in query
        or "items" in query
    ):
        intent["group_by"] = "Product"

    elif (
        "category" in query
        or "categories" in query
    ):
        intent["group_by"] = "Category"

    elif (
        "region" in query
        or "regions" in query
        or "area" in query
        or "location" in query
    ):
        intent["group_by"] = "Region"

    elif "city" in query:
        intent["group_by"] = "City"    

    # -----------------------------
    # Detect visualization request
    # -----------------------------

    chart_type = None

    if any(word in query for word in [
        "scatter",
        "relationship",
        "correlation",
        "correlate"
    ]):
        chart_type = "scatter"

    elif any(word in query for word in [
        "histogram",
        "distribution",
        "frequency distribution"
    ]):
        chart_type = "histogram"

    elif any(word in query for word in [
        "box plot",
        "boxplot",
        "outliers",
        "outlier"
    ]):
        chart_type = "box"

    elif any(word in query for word in [
        "heatmap",
        "correlation heatmap"
    ]):
        chart_type = "heatmap"

    intent["chart_type"] = chart_type

    # -----------------------------
    # Detect operation
    # -----------------------------

    if (
        "top" in query
        or "highest" in query
        or "best" in query
        or "most" in query
        or "maximum" in query
        or "max" in query
    ):
        intent["type"] = "top"

    elif (
        "bottom" in query
        or "lowest" in query
        or "worst" in query
        or "least" in query
        or "minimum" in query
        or "min" in query
    ):
        intent["type"] = "bottom"

    elif "by" in query:
        intent["type"] = "group"

    else:
        intent["type"] = "group"

    # -----------------------------
    # Detect numeric limit
    # -----------------------------

    number_words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10
    }

    for number in range(1, 11):

        if str(number) in query:

            intent["limit"] = number
            break

    if intent["limit"] is None:

        for word, number in number_words.items():

            if word in query:

                intent["limit"] = number
                break

    # -----------------------------
    # Detect time/trend queries
    # -----------------------------

    if (
        "trend" in query
        or "over time" in query
        or "monthly" in query
        or "month" in query
        or "daily" in query
        or "weekly" in query
        or "change over time" in query
    ):
        intent["type"] = "trend"
        intent["time_based"] = True

    # -----------------------------
    # Detect share / percentage queries
    # -----------------------------

    if (
        "share" in query
        or "percentage" in query
        or "percent" in query
        or "contribution" in query
        or "proportion" in query
    ):
        intent["share"] = True

    # --------------------------------
    # Default metric for "best" queries
    # --------------------------------

    if (
        intent["metric"] is None
        and intent["type"] in ["top", "bottom"]
    ):
        intent["metric"] = "Sales"



    # -----------------------------
#     Detect requested chart
    # -----------------------------

    chart_type = None

    if any(word in query for word in [
        "scatter",
        "relationship"
    ]):
        chart_type = "scatter"

    elif any(word in query for word in [
        "histogram",
        "distribution"
    ]):
        chart_type = "histogram"

    elif any(word in query for word in [
        "box plot",
        "boxplot",
        "outlier",
        "outliers"
    ]):
        chart_type = "box"

    elif any(word in query for word in [
        "heatmap",
        "correlation"
    ]):
        chart_type = "heatmap"

    intent["chart_type"] = chart_type

    # -----------------------------
    # Detect X and Y columns
    # -----------------------------

    intent["x_column"] = None
    intent["y_column"] = None

    if chart_type == "scatter":

    # Sales vs Profit
        if "sales" in query and "profit" in query:

            intent["x_column"] = "Sales"
            intent["y_column"] = "Profit"

    # Sales vs Quantity
        elif "sales" in query and "quantity" in query:

            intent["x_column"] = "Sales"
            intent["y_column"] = "Quantity"

    # Profit vs Quantity
        elif "profit" in query and "quantity" in query:

            intent["x_column"] = "Profit"
            intent["y_column"] = "Quantity"
    
    return intent


if __name__ == "__main__":

    test_queries = [
        "Which region performed best?",
        "Which category performed best?",
        "Which product performed best?",
        "Show sales share by category",
        "Show percentage of sales by region",
        "Show sales contribution by product",
        "Show sales by trend",
        "Show sales by city",
        "Show relationship between sales and profit"
    ]

    for query in test_queries:

        print(f"\nQuery: {query}")

        intent = understand_query(
            query,
            "Sales"
        )

        print(f"Intent: {intent}")