def detect_filters(query, df):

    query = query.lower()

    filters = {}

    # -----------------------------
    # Region filter
    # -----------------------------

    if "Region" in df.columns:

        for value in df["Region"].dropna().unique():

            if str(value).lower() in query:

                filters["Region"] = value

    # -----------------------------
    # Category filter
    # -----------------------------

    if "Category" in df.columns:

        for value in df["Category"].dropna().unique():

            if str(value).lower() in query:

                filters["Category"] = value

    # -----------------------------
    # Product filter
    # -----------------------------

    if "Product" in df.columns:

        for value in df["Product"].dropna().unique():

            if str(value).lower() in query:

                filters["Product"] = value

    return filters

if __name__ == "__main__":

    from analysis.data_loader import load_dataset

    df = load_dataset(
        "data/processed/cleaned_sales.csv"
    )

    queries = [
        "Show sales by category for North",
        "Show top products in Electronics",
        "Show sales for Laptop"
    ]

    for query in queries:

        print(f"\nQuery: {query}")

        filters = detect_filters(
            query,
            df
        )

        print("Filters:", filters)


if __name__ == "__main__":

    from analysis.data_loader import load_dataset

    df = load_dataset(
        "data/processed/cleaned_sales.csv"
    )

    queries = [
        "Show sales by product for North in Electronics",
        "Show sales for Laptop in North",
        "Show top products in Electronics in North"
    ]

    for query in queries:

        print(f"\nQuery: {query}")

        filters = detect_filters(
            query,
            df
        )

        print("Filters:", filters)       