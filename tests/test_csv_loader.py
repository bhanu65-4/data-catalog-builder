import os
import pandas as pd
from cataloger import scan_csv_folder


def test_scan_csv_folder_produces_catalog(tmp_path):
    csv_dir = tmp_path / 'data'
    csv_dir.mkdir()
    file_path = csv_dir / 'employees.csv'
    file_path.write_text('employee_id,name\nage,30\n')
    catalog = scan_csv_folder(str(csv_dir), sample_size=1)
    assert 'tables' in catalog
    assert len(catalog['tables']) == 1
    table = catalog['tables'][0]
    assert table['name'] == 'employees'
    assert table['row_count'] == 1
    assert any(col['name'] == 'employee_id' for col in table['columns'])
