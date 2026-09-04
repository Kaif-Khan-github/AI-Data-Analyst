# agents/query_agent.py

from agents.nlp_query_agent import predict_intent


# =========================================================
# CONFIDENCE THRESHOLD
# =========================================================

NLP_CONFIDENCE_THRESHOLD = 0.50


# =========================================================
# NORMALIZE INTENT
# =========================================================

def normalize_intent(label):

    label = label.lower().strip()

    valid_intents = [
        "total",
        "group",
        "top",
        "bottom",
        "trend",
        "share",
        "comparison",
        "relationship",
        "distribution",
        "anomaly"
    ]

    if label in valid_intents:
        return label

    return None


# =========================================================
# ENTITY EXTRACTION
# =========================================================

def extract_entities(query):

    query_lower = query.lower()

    metric = None
    group_by = None
    limit = None

# -----------------------------------------------------
# METRIC
# -----------------------------------------------------

    if "sales" in query_lower:
        metric = "Sales"

    elif "profit" in query_lower:
        metric = "Profit"

    elif "quantity" in query_lower:
        metric = "Quantity"

    elif "revenue" in query_lower:
        metric = "Sales"

# If user says "performed best/worst"
# default to Sales
    elif (
        "performed best" in query_lower
        or "performed worst" in query_lower
        or "performed well" in query_lower
        or "best performing" in query_lower
        or "worst performing" in query_lower
    ):
        metric = "Sales"

    # -----------------------------------------------------
    # GROUP BY
    # -----------------------------------------------------

    if (
        "product" in query_lower
        or "products" in query_lower
        or "item" in query_lower
        or "items" in query_lower
    ):
        group_by = "Product"

    elif (
        "category" in query_lower
        or "categories" in query_lower
    ):
        group_by = "Category"

    elif (
        "region" in query_lower
        or "regions" in query_lower
        or "area" in query_lower
    ):
        group_by = "Region"

    elif "city" in query_lower:
        group_by = "City"

    elif "state" in query_lower:
        group_by = "State"

    # -----------------------------------------------------
    # LIMIT
    # -----------------------------------------------------

    words = query_lower.split()

    for i, word in enumerate(words):

        cleaned = word.replace(",", "")

        if cleaned.isdigit():

            number = int(cleaned)

            if i > 0:

                previous = words[i - 1]

                if previous in [
                    "top",
                    "bottom"
                ]:
                    limit = number

    return {
        "metric": metric,
        "group_by": group_by,
        "limit": limit
    }


# =========================================================
# MAIN QUERY UNDERSTANDING
# =========================================================

def understand_query(query):

    # -----------------------------------------------------
    # NLP MODEL
    # -----------------------------------------------------

    nlp_result = predict_intent(query)

    predicted_intent = normalize_intent(
        nlp_result["intent"]
    )

    confidence = nlp_result["confidence"]


    # -----------------------------------------------------
# ENTITY DETECTION
# -----------------------------------------------------

    query_lower = query.lower()

    metric = None
    group_by = None
    x_column = None
    y_column = None


# -----------------------------------------------------
# METRIC DETECTION
# -----------------------------------------------------

    if "sales" in query_lower:
        metric = "Sales"

    elif "profit" in query_lower:
        metric = "Profit"

    elif "quantity" in query_lower:
        metric = "Quantity"

    elif "revenue" in query_lower:
        metric = "Sales"


# -----------------------------------------------------
# GROUP DETECTION
# -----------------------------------------------------

    if "product" in query_lower:
        group_by = "Product"

    elif "category" in query_lower:
        group_by = "Category"

    elif "region" in query_lower:
        group_by = "Region"

    elif "city" in query_lower:
        group_by = "City"


# -----------------------------------------------------
# RELATIONSHIP DETECTION
# -----------------------------------------------------

    if predicted_intent == "relationship":

        if "sales" in query_lower and "profit" in query_lower:

            x_column = "Sales"
            y_column = "Profit"

        elif "sales" in query_lower and "quantity" in query_lower:

            x_column = "Sales"
            y_column = "Quantity"

        elif "profit" in query_lower and "quantity" in query_lower:

            x_column = "Profit"
            y_column = "Quantity"


    # -----------------------------------------------------
# LOW CONFIDENCE HANDLING
# -----------------------------------------------------

    if confidence < NLP_CONFIDENCE_THRESHOLD:

        print(
            f"Low NLP confidence: {confidence:.3f}"
        )

        if predicted_intent is not None:

            print(
                f"Using predicted intent: {predicted_intent}"
            )



    # -----------------------------------------------------
    # ENTITIES
    # -----------------------------------------------------

    entities = extract_entities(query)

    if metric is None:
        metric = entities["metric"]

    if group_by is None:
        group_by = entities["group_by"]

    limit = entities["limit"]

    # -----------------------------------------------------
# CREATE INTENT
# -----------------------------------------------------

    intent = {

        "type": predicted_intent,

        "metric": metric,

        "group_by": group_by,

        "limit": limit,

        "time_based": predicted_intent == "trend",

        "share": predicted_intent == "share",

        "chart_type": (
            "scatter" if predicted_intent == "relationship"
            else "histogram" if predicted_intent == "distribution"
            else None
),

        "x_column": x_column,

        "y_column": y_column,

        "nlp_confidence": confidence

    }

    
    # -----------------------------------------------------
    # PRINT DEBUG
    # -----------------------------------------------------

    print(
        f"NLP Intent: {predicted_intent}"
    )

    print(
        f"NLP Confidence: {confidence:.3f}"
    )

    print(
        f"Metric: {metric}"
    )

    print(
        f"Group By: {group_by}"
    )

    print(
        f"Limit: {limit}"
    )

    return intent


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    queries = [

        "Show sales by category",

        "Which region performed best?",

        "Which product has the highest sales?",

        "Show top 5 products by sales",

        "Which region has the lowest profit?",

        "Show sales trend",

        "Show percentage of sales by region",

        "Compare North and South",

        "Show relationship between Sales and Profit",

        "Show distribution of Profit",

        "Find unusual Sales",

        "What are the total sales?"

    ]

    for query in queries:

        print("\n" + "=" * 60)

        print("Query:", query)

        intent = understand_query(query)

        print("Final Intent:")

        print(intent)