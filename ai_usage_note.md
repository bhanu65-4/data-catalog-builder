# AI Usage Note

What AI helped with:
- Generated concise, business-friendly descriptions per column using `llm_enrich.py`.
- Identified likely identifier, email-like, and numeric columns with simple heuristics.

What AI got wrong / limitations:
- Descriptions are best-effort and may be inaccurate for ambiguous column names.
- No sensitive-data detection; avoid running on production PII without review.

Best prompts used:
- Column description prompt (see `prompts.md`)

How to reproduce:
1. Generate catalog: `python cataloger.py --csv-folder data --out catalog.json`
2. Enrich + report: `python enrich_and_report.py --catalog catalog.json`
