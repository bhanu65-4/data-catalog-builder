import os
import time

try:
    import requests
except ImportError:
    requests = None

from catalog_utils import detect_relationships

def _generate_fallback_description(col_name, samples):
    normalized = col_name.strip().lower()
    tokens = normalized.replace('-', '_').split('_')

    manual = {
        'customer_id': "Unique customer identifier.",
        'order_id': "Order's unique identifier used to track purchases.",
        'employee_id': "Unique employee identifier.",
        'id': "Unique identifier for the record.",
        'first_name': "Customer's first name.",
        'last_name': "Customer's last name.",
        'age': "Employee age in years.",
        'name': "Full name of the person or employee.",
        'email': "Customer email address used for communication.",
        'created_at': "Date when the customer registered.",
        'created_on': "Date when the customer registered.",
        'signup_date': "Date when the customer registered.",
        'registration_date': "Date when the customer registered.",
        'order_total': "Total order value in currency units.",
        'amount': "Total order amount.",
        'salary': "Employee compensation amount.",
        'price': "Price in currency units.",
        'status': "Current status of the record.",
        'phone_number': "Phone number used for contact.",
        'postal_code': "Postal code for the address.",
        'city': "City of the customer address.",
        'state': "State or region of the customer address.",
    }

    if normalized in manual:
        return manual[normalized]
    if 'customer_id' in normalized:
        return "Customer's unique identifier used to distinguish records."
    if 'email' in normalized:
        return "Email address used for communication."
    if normalized.endswith('_id') or normalized == 'id' or 'id' in tokens:
        entity = normalized.replace('_id', '').replace('id', '').strip().replace('_', ' ')
        entity = entity if entity else 'record'
        return f"Unique identifier for the {entity}."
    if 'first_name' in normalized or 'last_name' in normalized:
        if 'first_name' in normalized:
            return "Customer's first name."
        return "Customer's last name."
    if 'name' in normalized:
        entity = normalized.replace('name', '').replace('_', ' ').strip()
        if entity:
            return f"Name of the {entity}."
        return "Name of the item."
    if 'created' in normalized or 'signup' in normalized or 'registration' in normalized or 'registered' in normalized:
        return f"Date when the {normalized.replace('_', ' ')} occurred."
    if 'date' in normalized or 'time' in normalized or 'timestamp' in normalized:
        return f"Date or timestamp for the {normalized.replace('_', ' ')}."
    if 'amount' in normalized or 'price' in normalized or 'salary' in normalized or 'total' in normalized or 'value' in normalized:
        return f"Monetary amount for the {normalized.replace('_', ' ')}."
    if 'status' in normalized:
        return f"Current status of the {normalized.replace('_', ' ')}."
    if all(_is_number(v) for v in samples if v):
        sample_text = ' | '.join(samples[:5])
        return f"Numeric values for {normalized.replace('_', ' ')} (examples: {sample_text})."
    if samples:
        sample_text = ' | '.join(samples[:5])
        return f"Example values for {normalized.replace('_', ' ')}: {sample_text}."
    return f"Business description for {normalized.replace('_', ' ')}."


def _build_column_prompt(col_name, samples):
    sample_text = ', '.join(samples[:5]) if samples else 'no sample values available'
    return (
        f"You are a data catalog assistant. Write a concise, business-friendly description for the column '{col_name}'. "
        f"Use plain language and keep it to one or two sentences. "
        f"Example values: {sample_text}."
    )


def _build_table_prompt(table):
    cols = [c.get('name') for c in table.get('columns', [])]
    descs = [c.get('description') for c in table.get('columns', []) if c.get('description')]
    cols_text = ', '.join(cols)
    desc_text = ' | '.join(descs[:5]) if descs else 'no column descriptions yet'
    return (
        f"You are a data catalog assistant. Write a concise 2-3 sentence business summary for the table '{table.get('name')}'. "
        f"The table contains these columns: {cols_text}. "
        f"Column details: {desc_text}."
    )


def _is_number(s):
    try:
        float(s)
        return True
    except Exception:
        return False


