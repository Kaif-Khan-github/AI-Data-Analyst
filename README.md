# AI Data Analyst

An intelligent, automated data analysis application built with Python, Pandas, Plotly, and Streamlit.

## Overview

AI Data Analyst allows users to upload CSV or Excel datasets and automatically perform data profiling, cleaning, KPI calculation, natural-language querying, visualization, anomaly detection, business insight generation, recommendations, and report creation.

The project is designed to work with different structured datasets, including sales, retail, customer behavior, churn, marketing, finance, HR, inventory, and other tabular data.

## Features

- CSV and Excel upload
- File validation and dataset preview
- Automatic dataset profiling
- Missing-value and duplicate detection
- Data cleaning and cleaning logs
- Dynamic schema detection
- Dynamic KPI dashboard
- Natural-language query understanding
- Local NLP-based intent classification
- Total, group, top, bottom, trend, share, comparison, relationship, distribution, and anomaly analysis
- Interactive Plotly charts
- Dynamic filters
- Business insights
- Business recommendations
- Anomaly detection
- Downloadable HTML reports
- Reusable number formatting utilities
- Local and free execution without mandatory paid APIs

## Example Questions

```text
What is the total sales?
Show sales by category.
Which region performed best?
Show the top 5 products.
Show the sales trend.
Show percentage of sales by region.
Which region has the lowest profit?
Show the relationship between sales and profit.
Find unusual sales values.
```

## Architecture

```text
Upload Dataset
      ↓
Validate File
      ↓
Profile Dataset
      ↓
Detect Schema
      ↓
Clean Data
      ↓
Check Data Quality
      ↓
Calculate KPIs
      ↓
Understand User Query
      ↓
Execute Analysis
      ↓
Generate Visualization
      ↓
Detect Insights and Anomalies
      ↓
Generate Recommendations
      ↓
Create Downloadable Report
```

## Project Structure

```text
AI-Data-Analyst/
│
├── agents/
│   ├── anomaly_agent.py
│   ├── filter_agent.py
│   ├── insight_agent.py
│   ├── profile_agent.py
│   ├── quality_agent.py
│   ├── query_agent.py
│   └── visualization_agent.py
│
├── analysis/
│   ├── answer_generator.py
│   ├── cleaner.py
│   ├── data_loader.py
│   ├── filter_engine.py
│   ├── profiler.py
│   └── query_engine.py
│
├── app/
│   └── main.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── model/
│   └── nlp_query_model/
│
├── reports/
├── tests/
│
├── utils/
│   ├── file_handler.py
│   ├── formatters.py
│   ├── report_generator.py
│   └── schema_detector.py
│
├── .gitignore
├── README.md
├── requirements.txt
└── requirements-full.txt


☁️ Deployment Architecture

The project separates the application from the large NLP model.

┌─────────────────────────────┐
│       GitHub Repository     │
│                             │
│  Python source code         │
│  Streamlit dashboard        │
│  Analysis modules           │
│  Agent modules              │
│  Requirements               │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│    Streamlit Community      │
│           Cloud             │
│                             │
│  Hosts the web application  │
│  Handles user interaction   │
│  Runs data analysis         │
│  Displays Plotly charts     │
└──────────────┬──────────────┘
               │
               │ Downloads model when required
               ▼
┌─────────────────────────────┐
│       Hugging Face Hub      │
│                             │
│  Fine-tuned NLP model       │
│  Model configuration        │
│  Tokenizer files            │
│  Large model weights        │
└─────────────────────────────┘
Why Hugging Face Is Used

The trained model is too large to store conveniently in the GitHub repository.

Therefore:

GitHub stores the application source code.

Hugging Face stores the trained model.

Streamlit Cloud runs the application.

The application loads the model from Hugging Face when needed.

This keeps the source repository smaller and makes model management easier.
```

## Technology Stack

