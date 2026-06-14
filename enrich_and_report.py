import json
from pathlib import Path
from llm_enrich import enrich_catalog, _generate_fallback_description


def make_markdown_report(catalog, out_md_path):
    lines = ["# Data Catalog Report\n"]
    for table in catalog.get('tables', []):
        lines.append(f"## {table.get('name')} ({table.get('source')})\n")
        lines.append(f"**Path:** {table.get('path')}\n")
        lines.append("| Column | Type | Description | Sample values |\n")
        lines.append("|---|---:|---|---|\n")
        for col in table.get('columns', []):
            name = col.get('name')
            dtype = col.get('dtype')
            desc = col.get('description') or _generate_fallback_description(name, col.get('sample_values', []))
            samples = ', '.join(col.get('sample_values', [])[:5])
            # escape pipes
            samples = samples.replace('|', '\\|')
            desc = desc.replace('|', '\\|') if desc else ''
            lines.append(f"| {name} | {dtype} | {desc} | {samples} |\n")
        lines.append('\n')
    Path(out_md_path).write_text(''.join(lines), encoding='utf-8')


def make_html_report(md_path, out_html_path):
    # Minimal HTML wrapper using GitHub-flavored markdown via simple replacement
    md = Path(md_path).read_text(encoding='utf-8')
    html = f"<html><head><meta charset=\"utf-8\"><title>Data Catalog Report</title></head><body><pre style='white-space:pre-wrap;font-family:Segoe UI,Arial'>{md}</pre></body></html>"
    Path(out_html_path).write_text(html, encoding='utf-8')


def main(catalog_path='catalog.json'):
    p = Path(catalog_path)
    if not p.exists():
        print('catalog not found:', catalog_path)
        return
    catalog = json.loads(p.read_text(encoding='utf-8'))
    # Enrich descriptions (uses fallback heuristics if no API key)
    catalog = enrich_catalog(catalog)
    # Save enriched catalog
    p.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding='utf-8')
    # Write markdown and html reports
    md = 'catalog_report.md'
    html = 'catalog_report.html'
    make_markdown_report(catalog, md)
    make_html_report(md, html)
    print('Wrote enriched catalog and reports:', p, md, html)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--catalog', default='catalog.json')
    args = parser.parse_args()
    main(args.catalog)
