import os
import json


def test_enriched_catalog_exists():
    assert os.path.exists('catalog.json')
    c = json.loads(open('catalog.json','r',encoding='utf-8').read())
    assert 'tables' in c and len(c['tables']) >= 1


def test_reports_generated():
    assert os.path.exists('outputs/final_report.md'), 'Expected report file outputs/final_report.md'
    assert os.path.exists('catalog.json'), 'Expected catalog.json to exist'