def enrich_catalog(catalog, provider='auto', model='gpt-3.5-turbo'):
    """Enriches catalog in-place. If OPENAI_API_KEY is set, will use OpenAI; otherwise falls back to heuristics."""
    use_openai = False
    if provider == 'openai' or (provider == 'auto' and os.getenv('OPENAI_API_KEY')):
        try:
            import openai
            openai.api_key = os.getenv('OPENAI_API_KEY')
            use_openai = True
        except Exception:
            use_openai = False

    for table in catalog.get('tables', []):
        for col in table.get('columns', []):
            if col.get('description'):
                continue
            samples = col.get('sample_values', [])
            if use_openai:
                try:
                    import openai
                    prompt = _build_column_prompt(col['name'], samples)
                    resp = openai.ChatCompletion.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a helpful data catalog assistant."},
                            {"role": "user", "content": prompt},
                        ],
                        max_tokens=120,
                        temperature=0.2,
                        top_p=1.0,
                    )
                    text = resp['choices'][0]['message']['content'].strip()
                    col['description'] = text
                    # gentle pause to avoid rate limits
                    time.sleep(0.2)
                    continue
                except Exception:
                    col['description'] = _generate_fallback_description(col['name'], samples)
            else:
                col['description'] = _generate_fallback_description(col['name'], samples)
        # Generate table-level summary if missing
        if not table.get('summary'):
            if use_openai:
                try:
                    import openai
                    prompt = _build_table_prompt(table)
                    resp = openai.ChatCompletion.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are a helpful data catalog assistant."},
                            {"role": "user", "content": prompt},
                        ],
                        max_tokens=200,
                        temperature=0.2,
                        top_p=1.0,
                    )
                    text = resp['choices'][0]['message']['content'].strip()
                    table['summary'] = text
                    time.sleep(0.2)
                except Exception:
                    table['summary'] = _generate_table_summary(table)
            else:
                table['summary'] = _generate_table_summary(table)
    return catalog


def _generate_table_summary(table):
    # Simple heuristic summary from column names and descriptions
    cols = [c.get('name') for c in table.get('columns', [])][:6]
    descs = [c.get('description') for c in table.get('columns', []) if c.get('description')][:3]
    parts = []
    if cols:
        parts.append('Columns: ' + ', '.join(cols))
    if descs:
        parts.append('Sample column descriptions: ' + ' | '.join(descs))
    if parts:
        return f"{table.get('name')} — " + ' '.join(parts)
    return f"{table.get('name')} table."    

def _build_catalog_question_prompt(catalog, question):
    tables = catalog.get('tables', [])
    table_summaries = []
    for table in tables[:8]:
        cols = ', '.join([c.get('name') for c in table.get('columns', [])])
        table_summaries.append(f"{table.get('name')}: {cols}")
    catalog_text = '\n'.join(table_summaries)
    return (
        "You are a data catalog assistant. Answer the question using the catalog metadata and sample values. "
        "Use plain language and mention the relevant table and column names when applicable."
        f"\n\nCatalog metadata:\n{catalog_text}\n\nQuestion: {question}"
    )


