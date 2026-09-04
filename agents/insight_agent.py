import pandas as pd


# ==========================================
# COMPACT NUMBER FORMAT
# ==========================================

def compact_value(value):

    value = float(value)

    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"

    elif abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"

    else:
        return f"{value:,.0f}"


# ==========================================
# PERCENTAGE
# ==========================================

def percentage(part, total):

    if total == 0:
        return 0

    return (part / total) * 100


# ==========================================
# GENERATE INSIGHTS
# ==========================================

def generate_insights(result, intent):

    metric = intent.get("metric")
    group_by = intent.get("group_by")
    query_type = intent.get("type")
    print("INSIGHT DEBUG:", query_type, type(result))
    chart_type = intent.get("chart_type")

    # ==========================================
    # NO RESULT
    # ==========================================

    if result is None:
        return []

    if hasattr(result, "empty") and result.empty:
        return []

    # ==========================================
    # SCATTER / RELATIONSHIP
    # ==========================================

    if chart_type == "scatter":

        x_column = intent.get("x_column")
        y_column = intent.get("y_column")

        if not isinstance(result, pd.DataFrame):
            return [
                "The relationship analysis could not "
                "be calculated from the available data."
            ]

        if (
            x_column not in result.columns
            or y_column not in result.columns
        ):
            return [
                "The selected columns could not be used "
                "for relationship analysis."
            ]

        scatter_df = result[
            [x_column, y_column]
        ].copy()

        scatter_df[x_column] = pd.to_numeric(
            scatter_df[x_column],
            errors="coerce"
        )

        scatter_df[y_column] = pd.to_numeric(
            scatter_df[y_column],
            errors="coerce"
        )

        scatter_df = scatter_df.dropna()

        if len(scatter_df) < 2:

            return [
                f"There is not enough valid data to "
                f"analyze the relationship between "
                f"{x_column} and {y_column}."
            ]

        correlation = scatter_df[
            x_column
        ].corr(
            scatter_df[y_column]
        )

        if pd.isna(correlation):

            return [
                f"No meaningful relationship could be "
                f"calculated between {x_column} and "
                f"{y_column}."
            ]

        abs_corr = abs(correlation)

        if abs_corr >= 0.7:
            strength = "strong"

        elif abs_corr >= 0.4:
            strength = "moderate"

        else:
            strength = "weak"

        if correlation > 0:
            direction = "positive"

        elif correlation < 0:
            direction = "negative"

        else:
            direction = "no clear"

        return [
            f"📊 {x_column} and {y_column} have a "
            f"{strength} {direction} relationship "
            f"(correlation: {correlation:.2f})."
        ]

    # ==========================================
    # TREND ANALYSIS
    # ==========================================

    if query_type == "trend":

        # Make sure result is a Series
        if not isinstance(result, pd.Series):

            return [
                "The trend could not be analyzed "
                "from the available data."
            ]

        # Convert values to numeric
        trend = pd.to_numeric(
            result,
            errors="coerce"
        ).dropna()

        if trend.empty:

            return [
                "There is not enough valid data "
                "to analyze the trend."
            ]

        if len(trend) < 2:

            return [
                "There is not enough time-based data "
                "to identify a trend."
            ]

        # ------------------------------------------
        # Highest
        # ------------------------------------------

        highest_period = trend.idxmax()
        highest_value = trend.max()

        # ------------------------------------------
        # Lowest
        # ------------------------------------------

        lowest_period = trend.idxmin()
        lowest_value = trend.min()

        # ------------------------------------------
        # First and latest
        # ------------------------------------------

        first_period = trend.index[0]
        first_value = trend.iloc[0]

        latest_period = trend.index[-1]
        latest_value = trend.iloc[-1]

        # ------------------------------------------
        # Average
        # ------------------------------------------

        average_value = trend.mean()

        # ------------------------------------------
        # Total
        # ------------------------------------------

        total_value = trend.sum()

        # ------------------------------------------
        # Overall change
        # ------------------------------------------

        change = latest_value - first_value

        if first_value != 0:

            change_percentage = (
                change / abs(first_value)
            ) * 100

        else:

            change_percentage = 0

        # ------------------------------------------
        # Determine direction
        # ------------------------------------------

        if change_percentage > 1:

            direction = "increased"

        elif change_percentage < -1:

            direction = "decreased"

        else:

            direction = "remained relatively stable"

        # ------------------------------------------
        # Build insights
        # ------------------------------------------

        insights = []

        # Peak
        insights.append(
            f"🏆 {metric} peaked in "
            f"{highest_period} at "
            f"{compact_value(highest_value)}."
        )

        # Lowest
        insights.append(
            f"📉 {metric} was lowest in "
            f"{lowest_period} at "
            f"{compact_value(lowest_value)}."
        )

        # Average
        insights.append(
            f"📊 Average {metric.lower()} per period "
            f"was {compact_value(average_value)}."
        )

        # Total
        insights.append(
            f"💰 Total {metric.lower()} during "
            f"the period was "
            f"{compact_value(total_value)}."
        )

        # Overall movement
        if direction == "remained relatively stable":

            insights.append(
                f"➡️ {metric} remained relatively "
                f"stable from {first_period} to "
                f"{latest_period}."
            )

        else:

            insights.append(
                f"📈 {metric} {direction} by "
                f"{compact_value(abs(change))} "
                f"({abs(change_percentage):.1f}%) "
                f"from {first_period} to "
                f"{latest_period}."
            )

        return insights

    # ==========================================
    # GROUPED ANALYSIS
    # ==========================================

    if isinstance(result, pd.Series):

        grouped = pd.to_numeric(
            result,
            errors="coerce"
        ).dropna()

        if grouped.empty:
            return []

        highest_name = grouped.idxmax()
        highest_value = grouped.max()

        lowest_name = grouped.idxmin()
        lowest_value = grouped.min()

        total_value = grouped.sum()
        average_value = grouped.mean()

        highest_share = percentage(
            highest_value,
            total_value
        )

        difference = (
            highest_value - lowest_value
        )

        if lowest_value != 0:

            difference_percentage = (
                difference /
                abs(lowest_value)
            ) * 100

        else:

            difference_percentage = 0

        insights = []

        # Highest
        insights.append(
            f"🏆 {highest_name} generated the "
            f"highest {metric} at "
            f"{compact_value(highest_value)}."
        )

        # Lowest
        insights.append(
            f"📉 {lowest_name} generated the "
            f"lowest {metric} at "
            f"{compact_value(lowest_value)}."
        )

        # Contribution
        insights.append(
            f"📊 {highest_name} contributed "
            f"{highest_share:.1f}% of total "
            f"{metric}."
        )

        # Difference
        insights.append(
            f"💡 {highest_name} generated "
            f"{compact_value(difference)} more "
            f"{metric} than {lowest_name} "
            f"({difference_percentage:.1f}% higher)."
        )

        # Average
        if group_by:

            insights.append(
                f"📈 Average {metric.lower()} "
                f"across {group_by.lower()}s "
                f"was "
                f"{compact_value(average_value)}."
            )

        return insights

    # ==========================================
    # SINGLE NUMBER
    # ==========================================

    if isinstance(result, (int, float)):

        return [
            f"📊 {metric} is "
            f"{compact_value(result)}."
        ]

    # ==========================================
    # DATAFRAME FALLBACK
    # ==========================================

    if isinstance(result, pd.DataFrame):

        return [
            "📊 The analysis was completed "
            "successfully."
        ]

    # ==========================================
    # FALLBACK
    # ==========================================

    return [
        "The analysis was completed successfully."
    ]