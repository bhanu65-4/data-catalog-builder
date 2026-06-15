import json
import os
from cataloger import build_catalog


def test_catalog_json_exists():
    assert os.path.exists('catalog.json')
    with open('catalog.json', 'r', encoding='utf-8') as f:
        c = json.load(f)
    assert 'tables' in c
    assert isinstance(c['tables'], list)


def test_build_catalog_writes_file(tmp_path):
    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    csv_file = data_dir / 'products.csv'
    csv_file.write_text('product_id,product_name\nPRD1,Widget\n')
    out_file = tmp_path / 'catalog_out.json'
    catalog = build_catalog(csv_folder=str(data_dir), out_path=str(out_file))
    assert os.path.exists(str(out_file))
    assert catalog['tables'][0]['name'] == 'products'
    assert catalog['tables'][0]['row_count'] == 1
