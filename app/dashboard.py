# =========================================================
# 1. IMPORTS
# =========================================================
import sys
import os

# Add the project root to the Python path so it can find your modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import re

from analysis.data_loader import load_dataset
from agents.query_agent import understand_query
from agents.filter_agent import detect_filters
from analysis.filter_engine import apply_filters
from analysis.query_engine import execute_query
from analysis.answer_generator import generate_answer

from agents.visualization_agent import choose_chart
from agents.visualization_agent import create_plotly_chart
from agents.insight_agent import generate_insights
from agents.visualization_agent import create_map_chart
from utils.formatters import compact_value
from agents.recommendation_agent import generate_recommendations
from agents.anomaly_agent import (
    generate_anomaly_insights,
    format_anomaly_insights
)
from agents.quality_agent import (
    analyze_data_quality,
    generate_quality_report
)
from agents.profile_agent import (
    generate_profile,
    generate_profile_report
)
from utils.report_generator import generate_html_report

# =========================================================
# 2. STREAMLIT PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 3. GLOBAL CONSTANTS & CONFIGURATION
# =========================================================
COLOR_PRIMARY = "#0052CC"
COLOR_SECONDARY = "#5243AA"
COLOR_POSITIVE = "#00875A"
COLOR_NEGATIVE = "#DE350B"
COLOR_ACCENT = "#FF991F"
COLOR_NEUTRAL = "#5E6C84"
COLOR_BG_CARD = "#FFFFFF"
COLOR_BG_APP = "#F0F4F8"

CHART_HEIGHT_STANDARD = 320
CHART_HEIGHT_FEATURED = 400
SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL = 8, 16, 24, 32

# Professional global Plotly theme (single source of truth for all charts)
pio.templates["bi_theme"] = pio.templates["plotly_white"]
pio.templates["bi_theme"].layout.colorway = [
    COLOR_PRIMARY, COLOR_POSITIVE, COLOR_ACCENT, COLOR_NEGATIVE, COLOR_SECONDARY,
    "#00B8D9", "#FF5630", "#36B37E", "#FFC400", "#6554C0"
]
pio.templates.default = "bi_theme"

# =========================================================
# 4. CUSTOM CSS / DESIGN SYSTEM
# =========================================================
st.markdown(f"""
    <style>
    .stApp, [data-testid="stAppViewContainer"] {{
        background-color: {COLOR_BG_APP} !important;
    }}
    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    div[data-testid="metric-container"] {{
        background-color: {COLOR_BG_CARD};
        border: 1px solid #DFE1E6;
        padding: 20px 15px;
        border-radius: 10px;
        box-shadow: 0px 4px 6px rgba(9, 30, 66, 0.06);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        transition: box-shadow 0.2s ease-in-out;
    }}
    div[data-testid="metric-container"]:hover {{
        box-shadow: 0px 6px 14px rgba(9, 30, 66, 0.12);
    }}
    div[data-testid="stMetricLabel"] {{
        font-size: 14px;
        font-weight: 600;
        color: {COLOR_NEUTRAL};
        margin-bottom: 5px;
    }}
    div[data-testid="stMetricValue"] {{
        font-size: 26px;
        font-weight: 700;
        color: #172B4D;
    }}
    h1, h2, h3, h4 {{
        color: #172B4D;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    [data-testid="stSidebar"] {{
        background-color: {COLOR_BG_CARD} !important;
        border-right: 1px solid #DFE1E6;
        padding-top: 1.5rem;
    }}
    .stPlotlyChart {{
        background-color: {COLOR_BG_CARD};
        border-radius: 10px;
        box-shadow: 0px 2px 4px rgba(9, 30, 66, 0.05);
        border: 1px solid #DFE1E6;
        padding: 10px;
    }}
    .streamlit-expanderHeader {{
        background-color: {COLOR_BG_CARD};
        border-radius: 8px;
        font-weight: 600;
        color: #172B4D;
    }}
    .insight-card {{
        background-color: {COLOR_BG_CARD};
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: {SPACING_MD}px;
        box-shadow: 0px 2px 6px rgba(9, 30, 66, 0.06);
        border: 1px solid #EBEDF2;
        border-left: 4px solid var(--tone-color, {COLOR_PRIMARY});
        display: flex;
        align-items: flex-start;
        gap: 12px;
        height: 100%;
        transition: box-shadow 0.2s ease-in-out, transform 0.2s ease-in-out;
    }}
    .insight-card:hover {{
        box-shadow: 0px 8px 16px rgba(9, 30, 66, 0.10);
        transform: translateY(-1px);
    }}
    .insight-icon {{
        flex-shrink: 0;
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background-color: var(--tone-bg, #EAF0FF);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }}
    .insight-text {{
        font-size: 14.5px;
        line-height: 1.5;
        color: #253858;
        padding-top: 2px;
    }}
    .insight-text strong {{
        color: #172B4D;
        font-weight: 700;
    }}
    .section-title {{
        margin-top: {SPACING_XL}px;
        margin-bottom: {SPACING_MD}px;
    }}
    </style>
""", unsafe_allow_html=True)


