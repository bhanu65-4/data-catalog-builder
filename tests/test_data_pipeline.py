"""Test that the real data/ folder CSV files produce the expected catalog output."""
import json
import os
import pytest
from cataloger import build_catalog, scan_csv_folder


SAMPLE_DATA = {
    'customers': {'columns': ['customer_id', 'first_name', 'last_name', 'email', 'phone_number', 'city'], 'rows': 20},
    'orders':    {'columns': ['order_id', 'customer_id', 'product_id', 'quantity', 'amount', 'payment_method', 'order_status', 'shipping_city'], 'rows': 30},
    'products':  {'columns': ['product_id', 'product_name', 'category', 'brand', 'price', 'stock_quantity'], 'rows': 20},
    'departments': {'columns': ['department_id', 'department_name', 'manager_name', 'employee_count', 'location'], 'rows': 12},
}


def test_data_folder_csv_files_exist():
    """All expected CSV input files are present."""
    for table_name in SAMPLE_DATA:
        csv_path = f'data/{table_name}.csv'
        assert os.path.exists(csv_path), f'Missing input file: {csv_path}'


def test_catalog_json_exists():
    """catalog.json was generated and has the expected structure."""
    assert os.path.exists('catalog.json')
    with open('catalog.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    assert 'tables' in catalog
    assert len(catalog['tables']) >= 4, 'Expected at least 4 tables in catalog'


def test_all_csv_files_are_cataloged():
    """Every CSV file in the data folder appears as a table in catalog.json."""
    with open('catalog.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    catalog_table_names = {t['name'] for t in catalog['tables']}
    for table_name in SAMPLE_DATA:
        assert table_name in catalog_table_names, f'Table {table_name} missing from catalog'


def test_catalog_has_correct_column_names():
    """Each table in catalog.json has the expected column names."""
    with open('catalog.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    for table in catalog['tables']:
        name = table['name']
        if name in SAMPLE_DATA:
            actual_cols = {c['name'] for c in table['columns']}
            expected_cols = set(SAMPLE_DATA[name]['columns'])
            assert actual_cols == expected_cols, (
                f'Columns mismatch for {name}: expected {expected_cols}, got {actual_cols}'
            )


def test_catalog_has_sample_values():
    """Each column should have at least one sample value."""
    with open('catalog.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    for table in catalog['tables']:
        for col in table['columns']:
            samples = col.get('sample_values', [])
            assert len(samples) > 0, (
                f'Column {col["name"]} in table {table["name"]} has no sample values'
            )


def test_catalog_has_data_types():
    """Each column should have a data type string."""
    with open('catalog.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    for table in catalog['tables']:
        for col in table['columns']:
            assert col.get('dtype'), f'Column {col["name"]} in table {table["name"]} has no dtype'


def test_scan_csv_folder_on_real_data():
    """Happy-path: scan_csv_folder on the real data/ folder produces correct results."""
    catalog = scan_csv_folder('data', sample_size=5)
    assert len(catalog['tables']) == len(SAMPLE_DATA)
    for table in catalog['tables']:
        name = table['name']
        assert name in SAMPLE_DATA, f'Unexpected table {name}'
        assert table['source'] == 'csv'
        assert table['row_count'] == SAMPLE_DATA[name]['rows'], (
            f'Row count for {name}: expected {SAMPLE_DATA[name]["rows"]}, got {table["row_count"]}'
        )


def test_build_catalog_pipeline(tmp_path):
    """Full pipeline: build_catalog from real data folder produces valid output."""
    out_file = tmp_path / 'test_pipeline_catalog.json'
    catalog = build_catalog(csv_folder='data', out_path=str(out_file))
    assert os.path.exists(str(out_file))
    assert len(catalog['tables']) == len(SAMPLE_DATA)
    # Verify the file on disk matches
    with open(str(out_file), 'r', encoding='utf-8') as f:
        reloaded = json.load(f)
    assert reloaded['tables'][0]['name'] == catalog['tables'][0]['name']


def test_relationships_discovered():
    """At least one relationship should be discovered between shared columns."""
    from catalog_utils import detect_relationships
    with open('catalog.json', 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    rels = detect_relationships(catalog['tables'])
    # customers.customer_id → orders.customer_id should be detected
    customer_order_rels = [
        r for r in rels
        if r['parent'] == 'customers' and r['child'] == 'orders' and r['column'] == 'customer_id'
    ]
    assert len(customer_order_rels) >= 1, (
        'Expected relationship customers.customer_id → orders.customer_id'
    )


def test_customers_csv_has_expected_rows():
    """Validate the actual content of customers.csv."""
    import pandas as pd
    df = pd.read_csv('data/customers.csv')
    assert len(df) == SAMPLE_DATA['customers']['rows']
    assert list(df.columns) == SAMPLE_DATA['customers']['columns']
    # Check first row values
    row = df.iloc[0]
    assert row['customer_id'] == 1
    assert row['first_name'] == 'Harsha'
    assert row['email'] == 'harsha.sharma@example.com'


def test_orders_csv_has_expected_rows():
    """Validate the actual content and structure of orders.csv."""
    import pandas as pd
    df = pd.read_csv('data/orders.csv')
    assert len(df) == SAMPLE_DATA['orders']['rows']
    assert list(df.columns) == SAMPLE_DATA['orders']['columns']
    # Check first row values
    row = df.iloc[0]
    assert row['order_id'] == 1001
    assert row['customer_id'] == 1


def test_departments_csv_has_expected_rows():
    """Validate the actual content and structure of departments.csv."""
    import pandas as pd
    df = pd.read_csv('data/departments.csv')
    assert len(df) == SAMPLE_DATA['departments']['rows']
    assert list(df.columns) == SAMPLE_DATA['departments']['columns']
