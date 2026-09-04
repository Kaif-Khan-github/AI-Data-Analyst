import pandas as pd

from utils.formatters import compact_value


def generate_recommendations(
    result,
    intent,
    insights=None,
    anomaly_insights=None
):
    """
    Generate simplpythone business recommendations
    from query results, insights and anomalies.
    """

    recommendations = []

    if intent is None:
        return recommendations

    query_type = intent.get("type")
    metric = intent.get("metric")
    group_by = intent.get("group_by")

    # --------------------------------------------------
    # GROUP ANALYSIS
    # --------------------------------------------------

    if query_type in ["group", "top", "bottom"]:

        if isinstance(result, pd.Series) and not result.empty:

            highest_name = result.idxmax()
            highest_value = result.max()

            lowest_name = result.idxmin()
            lowest_value = result.min()

            if metric and group_by:

                recommendations.append(
                    f"💡 Focus on {highest_name}, which has the highest "
                    f"{metric} at {compact_value(highest_value)}."
                )

                if highest_name != lowest_name:

                    recommendations.append(
                        f"📉 Investigate {lowest_name} because it has the "
                        f"lowest {metric} at {compact_value(lowest_value)}."
                    )

                # Difference
                difference = highest_value - lowest_value

                if difference > 0:

                    recommendations.append(
                        f"🎯 Consider improving {lowest_name} to reduce the "
                        f"performance gap of {compact_value(difference)}."
                    )

    # --------------------------------------------------
    # TREND ANALYSIS
    # --------------------------------------------------

    elif query_type == "trend":

        if isinstance(result, pd.Series) and len(result) >= 2:

            first_value = result.iloc[0]
            last_value = result.iloc[-1]

            if first_value != 0:

                change = (
                    (last_value - first_value)
                    / abs(first_value)
                ) * 100

                if change > 10:

                    recommendations.append(
                        f"📈 {metric} is showing strong growth. "
                        f"Consider maintaining the current strategy."
                    )

                elif change < -10:

                    recommendations.append(
                        f"📉 {metric} is declining significantly. "
                        f"Investigate the causes and consider corrective action."
                    )

                else:

                    recommendations.append(
                        f"➡️ {metric} is relatively stable. "
                        f"Continue monitoring the trend."
                    )

    # --------------------------------------------------
    # RELATIONSHIP ANALYSIS
    # --------------------------------------------------

    elif query_type == "relationship":

        x_column = intent.get("x_column")
        y_column = intent.get("y_column")

        if x_column and y_column:

            recommendations.append(
                f"📊 Monitor the relationship between "
                f"{x_column} and {y_column} to identify patterns "
                f"that may support better business decisions."
            )

    # --------------------------------------------------
    # SHARE ANALYSIS
    # --------------------------------------------------

    # --------------------------------------------------
    # SHARE ANALYSIS
    # --------------------------------------------------

    elif query_type == "share":

        if isinstance(result, pd.Series) and not result.empty:

            highest_name = result.idxmax()
            highest_value = result.max()
            total_value = result.sum() # Get the total sum of all groups
            
            # Safely calculate the actual percentage
            actual_percentage = (highest_value / total_value) * 100 if total_value != 0 else 0

            recommendations.append(
                f"🏆 {highest_name} represents the largest share "
                f"of {metric} at {actual_percentage:.1f}%."
            )

            recommendations.append(
                f"🎯 Consider protecting the performance of "
                f"{highest_name} while identifying opportunities "
                f"to improve lower-share segments."
            )

    # --------------------------------------------------
    # ANOMALY ANALYSIS
    # --------------------------------------------------

    elif query_type == "anomaly":

        recommendations.append(
            f"🚨 Investigate unusual {metric} values to determine "
            f"whether they are caused by data issues or genuine "
            f"business events."
        )

    # --------------------------------------------------
    # TOTAL ANALYSIS
    # --------------------------------------------------

    elif query_type == "total":

        if metric:

            recommendations.append(
                f"💰 Use the total {metric} as a baseline for "
                f"monitoring future business performance."
            )

    # --------------------------------------------------
    # USE ANOMALY INFORMATION
    # --------------------------------------------------

    if anomaly_insights:

        recommendations.append(
            "🔍 Review detected anomalies before making major "
            "business decisions because unusual values may "
            "significantly affect the analysis."
        )

    # --------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------

    recommendations = list(dict.fromkeys(recommendations))

    return recommendations