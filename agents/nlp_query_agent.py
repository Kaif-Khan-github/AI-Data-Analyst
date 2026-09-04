from pathlib import Path

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline
)


# --------------------------------
# MODEL PATH
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "model"
    / "nlp_query_model"
)

print("Loading model from:")
print(MODEL_PATH)

# Check model exists
if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Model folder not found: {MODEL_PATH}"
    )


# --------------------------------
# LOAD TOKENIZER
# --------------------------------

tokenizer = AutoTokenizer.from_pretrained(
    str(MODEL_PATH),
    local_files_only=True
)


# --------------------------------
# LOAD MODEL
# --------------------------------

model = AutoModelForSequenceClassification.from_pretrained(
    str(MODEL_PATH),
    local_files_only=True
)


# --------------------------------
# CLASSIFIER
# --------------------------------

classifier = pipeline(
    "text-classification",
    model=model,
    tokenizer=tokenizer,
    top_k=1
)


# --------------------------------
# PREDICT INTENT
# --------------------------------

def predict_intent(query):

    results = classifier(query)

    # --------------------------------
    # Normalize pipeline output
    # --------------------------------

    while isinstance(results, list):

        if len(results) == 0:
            raise ValueError("NLP model returned no prediction.")

        results = results[0]

    # Now results should be a dictionary
    if not isinstance(results, dict):
        raise TypeError(
            f"Unexpected model output: {type(results)}"
        )

    label = results.get("label")
    score = results.get("score")

    if label is None or score is None:
        raise ValueError(
            f"Invalid model prediction: {results}"
        )

    return {
        "intent": label,
        "confidence": float(score)
    }

# --------------------------------
# TEST
# --------------------------------

if __name__ == "__main__":

    queries = [
        "Show sales by category",
        "Which region performed best?",
        "Show sales trend",
        "Show percentage of sales by region",
        "Show relationship between Sales and Profit",
        "Find unusual Sales",
        "What are the total sales?"
    ]

    for query in queries:

        result = predict_intent(query)

        print(
            f"\nQuery: {query}"
        )

        print(
            f"Intent: {result['intent']}"
        )

        print(
            f"Confidence: {result['confidence']:.3f}"
        )