# AI Usage Note

## What AI helped with
- `llm_enrich.py` uses AI-assisted enrichment to generate business-friendly descriptions for catalog columns and tables.
- The app supports a natural-language catalog query feature through an LLM-style Ollama/OpenAI integration path.
- AI was used to improve sample metadata, explain table relationships, and enhance search query handling.

## What AI got wrong
- Some column descriptions are based on heuristic inference and may be inaccurate for ambiguous or non-standard column names.
- The current AI enrichment path falls back to local heuristics when external LLM access is unavailable.
- The project does not automatically validate PII or sensitive content in uploaded datasets.

## Best prompts used
- "Write a concise, business-friendly description for the column 'customer_id'. Example values: 1, 2, 3."
- "Describe the business meaning of the column 'order_status' in one or two sentences."
- "Which table contains customer emails?"
- "Show relationships involving orders."

## How AI was integrated
- `llm_enrich.py` can call OpenAI if `OPENAI_API_KEY` is set.
- If OpenAI is unavailable, the project falls back to a heuristic description generator.
- Streamlit UI uses `ask_catalog_question()` to provide catalog answers and LLM-driven responses.

## Reproduce
1. Generate catalog: `python cataloger.py --csv-folder data --out catalog.json`
2. Run the app: `streamlit run streamlit_app.py -- --catalog catalog.json`
3. In the Streamlit app, use the AI question box to ask catalog-aware queries like "Which table contains customer emails?".
