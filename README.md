# Data Catalog Builder

A lightweight data cataloging application that scans CSV files and SQL databases, extracts metadata, profiles datasets, discovers relationships, and provides an interactive Streamlit interface for exploration.

## Features

* Upload and register CSV datasets
* Automatic metadata extraction
* Column profiling and statistics
* Relationship discovery between tables
* Searchable data catalog
* Interactive Streamlit dashboard
* Export catalog functionality
* LLM-ready metadata descriptions

## Project Structure

```text
data-catalog-builder/
├── data/
├── outputs/
├── cataloger.py
├── streamlit_app.py
├── requirements.txt
├── README.md
└── catalog.json
```

## Installation

Create a virtual environment and install dependencies:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

## Usage

### Generate Catalog

```bash
python cataloger.py --csv-folder data --out catalog.json
```

### Run the Streamlit Application

```bash
streamlit run streamlit_app.py -- --catalog catalog.json
```

## Sample Workflow

1. Upload one or more CSV files.
2. Generate metadata and profiles.
3. Explore tables, columns, and relationships.
4. Search catalog contents.
5. Export the catalog for reporting or sharing.

## Technologies Used

* Python
* Streamlit
* Pandas
* NumPy
* JSON
* Git & GitHub

## Outputs

Generated outputs and reports are stored in the `outputs/` folder.

## Submission Checklist

* Public GitHub repository
* README with setup instructions
* Demo video (5–7 minutes)
* Team information
* Sample datasets
* Generated outputs
* AI usage documentation

## Future Enhancements

* Support for additional database systems
* Advanced data lineage tracking
* Automated data quality checks
* Enhanced AI-generated descriptions
* Role-based access control

## License

This project is intended for educational and prototype demonstration purposes.