# =========================================================
# HELPER: REUSABLE CHART THEME (avoids repeating styling code)
# =========================================================
def apply_chart_theme(fig, height=CHART_HEIGHT_STANDARD, hovermode="closest"):
    """Apply consistent professional styling to every Plotly chart."""
    fig.update_layout(
        height=height,
        hovermode=hovermode,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Tahoma, Verdana, sans-serif", size=12, color="#172B4D"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        title=dict(font=dict(size=15, color="#172B4D")),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#EEF1F5", zeroline=False)
    return fig


def get_currency_symbol():
    return st.session_state.get("currency_symbol", "₹")


def format_chart_value(value):
    symbol = get_currency_symbol()
    if value >= 1_000_000:
        return f"{symbol}{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{symbol}{value / 1_000:.1f}K"
    else:
        return f"{symbol}{value:,.0f}"


def format_number(value):
    if value >= 10_000_000:
        return f"{value / 10_000_000:.2f} Cr"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.2f} M"
    elif value >= 100_000:
        return f"{value / 100_000:.2f} L"
    elif value >= 1_000:
        return f"{value / 1_000:.1f} K"
    return f"{value:,.0f}"


# Map charts need a column of REAL, geocodable place names (city/state/
# country). Business labels like "Region" (e.g. "East"/"West") or "Segment"
# look like categoricals but aren't places, so a mapping/geocoding call
# finds no matches and silently renders a blank map.
MAP_GEO_COLUMN_PRIORITY = [
    ["city", "town"],
    ["state", "province"],
    ["country", "nation"],
    ["market", "continent"],
]
MAP_NON_GEOGRAPHIC_HINTS = ["region", "segment", "ship_mode", "ship mode", "priority", "mode"]


def pick_map_location_column(string_columns, preferred_column=None):
    """
    Choose the best column to use as the map's location field.
    Trusts `preferred_column` (e.g. from the AI query) only if it doesn't
    look like a non-geographic business label; otherwise falls back to the
    most specific real-geography column available, then to the first
    string column as a last resort.
    """
    preferred_is_non_geographic = (
        isinstance(preferred_column, str)
        and any(hint in preferred_column.lower() for hint in MAP_NON_GEOGRAPHIC_HINTS)
    )
    if preferred_column in string_columns and not preferred_is_non_geographic:
        return preferred_column

    for keyword_group in MAP_GEO_COLUMN_PRIORITY:
        for column in string_columns:
            if any(keyword in column.lower() for keyword in keyword_group):
                return column

    return string_columns[0] if string_columns else None


def calc_period_growth(data, date_col, value_col):
    """
    Split the current (filtered) date range into two equal halves and
    return the % change of the metric from the first half to the second half.
    This gives a meaningful 'growth vs previous period' KPI delta that
    automatically adapts to whatever date range the user has selected.
    """
    valid = data.dropna(subset=[date_col])
    if valid.empty:
        return None
    valid = valid.sort_values(date_col)
    midpoint = valid[date_col].min() + (valid[date_col].max() - valid[date_col].min()) / 2
    first_half = valid[valid[date_col] <= midpoint][value_col].sum()
    second_half = valid[valid[date_col] > midpoint][value_col].sum()
    if first_half == 0:
        return None
    return ((second_half - first_half) / abs(first_half)) * 100


# =========================================================
# 5. SCHEMA DETECTION HELPERS
# =========================================================
def coerce_numeric_like_columns(df):
    """
    Some uploaded files store numeric metrics (Sales, Profit, Quantity...) as
    text — e.g. "$1,204.50", "1,204", "(50.00)" for negatives, or a column
    with a stray blank/text cell that made pandas infer 'object' dtype.
    Those columns are invisible to detect_schema()'s numeric-only matching,
    which causes valid columns to be reported as "missing". This scans
    object columns, strips common currency/formatting characters, and
    promotes a column to numeric if the vast majority of values parse
    cleanly — without touching genuinely categorical/text columns.
    """
    df = df.copy()
    for column in df.columns:
        # Skip columns that are already numeric or already datetime.
        # Works across pandas versions: older pandas defaults text columns
        # to 'object' dtype, newer pandas (2.x/3.x) may default to a
        # dedicated 'string' dtype instead — both need to be checked here.
        if pd.api.types.is_numeric_dtype(df[column]) or pd.api.types.is_datetime64_any_dtype(df[column]):
            continue
        original_non_null = df[column].notna().sum()
        if original_non_null == 0:
            continue
        cleaned = (
            df[column]
            .astype(str)
            .str.replace(r"[₹$£€,]", "", regex=True)
            .str.replace(r"^\((.*)\)$", r"-\1", regex=True)  # (50.00) -> -50.00
            .str.strip()
        )
        converted = pd.to_numeric(cleaned, errors="coerce")
        parse_ratio = converted.notna().sum() / original_non_null
        if parse_ratio >= 0.9:
            df[column] = converted
    return df


def detect_schema(df):
    """
    Inspects a DataFrame and returns metadata describing which columns
    look like numeric metrics, categorical fields, and date fields.
    """
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    categorical_columns = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()

    date_columns = []
    for column in df.columns:
        if "date" in column.lower():
            date_columns.append(column)

    metric_aliases = {
        "sales": ["sales", "revenue", "purchase amount", "purchase amount (usd)", "amount", "income", "price", "value"],
        "profit": ["profit", "profit amount", "net profit", "earnings"],
        "quantity": ["quantity", "qty", "units", "count"],
    }

    metrics = {}
    for metric_name, aliases in metric_aliases.items():
        for column in numeric_columns:
            column_lower = column.lower()
            if any(alias in column_lower for alias in aliases):
                metrics[metric_name] = column
                break

    return {
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "date_columns": date_columns,
        "metrics": metrics,
    }


