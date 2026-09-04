import html
import re
import pandas as pd
import numpy as np

def _format_kpi(value, is_currency=True):
    """Formats large numbers into Cr, M, K for executive dashboards."""
    if value is None or pd.isna(value):
        return "0"
    try:
        val = float(value)
        prefix = "₹" if is_currency else ""
        if abs(val) >= 10000000:
            return f"{prefix}{val/10000000:.2f} Cr"
        elif abs(val) >= 1000000:
            return f"{prefix}{val/1000000:.2f} M"
        elif abs(val) >= 1000:
            return f"{prefix}{val/1000:.1f} K"
        else:
            if val.is_integer():
                return f"{prefix}{int(val):,}"
            return f"{prefix}{val:,.2f}"
    except (ValueError, TypeError):
        return str(value)

def _parse_markdown(text):
    """Converts basic markdown like **bold** to HTML tags."""
    if not isinstance(text, str):
        return str(text)
    
    # Escape HTML first to prevent injection, but allow our own tags later
    escaped_text = html.escape(text)
    
    # Replace **bold** with <strong>bold</strong>
    bold_parsed = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', escaped_text)
    
    # Replace newlines with <br>
    final_html = bold_parsed.replace('\n', '<br>')
    return final_html

def _format_table_value(val):
    """Attempts to format numeric table values cleanly."""
    if isinstance(val, (int, float)) and not pd.isna(val):
        # If it looks like a large currency amount
        if val > 1000 or val < -1000:
            return _format_kpi(val, is_currency=True)
        # Normal float
        if isinstance(val, float):
            return f"{val:,.2f}"
    return html.escape(str(val))

def _format_section(data, is_table=False):
    """Convert different result types into readable HTML with business formatting."""
    if data is None:
        return "<p class='no-data'>No data available.</p>"

    # DataFrame
    if isinstance(data, pd.DataFrame):
        if data.empty:
            return "<p class='no-data'>No data available.</p>"
        
        # Apply formatting if it's the analysis result table
        if is_table:
            df_copy = data.copy()
            for col in df_copy.select_dtypes(include=[np.number]).columns:
                df_copy[col] = df_copy[col].apply(_format_table_value)
            
            return df_copy.to_html(index=False, classes="data-table", border=0, escape=False)
            
        return data.to_html(index=False, classes="data-table", border=0)

    # Series
    if isinstance(data, pd.Series):
        if data.empty:
            return "<p class='no-data'>No data available.</p>"
        temp = data.reset_index()
        if len(temp.columns) >= 2:
            temp.columns = ["Category", "Value"] + list(temp.columns[2:])
            
        if is_table:
            for col in temp.select_dtypes(include=[np.number]).columns:
                temp[col] = temp[col].apply(_format_table_value)
                
        return temp.to_html(index=False, classes="data-table", border=0, escape=False)

    # Dictionary
    if isinstance(data, dict):
        if not data:
            return "<p class='no-data'>No data available.</p>"
        rows = ""
        for key, value in data.items():
            rows += f"""
            <tr>
                <td><strong>{html.escape(str(key))}</strong></td>
                <td>{html.escape(str(value))}</td>
            </tr>
            """
        return f"""
        <table class="data-table">
            <tr>
                <th>Field</th>
                <th>Value</th>
            </tr>
            {rows}
        </table>
        """

    # List or Tuple
    if isinstance(data, (list, tuple)):
        if not data:
            return "<p class='no-data'>No data available.</p>"
        output = "<ul class='insight-list'>"
        for item in data:
            output += f"<li>{_parse_markdown(str(item))}</li>"
        output += "</ul>"
        return output

    # Normal String / Value
    return f"<p>{_parse_markdown(str(data))}</p>"


