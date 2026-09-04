def analyze_business_metrics(df, numerical_columns, categorical_columns):

    results = {}

    if not numerical_columns:
        return results

    # --------------------------------
    # Detect primary business metric
    # --------------------------------

    metric_column = None

    priority_keywords = [
        "sales",
        "revenue",
        "amount",
        "income",
        "value",
        "profit"
    ]

    for keyword in priority_keywords:

        for column in numerical_columns:

            if keyword in column.lower():
                metric_column = column
                break

        if metric_column:
            break

    # If no business metric is found,
    # use the first numerical column
    if metric_column is None:
        metric_column = numerical_columns[0]

    results["metric_column"] = metric_column

    # --------------------------------
    # Group analysis
    # --------------------------------

    results["by_category"] = {}

    for column in categorical_columns:

        grouped = (
            df.groupby(column)[metric_column]
            .sum()
            .sort_values(ascending=False)
        )

        results["by_category"][column] = grouped.to_dict()

    return results



def calculate_business_metrics(df, numerical_columns):

    results = {}

    sales_column = None
    profit_column = None
    quantity_column = None

    for column in numerical_columns:

        name = column.lower()

        if "sales" in name or "revenue" in name:
            sales_column = column

        elif "profit" in name or "income" in name:
            profit_column = column

        elif "quantity" in name or "units" in name:
            quantity_column = column

    if sales_column:
        results["total_sales"] = df[sales_column].sum()

    if profit_column:
        results["total_profit"] = df[profit_column].sum()

    if quantity_column:
        results["total_quantity"] = df[quantity_column].sum()

    if sales_column and profit_column:

        total_sales = df[sales_column].sum()
        total_profit = df[profit_column].sum()

        if total_sales != 0:

            results["profit_margin"] = (
                total_profit / total_sales
            ) * 100

    return results


def analyze_top_bottom_performers(
    df,
    metric_column,
    categorical_columns
):

    results = {}

    for column in categorical_columns:

        grouped = (
            df.groupby(column)[metric_column]
            .sum()
            .sort_values(ascending=False)
        )

        results[column] = {
            "top": grouped.head(3).to_dict(),
            "bottom": grouped.tail(3).sort_values().to_dict()
        }

    return results