# Alias lists used to map non-metric standard columns (categoricals, IDs)
CATEGORICAL_ALIASES = {
    # Sub_Category is checked before Category: "category" is a substring of
    # "sub_category" / "sub category", so matching Category first would
    # wrongly claim the sub-category column.
    "Sub_Category": ["sub category", "sub-category", "subcategory", "sub_category"],
    "Category": ["product category", "category", "segment", "department"],
    "Product": ["product name", "product", "item name", "item"],
    "Region": ["region", "state", "market", "location", "area", "country"],
}

ID_ALIASES = ["order id", "order number", "transaction id", "invoice id", "order_id", "orderid", "id"]

# The columns the rest of the dashboard depends on. All must be resolvable
# (either found directly, or renamed from a detected alias) or we stop.
REQUIRED_STANDARD_COLUMNS = [
    "Order_Date", "Sales", "Profit", "Quantity",
    "Category", "Product", "Region", "Order_ID",
]


def _normalize_column_name(name):
    """Lowercase and turn underscores/hyphens into spaces so 'product_name'
    lines up with the alias phrase 'product name'."""
    return name.lower().replace("_", " ").replace("-", " ").strip()


def _find_categorical_match(candidate_columns, aliases):
    """
    Return the best-matching column for a list of alias phrases, given in
    priority order (most specific first, e.g. "product name" before the
    generic "product"). Matching is done alias-by-alias rather than
    column-by-column: this ensures a specific alias like "product name"
    beats a generic one like "product" even if the generic one appears
    earlier in the dataframe's column order (e.g. "product_id" would
    otherwise wrongly win over "product_name").
    """
    normalized_lookup = {_normalize_column_name(col): col for col in candidate_columns}

    # Pass 1: exact match, trying aliases in priority order.
    for alias in aliases:
        if alias in normalized_lookup:
            return normalized_lookup[alias]

    # Pass 2: substring match, trying aliases in priority order.
    for alias in aliases:
        for column in candidate_columns:
            if alias in _normalize_column_name(column):
                return column

    return None


def map_schema_to_standard(df):
    """
    Uses detect_schema() plus alias matching to build a rename map from the
    uploaded file's actual column names to the dashboard's standard names.
    Returns (renamed_df, missing_columns).
    """
    df = coerce_numeric_like_columns(df)
    schema = detect_schema(df)
    rename_map = {}
    used_source_columns = set()

    # --- Numeric metrics: Sales, Profit, Quantity ---
    metric_to_standard = {"sales": "Sales", "profit": "Profit", "quantity": "Quantity"}
    for metric_key, standard_name in metric_to_standard.items():
        source_col = schema["metrics"].get(metric_key)
        if source_col and source_col not in used_source_columns:
            rename_map[source_col] = standard_name
            used_source_columns.add(source_col)

    # --- Date column: Order_Date ---
    if schema["date_columns"]:
        date_source = schema["date_columns"][0]
        if date_source not in used_source_columns:
            rename_map[date_source] = "Order_Date"
            used_source_columns.add(date_source)

    # --- Order ID ---
    remaining_columns = [c for c in df.columns if c not in used_source_columns]
    id_source = _find_categorical_match(remaining_columns, ID_ALIASES)
    if id_source:
        rename_map[id_source] = "Order_ID"
        used_source_columns.add(id_source)

    # --- Categorical columns: Category, Product, Region ---
    for standard_name, aliases in CATEGORICAL_ALIASES.items():
        remaining_columns = [c for c in df.columns if c not in used_source_columns]
        match = _find_categorical_match(remaining_columns, aliases)
        if match:
            rename_map[match] = standard_name
            used_source_columns.add(match)

    renamed_df = df.rename(columns=rename_map)

    missing_columns = [col for col in REQUIRED_STANDARD_COLUMNS if col not in renamed_df.columns]

    return renamed_df, missing_columns, rename_map


# =========================================================
# 6. FILE UPLOAD SECTION (must run before any filters/charts)
# =========================================================
st.markdown("## 📁 Upload Your Sales Data")
st.caption("Upload a CSV or Excel file. Columns are automatically matched to the dashboard's expected schema "
           "(Order Date, Sales, Profit, Quantity, Category, Product, Region, Order ID).")

upload_col, currency_col = st.columns([3, 1])

with upload_col:
    uploaded_file = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx"],
        help="Accepted formats: .csv, .xlsx",
    )

with currency_col:
    currency_options = {"₹ INR": "₹", "$ USD": "$", "€ EUR": "€", "£ GBP": "£", "No symbol": ""}
    currency_label = st.selectbox("Currency", options=list(currency_options.keys()), index=1)
    st.session_state.currency_symbol = currency_options[currency_label]

if uploaded_file is None:
    st.info("Please upload a CSV or Excel file to begin.")
    st.stop()

# Only re-parse and re-map the file when a new/different file is uploaded,
# so the mapped data persists across reruns triggered by filters etc.
file_identity = (uploaded_file.name, uploaded_file.size)