- **Python** – application development
- **Pandas** – data loading, cleaning, grouping, and analysis
- **NumPy** – numerical operations
- **Plotly** – interactive charts
- **Streamlit** – web dashboard
- **Scikit-learn** – machine-learning and statistical utilities
- **Transformers** – local NLP model support
- **PyTorch** – local model execution
- **OpenPyXL** – Excel file support
- **Git and GitHub** – version control and collaboration

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Kaif-Khan-github/AI-Data-Analyst.git
cd AI-Data-Analyst
```

### 2. Create a virtual environment

On Windows:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

If you need the complete dependency list:

```powershell
pip install -r requirements-full.txt
```

## Run the Application

Run the Streamlit application with:

```powershell
python -m streamlit run app/main.py
```

If the dashboard file is located at the project root, use:

```powershell
python -m streamlit run dashboard.py
```

Then open the local Streamlit URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Workflow

1. Start the application.
2. Upload a CSV or Excel file.
3. Review the dataset preview.
4. Inspect the profile and data-quality report.
5. Apply available filters.
6. View automatically calculated KPIs.
7. Ask a question in natural language.
8. Review the generated answer and chart.
9. Read the business insights and recommendations.
10. Download the report.

## Automatic Schema Detection

The application detects columns according to their business meaning rather than relying only on fixed names.

| Business meaning | Possible column names |
|---|---|
| Sales | Sales, Revenue, Purchase Amount, Amount |
| Profit | Profit, Net Profit, Earnings |
| Quantity | Quantity, Qty, Units |
| Product | Product, Item Purchased, Product Name |
| Category | Category, Segment, Type |
| Region | Region, Location, City, State |
| Customer | Customer ID, User ID, Customer |

This allows the same dashboard to work with different datasets.

## Dynamic KPI Examples

Depending on the uploaded dataset, the dashboard can calculate:

- Total sales or primary numeric value
- Total profit
- Profit margin
- Total quantity
- Unique records
- Average value
- Average order value
- Period growth
- Number of columns

Some KPIs are skipped when the required columns are unavailable.

For example, profit margin cannot be calculated if the dataset has no profit column, and trend growth cannot be calculated if there is no date column.

## Query Agent

The query agent converts natural-language questions into structured intents.

Example:

```python
{
    "type": "group",
    "metric": "Sales",
    "group_by": "Category",
    "limit": None,
    "time_based": False,
    "share": False
}
```

Supported intent types include:

- `total`
- `group`
- `top`
- `bottom`
- `trend`
- `share`
- `comparison`
- `relationship`
- `distribution`
- `anomaly`

The project uses a local NLP model to reduce dependence on paid external APIs.

## Visualization

The visualization agent selects charts based on the analysis result:

- Bar chart for category comparisons
- Horizontal bar chart for rankings
- Line chart for time trends
- Pie chart for percentage contribution
- Scatter plot for relationships between numeric columns
- Map chart when geographic information is available

## Data Quality

The application checks:

- Missing values
- Duplicate rows
- Numeric columns
- Categorical columns
- Date columns
- Invalid or inconsistent values
- Cleaning actions

The quality report compares the dataset before and after cleaning.

## Anomaly Detection

The anomaly agent identifies unusual numeric values using statistical and outlier-based techniques.

The report may include:

- Affected column
- Number of unusual records
- Unusual values
- Possible business interpretation

An anomaly is not automatically a data error. It may represent a legitimate transaction or unusual business event and should be reviewed.

## Business Insights and Recommendations

The insight agent identifies meaningful patterns such as:

- Highest-performing category
- Lowest-performing category
- Largest contribution to total value
- Differences between groups
- Trends over time
- Relationships between numeric variables

The recommendation module converts these findings into practical suggestions, such as:

- Focus on high-performing categories.
- Investigate weak-performing regions.
- Review low-profit products.
- Improve inventory planning.
- Examine unusual transactions.
- Analyze customer groups with low activity.

## Report Generation

The application can generate an HTML report containing:

- Dataset summary
- Data-quality results
- KPI values
- Query results
- Charts
- Business insights
- Recommendations
- Anomaly findings

## Supported Dataset Examples

The application can be tested with:

- Retail sales data
- Customer shopping behavior data
- Superstore sales data
- Customer churn data
- Employee attrition data
- Marketing campaign data
- House-price data
- Student-performance data
- Inventory data

The application gracefully skips analyses when required fields are unavailable.

## Limitations

- Advanced analyses require suitable numeric, categorical, or date columns.
- Intent detection may be less accurate for ambiguous questions.
- Local NLP models can require significant memory and disk space.
- Very large datasets may need performance optimization.
- Automatic schema detection depends on meaningful column names.
- Recommendations should be validated with business knowledge.
- The project currently focuses on structured tabular datasets.

## Future Improvements

- Better semantic schema detection
- More robust date detection
- SQL and SQLite query execution
- Advanced statistical testing
- Forecasting
- Customer segmentation
- More anomaly-detection methods
- PDF report export
- Authentication
- Multilingual query support
- Automated testing across many datasets
- Cloud deployment
- More intelligent agent routing

## Security

Do not commit:

- API keys
- Passwords
- GitHub tokens
- Private credentials
- Confidential datasets
- `.streamlit/secrets.toml`
- Large local model files

Recommended `.gitignore`:

```gitignore
venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
.env
.streamlit/secrets.toml
model/
```

The local NLP model is excluded from Git because it can be very large. It should be downloaded or configured separately when required.

## Deployment

The project can be deployed using Streamlit Community Cloud.

General deployment steps:

1. Push the project to GitHub.
2. Confirm that `requirements.txt` contains all required packages.
3. Keep private files and large model files out of Git.
4. Open Streamlit Community Cloud.
5. Connect the GitHub repository.
6. Select the application entry file.
7. Deploy the application.


## Hugging Face

The NLP model is hosted separately:

Open the NLP Model 

Deployment Flow
Developer pushes code to GitHub
              ↓
Streamlit Community Cloud pulls the repository
              ↓
Dependencies are installed
              ↓
Application starts
              ↓
NLP model is loaded from Hugging Face
              ↓
Users upload and analyze datasets


## Author

**Kaif Khan**  
BSc Data Science
