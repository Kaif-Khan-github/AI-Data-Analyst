def analyze_statistics(df, numerical_columns):

    statistics = {}

    for column in numerical_columns:

        statistics[column] = {
            "total": df[column].sum(),
            "mean": df[column].mean(),
            "median": df[column].median(),
            "minimum": df[column].min(),
            "maximum": df[column].max(),
            "standard_deviation": df[column].std()
        }

    return statistics


def analyze_correlations(df, numerical_columns):

    correlations = {}

    if len(numerical_columns) < 2:
        return correlations

    correlation_matrix = df[numerical_columns].corr()

    for i in range(len(numerical_columns)):

        for j in range(i + 1, len(numerical_columns)):

            column_1 = numerical_columns[i]
            column_2 = numerical_columns[j]

            value = correlation_matrix.loc[
                column_1,
                column_2
            ]

            if abs(value) >= 0.7:
                strength = "Strong"

            elif abs(value) >= 0.4:
                strength = "Moderate"

            else:
                strength = "Weak"

            correlations[
                f"{column_1} vs {column_2}"
            ] = {
                "correlation": value,
                "strength": strength
            }

    return correlations

def generate_statistical_insights(statistics, correlations):

    insights = []

    for column, values in statistics.items():

        mean = values["mean"]
        std = values["standard_deviation"]

        if mean != 0:

            coefficient_of_variation = (
                std / abs(mean)
            ) * 100

            if coefficient_of_variation >= 50:

                insights.append(
                    f"{column} has high variability "
                    f"({coefficient_of_variation:.1f}%)."
                )

            elif coefficient_of_variation >= 20:

                insights.append(
                    f"{column} has moderate variability "
                    f"({coefficient_of_variation:.1f}%)."
                )

            else:

                insights.append(
                    f"{column} has low variability "
                    f"({coefficient_of_variation:.1f}%)."
                )

    for pair, result in correlations.items():

        correlation = result["correlation"]

        if result["strength"] == "Strong":

            if correlation > 0:

                insights.append(
                    f"{pair} has a strong positive relationship "
                    f"({correlation:.2f})."
                )

            else:

                insights.append(
                    f"{pair} has a strong negative relationship "
                    f"({correlation:.2f})."
                )

        elif result["strength"] == "Moderate":

            insights.append(
                f"{pair} has a moderate relationship "
                f"({correlation:.2f})."
            )

    return insights