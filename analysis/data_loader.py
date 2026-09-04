import pandas as pd


def load_dataset(file_path):
    """
    Load a dataset from a backend path.
    Kept for compatibility with existing project code.
    """

    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)

    if file_path.endswith(".xlsx"):
        return pd.read_excel(file_path)

    raise ValueError(
        "Unsupported file type. Only CSV and Excel files are supported."
    )


def load_dataframe(df):
    """
    Accept an already-loaded DataFrame.
    """

    if df is None:
        raise ValueError("No dataset was provided.")

    if df.empty:
        raise ValueError("Dataset is empty.")

    return df.copy()