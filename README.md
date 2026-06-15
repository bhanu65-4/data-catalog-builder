# Data Catalog Builder

A lightweight data cataloging application that scans CSV files and SQL databases, extracts metadata, profiles datasets, discovers relationships between tables, and provides an interactive Streamlit interface for exploration. This tool helps data teams understand, document, and search their data assets in one place.

## Problem Statement

Organizations often have data scattered across CSV files and databases with little to no documentation. Understanding what data exists, what each column means, and how tables relate to each other requires manual effort and tribal knowledge. Data Catalog Builder solves this by automatically scanning data sources, extracting schema metadata, profiling rows, discovering foreign-key-like relationships, and providing a searchable, AI-enhanced catalog interface.

## Team Members

| Name | Branch | Roll No | Email |
| --- | --- | --- | --- |
| D. Bhanu | CSE-AI | 232T1A03114 | ayeshabhanu03@gmail.com |
| D. Lasya Priya | CSE | 232T1A0544 | donaparthyl@gmail.com |
| B. Gowthami | CSE-AI | 232T1A03109 | butragowthami@gmail.com |
| P. Shivani | EEE | 232T1A0227 | shivaniputta962@gmail.com |

## Team Contributions

| Team Member | Contribution |
|------------|-------------|
| D. Bhanu | Project architecture, catalog generation engine, Streamlit dashboard, GitHub integration |
| D. Lasya Priya | Metadata enrichment, testing, documentation |
| B. Gowthami | Dataset preparation, profiling validation, relationship discovery testing |
| P. Shivani | Reporting, README preparation, demo video support |

> **Resumes**: Team member resumes are available in the [`resumes/`](resumes/) folder as a PDF file.

## Live Demo

The Data Catalog Builder dashboard can be viewed at:

