import pandas as pd


def profile_dataset(df):

    profile = {}

    # --------------------------------
    # Basic information
    # --------------------------------

    profile["rows"] = df.shape[0]
    profile["columns"] = df.shape[1]

    # Column names
    profile["column_names"] = list(df.columns)

    # Missing values
    profile["missing_values"] = df.isnull().sum().to_dict()

    # Duplicate rows
    profile["duplicate_rows"] = df.duplicated().sum()

    # Data types
    profile["data_types"] = df.dtypes.astype(str).to_dict()

    # --------------------------------
    # Column classification
    # --------------------------------

    identifier_columns = []
    numerical_columns = []
    categorical_columns = []
    date_columns = []

    for column in df.columns:

        if pd.api.types.is_numeric_dtype(df[column]):
            if (
                df[column].nunique() == len(df)
                and (
                    "id" in column.lower()
                    or "code" in column.lower()
                    or "number" in column.lower()
                )
            ):
                identifier_columns.append(column)
            else:
                numerical_columns.append(column)

        elif pd.api.types.is_datetime64_any_dtype(df[column]):

            date_columns.append(column)

        else:

            # Try to detect date-like columns
            converted_dates = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            valid_dates = converted_dates.notna().sum()
            total_values = df[column].notna().sum()

            if total_values > 0 and valid_dates / total_values >= 0.8:

                date_columns.append(column)

            else:

                categorical_columns.append(column)

    profile["numerical_columns"] = numerical_columns
    profile["categorical_columns"] = categorical_columns
    profile["date_columns"] = date_columns
    profile["identifier_columns"] = identifier_columns

    # --------------------------------
    # Column-level details
    # --------------------------------

    column_details = {}

    for column in df.columns:

        details = {}

        # Basic information
        details["data_type"] = profile["data_types"][column]
        details["missing"] = int(df[column].isnull().sum())
        details["unique"] = int(df[column].nunique())

        # Numerical statistics
        if column in numerical_columns:

            details["minimum"] = float(df[column].min())
            details["maximum"] = float(df[column].max())
            details["mean"] = float(df[column].mean())
            details["median"] = float(df[column].median())
            details["std"] = float(df[column].std())

        # Categorical statistics
        elif column in categorical_columns:

            details["top_values"] = (
                df[column]
                .value_counts()
                .head(5)
                .to_dict()
            )

        # Date statistics
        elif column in date_columns:

            converted_dates = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            details["minimum"] = str(converted_dates.min())
            details["maximum"] = str(converted_dates.max())

        column_details[column] = details

    profile["column_details"] = column_details

    # --------------------------------
    # Data quality analysis
    # --------------------------------

    total_cells = df.shape[0] * df.shape[1]

    total_missing = int(df.isnull().sum().sum())

    duplicate_rows = int(df.duplicated().sum())

    if total_cells > 0:
        missing_percentage = (total_missing / total_cells) * 100
    else:
        missing_percentage = 0

    # Start with a perfect score
    quality_score = 100

    # Deduct points for missing values
    quality_score -= missing_percentage

    # Deduct points for duplicate rows
    if df.shape[0] > 0:
        duplicate_percentage = (
            duplicate_rows / df.shape[0]
        ) * 100

        quality_score -= duplicate_percentage

    # Make sure score stays between 0 and 100
    quality_score = max(0, min(100, quality_score))

    if quality_score >= 90:
        quality_status = "Excellent"

    elif quality_score >= 75:
        quality_status = "Good"

    elif quality_score >= 50:
        quality_status = "Needs Cleaning"

    else:
        quality_status = "Poor"

    profile["quality"] = {
        "score": round(quality_score, 2),
        "status": quality_status,
        "total_missing": total_missing,
        "missing_percentage": round(missing_percentage, 2),
        "duplicate_rows": duplicate_rows
    }

    # --------------------------------
    # Automatic dataset summary
    # --------------------------------

    summary = (
        f"The dataset contains {profile['rows']} rows and "
        f"{profile['columns']} columns. "

        f"It has {len(profile['numerical_columns'])} numerical columns, "
        f"{len(profile['categorical_columns'])} categorical columns, "
        f"and {len(profile['date_columns'])} date columns. "

        f"There are {profile['quality']['total_missing']} missing values "
        f"and {profile['quality']['duplicate_rows']} duplicate rows. "

        f"Overall data quality is "
        f"{profile['quality']['status']} with a score of "
        f"{profile['quality']['score']}/100."
    )

    profile["summary"] = summary



    return profile

    return profile