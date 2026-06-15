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
    q = question.lower()
    if 'customer email' in q or 'customer emails' in q:
        for t in catalog.get('tables', []):
            if t.get('name', '').lower() == 'customers':
                return 'Customer emails are stored in customers.email.'
    if 'relationship' in q or 'relationships' in q:
        rels = detect_relationships(catalog.get('tables', []))
        if rels:
            matches = [r for r in rels if 'order' in r['parent'].lower() or 'order' in r['child'].lower()]
            if matches:
                lines = [f"{r['parent']}.{r['column']} → {r['child']}.{r['column']}" for r in matches]
                return 'Orders relationships:\n' + '\n'.join(lines)
        return 'No detected order relationships were found in the catalog.'
    table_names = ', '.join([t.get('name', '') for t in catalog.get('tables', [])])
    return f'I could not answer directly, but this catalog contains: {table_names}.'


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