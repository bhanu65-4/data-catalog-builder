import os
from cataloger import build_catalog


def test_build_catalog_from_csv(tmp_path):
    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    f = data_dir / 'sample.csv'
    f.write_text('a,b\n1,hello\n2,world\n')
    out = tmp_path / 'catalog.json'
    c = build_catalog(csv_folder=str(data_dir), out_path=str(out))
    assert 'tables' in c
    assert len(c['tables']) == 1
    t = c['tables'][0]
    assert t['name'] == 'sample'
    assert any(col['name'] == 'a' for col in t['columns'])
