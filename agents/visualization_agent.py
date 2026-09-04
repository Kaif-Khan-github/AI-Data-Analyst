import plotly.express as px
import pandas as pd
import time
import requests
from utils.formatters import compact_value

# --------------------------------
# City Coordinates Lookup
# --------------------------------
CITY_COORDINATES = {
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.6139, 77.2090),
    "Bangalore": (12.9716, 77.5946),
    "Bengaluru": (12.9716, 77.5946),
    "Pune": (18.5204, 73.8567),
    "Hyderabad": (17.3850, 78.4867),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Surat": (21.1702, 72.8311),
    "Nagpur": (21.1458, 79.0882),
    "Lucknow": (26.8467, 80.9462),
    "Indore": (22.7196, 75.8577),
    "Bhopal": (23.2599, 77.4126)
}

def get_coordinates(place_name):
    """
    Fetches coordinates from cache, or falls back to the OpenStreetMap API
    directly. Works for ANY real place name — city, state/province, or
    country — not just cities. The cache dict is keyed by the raw place
    name string, so a state called "Maharashtra" and a city called
    "Mumbai" simply live as separate cache entries.
    """
    if not place_name or pd.isna(place_name):
        return (None, None)

    place_name = str(place_name).strip()

    # 1. Check local cache first (Instant execution)
    if place_name in CITY_COORDINATES:
        return CITY_COORDINATES[place_name]

    # 2. Use direct API request to avoid memory limits
    try:
        time.sleep(1) # Respect rate limits

        url = f"https://nominatim.openstreetmap.org/search?q={place_name}&format=json&limit=1"
        headers = {"User-Agent": "autonomous_data_analyst_v1"}

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data:
                # API returns strings, so we convert to float
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])

                print(f"API fetched coordinates for: {place_name}")
                CITY_COORDINATES[place_name] = (lat, lon)
                return (lat, lon)

    except Exception as e:
        print(f"Warning: Geocoding failed for {place_name} - {e}")

    return (None, None)


def choose_chart(intent):

    if intent is None:
        return None

    # --------------------------------
    # Explicit chart detected
    # --------------------------------

    chart_type = intent.get("chart_type")

    if chart_type:
        return chart_type


    intent_type = intent.get("type")
    # --------------------------------
    # Relationship -> Scatter
    # --------------------------------
    if intent_type == "relationship":
        return "scatter"

    # --------------------------------
    # Trend
    # --------------------------------

    if intent.get("type") == "trend":
        return "line"

    # --------------------------------
    # Share
    # --------------------------------

    if intent.get("share", False):
        return "pie"



    # --------------------------------
    # Distribution -> Histogram
    # --------------------------------
    if intent_type == "distribution":
        return "histogram"
    # --------------------------------
    # Grouped analysis
    # --------------------------------

    if intent.get("type") in [
        "group",
        "top",
        "bottom"
    ]:

        if intent.get("group_by"):
            return "bar"

    return None


def create_map_chart(df, metric, location_column):

    if df is None or df.empty:
        return None

    # --------------------------------
    # Case 1: Dataset already has coordinates
    # --------------------------------

    if (
        "Latitude" in df.columns
        and "Longitude" in df.columns
    ):

        map_df = df.copy()

    # --------------------------------
    # Case 2: Geocode from a place-name column.
    #
    # Previously this only ran when location_column == "City", so any
    # other real place-name column (State, Country, Market, ...) fell
    # through to `return None` and rendered a blank map, even though
    # get_coordinates() geocodes any place name just fine. Generalized
    # to accept whichever column the caller passes in, as long as it's
    # an actual column in the dataframe.
    # --------------------------------

    elif location_column in df.columns:
        map_df = df.copy()

        # Get unique place names to minimize API calls
        unique_places = map_df[location_column].unique()

        # Build a temporary mapping for just the places in this dataset
        coord_map = {place: get_coordinates(place) for place in unique_places}

        # Apply the mapping to the dataframe
        map_df["Latitude"] = map_df[location_column].map(lambda x: coord_map.get(x, (None, None))[0])
        map_df["Longitude"] = map_df[location_column].map(lambda x: coord_map.get(x, (None, None))[1])

    else:
        return None

    # --------------------------------
    # Remove unknown locations
    # --------------------------------

    map_df = map_df.dropna(
        subset=["Latitude", "Longitude"]
    )

    if map_df.empty:
        return None

    # --------------------------------
    # Aggregate by location
    # --------------------------------

    map_df = (
        map_df
        .groupby(location_column, as_index=False)
        .agg(
            **{
                metric: (metric, "sum"),
                "Latitude": ("Latitude", "first"),
                "Longitude": ("Longitude", "first")
            }
        )
    )

    # --------------------------------
    # Create map
    # --------------------------------

    fig = px.scatter_map(
        map_df,
        lat="Latitude",
        lon="Longitude",
        size=metric,
        color=metric,
        hover_name=location_column,
        hover_data={
            metric: ":,.0f"
        },
        zoom=4,
        height=600,
        title=f"{metric} by {location_column}"
    )

    fig.update_layout(
        map_style="open-street-map",
        template="plotly_white"
    )

    return fig


def create_plotly_chart(result, intent):

    if result is None:
        return None

    chart_type = choose_chart(intent)

    if chart_type is None:
        return None

    metric = intent.get("metric")
    group_by = intent.get("group_by")

    # --------------------------------