**[🔗 http://localhost:8501](http://localhost:8501)**

## Features Implemented

- Upload and register CSV datasets
- Automatic metadata extraction (column names, data types, row counts)
- Column profiling and statistics
- Relationship discovery between tables (matching key columns across tables)
- Searchable data catalog with keyword querying
- Interactive Streamlit dashboard for browsing tables, columns, and relationships
- Export catalog functionality (JSON format)
- AI-assisted column descriptions via LLM enrichment (OpenAI or local heuristic fallback)
- Natural-language catalog querying through an AI question box

## Architecture Overview

```text
data-catalog-builder/
├── data/                      # Sample CSV datasets (customers, orders, products, departments)
├── outputs/                   # Generated catalog reports and sample outputs
├── resumes/                   # Team member resumes (PDF)
├── cataloger.py               # Core engine: scan CSV files, SQLite, or SQL databases
├── cataloger_cli.py           # CLI wrapper for catalog generation
├── llm_enrich.py              # AI enrichment module (OpenAI / heuristic fallback)
├── catalog_utils.py           # Utility helpers for catalog manipulation
├── enrich_and_report.py       # Enrich catalog and generate reports
├── create_pretty_report.py    # Generate formatted markdown reports
├── streamlit_app.py           # Interactive Streamlit dashboard
├── viewer.py                  # Lightweight catalog viewer
├── requirements.txt           # Python dependencies
├── catalog.json               # Generated catalog output
└── prompts.md                 # AI prompt examples used
```

The pipeline flows as:

1. **Data Ingestion** — `cataloger.py` scans a folder of CSV files or connects to SQL databases, reads schema metadata and sample rows.
2. **Catalog Generation** — The extracted metadata is assembled into a structured JSON catalog (`catalog.json`).
3. **AI Enrichment** — `llm_enrich.py` optionally enriches column descriptions using OpenAI (or heuristic fallback).
4. **Interactive Dashboard** — `streamlit_app.py` loads the catalog and provides search, browse, relationship visualization, and AI Q&A.
5. **Reporting** — Reports can be generated in Markdown format via `create_pretty_report.py` and `enrich_and_report.py`.

## Tools and Technologies Used

- **Python** — Core programming language
- **Streamlit** — Interactive web dashboard
- **Pandas** — Data loading and profiling
- **NumPy** — Numerical computations
- **SQLAlchemy** — SQL database connectivity
- **JSON** — Catalog storage format
- **Git & GitHub** — Version control and collaboration
- **OpenAI API** — AI enrichment (optional)
- **pypdf** — PDF extraction utilities

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/bhanu65-4/data-catalog-builder.git
cd data-catalog-builder

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Testing

### Running Tests

This project uses `pytest` for testing. To run all tests:

```bash
# Install test dependencies (if not already installed)
pip install pytest

# Run all tests
python -m pytest tests/ -v
```

All **19 tests** should pass, covering:

- **Input validation** — All CSV files in `data/` exist and have expected columns/rows
- **Catalog generation** — `scan_csv_folder` and `build_catalog` produce correct output structure
- **Metadata correctness** — Column names, data types, sample values, and row counts match expected values
- **Relationship discovery** — Shared columns (e.g. `customers.customer_id` → `orders.customer_id`) are detected
- **Pipeline integration** — End-to-end catalog build from CSV to JSON output
- **Submission artifacts** — Generated reports and catalog files exist

### Sample Data

The `data/` folder contains CSV input files used by both the application and the test suite:

| File | Columns | Rows | Description |
|------|---------|------|-------------|
| `customers.csv` | customer_id, first_name, last_name, email, phone_number, city | 20 | Customer records |
| `orders.csv` | order_id, customer_id, product_id, quantity, amount, payment_method, order_status, shipping_city | 30 | Order transactions |
| `products.csv` | product_id, product_name, category, brand, price, stock_quantity | 20 | Product catalog |
| `departments.csv` | department_id, department_name, manager_name, employee_count, location | 12 | Department info |

### Expected Outputs

Running `python cataloger.py --csv-folder data --out catalog.json` generates `catalog.json` containing:
- 4 tables with full schema metadata
- Column names, data types, and sample values for all columns
- Row counts for each table
- A searchable, AI-enrichable catalog structure

## Run Instructions

### 1. Generate a Catalog from CSV Files

```bash
python cataloger.py --csv-folder data --out catalog.json
```

This scans all CSV files in the `data/` folder and produces a `catalog.json` file with table schemas, column types, sample values, and row counts.

### 2. (Optional) Enrich with AI Descriptions

```bash
# Set your OpenAI API key (optional — falls back to heuristics)
set OPENAI_API_KEY=your-key-here

# Run enrichment
python enrich_and_report.py
```

### 3. Launch the Interactive Dashboard

```bash
streamlit run streamlit_app.py -- --catalog catalog.json
```

Navigate to the URL shown in the terminal (typically `http://localhost:8501`) to explore tables, columns, relationships, search the catalog, and use the AI question box.

### 4. (Alternative) Generate a Report

```bash
python create_pretty_report.py --catalog catalog.json --output outputs/final_report.md
```

## Sample Input and Sample Output

### Sample Input (CSV files in `data/`)

**`data/customers.csv`** (first few rows):
```csv
customer_id,first_name,last_name,email,department_id
1,John,Doe,john@example.com,101
2,Jane,Smith,jane@example.com,102
3,Bob,Johnson,bob@example.com,101
```

**`data/orders.csv`** (first few rows):
```csv
order_id,customer_id,product_id,order_date,amount,status
1001,1,201,2024-01-15,250.00,shipped
1002,2,202,2024-01-16,150.00,pending
1003,1,203,2024-01-17,99.99,delivered
```

### Sample Output (`catalog.json` — partial)

```json
{
  "tables": [
    {
      "source": "csv",
      "name": "customers",
      "path": "data/customers.csv",
      "row_count": 92,
      "columns": [
        {
          "name": "customer_id",
          "dtype": "int64",
          "sample_values": ["1", "2", "3"],
          "description": "Unique identifier for each customer"
        },
        {
          "name": "email",
          "dtype": "object",
          "sample_values": ["john@example.com", "jane@example.com"],
          "description": "Customer email address"
        }
      ]
    },
    {
      "source": "csv",
      "name": "orders",
      "path": "data/orders.csv",
      "row_count": 92,
      "columns": [
        {
          "name": "order_id",
          "dtype": "int64",
          "sample_values": ["1001", "1002"],
          "description": "Unique order identifier"
        },
        {
          "name": "customer_id",
          "dtype": "int64",
          "sample_values": ["1", "2"],
          "description": "Foreign key referencing customers.customer_id"
        }
      ]
    }
  ]
}
```

### Sample Catalog Metrics

| Metric | Value |
|--------|-------|
| Tables | 5 |
| Columns | 32 |
| Relationships | 3 |
| Rows Profiled | 92 |

## AI Capability Demonstrated

1. **AI-Assisted Column Description Generation**: `llm_enrich.py` uses OpenAI (or a heuristic fallback) to generate business-friendly descriptions for each column based on its name and sample values. Example prompt: *"Write a concise, business-friendly description for the column 'customer_id'. Example values: 1, 2, 3."*

2. **Natural-Language Catalog Query**: The Streamlit dashboard includes an AI question box where users can ask questions like *"Which table contains customer emails?"* or *"Show relationships involving orders"* and get intelligent responses based on the catalog metadata.

3. **LLM Integration Path**: The project supports an OpenAI-based enrichment pipeline with graceful fallback to local heuristics when an API key is not available.

## Assumptions and Limitations

### Assumptions
- CSV files follow a consistent format with headers in the first row
- Columns with matching names across tables are potential relationships
- Sample data (first 5 rows) is representative enough for profiling
- UTF-8 encoding for CSV files (with fallback to other encodings)

### Limitations
- Relationship discovery is heuristic (based on column name matching) — not true foreign key detection
- AI-generated column descriptions may be inaccurate for ambiguous column names
- No automatic PII or sensitive data detection
- Limited to CSV files and SQL databases (no support for APIs, cloud storage, or NoSQL databases)
- Sample-based profiling may not capture full data distribution
- The AI enrichment path requires an OpenAI API key; without it, only heuristic descriptions are generated
- No data lineage tracking or versioning of catalogs

## Demo Video Link

A demo video (5–7 minutes) walking through the project is available here:

**[▶ Watch Demo Video](https://www.loom.com/share/22237668d58644a59dcbe5fcd8571fa5)**

## Submission Checklist

- [x] Public GitHub repository
- [x] README with setup instructions
- [x] Demo video (5–7 minutes)
- [x] Team information
- [x] Sample datasets
- [x] Generated outputs
- [x] AI usage documentation
- [x] Team resumes available in `resumes/` folder

## Future Enhancements

- Support for additional database systems (PostgreSQL, MySQL, MongoDB)
- Advanced data lineage tracking
- Automated data quality checks
- Enhanced AI-generated descriptions with context-aware prompts
- Role-based access control
- Real-time catalog updates from live data sources

## License

This project is intended for educational and prototype demonstration purposes.