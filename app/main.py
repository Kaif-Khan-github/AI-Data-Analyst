from analysis.trend_analysis import (
    analyze_trend,
    explain_trend
)
from analysis.visualizer import (
    create_trend_chart,
    create_bar_chart,
    create_horizontal_bar_chart,
    create_pie_chart
)
from agents.filter_agent import detect_filters
from analysis.filter_engine import apply_filters
from agents.visualization_agent import choose_chart
from agents.query_agent_backup import understand_query
from analysis.query_engine import execute_query
from analysis.answer_generator import generate_answer
from analysis.cleaner import clean_dataset
from analysis.data_loader import load_dataset
from analysis.profiler import profile_dataset
from analysis.statistics import (
    analyze_statistics,
    analyze_correlations,
    generate_statistical_insights
)
from analysis.business_analysis import (
    analyze_business_metrics,
    calculate_business_metrics,
    analyze_top_bottom_performers
)
from utils.file_handler import (
    validate_uploaded_file,
    load_uploaded_file,
    get_dataset_summary
)


print("MAIN.PY STARTED")

file_path = "data/raw/sales.csv"

df = load_dataset(file_path)

if df is not None:

    initial_profile = profile_dataset(df)

    cleaned_df, cleaning_report = clean_dataset(
        df,
        initial_profile["date_columns"]
    )

    output_path = "data/processed/cleaned_sales.csv"

    cleaned_df.to_csv(output_path, index=False)

    print("FILE SAVE COMPLETED")
    print(f"\nCleaned dataset saved to: {output_path}")

    profile = profile_dataset(cleaned_df)
    statistics = analyze_statistics(
        cleaned_df,
        profile["numerical_columns"]
    )

    correlations = analyze_correlations(
    cleaned_df,
    profile["numerical_columns"]
    )

    statistical_insights = generate_statistical_insights(
    statistics,
    correlations
    )

    business_metrics = analyze_business_metrics(
    cleaned_df,
    profile["numerical_columns"],
    profile["categorical_columns"]
    )

    business_summary = calculate_business_metrics(
    cleaned_df,
    profile["numerical_columns"]
    )

    top_bottom = analyze_top_bottom_performers(
    cleaned_df,
    business_metrics["metric_column"],
    profile["categorical_columns"]
    )


    print("\n================================")
    print("STATISTICAL INSIGHTS")
    print("================================")

    for insight in statistical_insights:
        print(f"- {insight}")

    print("\n================================")
    print("CORRELATION ANALYSIS")
    print("================================")
    for pair, result in correlations.items():
        print(
             f"\n{pair}"
        )
        print(
            f"  Correlation: "
            f"{result['correlation']:.2f}"
        )
        print(
            f"  Strength: "
            f"{result['strength']}"
            )

    print("\n================================")
    print("TOP & BOTTOM PERFORMERS")
    print("================================")
    for column, results in top_bottom.items():
        print(f"\n{column}")
        print("\nTop Performers:")
        for name, value in results["top"].items():
            print(
                f"  - {name}: {value:.2f}"
                )


        print("\nBottom Performers:")

        for name, value in results["bottom"].items():
            print(
                 f"  - {name}: {value:.2f}"
                 )

    print("\n================================")
    print("BUSINESS METRICS")
    print("================================")
    for metric, value in business_summary.items():
        print(
            f"{metric}: {value:.2f}"
        )

    print("\n================================")
    print("BUSINESS ANALYSIS")
    print("================================")

    print(
        f"\nPrimary Metric: "
        f"{business_metrics['metric_column']}"
    )
    for column, values in business_metrics["by_category"].items():
        print(f"\n{column}:")
        for category, total in values.items():
            print(
                f"  - {category}: {total:.2f}"
            )
    print("\n================================")
    print("STATISTICAL ANALYSIS")
    print("================================")
    for column, values in statistics.items():
        print(f"\n{column}")

        print(f"  Total: {values['total']:.2f}")
        print(f"  Mean: {values['mean']:.2f}")
        print(f"  Median: {values['median']:.2f}")
        print(f"  Minimum: {values['minimum']:.2f}")
        print(f"  Maximum: {values['maximum']:.2f}")
        print(
            f"  Standard Deviation: "
            f"{values['standard_deviation']:.2f}"
        )

    print("\n================================")
    print("CLEANING VERIFICATION")
    print("================================")

    print(
        f"\nMissing values before: "
        f"{initial_profile['quality']['total_missing']}"
    )

    print(
        f"Missing values after: "
        f"{profile['quality']['total_missing']}"
    )

    print(
        f"Duplicate rows before: "
        f"{initial_profile['duplicate_rows']}"
    )

    print(
        f"Duplicate rows after: "
        f"{profile['duplicate_rows']}"
    )

    if (
        profile["quality"]["total_missing"] == 0
        and profile["duplicate_rows"] == 0
    ):
        print("\nVerification: PASSED")
        print("Dataset cleaning was successful.")

    else:
        print("\nVerification: WARNING")
        print("Some data quality issues remain.")

    print("================================")
    print("AI DATA ANALYST SYSTEM")
    print("================================")

    print("\nDataset loaded successfully!")

    print(f"\nRows: {profile['rows']}")
    print(f"Columns: {profile['columns']}")

    print("\nColumn names:")

    for column in profile["column_names"]:
        print(f"- {column}")

    print("\nMissing Values:")

    for column, count in profile["missing_values"].items():
        print(f"- {column}: {count}")

    print(f"\nDuplicate Rows: {profile['duplicate_rows']}")

    print("\nData Types:")

    for column, data_type in profile["data_types"].items():
        print(f"- {column}: {data_type}")

    print("\nColumn Classification:")

    print("\nNumerical Columns:")

    for column in profile["numerical_columns"]:
        print(f"- {column}")

    print("\nIdentifier Columns:")
    for column in profile["identifier_columns"]:
        print(f"- {column}")   

    print("\nCategorical Columns:")

    for column in profile["categorical_columns"]:
        print(f"- {column}")

    print("\nDate Columns:")

    for column in profile["date_columns"]:
        print(f"- {column}")

    print("\n================================")
    print("COLUMN DETAILS")
    print("================================")

    for column, details in profile["column_details"].items():

        print(f"\n{column}")

        print(f"  Data Type: {details['data_type']}")
        print(f"  Missing Values: {details['missing']}")
        print(f"  Unique Values: {details['unique']}")

        if column in profile["numerical_columns"]:

            print(f"  Minimum: {details['minimum']}")
            print(f"  Maximum: {details['maximum']}")
            print(f"  Mean: {details['mean']:.2f}")
            print(f"  Median: {details['median']:.2f}")
            print(f"  Standard Deviation: {details['std']:.2f}")

        elif column in profile["categorical_columns"]:

            print("  Top Values:")

            for value, count in details["top_values"].items():
                print(f"    - {value}: {count}")

        elif column in profile["date_columns"]:

            print(f"  Earliest Date: {details['minimum']}")
            print(f"  Latest Date: {details['maximum']}")

    print("\n================================")
    print("DATA QUALITY REPORT")
    print("================================")

    quality = profile["quality"]

    print(f"\nQuality Score: {quality['score']}/100")
    print(f"Status: {quality['status']}")

    print(f"\nTotal Missing Values: {quality['total_missing']}")
    print(f"Missing Percentage: {quality['missing_percentage']}%")
    print(f"Duplicate Rows: {quality['duplicate_rows']}")

    print("\n================================")
    print("DATASET SUMMARY")
    print("================================")

    print(f"\n{profile['summary']}")

    print("\n================================")
    print("CLEANING REPORT")
    print("================================")

    print(
        f"\nMissing values fixed: "
        f"{cleaning_report['missing_values_fixed']}"
    )

    print(
        f"Duplicate rows removed: "
        f"{cleaning_report['duplicate_rows_removed']}"
    )

    print(
        f"Date columns converted: "
        f"{cleaning_report['dates_converted']}"
    )

    print(
    f"Categorical columns standardized: "
    f"{cleaning_report['categorical_columns_standardized']}"

    )
    print("\n================================")
    print("CLEANING ACTION LOG")
    print("================================")

    for action in cleaning_report["actions"]:
        print(f"- {action}")


    print("\n================================")
    print("QUERY SYSTEM")
    print("================================")

    print("\nAsk a question about your dataset.")
    print("Type 'exit' to stop.")
    while True:
        query = input("\nYou: ")
        if query.lower().strip() == "exit":
            print("\nExiting Query System...")
            break
        intent = understand_query(
            query,
            business_metrics["metric_column"]
        )
        filters = detect_filters(
            query,
            cleaned_df
        )

        filtered_df = apply_filters(
            cleaned_df,
            filters
        )


        if intent["type"] == "trend":
            date_column = profile["date_columns"][0]
            result = analyze_trend(
                filtered_df,
                date_column,
                intent["metric"]
            )

            trend_explanation = explain_trend(
                result,
                intent["metric"]
            )

            chart_path = create_trend_chart(
                result,
                intent["metric"]
            )
        else:
            result = execute_query(
                filtered_df,
                intent
                )
            chart_type = choose_chart(intent)
            chart_path = None
            if chart_type == "line":
                chart_path = create_trend_chart(
                    result,
                    intent["metric"]
                )

            elif chart_type == "horizontal_bar":
                if intent["group_by"] is not None:
                    chart_path = create_horizontal_bar_chart(
                    result,
                    intent["metric"],
                    intent["group_by"]
                )

                else:
                    chart_path = None

            elif chart_type == "bar":
                chart_path = create_bar_chart(
                    result,
                    intent["metric"],
                    intent["group_by"]
                )

            elif chart_type == "pie":
                chart_path = create_pie_chart(
                    result,
                    intent["metric"],
                    intent["group_by"]
                )
            else:
                chart_path = None
        answer = generate_answer(
            query,
            intent,
            result
            )
        if chart_path is not None:
            answer += (
                f"\n\nChart saved to: "
                f"{chart_path}"
            )

        if intent["type"] == "trend":
            answer += (
                "\n\nTrend Insight:\n"
                + trend_explanation
            )

        print("\nAnswer:")
        print(answer)




    