# Convert result to DataFrame
# --------------------------------

    if isinstance(result, pd.DataFrame):

        chart_df = result.copy()

    elif hasattr(result, "reset_index"):

        chart_df = result.reset_index()

    else:

        return None

    # --------------------------------
    # Rename grouped result
    # --------------------------------

    if group_by and metric:

        if len(chart_df.columns) >= 2:

            chart_df = chart_df.iloc[:, :2]

            chart_df.columns = [
                group_by,
                metric
            ]

    # --------------------------------
    # Make metric numeric
    # --------------------------------

    if metric in chart_df.columns:

        chart_df[metric] = pd.to_numeric(
            chart_df[metric],
            errors="coerce"
        )

        chart_df = chart_df.dropna(
            subset=[metric]
        )

        # Display-only value
        chart_df["DisplayValue"] = (
            chart_df[metric].apply(compact_value)
        )

    # =================================
    # LINE CHART
    # =================================

    if chart_type == "line":

        x_column = group_by

        if x_column is None:
            x_column = chart_df.columns[0]

        fig = px.line(
            chart_df,
            x=x_column,
            y=metric,
            text="DisplayValue",
            markers=True,
            title=f"{metric} Trend"
        )

        fig.update_traces(
            textposition="top center"
        )

    # =================================
    # HORIZONTAL BAR
    # =================================

    elif chart_type == "horizontal_bar":

        if group_by is None:
            return None

        fig = px.bar(
            chart_df,
            x=metric,
            y=group_by,
            orientation="h",
            text="DisplayValue",
            title=f"{metric} by {group_by}"
        )

        fig.update_traces(
            textposition="outside"
        )

    # =================================
    # BAR CHART
    # =================================

    elif chart_type == "bar":

        if group_by is None:
            return None

        fig = px.bar(
            chart_df,
            x=group_by,
            y=metric,
            text="DisplayValue",
            title=f"{metric} by {group_by}"
        )

        fig.update_traces(
            textposition="outside"
        )

    # =================================
    # PIE CHART
    # =================================

    elif chart_type == "pie":

        if group_by is None:
            return None

        fig = px.pie(
            chart_df,
            names=group_by,
            values=metric,
            hole=0.45,
            title=f"{metric} Share by {group_by}"
        )

        # Show compact values in hover
        fig.update_traces(
            hovertemplate=(
                "<b>%{label}</b><br>"
                f"{metric}: %{{value:,.2f}}"
                "<br>"
                "Share: %{percent}"
                "<extra></extra>"
            )
        )

    # =================================
   # SCATTER CHART
# =================================

    elif chart_type == "scatter":

        x_column = intent.get("x_column")
        y_column = intent.get("y_column")

        if (
            x_column is None
            or y_column is None
        ):
            return None

    # --------------------------------
    # Check columns exist
    # --------------------------------

        if (
            x_column not in chart_df.columns
            or y_column not in chart_df.columns
        ):
            return None

    # --------------------------------
    # Make numeric
    # --------------------------------

        chart_df[x_column] = pd.to_numeric(
            chart_df[x_column],
            errors="coerce"
        )

        chart_df[y_column] = pd.to_numeric(
            chart_df[y_column],
            errors="coerce"
        )

        chart_df = chart_df.dropna(
            subset=[
                x_column,
                y_column
            ]
        )

    # --------------------------------
    # Create scatter
    # --------------------------------

        fig = px.scatter(
            chart_df,
            x=x_column,
            y=y_column,
            title=f"{y_column} vs {x_column}",
            hover_data=[
                x_column,
                y_column
            ]
        )

        fig.update_layout(
            template="plotly_white",
            xaxis_title=x_column,
            yaxis_title=y_column
        )

    # =================================
    # HISTOGRAM
    # =================================

    elif chart_type == "histogram":

        numeric_columns = chart_df.select_dtypes(
            include="number"
        ).columns.tolist()

        if metric in numeric_columns:

            histogram_column = metric

        elif numeric_columns:

            histogram_column = numeric_columns[0]

        else:

            return None

        fig = px.histogram(
            chart_df,
            x=histogram_column,
            nbins=30,
            title=f"{histogram_column} Distribution"
        )

    # =================================
    # BOX PLOT
    # =================================

    elif chart_type == "box":

        numeric_columns = chart_df.select_dtypes(
            include="number"
        ).columns.tolist()

        if metric in numeric_columns:

            box_column = metric

        elif numeric_columns:

            box_column = numeric_columns[0]

        else:

            return None

        fig = px.box(
            chart_df,
            y=box_column,
            points="outliers",
            title=f"{box_column} Distribution & Outliers"
        )

    # =================================
    # CORRELATION HEATMAP
    # =================================

    elif chart_type == "heatmap":

        numeric_df = chart_df.select_dtypes(
            include="number"
        )

        if numeric_df.shape[1] < 2:
            return None

        correlation = numeric_df.corr()

        fig = px.imshow(
            correlation,
            text_auto=".2f",
            aspect="auto",
            title="Correlation Heatmap"
        )

    else:

        return None

    # =================================
    # COMMON LAYOUT
    # =================================

    fig.update_layout(
        template="plotly_white",
        hovermode="closest"
    )

    # =================================
    # COMMON HOVER
    # =================================

    if chart_type in [
        "bar",
        "horizontal_bar",
        "line"
    ]:

        fig.update_traces(
            hovertemplate=(
                "<b>%{x}</b><br>"
                f"{metric}: %{{y:,.2f}}"
                "<extra></extra>"
            )
        )

    return fig