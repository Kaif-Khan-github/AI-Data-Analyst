import pandas as pd


def clean_dataset(df, date_columns=None):
    cleaned_df = df.copy()
    cleaning_report = {
        "missing_values_fixed": 0,
        "duplicate_rows_removed": 0,
        "dates_converted": 0,
        "categorical_columns_standardized": 0,
        "actions": []
    }

    if date_columns is None:
        date_columns = []

    # -----------------------------
    # Handle missing values
    # -----------------------------
    for column in cleaned_df.columns:
        missing_count = cleaned_df[column].isnull().sum()
        if missing_count == 0:
            continue

        if pd.api.types.is_numeric_dtype(cleaned_df[column]):
            cleaned_df[column] = cleaned_df[column].fillna(
                cleaned_df[column].median()
            )
        else:
            mode = cleaned_df[column].mode()
            if not mode.empty:
                cleaned_df[column] = cleaned_df[column].fillna(mode[0])

        cleaning_report["missing_values_fixed"] += int(missing_count)
        cleaning_report["actions"].append(
            f"{column}: {missing_count} missing value(s) filled"
            )

    # -----------------------------
    # Convert detected date columns
    # -----------------------------
    if date_columns:
        for column in date_columns:
            if column in cleaned_df.columns:
                if not pd.api.types.is_datetime64_any_dtype(
                    cleaned_df[column]
                ):
                    cleaned_df[column] = pd.to_datetime(
                        cleaned_df[column], errors="coerce"
                    )
                cleaning_report["dates_converted"] += 1
                cleaning_report["actions"].append(
                    f"{column}: converted to datetime"
                    )

    # -----------------------------
    # Standardize categorical values
    # -----------------------------
    categorical_columns = []
    for column in cleaned_df.columns:
        if column not in date_columns:
            if not pd.api.types.is_numeric_dtype(cleaned_df[column]):
                categorical_columns.append(column)
                cleaned_df[column] = (
                    cleaned_df[column].astype("string").str.strip().str.title()
                )
                cleaning_report["actions"].append(
                    f"{column}: standardized categorical values"
                    )

    cleaning_report["categorical_columns_standardized"] = len(
        categorical_columns
    )

    # -----------------------------
    # Remove duplicate rows
    # -----------------------------
    duplicate_count = cleaned_df.duplicated().sum()
    if duplicate_count > 0:
        cleaning_report["actions"].append(
            f"Removed {duplicate_count} duplicate row(s)"
            )
    cleaned_df = cleaned_df.drop_duplicates()
    cleaning_report["duplicate_rows_removed"] = int(duplicate_count)

    return cleaned_df, cleaning_report