if st.session_state.get("uploaded_file_identity") != file_identity:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            raw_df = pd.read_csv(uploaded_file)
        else:
            raw_df = pd.read_excel(uploaded_file)
    except Exception as exc:
        st.error(f"Could not read the uploaded file. It may be corrupted or in an unsupported format. Details: {exc}")
        st.stop()

    if raw_df.empty:
        st.error("The uploaded file appears to be empty. Please upload a file that contains data.")
        st.stop()

    try:
        mapped_df, missing_columns, rename_map = map_schema_to_standard(raw_df)
    except Exception as exc:
        st.error(f"Something went wrong while analyzing the file's structure. Details: {exc}")
        st.stop()

    if missing_columns:
        st.error(
            "Your file is missing data the dashboard needs to work: "
            f"**{', '.join(missing_columns)}**. "
            "Please check your column headers (e.g. a date column, a sales/revenue column, "
            "a product/category column) and re-upload."
        )
        st.stop()

    st.session_state.uploaded_df = mapped_df
    st.session_state.uploaded_file_identity = file_identity
    st.session_state.uploaded_rename_map = rename_map

with st.expander("🔍 How your columns were mapped", expanded=False):
    if st.session_state.get("uploaded_rename_map"):
        mapping_display = pd.DataFrame(
            [{"Your Column": src, "Mapped To": dst} for src, dst in st.session_state.uploaded_rename_map.items()]
        )
        st.dataframe(mapping_display, use_container_width=True, hide_index=True)
    else:
        st.write("No column renaming was necessary — your file already used the standard column names.")

df = st.session_state.uploaded_df.copy()

st.success(f"Loaded **{uploaded_file.name}** — {df.shape[0]:,} rows detected.")
st.divider()

# =========================================================
# 7. DATA CLEANING & VALIDATION
# =========================================================
df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
for numeric_col in ["Sales", "Profit", "Quantity"]:
    if numeric_col in df.columns:
        df[numeric_col] = pd.to_numeric(df[numeric_col], errors="coerce")

n_missing_dates = df["Order_Date"].isna().sum()
if n_missing_dates > 0:
    df = df[df["Order_Date"].notna()]

if df.empty:
    st.error("After cleaning, no valid rows remained (e.g. all dates failed to parse). "
              "Please check the date column format in your file and re-upload.")
    st.stop()

# =========================================================
# 8. FEATURE ENGINEERING
# =========================================================
df["Month"] = df["Order_Date"].dt.to_period("M").astype(str)
df["Year"] = df["Order_Date"].dt.year
df["Quarter"] = df["Order_Date"].dt.to_period("Q").astype(str)

# =========================================================
# 9. SIDEBAR FILTERS
# =========================================================
if "filters_reset" not in st.session_state:
    st.session_state.filters_reset = 0

st.sidebar.markdown("## 🎛️ Dashboard Filters")
st.sidebar.caption("Adjust the context for every KPI, chart, and insight below.")
st.sidebar.divider()

regions = sorted(df["Region"].dropna().unique().tolist())
categories = sorted(df["Category"].dropna().unique().tolist())
products = sorted(df["Product"].dropna().unique().tolist())
min_date = df["Order_Date"].min().date()
max_date = df["Order_Date"].max().date()

reset_suffix = st.session_state.filters_reset

with st.sidebar.expander("📅 Time Period", expanded=True):
    selected_dates = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key=f"date_{reset_suffix}",
    )

with st.sidebar.expander("🌍 Geography", expanded=True):
    selected_regions = st.multiselect("Region", options=regions, default=regions, key=f"region_{reset_suffix}")

with st.sidebar.expander("📂 Business", expanded=True):
    selected_categories = st.multiselect("Category", options=categories, default=categories, key=f"category_{reset_suffix}")

    if "Sub_Category" in df.columns:
        sub_categories = sorted(df["Sub_Category"].dropna().unique().tolist())
        selected_sub_categories = st.multiselect(
            "Sub-Category", options=sub_categories, default=sub_categories, key=f"subcategory_{reset_suffix}"
        )
    else:
        selected_sub_categories = None
        st.caption("ℹ️ Sub-Category is not available in this dataset.")

    selected_products = st.multiselect("Product", options=products, default=products, key=f"product_{reset_suffix}")

st.sidebar.divider()
if st.sidebar.button("🔄 Reset Filters", use_container_width=True):
    st.session_state.filters_reset += 1
    st.rerun()

# =========================================================
# 10. FILTERED DATA
# =========================================================
filtered_df = df.copy()

if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered_df = filtered_df[
        (filtered_df["Order_Date"].dt.date >= start_date) &
        (filtered_df["Order_Date"].dt.date <= end_date)
    ]

# Safe filtering: if user clears the box, act as if "All" are selected
active_regions = selected_regions if selected_regions else regions
active_categories = selected_categories if selected_categories else categories
active_products = selected_products if selected_products else products

filtered_df = filtered_df[
    (filtered_df["Region"].isin(active_regions)) &
    (filtered_df["Category"].isin(active_categories)) &
    (filtered_df["Product"].isin(active_products))
]

if "Sub_Category" in filtered_df.columns and selected_sub_categories is not None:
    sub_categories = sorted(df["Sub_Category"].dropna().unique().tolist())
    active_sub_categories = selected_sub_categories if selected_sub_categories else sub_categories
    filtered_df = filtered_df[filtered_df["Sub_Category"].isin(active_sub_categories)]

if filtered_df.empty:
    st.warning("No data matches the selected filters. Please adjust your criteria.")
    st.stop()

# =========================================================
# 11. KPI CALCULATIONS
# =========================================================
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_quantity = filtered_df["Quantity"].sum()
total_orders = filtered_df["Order_ID"].nunique()
avg_order_value = total_sales / total_orders if total_orders else 0
profit_margin = (total_profit / total_sales * 100) if total_sales != 0 else 0