def generate_html_report(
    filtered_df,
    query=None,
    answer=None,
    result=None,
    insights=None,
    recommendations=None,
    anomaly_insights=None,
    intent=None
):
    # -----------------------------------------
    # KPI CALCULATIONS (Unchanged Logic)
    # -----------------------------------------
    total_sales = 0
    total_profit = 0
    total_quantity = 0
    total_orders = 0
    profit_margin = 0

    if filtered_df is not None and not filtered_df.empty:
        if "Sales" in filtered_df.columns:
            total_sales = filtered_df["Sales"].sum()
        if "Profit" in filtered_df.columns:
            total_profit = filtered_df["Profit"].sum()
        if "Quantity" in filtered_df.columns:
            total_quantity = filtered_df["Quantity"].sum()
        if "Order_ID" in filtered_df.columns:
            total_orders = filtered_df["Order_ID"].nunique()
        else:
            total_orders = len(filtered_df)

        if total_sales != 0:
            profit_margin = (total_profit / total_sales) * 100
            
    # Data Quality Stats
    row_count = len(filtered_df) if filtered_df is not None else 0
    col_count = len(filtered_df.columns) if filtered_df is not None else 0

    # -----------------------------------------
    # INTENT SUMMARIZATION (Cleaned up)
    # -----------------------------------------
    intent_html = ""
    if isinstance(intent, dict):
        
        # Bulletproof helper to extract and clean intent values
        def _clean_intent(key, default_val):
            val = intent.get(key)
            if not val:  # Catches None, empty strings, empty lists
                return default_val
            if isinstance(val, list):  # If NLP returns a list like ['Sales', 'Profit']
                return ", ".join(str(v).title() for v in val)
            return str(val).title()
            
        q_type = _clean_intent("type", "General Analysis")
        metric = _clean_intent("metric", "All")
        group = _clean_intent("group_by", "Overall")
        
        intent_html = f"""
        <div class="summary-tags">
            <span class="tag"><strong>Analysis:</strong> {q_type}</span>
            <span class="tag"><strong>Metric:</strong> {metric}</span>
            <span class="tag"><strong>Dimension:</strong> {group}</span>
        </div>
        """
    else:
        intent_html = "<p>Standard Analysis</p>"

    # -----------------------------------------
    # CONDITIONAL ANOMALY RENDERING
    # -----------------------------------------
    anomaly_section = ""
    if anomaly_insights is not None:
        # Check if it's not an empty structure
        is_empty_df = isinstance(anomaly_insights, pd.DataFrame) and anomaly_insights.empty
        is_empty_list = isinstance(anomaly_insights, (list, dict)) and len(anomaly_insights) == 0
        
        if not is_empty_df and not is_empty_list:
            rendered_anomaly = _format_section(anomaly_insights)
            if "No data available" not in rendered_anomaly:
                anomaly_section = f"""
                <h2>🚨 Anomaly Detection</h2>
                <div class="card anomaly-card">
                    {rendered_anomaly}
                </div>
                """

    # -----------------------------------------
    # HTML REPORT CONSTRUCTION
    # -----------------------------------------
    report = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Data Analyst Report</title>
    <style>
        :root {{
            --primary: #2563eb;
            --text-main: #1f2937;
            --text-muted: #6b7280;
            --bg-page: #f3f4f6;
            --bg-card: #ffffff;
            --border: #e5e7eb;
        }}
        
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            margin: 0;
            padding: 40px 20px;
            background: var(--bg-page);
            color: var(--text-main);
            line-height: 1.6;
        }}
        
        .report-container {{
            max-width: 1000px;
            margin: 0 auto;
        }}

        h1 {{
            color: var(--text-main);
            font-size: 28px;
            margin-bottom: 5px;
            border-bottom: 3px solid var(--primary);
            padding-bottom: 15px;
            display: inline-block;
        }}

        h2 {{
            margin-top: 40px;
            font-size: 18px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
        }}

        .card {{
            background: var(--bg-card);
            padding: 24px;
            margin-top: 15px;
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        }}
        
        .anomaly-card {{
            border-left: 4px solid #ef4444;
        }}

        /* EXEC SUMMARY */
        .exec-query {{
            font-size: 18px;
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 15px;
        }}
        
        .summary-tags {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }}
        
        .tag {{
            background: #eff6ff;
            color: #1d4ed8;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 14px;
            border: 1px solid #bfdbfe;
        }}

        /* KPIs */
        .kpi-container {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 20px;
        }}

        .kpi {{
            flex: 1;
            min-width: 150px;
            background: var(--bg-card);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            text-align: center;
        }}

        .kpi-title {{
            color: var(--text-muted);
            font-size: 13px;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}

        .kpi-value {{
            font-size: 28px;
            font-weight: 700;
            color: var(--text-main);
            margin-top: 8px;
        }}

        /* TABLES */
        .data-table {{
            border-collapse: collapse;
            width: 100%;
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }}

        .data-table th {{
            background: #f8fafc;
            color: var(--text-muted);
            padding: 12px 16px;
            text-align: left;
            font-size: 13px;
            text-transform: uppercase;
            font-weight: 600;
            border-bottom: 2px solid var(--border);
        }}

        .data-table td {{
            border-bottom: 1px solid var(--border);
            padding: 12px 16px;
            font-size: 15px;
        }}
        
        .data-table tr:last-child td {{
            border-bottom: none;
        }}

        /* LISTS */
        .insight-list {{
            margin: 0;
            padding-left: 20px;
        }}
        
        .insight-list li {{
            margin-bottom: 12px;
            padding-left: 5px;
        }}

        /* FOOTER & UTILS */
        .no-data {{
            color: var(--text-muted);
            font-style: italic;
            margin: 0;
        }}

        .footer {{
            margin-top: 50px;
            text-align: center;
            color: var(--text-muted);
            font-size: 13px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
        }}
        
        .dq-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 15px;
            text-align: center;
        }}
        
        .dq-stat {{
            background: #f8fafc;
            padding: 15px;
            border-radius: 8px;
        }}
    </style>
