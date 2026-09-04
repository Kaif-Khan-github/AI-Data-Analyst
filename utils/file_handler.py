import pandas as pd
from io import BytesIO


ALLOWED_EXTENSIONS = [".csv", ".xlsx"]


def get_file_extension(filename):
    return "." + filename.split(".")[-1].lower()


def validate_uploaded_file(uploaded_file, max_size_mb=50):
    """
    Validate uploaded CSV/Excel file.
    """

    if uploaded_file is None:
        return False, "No file was uploaded."

    filename = uploaded_file.name
    extension = get_file_extension(filename)

    if extension not in ALLOWED_EXTENSIONS:
        return False, "Unsupported file type. Please upload a CSV or Excel (.xlsx) file."

    file_size_mb = uploaded_file.size / (1024 * 1024)

    if file_size_mb > max_size_mb:
        return False, f"File is too large. Maximum allowed size is {max_size_mb} MB."

    if uploaded_file.size == 0:
        return False, "The uploaded file is empty."

    return True, None


def load_uploaded_file(uploaded_file):
    """
    Load CSV or Excel file directly into a pandas DataFrame.
    """

    extension = get_file_extension(uploaded_file.name)

    uploaded_file.seek(0)

    if extension == ".csv":
        df = pd.read_csv(uploaded_file)

    elif extension == ".xlsx":
        df = pd.read_excel(uploaded_file)

    else:
        raise ValueError(
            "Unsupported file type. Only CSV and Excel files are supported."
        )

    if df.empty:
        raise ValueError("The uploaded file contains no data.")

    if len(df.columns) == 0:
        raise ValueError("The uploaded file contains no columns.")

    return df


def get_dataset_summary(df):
    """
    Return basic dataset information for the upload screen.
    """

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_columns": len(df.select_dtypes(include="number").columns),
        "text_columns": len(df.select_dtypes(include="object").columns),
    }