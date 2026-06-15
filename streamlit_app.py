import streamlit as st
import json
import argparse
import pandas as pd
from io import BytesIO
from pathlib import Path
from datetime import datetime


DEFAULT_CATALOG = 'catalog.json'
DATA_DIR = Path('data')


def load_catalog(path):
    if Path(path).exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'tables': []}


def save_catalog(catalog, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)


def build_table_metadata(df, table_name, source='uploaded', path='uploaded'):
    columns = []
    for col in df.columns:
        samples = df[col].dropna().astype(str).head(5).tolist()
        columns.append({
            'name': col,
            'dtype': str(df[col].dtype),
            'sample_values': samples,
            'description': None
        })
    return {
        'source': source,
        'name': table_name,
        'path': path,
        'row_count': int(len(df)),
        'columns': columns
    }


def show_metrics(cards):
    cols = st.columns(len(cards))
    for idx, card in enumerate(cards):
        cols[idx].metric(card['label'], card['value'], delta=card.get('delta', ''))


def set_background():
    st.markdown(
        """<style>
        :root { color-scheme: dark; }
        .stApp { background: #0F172A; color: #F8FAFC; }
        .block-container { background: #0F172A; color: #F8FAFC; }
        .stApp .main, .stApp .block-container { background: #0F172A; color: #F8FAFC; }
        .css-1d391kg .css-1dh4zb1 { background-color: #0F172A !important; }
        .css-1d391kg .css-1venc0e { background-color: #0F172A !important; }
        .css-1vq4p4l.egzxvld0 { background-color: #0F172A !important; }
        .stSidebar { background: #0F172A; color: #F8FAFC; }
        .stSidebar .css-1lcbmhc.e1fqkh3o3 { color: #F8FAFC; }
        .card { border-radius: 18px; background: #1E293B; padding: 18px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.25); }
        .section-title { color: #F8FAFC; font-size: 1.2rem; font-weight: 700; }
        .small-muted { color: #94A3B8; }
        .data-card { border: 1px solid #334155; border-radius: 14px; padding: 16px; margin-bottom: 12px; background: #1E293B; }
        .table-header { font-size: 1rem; font-weight: 700; color: #F8FAFC; }
        .stButton button, button[type="submit"] { background-color: #3B82F6 !important; color: #FFFFFF !important; border: none !important; }
        .stButton button:hover, button[type="submit"]:hover { background-color: #2563EB !important; }
        .stSuccess { color: #10B981 !important; }
        .stAlert { border-left-color: #10B981 !important; }
        .stMarkdown svg, .stHeader svg, .stMetric svg, .stText svg { color: #3B82F6 !important; fill: #3B82F6 !important; }
        .stMarkdown > div > p, .stMarkdown > div > span, .stText > div, .stHeader > div, .stMetric > div, .stTextInput>div>div>input, .stTextInput>div>label {
            color: #F8FAFC !important;
        }
        .css-14xtw13.e8zbici2 { background-color: #1E293B !important; }
        .css-1q8dd3e.e1fqkh3o3 { background-color: #0F172A !important; }
        </style>""",
        unsafe_allow_html=True,
    )