</head>
<body>

<div class="report-container">

    <h1>🤖 Automated Business Intelligence Report</h1>

    <!-- ============================= -->
    <!-- EXECUTIVE SUMMARY -->
    <!-- ============================= -->
    <h2>Executive Summary</h2>
    <div class="card">
        <div class="exec-query">"{html.escape(str(query)) if query else 'Standard Report'}"</div>
        {intent_html}
    </div>

    <!-- ============================= -->
    <!-- KPI -->
    <!-- ============================= -->
    <h2>Key Performance Indicators</h2>
    <div class="kpi-container">
        <div class="kpi">
            <div class="kpi-title">Total Sales</div>
            <div class="kpi-value">{_format_kpi(total_sales, True)}</div>
        </div>
        <div class="kpi">
            <div class="kpi-title">Total Profit</div>
            <div class="kpi-value">{_format_kpi(total_profit, True)}</div>
        </div>
        <div class="kpi">
            <div class="kpi-title">Quantity</div>
            <div class="kpi-value">{_format_kpi(total_quantity, False)}</div>
        </div>
        <div class="kpi">
            <div class="kpi-title">Orders</div>
            <div class="kpi-value">{_format_kpi(total_orders, False)}</div>
        </div>
        <div class="kpi">
            <div class="kpi-title">Margin</div>
            <div class="kpi-value">{profit_margin:.1f}%</div>
        </div>
    </div>

    <!-- ============================= -->
    <!-- AI ANSWER -->
    <!-- ============================= -->
    <h2>💬 AI Answer</h2>
    <div class="card">
        {_format_section(answer)}
    </div>

    <!-- ============================= -->
    <!-- ANALYSIS RESULT -->
    <!-- ============================= -->
    <h2>🔎 Analysis Table</h2>
    <div class="card">
        {_format_section(result, is_table=True)}
    </div>

    <!-- ============================= -->
    <!-- INSIGHTS -->
    <!-- ============================= -->
    <h2>💡 Key Insights</h2>
    <div class="card">
        {_format_section(insights)}
    </div>

    <!-- ============================= -->
    <!-- RECOMMENDATIONS -->
    <!-- ============================= -->
    <h2>🎯 Business Recommendations</h2>
    <div class="card">
        {_format_section(recommendations)}
    </div>

    <!-- ============================= -->
    <!-- ANOMALIES (Conditional) -->
    <!-- ============================= -->
    {anomaly_section}

    <!-- ============================= -->
    <!-- DATA QUALITY -->
    <!-- ============================= -->
    <h2>🧹 Data Quality</h2>
    <div class="card">
        <div class="dq-grid">
            <div class="dq-stat">
                <strong>{row_count:,}</strong><br><span style="color:var(--text-muted); font-size:13px;">Records Analysed</span>
            </div>
            <div class="dq-stat">
                <strong>{col_count}</strong><br><span style="color:var(--text-muted); font-size:13px;">Data Columns</span>
            </div>
            <div class="dq-stat" style="color: #059669;">
                <strong>Good</strong><br><span style="color:var(--text-muted); font-size:13px;">Data Quality Status</span>
            </div>
        </div>
    </div>

    <div class="footer">
        Generated automatically by AI Data Analyst
    </div>

</div>

</body>
</html>
"""
    return report