def _call_ollama(prompt, model='gpt-4o-mini', url=None):
    if requests is None:
        raise ImportError('requests is required for Ollama integration')
    endpoint = url or os.getenv('OLLAMA_URL', 'http://127.0.0.1:11434/v1/chat/completions')
    payload = {
        'model': os.getenv('OLLAMA_MODEL', model),
        'messages': [
            {'role': 'system', 'content': 'You are a helpful data catalog assistant.'},
            {'role': 'user', 'content': prompt},
        ],
        'temperature': 0.2,
        'top_p': 1.0,
        'max_tokens': 200,
    }
    resp = requests.post(endpoint, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if 'choices' in data and data['choices']:
        return data['choices'][0]['message']['content'].strip()
    if 'text' in data:
        return data['text'].strip()
    return str(data)


def _answer_question_from_catalog(catalog, question):
    """
    Intelligent question answering engine that queries catalog metadata.
    Can answer questions about:
    - Column names in a table ('what columns exist in orders?')
    - Row counts / table sizes ('how many departments exist?')
    - Table names ('what tables are available?')
    - Column data types
    - Sample / example values
    - Relationships between tables
    - Email columns or other specific columns
    - Any combination of the above
    """
    q = question.lower().strip().rstrip('?')
    tables = catalog.get('tables', [])
    if not tables:
        return 'The catalog is empty — no tables found.'
    
    # Build lookup indices
    name_to_table = {}
    for t in tables:
        name_lower = t.get('name', '').lower()
        name_to_table[name_lower] = t
        # Also index by singular form
        if name_lower.endswith('s') and len(name_lower) > 2:
            name_to_table[name_lower[:-1]] = t
    
    # ── 1. Find which table(s) the question mentions ──────────────────────
    q_words = set(w.strip('.,;:!?\'"') for w in q.split())
    mentioned = []
    for word in q_words:
        if word in name_to_table:
            mentioned.append(name_to_table[word])
    # If no direct match, try substring matching
    if not mentioned:
        for word in sorted(q_words, key=len, reverse=True):
            if len(word) < 3:
                continue
            for name_lower, t in name_to_table.items():
                if word in name_lower or name_lower.startswith(word):
                    mentioned.append(t)
                    break
        if mentioned:
            mentioned = [mentioned[0]]
    
    # ── 2. Detect question intents ─────────────────────────────────────────
    asking_columns = any(w in q for w in ['column', 'columns', 'field', 'fields', 'schema', 'what columns', 'list columns', 'show columns', 'which columns', 'attributes'])
    asking_rows = any(w in q for w in ['row', 'rows', 'records', 'entries', 'size', 'how many', 'number of', 'count of', 'total'])
    asking_tables = any(w in q for w in ['table', 'tables', 'what tables', 'list tables', 'which tables', 'available tables'])
    asking_rels = any(w in q for w in ['relationship', 'relationships', 'relation', 'foreign key', 'references', 'relates', 'lineage', 'join'])
    asking_dtypes = any(w in q for w in ['type', 'types', 'dtype', 'datatype', 'data type', 'data types'])
    asking_sample = any(w in q for w in ['sample', 'example', 'examples', 'values', 'data', 'show me', 'examples of'])
    asking_email = any(w in q for w in ['email', 'emails', 'mail', 'e-mail'])
    asking_describe = any(w in q for w in ['describe', 'summary', 'overview', 'tell me about', 'details'])
    
    # ── 3. Respond intelligently based on intent ─────────────────────────
    
    # 3a. "Which table contains emails?" — must check before generic table listing
    asking_which_table = any(w in q for w in ['which table', 'what table', 'where is', 'which table has', 'which table contains', 'what table contains', 'what table has'])
    if asking_which_table or asking_email:
        for t in tables:
            for c in t.get('columns', []):
                cn_lower = c['name'].lower()
                # Check if question mentions this column content
                q_without_stop = q.replace('which', '').replace('table', '').replace('contains', '').replace('has', '').replace('where', '').replace('is', '').replace('what', '').strip()
                # Extract the key term from the question (e.g. "emails", "customer_id")
                for word in q_words:
                    if len(word) >= 3 and (word in cn_lower or cn_lower in word or cn_lower.startswith(word)):
                        return f"**`{t['name']}.{c['name']}`** is in the **{t['name']}** table."
                if cn_lower in q or cn_lower + 's' in q or cn_lower.replace('_', ' ') in q:
                    return f"**`{t['name']}.{c['name']}`** is in the **{t['name']}** table."
        # If asking about emails specifically but none found with column match
        if asking_email:
            for t in tables:
                for c in t.get('columns', []):
                    if 'email' in c['name'].lower():
                        return f"**Emails are stored in `{t['name']}.{c['name']}`** column."
            return "No email column found in any table."
    
    # 3b. List all tables
    if asking_tables and not mentioned:
        lines = []
        for t in tables:
            cc = len(t.get('columns', []))
            rc = t.get('row_count', '?')
            lines.append(f"  • **{t['name']}** — {cc} columns, {rc} rows")
        return f"This catalog contains **{len(tables)} tables**:\n" + '\n'.join(lines)
    
    # 3c. All relationships
    if asking_rels and not mentioned:
        rels = detect_relationships(tables)
        if not rels:
            return "No relationships (shared columns) were detected between tables."
        lines = [f"  • **{r['parent']}.{r['column']}** → **{r['child']}.{r['column']}**  *(One-to-Many)*" for r in rels]
        return f"**{len(rels)} relationships detected:**\n" + '\n'.join(lines)
    
    # 3d. Questions about a specific table
    if mentioned:
        t = mentioned[0]
        tn = t.get('name', '')
        cols = t.get('columns', [])
        rc = t.get('row_count', '?')
        
        # Columns list
        if asking_columns:
            col_names = [f"  • **{c['name']}** *({c.get('dtype', '?')})*" for c in cols]
            return f"**{tn}** has **{len(cols)} columns**:\n" + '\n'.join(col_names)
        
        # Row count
        if asking_rows:
            return f"**{tn}** has **{rc} rows**."
        
        # Data types
        if asking_dtypes:
            lines = [f"  • **{c['name']}**: {c.get('dtype', '?')}" for c in cols]
            return f"**{tn}** column data types:\n" + '\n'.join(lines)
        
        # Sample / example values
        if asking_sample:
            lines = []
            for c in cols[:5]:  # Limit to 5 columns for readability
                samples = c.get('sample_values', [])
                sample_text = ', '.join(str(s) for s in samples[:3])
                lines.append(f"  • **{c['name']}**: *{sample_text}*")
            return f"**{tn}** sample values (first columns):\n" + '\n'.join(lines)
        
        # Relationships involving this table
        if asking_rels:
            rels = detect_relationships(tables)
            tn_lower = tn.lower()
            related = [r for r in rels if r['parent'].lower() == tn_lower or r['child'].lower() == tn_lower]
            if not related:
                return f"**{tn}** has no detected relationships with other tables."
            lines = [f"  • **{r['parent']}.{r['column']}** → **{r['child']}.{r['column']}**" for r in related]
            return f"**{tn}** relationships:\n" + '\n'.join(lines)
        
        # Email search within table context
        if asking_email:
            for c in t.get('columns', []):
                if 'email' in c['name'].lower():
                    return f"**Emails are stored in `{t['name']}.{c['name']}`** column."
        
        # Describe / summary
        if asking_describe or (not asking_columns and not asking_rows and not asking_dtypes and not asking_sample and not asking_rels):
            col_list = ', '.join(c['name'] for c in cols)
            desc = t.get('summary', '')
            part = f"**{tn}** has **{len(cols)} columns** and **{rc} rows**.\nColumns: {col_list}."
            if desc:
                part += f"\n\n*{desc}*"
            return part
    
    # 3e. "Where is ...?" or "which table has ...?" — fallback if not caught above
    for t in tables:
        tn_lower = t.get('name', '').lower()
        for c in t.get('columns', []):
            cn_lower = c['name'].lower()
            # Check if the question mentions this column name or a related term
            if cn_lower in q_words or cn_lower + 's' in q_words or cn_lower.replace('_', ' ') in q:
                return f"**`{t['name']}.{c['name']}`** is in the **{t['name']}** table."
    
    # 3f. Specific count question like "how many departments exist?"
    if asking_rows or asking_how_many:
        for t in tables:
            tn_lower = t.get('name', '').lower()
            if tn_lower in q or tn_lower in q_words or (tn_lower.endswith('s') and tn_lower[:-1] in q_words):
                return f"**{t['name']}** has **{t.get('row_count', '?')} rows/records**."
    
    # 3g. Try matching column name in question to tables
    for t in tables:
        for c in t.get('columns', []):
            cn_lower = c['name'].lower()
            if cn_lower in q or cn_lower.replace('_', ' ') in q:
                return f"**`{t['name']}.{c['name']}`** is a column in the **{t['name']}** table (type: {c.get('dtype', '?')})."
    
    # ── 4. Fallback — give a helpful summary of everything we know ────────
    parts = []
    parts.append(f"This catalog contains {len(tables)} tables")
    for t in tables:
        cc = len(t.get('columns', []))
        rc = t.get('row_count', '?')
        cols_preview = ', '.join(c['name'] for c in t.get('columns', [])[:3])
        parts.append(f"  • **{t['name']}** ({rc} rows, {cc} cols: {cols_preview}, ...)")
    
    rels = detect_relationships(tables)
    if rels:
        rel_summary = '; '.join(f"{r['parent']}.{r['column']} → {r['child']}.{r['column']}" for r in rels[:3])
        parts.append(f"Relationships: {rel_summary}")
    
    return "I found catalog information:\n" + '\n'.join(parts)


def ask_catalog_question(catalog, question, provider='ollama', model='gpt-4o-mini', url=None):
    if not question:
        return 'Please ask a catalog question.'
    prompt = _build_catalog_question_prompt(catalog, question)
    if provider == 'ollama':
        try:
            return _call_ollama(prompt, model=model, url=url)
        except Exception:
            return _answer_question_from_catalog(catalog, question)
    if provider == 'openai' or (provider == 'auto' and os.getenv('OPENAI_API_KEY')):
        try:
            import openai
            openai.api_key = os.getenv('OPENAI_API_KEY')
            resp = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {'role': 'system', 'content': 'You are a helpful data catalog assistant.'},
                    {'role': 'user', 'content': prompt},
                ],
                max_tokens=200,
                temperature=0.2,
                top_p=1.0,
            )
            return resp['choices'][0]['message']['content'].strip()
        except Exception:
            return _answer_question_from_catalog(catalog, question)
    return _answer_question_from_catalog(catalog, question)