sales_growth = calc_period_growth(filtered_df, "Order_Date", "Sales")
profit_growth = calc_period_growth(filtered_df, "Order_Date", "Profit")

# =========================================================
# 12. DASHBOARD HEADER
# =========================================================
st.markdown("""
    <div style="padding: 10px 0px 20px 0px;">
        <h1 style="margin: 0; padding: 0; font-size: 36px;">📊 Executive Sales Analytics</h1>
        <p style="color: #5E6C84; font-size: 16px; margin-top: 5px;">
            Interactive business intelligence and performance analysis dashboard.
        </p>
    </div>
""", unsafe_allow_html=True)

# =========================================================
# 13. EXECUTIVE KPI SECTION
# =========================================================
c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.metric("Total Sales", format_number(total_sales),
               delta=f"{sales_growth:+.1f}% vs prior period" if sales_growth is not None else None)
with c2:
    st.metric("Total Profit", format_number(total_profit),
               delta=f"{profit_growth:+.1f}% vs prior period" if profit_growth is not None else None)
with c3:
    st.metric("Profit Margin", f"{profit_margin:.1f}%")
with c4:
    st.metric("Total Orders", f"{total_orders:,.0f}")
with c5:
    st.metric("Avg Order Value", format_number(avg_order_value))
with c6:
    st.metric("Quantity Sold", f"{total_quantity:,.0f}")

# =========================================================
# 14. MAIN TREND ANALYSIS
# =========================================================
st.markdown("### 📈 Performance Trend Analysis", help="How sales and profitability evolve over time.")

