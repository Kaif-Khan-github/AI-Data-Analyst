import pandas as pd


def analyze_trend(df, date_column, metric_column):

    data = df.copy()

    data[date_column] = pd.to_datetime(
        data[date_column],
        errors="coerce"
    )

    data = data.dropna(
        subset=[date_column]
    )

    data["Month"] = (
        data[date_column]
        .dt.to_period("M")
        .astype(str)
    )

    monthly = (
        data.groupby("Month")[metric_column]
        .sum()
        .sort_index()
    )

    return monthly


def explain_trend(monthly_data, metric):

    if len(monthly_data) < 2:

        return (
            f"Not enough data to determine the "
            f"{metric.lower()} trend."
        )

    first_value = monthly_data.iloc[0]
    last_value = monthly_data.iloc[-1]

    first_period = monthly_data.index[0]
    last_period = monthly_data.index[-1]

    if first_value == 0:

        return (
            f"{metric} changed from "
            f"{first_value:,.2f} to "
            f"{last_value:,.2f}."
        )

    percentage_change = (
        (last_value - first_value)
        / abs(first_value)
    ) * 100

    if percentage_change > 0:

        direction = "increased"

    elif percentage_change < 0:

        direction = "decreased"

    else:

        direction = "remained stable"

    return (
        f"{metric} {direction} by "
        f"{abs(percentage_change):.1f}% "
        f"from {first_period} to {last_period}."
    )

if __name__ == "__main__":

    from analysis.data_loader import load_dataset

    df = load_dataset(
        "data/processed/cleaned_sales.csv"
    )

    result = analyze_trend(
        df,
        "Order_Date",
        "Sales"
    )

    print("\nMONTHLY SALES TREND")
    print("===================")

    print(result)


