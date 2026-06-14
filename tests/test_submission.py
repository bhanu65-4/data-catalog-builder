import os
import json


def test_enriched_catalog_exists():
    assert os.path.exists('catalog.json')
    c = json.loads(open('catalog.json','r',encoding='utf-8').read())
    assert 'tables' in c and len(c['tables']) >= 1


def test_reports_generated():
    assert os.path.exists('catalog_report.md')
    assert os.path.exists('catalog_report.html')