monthly = (
    filtered_df.groupby("Month", as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
    .sort_values("Month")
)
category_sales = filtered_df.groupby("Category", as_index=False)["Sales"].sum()

trend_left, trend_right = st.columns(2)

with trend_left:
    fig_line = px.line(monthly, x="Month", y=["Sales", "Profit"], markers=True,
                        title="Monthly Sales & Profit Trend")
    fig_line.update_traces(line=dict(width=3), marker=dict(size=7))
    fig_line = apply_chart_theme(fig_line, hovermode="x unified")
    st.plotly_chart(fig_line, use_container_width=True)

with trend_right:
    fig_pie = px.pie(category_sales, names="Category", values="Sales", hole=0.5,
                      title="Sales Contribution by Category")
    fig_pie.update_traces(textinfo="percent+label",
                           hovertemplate="%{label}<br>Sales: %{value:,.0f}<br>Share: %{percent}<extra></extra>")
    fig_pie = apply_chart_theme(fig_pie)
    st.plotly_chart(fig_pie, use_container_width=True)

if monthly.shape[0] >= 2:
    peak_month = monthly.loc[monthly["Sales"].idxmax(), "Month"]
    low_month = monthly.loc[monthly["Sales"].idxmin(), "Month"]
    st.caption(f"📌 Peak sales month: **{peak_month}**  |  Lowest sales month: **{low_month}**")

# =========================================================
# 15. CATEGORY / SEGMENT ANALYSIS
# =========================================================
st.markdown("### 📊 Product & Category Analysis", help="What drives revenue and where the opportunities are.")

product_perf = (
    filtered_df.groupby("Product", as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
)
top10 = product_perf.sort_values("Sales", ascending=False).head(10)
bottom10 = product_perf.sort_values("Sales", ascending=True).head(10)

prod_left, prod_right = st.columns(2)

with prod_left:
    top10 = top10.assign(DisplaySales=top10["Sales"].apply(format_chart_value))
    fig_top = px.bar(top10.sort_values("Sales"), x="Sales", y="Product", orientation="h",
                      text="DisplaySales", title="Top 10 Products by Sales", color_discrete_sequence=[COLOR_PRIMARY])
    fig_top.update_traces(textposition="outside")
    fig_top = apply_chart_theme(fig_top)
    st.plotly_chart(fig_top, use_container_width=True)

with prod_right:
    bottom10 = bottom10.assign(DisplaySales=bottom10["Sales"].apply(format_chart_value))
    fig_bottom = px.bar(bottom10.sort_values("Sales", ascending=False), x="Sales", y="Product", orientation="h",
                         text="DisplaySales", title="Bottom 10 Products by Sales", color_discrete_sequence=[COLOR_NEGATIVE])
    fig_bottom.update_traces(textposition="outside")
    fig_bottom = apply_chart_theme(fig_bottom)
    st.plotly_chart(fig_bottom, use_container_width=True)

# =========================================================
# 16. REGIONAL ANALYSIS
# =========================================================
st.markdown("### 🌍 Regional Performance", help="Best and worst performing markets.")

region_perf = (
    filtered_df.groupby("Region", as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"))
    .sort_values("Sales", ascending=False)
)
region_perf["DisplaySales"] = region_perf["Sales"].apply(format_chart_value)

reg_left, reg_right = st.columns(2)

with reg_left:
    fig_region_sales = px.bar(region_perf, x="Region", y="Sales", text="DisplaySales", color="Profit",
                               title="Sales & Profit by Region",
                               color_continuous_scale=["#DE350B", "#FF991F", "#00875A"])
    fig_region_sales.update_traces(textposition="outside")
    fig_region_sales = apply_chart_theme(fig_region_sales)
    st.plotly_chart(fig_region_sales, use_container_width=True)

with reg_right:
    scatter_df = filtered_df.groupby(["Product", "Category"], as_index=False).agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum")
    )
    fig_scatter = px.scatter(scatter_df, x="Sales", y="Profit", size="Quantity", hover_name="Product",
                              color="Category", title="Product Sales vs Profit Matrix")
    fig_scatter = apply_chart_theme(fig_scatter)
    st.plotly_chart(fig_scatter, use_container_width=True)

# =========================================================
# 17. ADVANCED ANALYTICS — DYNAMIC BUSINESS INSIGHTS
# =========================================================
st.markdown("### 🧠 Key Business Insights", help="Automatically generated from the currently filtered data.")

# Tone -> (accent color, icon background) so every card reads at a glance
TONE_STYLES = {
    "success": (COLOR_POSITIVE, "#E3FCEF"),
    "warning": (COLOR_ACCENT, "#FFF4E5"),
    "danger": (COLOR_NEGATIVE, "#FFEBE6"),
    "info": (COLOR_PRIMARY, "#EAF0FF"),
}

business_insights = []  # list of dicts: icon, html text, tone

best_category_row = category_sales.loc[category_sales["Sales"].idxmax()]
business_insights.append({
    "icon": "🏆",
    "tone": "success",
    "text": (f"<strong>{best_category_row['Category']}</strong> is the top-performing category, "
              f"generating <strong>{format_number(best_category_row['Sales'])}</strong> in sales."),
})

most_profitable_region = region_perf.iloc[0]
weakest_region = region_perf.iloc[-1]
business_insights.append({
    "icon": "🌍",
    "tone": "info",
    "text": (f"<strong>{most_profitable_region['Region']}</strong> leads in sales at "
              f"<strong>{format_number(most_profitable_region['Sales'])}</strong>, while "
              f"<strong>{weakest_region['Region']}</strong> trails at "
              f"<strong>{format_number(weakest_region['Sales'])}</strong>."),
})

if not top10.empty:
    top_product_row = product_perf.sort_values("Sales", ascending=False).iloc[0]
    business_insights.append({
        "icon": "📦",
        "tone": "success",
        "text": (f"<strong>{top_product_row['Product']}</strong> is the best-selling product, "
                  f"contributing <strong>{format_number(top_product_row['Sales'])}</strong> in revenue."),
    })

# High sales / low profitability check
product_perf_nonzero = product_perf[product_perf["Sales"] > 0].copy()
if not product_perf_nonzero.empty:
    product_perf_nonzero["Margin"] = product_perf_nonzero["Profit"] / product_perf_nonzero["Sales"] * 100
    low_margin_high_sales = product_perf_nonzero.sort_values(
        ["Sales", "Margin"], ascending=[False, True]
    ).head(3)
    low_margin_candidate = low_margin_high_sales[low_margin_high_sales["Margin"] < profit_margin].head(1)
    if not low_margin_candidate.empty:
        row = low_margin_candidate.iloc[0]
        business_insights.append({
            "icon": "⚠️",
            "tone": "warning",
            "text": (f"<strong>{row['Product']}</strong> drives strong sales but has a below-average margin of "
                      f"<strong>{row['Margin']:.1f}%</strong>, worth a pricing or cost review."),
        })

if sales_growth is not None:
    trend_word = "growing" if sales_growth > 0 else "declining"
    tone = "success" if sales_growth > 0 else "danger"
    business_insights.append({
        "icon": "📈" if sales_growth > 0 else "📉",
        "tone": tone,
        "text": f"Sales are <strong>{trend_word}</strong> at <strong>{sales_growth:+.1f}%</strong> across the selected period.",
    })

insight_cols = st.columns(2)
for idx, item in enumerate(business_insights[:6]):
    accent_color, icon_bg = TONE_STYLES.get(item["tone"], TONE_STYLES["info"])
    card_html = (
        f"<div class='insight-card' style='--tone-color:{accent_color}; --tone-bg:{icon_bg};'>"
        f"<div class='insight-icon'>{item['icon']}</div>"
        f"<div class='insight-text'>{item['text']}</div>"
        f"</div>"
    )
    with insight_cols[idx % 2]:
        st.markdown(card_html, unsafe_allow_html=True)

# =========================================================
# 18. AI DATA ANALYST (existing capability, preserved)
# =========================================================
st.markdown("<br><hr><br>", unsafe_allow_html=True)
st.markdown("### 🤖 Ask Your Data (AI Analyst)")
st.caption("Ask questions in plain English to automatically generate insights, recommendations, and custom charts.")

user_query = st.text_input(
    "Query your dataset",
    placeholder="Example: show Map sales by city / Show me top 5 products by sales"
)

if user_query:
    with st.spinner("🧠 AI is analyzing your data..."):

        # 1. Understand query
        intent = understand_query(user_query)

        # Smart Entity Extractor
        if intent and isinstance(intent, dict):
            query_lower = user_query.lower()
            plural_fixes = {"cities": "city", "categories": "category", "products": "product", "states": "state", "regions": "region", "profits": "profit", "quantities": "quantity"}
            for p, s in plural_fixes.items(): query_lower = query_lower.replace(p, s)
            for col in df.columns:
                if col.lower() in query_lower:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        if not intent.get("metric"): intent["metric"] = col
                    else:
                        if not intent.get("group_by"): intent["group_by"] = col
            if intent.get("type") in ["top", "bottom"]:
                numbers = re.findall(r'\d+', query_lower)
                intent["limit"] = int(numbers[0]) if numbers else 5

        # 2. Detect & Apply filters
        filters = detect_filters(user_query, df)
        query_df = apply_filters(df, filters)

        # 3. Execute query
        if intent is None:
            st.error("Query Agent could not understand this question. Please rephrase.")
        else:
            result = execute_query(query_df, intent)

            if result is None:
                st.warning("I could not find a result for this query.")
            else:
                # --- A. AI ANSWER (Top, Full Width) ---
                answer = generate_answer(user_query, intent, result)
                st.success(f"**Answer:** {answer}")

                # --- B. HORIZONTAL INSIGHTS & RECOMMENDATIONS ---
                col_insights, col_recs = st.columns(2)

                anomaly_results = None
                with col_insights:
                    try:
                        insights = generate_insights(result, intent)
                        if insights:
                            st.markdown("#### 💡 Business Insights")
                            for insight in insights: st.info(insight)
                    except Exception:
                        insights = None

                    query_type = intent.get("type")
                    metric = intent.get("metric")
                    if query_type == "anomaly" and metric:
                        anomaly_results = generate_anomaly_insights(filtered_df, selected_metric=metric)
                        if anomaly_results:
                            st.markdown("#### 🚨 Anomalies Detected")
                            for anomaly in format_anomaly_insights(anomaly_results): st.warning(anomaly)
                        else:
                            st.success(f"✅ No significant {metric} anomalies detected.")

                with col_recs:
                    recommendations = generate_recommendations(result=result, intent=intent, anomaly_insights=anomaly_results)
                    if recommendations:
                        st.markdown("#### 🎯 Business Recommendations")
                        for recommendation in recommendations:
                            if recommendation.startswith("💡"): st.success(recommendation)
                            elif recommendation.startswith("📉"): st.warning(recommendation)
                            elif recommendation.startswith("🎯"): st.info(recommendation)
                            elif recommendation.startswith("⚠️"): st.error(recommendation)
                            else: st.info(recommendation)

                # --- C. FULL WIDTH CHART (Below Insights/Recs) ---
                st.divider()
                st.markdown("#### 📊 Custom AI Visualization")

                c_sel, _ = st.columns([1, 3])
                with c_sel:
                    chart_options = ["Auto", "Bar", "Line", "Pie", "Scatter", "Histogram", "Box Plot", "Correlation Heatmap", "Map"]
                    selected_chart = st.selectbox("Choose chart type", chart_options, key="ai_chart_type", label_visibility="collapsed")

                chart = None
                if selected_chart == "Auto":
                    chart_type = choose_chart(intent)
                    if "map" in user_query.lower():
                        chart_type = "map"
                        query_string_columns = query_df.select_dtypes(include=["object", "string"]).columns.tolist()
                        intent["group_by"] = pick_map_location_column(query_string_columns, intent.get("group_by")) or "City"
                        if not intent.get("metric"): intent["metric"] = "Sales"
                    if chart_type == "map":
                        chart = create_map_chart(query_df, intent.get("metric", "Sales"), intent.get("group_by", "City"))
                    else:
                        chart = create_plotly_chart(result, intent)

                elif selected_chart == "Bar":
                    chart_df = result.reset_index() if hasattr(result, "reset_index") else result
                    if len(chart_df.columns) >= 2:
                        chart_df.columns = [intent["group_by"], intent["metric"]]
                        chart_df[intent["metric"]] = pd.to_numeric(chart_df[intent["metric"]], errors="coerce")
                        chart_df["DisplayValue"] = chart_df[intent["metric"]].apply(format_chart_value)
                        chart = px.bar(chart_df, x=intent["group_by"], y=intent["metric"], custom_data=["DisplayValue"], title=f"{intent['metric']} by {intent['group_by']}")
                        chart.update_traces(texttemplate="%{customdata[0]}", textposition="outside", hovertemplate="<b>%{x}</b><br>Sales: " + get_currency_symbol() + "%{y:,.2f}<extra></extra>")

                elif selected_chart == "Line":
                    if hasattr(result, "reset_index"):
                        chart_df = result.reset_index()
                        chart_df.columns = [intent["group_by"] or "Month", intent["metric"]]
                        chart = px.line(chart_df, x=chart_df.columns[0], y=intent["metric"], markers=True, title=f"{intent['metric']} Trend")
                        chart.update_traces(textposition="top center", hovertemplate="<b>%{x}</b><br>" + f"{intent['metric']}: {get_currency_symbol()}%{{y:,.2f}}<extra></extra>")
                        chart.update_layout(xaxis_title="Month", yaxis_title=intent["metric"])

                elif selected_chart == "Pie":
                    chart_df = result.reset_index() if hasattr(result, "reset_index") else result
                    if len(chart_df.columns) >= 2:
                        chart_df.columns = [intent["group_by"], intent["metric"]]
                        chart = px.pie(chart_df, names=intent["group_by"], values=intent["metric"], hole=0.45, title=f"{intent['metric']} Share by {intent['group_by']}")
                        chart.update_traces(hovertemplate="<b>%{label}</b><br>" + f"{intent['metric']}: {get_currency_symbol()}%{{value:,.2f}}<br>Share: %{{percent}}<extra></extra>")

                elif selected_chart == "Scatter":
                    numeric_columns = query_df.select_dtypes(include="number").columns.tolist()
                    if len(numeric_columns) >= 2:
                        c_x, c_y, _ = st.columns([1, 1, 2])
                        with c_x: x_column = st.selectbox("X-axis", numeric_columns, key="scatter_x")
                        with c_y: y_column = st.selectbox("Y-axis", numeric_columns, index=1, key="scatter_y")
                        chart = px.scatter(query_df, x=x_column, y=y_column, hover_data=query_df.columns, title=f"{y_column} vs {x_column}")
                        chart.update_layout(xaxis_title=x_column, yaxis_title=y_column)

                elif selected_chart == "Histogram":
                    numeric_columns = query_df.select_dtypes(include="number").columns.tolist()
                    if len(numeric_columns) >= 1:
                        c_h, _ = st.columns([1, 3])
                        with c_h: histogram_column = st.selectbox("Select numeric column", numeric_columns, key="histogram_column")
                        chart = px.histogram(query_df, x=histogram_column, nbins=30, title=f"{histogram_column} Distribution")
                        chart.update_layout(xaxis_title=histogram_column, yaxis_title="Count")

                elif selected_chart == "Box Plot":
                    numeric_columns = query_df.select_dtypes(include="number").columns.tolist()
                    if len(numeric_columns) >= 1:
                        c_b, _ = st.columns([1, 3])
                        with c_b: box_column = st.selectbox("Select numeric column", numeric_columns, key="box_column")
                        chart = px.box(query_df, y=box_column, points="outliers", title=f"{box_column} Distribution & Outliers")
                        chart.update_layout(yaxis_title=box_column)

                elif selected_chart == "Correlation Heatmap":
                    numeric_df = query_df.select_dtypes(include="number")
                    if numeric_df.shape[1] >= 2:
                        correlation = numeric_df.corr()
                        chart = px.imshow(correlation, text_auto=".2f", aspect="auto", title="Correlation Heatmap")

                elif selected_chart == "Map":
                    numeric_columns = query_df.select_dtypes(include="number").columns.tolist()
                    string_columns = query_df.select_dtypes(include=["object", "string"]).columns.tolist()
                    if len(numeric_columns) >= 1 and len(string_columns) >= 1:
                        default_location_column = pick_map_location_column(string_columns, intent.get("group_by"))
                        default_loc_idx = string_columns.index(default_location_column) if default_location_column in string_columns else 0
                        default_met_idx = numeric_columns.index(intent.get("metric")) if intent.get("metric") in numeric_columns else 0

                        c_loc, c_met, _ = st.columns([1, 1, 2])
                        with c_loc: location_column = st.selectbox("Location (e.g., City, State, Country)", string_columns, index=default_loc_idx, key="map_location")
                        with c_met: map_metric = st.selectbox("Metric", numeric_columns, index=default_met_idx, key="map_metric")

                        if any(hint in location_column.lower() for hint in MAP_NON_GEOGRAPHIC_HINTS):
                            st.warning(
                                f"⚠️ **{location_column}** looks like a business label (e.g. sales territory), not a real "
                                "place name, so the map will likely render blank. Try City, State, or Country instead."
                            )

                        chart = create_map_chart(df=query_df, metric=map_metric, location_column=location_column)

                if chart is not None:
                    chart = apply_chart_theme(chart, height=CHART_HEIGHT_FEATURED)
                    st.plotly_chart(chart, use_container_width=True)

                # AI Analysis Report Export
                st.divider()
                st.subheader("📄 Export AI Analysis")
                report_html = generate_html_report(
                    filtered_df=query_df, query=user_query, answer=answer,
                    result=result, insights=insights if 'insights' in locals() else None,
                    recommendations=recommendations if 'recommendations' in locals() else None,
                    anomaly_insights=anomaly_results, intent=intent
                )
                st.download_button(
                    label="📥 Download Complete AI Report (HTML)",
                    data=report_html, file_name="AI_Data_Analyst_Report.html", mime="text/html"
                )

# =========================================================
# 19. DATA HEALTH, PROFILE & DETAIL TABLE
# =========================================================
st.markdown("<br><hr><br>", unsafe_allow_html=True)
st.markdown("### 🧹 Data Health & Quality")
health_col1, health_col2 = st.columns(2)

with health_col1:
    profile = generate_profile(filtered_df)
    if profile:
        with st.expander("📋 Dataset Profile", expanded=False):
            for line in generate_profile_report(profile):
                st.write(line)

with health_col2:
    quality_result = analyze_data_quality(filtered_df)
    if quality_result:
        with st.expander("🧹 Data Quality Report", expanded=False):
            st.metric("Data Quality Score", f"{quality_result['score']}/100")
            st.caption(f"Status: {quality_result['label']}")
            st.divider()
            for item in generate_quality_report(quality_result):
                st.write(item)

st.markdown("### 📋 Filtered Data Table")
with st.expander("View and Export Raw Data", expanded=False):
    st.dataframe(filtered_df, use_container_width=True)
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered CSV",
        data=csv,
        file_name="filtered_sales.csv",
        mime="text/csv"
    )

# =========================================================
# 20. FOOTER
# =========================================================
st.markdown("""
    <div style="text-align: center; padding: 20px; color: #5E6C84; font-size: 14px;">
        <hr>
        <p><strong>Executive Sales Analytics</strong> — Interactive Business Intelligence & Data Analytics Platform</p>
        <p>Powered by Python, Streamlit, and Plotly</p>
    </div>
""", unsafe_allow_html=True)