def main(catalog_path):
    st.set_page_config(
        page_title='Data Catalog Builder',
        page_icon='📊',
        layout='wide'
    )
    set_background()

    catalog = load_catalog(catalog_path)
    if 'tables' not in catalog:
        catalog['tables'] = []

    if 'uploaded_tables' not in st.session_state:
        st.session_state.uploaded_tables = []

    st.sidebar.title('Data Catalog Controls')
    st.sidebar.markdown('Upload a new CSV to register it in the catalog.')
    uploaded_file = st.sidebar.file_uploader('Upload CSV', type='csv', key='file_uploader')
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            table_name = Path(uploaded_file.name).stem
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            uploaded_name = f'{table_name}_uploaded_{timestamp}'
            new_table = build_table_metadata(df, uploaded_name, source='uploaded', path=uploaded_file.name)
            catalog['tables'].append(new_table)
            st.session_state.uploaded_tables.append(uploaded_name)
            st.sidebar.success(f'Uploaded {uploaded_file.name} as table {uploaded_name}')
        except Exception as exc:
            st.sidebar.error(f'Upload failed: {exc}')

    st.sidebar.divider()
    if st.sidebar.button('Save Catalog', key='save_catalog'):
        save_catalog(catalog, catalog_path)
        st.sidebar.success('Catalog saved to ' + catalog_path)

    # Overview toggle
    if 'show_overview' not in st.session_state:
        st.session_state.show_overview = False
    if st.sidebar.button('Show Catalog Overview', key='show_overview_btn'):
        st.session_state.show_overview = not st.session_state.show_overview

    st.sidebar.markdown('---')
    st.sidebar.markdown('Streamlit Cloud deployment is supported: use this repo as an app and set the app file to `streamlit_app.py`.')
    st.sidebar.markdown('Use **Save Catalog** before closing to persist changes in the workspace.')

    tables = catalog.get('tables', [])
    total_tables = len(tables)
    total_columns = sum(len(t.get('columns', [])) for t in tables)
    total_rows = sum(int(t.get('row_count', 0) or 0) for t in tables)

    name_to_cols = {t.get('name'): [c.get('name') for c in t.get('columns', [])] for t in tables}
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
                parent, child = (src, dst) if src.get('row_count', 0) <= dst.get('row_count', 0) else (dst, src)
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
    total_relationships = len(relationship_rows)

    st.markdown('# 📊 Data Catalog Builder')
    st.markdown('### Enterprise-grade metadata explorer for CSV and SQL catalogs')

    show_metrics([
        {'label': 'Tables', 'value': total_tables},
        {'label': 'Columns', 'value': total_columns},
        {'label': 'Relationships', 'value': total_relationships},
        {'label': 'Rows Profiled', 'value': total_rows},
    ])

    def render_overview(tables, relationship_rows):
        st.header('Catalog Overview')
        st.markdown('Quick navigation to see what is available in the catalog.')
        with st.expander('Tables and columns', expanded=True):
            for t in tables:
                st.markdown(f"**{t.get('name')}** — Rows: {t.get('row_count', 'n/a')} — Columns: {len(t.get('columns', []))}")
                cols = ', '.join([c.get('name') for c in t.get('columns', [])])
                st.markdown(f"Columns: {cols}")
                st.divider()

        with st.expander('Relationships', expanded=True):
            if not relationship_rows:
                st.info('No detected relationships (shared column names).')
            else:
                for r in relationship_rows:
                    st.markdown(f"- **{r['type']}**: {r['parent']}.{r['column']} → {r['child']}.{r['column']}")

        with st.expander('Row profiles (samples & uniques)', expanded=False):
            for t in tables:
                st.markdown(f"**{t.get('name')}** — Rows: {t.get('row_count', 'n/a')}")
                try:
                    if t.get('path') and Path(t.get('path')).exists():
                        df = pd.read_csv(t.get('path'))
                    else:
                        # build small df from samples
                        cols = t.get('columns', [])
                        maxlen = max((len(c.get('sample_values', [])) for c in cols), default=0)
                        data = {}
                        for c in cols:
                            vals = c.get('sample_values', [])
                            vals = [str(v) for v in vals] + [""] * (maxlen - len(vals))
                            data[c.get('name')] = vals
                        df = pd.DataFrame(data)
                    # show simple profile
                    prof_rows = []
                    for col in df.columns:
                        col_ser = df[col].dropna().astype(str)
                        uniq = int(col_ser.nunique()) if not col_ser.empty else 0
                        samples = ', '.join(col_ser.unique()[:3])
                        prof_rows.append({'column': col, 'unique': uniq, 'samples': samples})
                    prof_df = pd.DataFrame(prof_rows)
                    st.table(prof_df)
                except Exception as exc:
                    st.write('Could not profile table:', exc)

    if st.session_state.show_overview:
        render_overview(tables, relationship_rows)

    with st.expander('Search and actions', expanded=True):
        q = st.text_input('Search tables or columns', placeholder='Search by table name, column name, or description...')
        if st.button('Enrich missing descriptions'):
            from llm_enrich import enrich_catalog
            catalog = enrich_catalog(catalog)
            save_catalog(catalog, catalog_path)
            st.success('Catalog enriched and saved')

        st.markdown('---')
        ai_question = st.text_input('Ask the catalog AI', placeholder='Which table contains customer emails?')
        if st.button('Ask AI', key='ask_ai'):
            from llm_enrich import ask_catalog_question
            answer = ask_catalog_question(catalog, ai_question)
            st.markdown('**AI Answer**')
            st.info(answer)

    def matches_table(item, q):
        if not q:
            return True
        ql = q.lower()
        return ql in item.get('name', '').lower()

    def get_col_description(c):
        from llm_enrich import _generate_fallback_description
        return c.get('description') or _generate_fallback_description(c.get('name'), c.get('sample_values', []))

    def matches_column(c, q, table_name=''):
        """
        Match a column against the query. Tokenize the query and require each token
        to match either the table name, column name, column description, or any
        sample value. This enables queries like "order 1001" or "employee bhanu".
        """
        if not q:
            return True
        tokens = [t.strip().lower() for t in q.split() if t.strip()]
        desc = get_col_description(c).lower()
        col_name = c.get('name', '').lower()
        samples = [str(s).lower() for s in c.get('sample_values', [])]
        for tok in tokens:
            matched = False
            if tok in table_name.lower():
                matched = True
            if not matched and tok in col_name:
                matched = True
            if not matched and tok in desc:
                matched = True
            if not matched:
                for s in samples:
                    if tok in s:
                        matched = True
                        break
            if not matched:
                return False
        return True

    def matched_columns(table, q):
        if not q:
            return table.get('columns', [])
        cols = [c for c in table.get('columns', []) if matches_column(c, q, table.get('name', ''))]
        if cols:
            return cols
        if matches_table(table, q):
            return table.get('columns', [])
        return []

    def find_matching_rows(table, q):
        """Return a DataFrame of rows matching all tokens in `q` across any column."""
        if not q:
            return None
        tokens = [t.strip().lower() for t in q.split() if t.strip()]
        # Load dataframe from path when available
        try:
            if table.get('path') and Path(table.get('path')).exists():
                df = pd.read_csv(table.get('path'))
            else:
                # build a small DataFrame from sample_values
                cols = table.get('columns', [])
                if not cols:
                    return None
                maxlen = max((len(c.get('sample_values', [])) for c in cols), default=0)
                data = {}
                for c in cols:
                    vals = c.get('sample_values', [])
                    # pad to maxlen
                    vals = [str(v) for v in vals] + [""] * (maxlen - len(vals))
                    data[c.get('name')] = vals
                df = pd.DataFrame(data)
        except Exception:
            return None

        if df.empty:
            return None

        mask = pd.Series([True] * len(df))
        for tok in tokens:
            # each token must appear in at least one column for the row
            mask_tok = df.apply(lambda row: row.astype(str).str.lower().str.contains(tok, na=False)).any(axis=1)
            mask = mask & mask_tok
        res = df[mask]
        if res.empty:
            return None
        return res

    search_results = []
    for t in tables:
        matched_cols = matched_columns(t, q)
        if q and not matched_cols:
            continue
        search_results.append((t, matched_cols))

    if q and len(search_results) == 0:
        st.warning('No tables or columns match your search.')

    any_row_matches = False
    any_col_matches = False
    for t, matched_cols in search_results:
        with st.container():
            st.markdown(f"### 📁 {t.get('name')}  <span class='small-muted'>({t.get('source')})</span>", unsafe_allow_html=True)
            if t.get('path'):
                st.caption(t.get('path'))
            if t.get('summary'):
                st.markdown(f"**Summary:** {t.get('summary')}")
            row_count = t.get('row_count')
            if row_count is not None:
                st.markdown(f"**Rows:** {row_count}")
            # If the query matches actual row values, show matching rows (individual data)
            matched_rows = None
            if q:
                try:
                    matched_rows = find_matching_rows(t, q)
                except Exception:
                    matched_rows = None
            if matched_rows is not None:
                st.markdown('**Matching rows**')
                for _idx, row in matched_rows.iterrows():
                    parts = []
                    for col in matched_rows.columns:
                        parts.append(f"<div><strong>{col}:</strong> {row[col]}</div>")
                    html = "<div class='data-card'>" + "".join(parts) + "</div>"
                    st.markdown(html, unsafe_allow_html=True)
                st.divider()
                any_row_matches = True
                continue
            if matched_cols:
                any_col_matches = True
            for c in matched_cols:
                name = c.get('name')
                dtype = c.get('dtype')
                desc = get_col_description(c)
                samples = ', '.join(c.get('sample_values', [])[:5])
                st.markdown(f"<div class='data-card'><div class='table-header'>{name} — {dtype}</div><div>{desc}</div><div><small>Samples: {samples}</small></div></div>", unsafe_allow_html=True)
                stats_shown = False
                try:
                    if t.get('source') == 'csv' and t.get('path') and Path(t.get('path')).exists():
                        col_ser = pd.read_csv(t.get('path'), usecols=[name], squeeze=True)
                    else:
                        col_ser = pd.Series(c.get('sample_values', []))
                except Exception:
                    col_ser = pd.Series(c.get('sample_values', []))
                try:
                    num = pd.to_numeric(col_ser.dropna(), errors='coerce')
                    if num.notna().any():
                        mn = num.min()
                        mx = num.max()
                        avg = num.mean()
                        st.write(f"Min: {mn}   |   Max: {mx}   |   Avg: {round(avg, 2)}")
                        stats_shown = True
                except Exception:
                    pass
                if not stats_shown:
                    try:
                        uniq = col_ser.dropna().astype(str).nunique()
                        st.write(f"Unique Values: {int(uniq)}")
                    except Exception:
                        pass
            st.divider()

    # If user searched and nothing matched at row or column level, show message
    if q and not any_row_matches and not any_col_matches:
        st.error(f'No data found for "{q}"')

    st.header('Dataset Lineage')
    if not relationship_rows:
        st.info('No lineage detected (no shared column names across tables).')
    else:
        rel = relationship_rows[0]
        st.markdown(f"**Relationship:** {rel['parent']}.{rel['column']} → {rel['child']}.{rel['column']}")
        st.code(
            f"{rel['parent']}.{rel['column']}\n"
            f"        │\n"
            f"        ▼\n"
            f"{rel['child']}.{rel['column']}",
            language='text'
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--catalog', default=DEFAULT_CATALOG)
    args = parser.parse_args()
    main(args.catalog)