import random
import pandas as pd
from utils.formatters import compact_value
from agents.anomaly_agent import format_anomaly_insights

def generate_answer(query, intent, result):
    # Fallback if intent is missing
    if not intent:
        return "I'm not quite sure I understood that. Could you try rephrasing your question?"

    metric = intent.get("metric", "data")
    group_by = intent.get("group_by", "category")
    query_type = intent.get("type")

    # --------------------------------
    # 1. QUERY ENGINE ERRORS
    # --------------------------------
    if isinstance(result, dict) and "error" in result: 
        error_type = result["error"]

        if error_type == "non_numeric_relationship":
            x_col = result.get("x_column", "Unknown")
            y_col = result.get("y_column", "Unknown")
            x_num = result.get("x_numeric", False)
            y_num = result.get("y_numeric", False)
            
            non_numeric = [col for col, is_num in [(x_col, x_num), (y_col, y_num)] if not is_num]
            
            return (
                f"⚠️ I cannot create a scatter plot because it requires two numeric columns.\n\n"
                f"Currently, **{', '.join(non_numeric)}** is not numeric.\n\n"
                f"💡 Try comparing numeric columns like **Sales and Profit**.\n"
                f"If you want to view categories, try asking for **{metric} by {x_col}** instead."
            )

        if error_type == "relationship_columns_missing":
            return (
                "⚠️ I couldn't identify the two columns needed for a relationship analysis.\n\n"
                "💡 Try asking something like: **Show relationship between Sales and Profit**."
            )

    # --------------------------------
    # 2. MISSING / EMPTY DATA
    # --------------------------------
    if result is None or (hasattr(result, "empty") and result.empty):
        if intent.get("chart_type") == "scatter":
            x_col = intent.get("x_column", "one column")
            y_col = intent.get("y_column", "another column")
            return (
                f"⚠️ I couldn't plot {x_col} against {y_col}. One of them might not be a valid numeric metric.\n"
                f"💡 Try comparing core metrics like **Sales and Profit**."
            )
        
        return f"I couldn't find any data for {metric} based on your current filters or question."

    # --------------------------------
    # 3. CONVERSATIONAL RESPONSES
    # --------------------------------

    # --- SINGLE VALUE (Totals) ---
    if isinstance(result, (int, float)):
        intros = [
            f"The total {metric} stands at",
            f"Based on your data, the overall {metric} is",
            f"Your total {metric} amounts to"
        ]
        return f"{random.choice(intros)} **{compact_value(result)}**."

    # --- RELATIONSHIP ---
    if query_type == "relationship":
        x_col = intent.get("x_column", "X")
        y_col = intent.get("y_column", "Y")
        return (
            f"📊 Here is the relationship analysis between **{x_col}** and **{y_col}**.\n\n"
            f"Take a look at the scatter plot to spot correlations, clusters, or outliers between these two metrics."
        )

    # --- DISTRIBUTION ---
    if query_type == "distribution":
        return (
            f"📊 I've analyzed the distribution for **{metric}**.\n\n"
            f"The histogram below will show you how the data is spread out, helping you spot averages and rare extremes."
        )

    # --- ANOMALY ---
    if query_type == "anomaly":
        if isinstance(result, str) and result.strip() == "": # Failsafe if string is empty
            return f"✅ Good news! No unusual {metric} values were detected."
            
        return (
            f"🚨 **Unusual {metric} Activity Detected:**\n\n"
            f"{format_anomaly_insights(result)}\n\n"
            f"I recommend investigating these spikes or drops to understand the root cause."
        )

    # --- TOP / BOTTOM (With smart comparison) ---
    if query_type in ["top", "bottom"]:
        is_top = query_type == "top"
        
        if len(result) == 1:
            name = result.index[0]
            val = result.iloc[0]
            if is_top:
                return f"🏆 **{name}** is leading the pack with the highest {metric} at **{compact_value(val)}**."
            return f"📉 **{name}** has the lowest {metric}, sitting at **{compact_value(val)}**."

        # Multiple Top/Bottom Results
        limit = intent.get("limit", len(result))
        direction = "Top" if is_top else "Bottom"
        
        answer = f"Here are the {direction} {len(result)} {group_by}s ranked by {metric}:\n\n"
        
        # Smart Insight: Compare #1 and #2
        if len(result) > 1 and is_top:
            first_val = result.iloc[0]
            second_val = result.iloc[1]
            diff = first_val - second_val
            if diff > 0:
                answer += f"💡 **{result.index[0]}** is in 1st place, beating the runner-up by {compact_value(diff)}.\n\n"

        for i, (name, value) in enumerate(result.items(), start=1):
            answer += f"{i}. **{name}** — {compact_value(value)}\n"

        return answer.strip()

    # --- TREND (With smart growth calculation) ---
    if query_type == "trend":
        if len(result) < 2:
            return "Not enough historical data to calculate a meaningful trend."

        first_val = result.iloc[0]
        last_val = result.iloc[-1]
        highest_period, highest_value = result.idxmax(), result.max()
        lowest_period, lowest_value = result.idxmin(), result.min()

        # Calculate actual growth/decline
        if first_val != 0:
            pct_change = ((last_val - first_val) / abs(first_val)) * 100
            trend_word = "grown" if pct_change > 0 else "declined"
            insight = f"Overall, {metric} has **{trend_word} by {abs(pct_change):.1f}%** over this period."
        else:
            insight = "Here is the historical performance breakdown."

        return (
            f"📈 **{metric} Trend Analysis**\n"
            f"{insight}\n\n"
            f"🟢 **Peak:** {highest_period} ({compact_value(highest_value)})\n"
            f"🔴 **Trough:** {lowest_period} ({compact_value(lowest_value)})\n"
            f"📊 **Average:** {compact_value(result.mean())} per period\n"
            f"💰 **Total:** {compact_value(result.sum())}"
        )

    # --- SHARE / PERCENTAGES ---
    if query_type == "share":
        total = result.sum()
        intros = [
            f"Here is how {metric} is distributed across your {len(result)} {group_by}s:",
            f"Breaking down the percentage share of {metric} by {group_by}:"
        ]
        
        lines = [f"pie {random.choice(intros)}\n"]
        for name, val in result.items():
            pct = (val / total) * 100 if total != 0 else 0
            lines.append(f"• **{name}**: {pct:.1f}%")
            
        return "\n".join(lines)

    # --- GROUP / CATEGORICAL ---
    if query_type == "group":
        intros = [
            f"Here is the breakdown of {metric} across your {len(result)} {group_by}s:",
            f"Let's take a look at {metric} grouped by {group_by}:"
        ]
        
        answer = f"📊 {random.choice(intros)}\n\n"
        for i, (name, value) in enumerate(result.items(), start=1):
            answer += f"{i}. **{name}** — {compact_value(value)}\n"

        return answer.strip()

    # --- FALLBACK ---
    return "I found the data, but I'm having trouble formatting the response. Please check the visualizations!"


if __name__ == "__main__":
    from analysis.data_loader import load_dataset
    from agents.query_agent import understand_query
    from analysis.query_engine import execute_query

    df = load_dataset("data/processed/cleaned_sales.csv")
    queries = [
        "Which product has the highest sales?",
        "Show top 3 products by sales",
        "Which region has the lowest profit?",
        "Show sales by category",
        "What are the total sales?",
        "Show sales trend",
        "Show percentage of sales by region",
        "which region perform best"
    ]

    for query in queries:
        print("\n" + "="*50)
        print("Question:", query)
        intent = understand_query(query)
        result = execute_query(df, intent)
        answer = generate_answer(query, intent, result)
        print("\nAnswer:\n" + answer)