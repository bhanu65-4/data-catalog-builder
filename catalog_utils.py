from pathlib import Path
import pandas as pd


def detect_relationships(tables):
    name_to_cols = {
        t.get('name'): [c.get('name') for c in t.get('columns', [])]
        for t in tables
    }
    relationship_rows = []
    seen_relations = set()
    for src in tables:
        for dst in tables:
            if src is dst:
                continue
            shared = set(name_to_cols.get(src.get('name'), [])) & set(name_to_cols.get(dst.get('name'), []))
            if not shared:
                continue
            for col in sorted(shared):
                src_name = src.get('name')
                dst_name = dst.get('name')
                if src_name == dst_name:
                    continue
                if (dst_name, src_name, col) in seen_relations:
                    continue
                parent, child = (src, dst) if int(src.get('row_count', 0) or 0) <= int(dst.get('row_count', 0) or 0) else (dst, src)
                rel_key = (parent.get('name'), child.get('name'), col)
                if rel_key in seen_relations:
                    continue
                seen_relations.add(rel_key)
                relationship_rows.append({
                    'type': 'One-to-Many',
                    'parent': parent.get('name'),
                    'child': child.get('name'),
                    'column': col,
                })
    return relationship_rows


def find_matching_rows(table, q):
    if not q:
        return None
    tokens = [t.strip().lower() for t in q.split() if t.strip()]
    try:
        if table.get('path') and Path(table.get('path')).exists():
            df = pd.read_csv(table.get('path'))
        else:
            cols = table.get('columns', [])
            if not cols:
                return None
            maxlen = max((len(c.get('sample_values', [])) for c in cols), default=0)
            data = {}
            for c in cols:
                vals = [str(v) for v in c.get('sample_values', [])]
                vals = vals + [""] * (maxlen - len(vals))
                data[c.get('name')] = vals
            df = pd.DataFrame(data)
    except Exception:
        return None

    if df.empty:
        return None

    mask = pd.Series([True] * len(df))
    for tok in tokens:
        mask_tok = df.apply(lambda row: row.astype(str).str.lower().str.contains(tok, na=False)).any(axis=1)
        mask = mask & mask_tok
    res = df[mask]
    if res.empty:
        return None
    return res
