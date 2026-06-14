import json
from pathlib import Path


def html_escape(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')) if s else ''


def generate(catalog_path='catalog.json', out='catalog_report_pretty.html'):
    p = Path(catalog_path)
    if not p.exists():
        print('catalog not found')
        return
    c = json.loads(p.read_text(encoding='utf-8'))
    parts = []
    parts.append("""
<html>
<head>
  <meta charset="utf-8">
  <title>Data Catalog Report</title>
  <style>
    body{font-family:Segoe UI,Arial;margin:24px;color:#111}
    h1{border-bottom:2px solid #eee;padding-bottom:8px}
    table{border-collapse:collapse;width:100%;margin-bottom:24px}
    th,td{border:1px solid #ddd;padding:8px;text-align:left}
    th{background:#f7f7f7}
    .meta{color:#666;font-size:0.95em;margin-bottom:12px}
  </style>
</head>
<body>
<h1>Data Catalog Report</h1>
""")

    for table in c.get('tables', []):
        parts.append(f"<h2>{html_escape(table.get('name'))} <small style='color:#666'>({html_escape(table.get('source'))})</small></h2>")
        parts.append(f"<div class=\"meta\">Path: {html_escape(table.get('path'))}</div>")
        parts.append('<table>')
        parts.append('<tr><th>Column</th><th>Type</th><th>Description</th><th>Sample values</th></tr>')
        for col in table.get('columns', []):
            name = html_escape(col.get('name'))
            dtype = html_escape(col.get('dtype'))
            desc = html_escape(col.get('description') or '')
            samples = ', '.join([html_escape(s) for s in col.get('sample_values', [])[:10]])
            parts.append(f"<tr><td>{name}</td><td>{dtype}</td><td>{desc}</td><td>{samples}</td></tr>")
        parts.append('</table>')

    parts.append('</body></html>')
    Path(out).write_text('\n'.join(parts), encoding='utf-8')
    print('Wrote', out)


if __name__ == '__main__':
    generate()
