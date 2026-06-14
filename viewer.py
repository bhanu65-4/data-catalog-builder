import json


def print_catalog(path):
    with open(path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    print(f"Catalog: {path}")
    print(f"Tables: {len(catalog.get('tables', []))}\n")
    for t in catalog.get('tables', []):
        print(f"Table: {t.get('name')}  (source={t.get('source')})")
        print(f"Path: {t.get('path')}")
        for c in t.get('columns', []):
            print(f"  - {c.get('name')} [{c.get('dtype')}]\n    desc: {c.get('description') or '<none>'}\n    samples: {', '.join(c.get('sample_values', [])[:5])}")
        print()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='View generated catalog JSON on the console')
    parser.add_argument('--catalog', default='catalog.json', help='Path to the generated catalog file')
    args = parser.parse_args()
    print_catalog(args.catalog)
