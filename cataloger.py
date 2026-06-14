import os
import json
import pandas as pd
from sqlalchemy import create_engine, inspect


def _count_csv_rows(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return max(sum(1 for _ in f) - 1, 0)
    except Exception:
        return 0


def scan_csv_folder(folder, sample_size=5):
    catalog = {"tables": []}
    if not folder:
        return catalog
    for fname in sorted(os.listdir(folder)):
        if not fname.lower().endswith('.csv'):
            continue
        path = os.path.join(folder, fname)
        table_name = os.path.splitext(fname)[0]
        try:
            df = pd.read_csv(path, nrows=sample_size)
        except Exception:
            df = pd.read_csv(path, nrows=sample_size, engine='python', encoding='utf-8')
        row_count = _count_csv_rows(path)
        columns = []
        for col in df.columns:
            samples = df[col].dropna().astype(str).head(sample_size).tolist()
            columns.append({"name": col, "dtype": str(df[col].dtype), "sample_values": samples, "description": None})
        catalog["tables"].append({"source": "csv", "name": table_name, "path": path, "columns": columns, "row_count": row_count})
    return catalog


def scan_sqlite(sqlite_path, sample_size=5):
    catalog = {"tables": []}
    if not sqlite_path or not os.path.exists(sqlite_path):
        return catalog
    engine = create_engine(f"sqlite:///{sqlite_path}")
    insp = inspect(engine)
    for table in insp.get_table_names():
        try:
            df = pd.read_sql_query(f'SELECT * FROM "{table}" LIMIT {sample_size}', con=engine)
        except Exception:
            df = pd.DataFrame()
        columns = []
        try:
            row_count = pd.read_sql_query(f'SELECT COUNT(*) as cnt FROM "{table}"', con=engine).iloc[0, 0]
        except Exception:
            row_count = 0
        for col in df.columns:
            samples = df[col].dropna().astype(str).head(sample_size).tolist()
            columns.append({"name": col, "dtype": str(df[col].dtype), "sample_values": samples, "description": None})
        catalog["tables"].append({"source": "sqlite", "name": table, "path": sqlite_path, "columns": columns, "row_count": int(row_count)})
    return catalog


def scan_sql_db(conn_str, sample_size=5):
    catalog = {"tables": []}
    if not conn_str:
        return catalog
    engine = create_engine(conn_str)
    insp = inspect(engine)
    for table in insp.get_table_names():
        try:
            df = pd.read_sql_query(f'SELECT * FROM "{table}" LIMIT {sample_size}', con=engine)
        except Exception:
            df = pd.DataFrame()
        columns = []
        try:
            row_count = pd.read_sql_query(f'SELECT COUNT(*) as cnt FROM "{table}"', con=engine).iloc[0, 0]
        except Exception:
            row_count = 0
        for col in df.columns:
            samples = df[col].dropna().astype(str).head(sample_size).tolist()
            columns.append({"name": col, "dtype": str(df[col].dtype), "sample_values": samples, "description": None})
        catalog["tables"].append({"source": "sql", "name": table, "path": conn_str, "columns": columns, "row_count": int(row_count)})
    return catalog


def build_catalog(csv_folder=None, sqlite_path=None, sql_conn=None, out_path='catalog.json'):
    catalog = {"tables": []}
    if csv_folder:
        catalog_csv = scan_csv_folder(csv_folder)
        catalog["tables"].extend(catalog_csv.get("tables", []))
    if sqlite_path:
        catalog_sqlite = scan_sqlite(sqlite_path)
        catalog["tables"].extend(catalog_sqlite.get("tables", []))
    if sql_conn:
        catalog_sql = scan_sql_db(sql_conn)
        catalog["tables"].extend(catalog_sql.get("tables", []))
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    return catalog


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv-folder', help='Folder containing CSV files')
    parser.add_argument('--sqlite', help='Path to sqlite file')
    parser.add_argument('--sql', help='SQLAlchemy connection string (Postgres etc)')
    parser.add_argument('--out', default='catalog.json')
    args = parser.parse_args()
    c = build_catalog(csv_folder=args.csv_folder, sqlite_path=args.sqlite, sql_conn=args.sql, out_path=args.out)
    print(f'Wrote catalog with {len(c.get("tables",[]))} tables to {args.out}')
