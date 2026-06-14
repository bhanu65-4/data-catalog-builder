# Prompt Templates

Use these prompts when calling an LLM to enrich the data catalog.

1) Column description (concise, business-friendly)

```
Write a concise (1-2 sentence) business-friendly description for the column named "{column_name}" in the table "{table_name}". Example values: {samples}.
Include likely semantics and any caveats.
```

2) Structured JSON output (for programmatic enrichment)

```
Return a JSON object with keys: name, description, data_type, example_values. Example values: {samples}.
```

3) Validation of generated description

```
Is the following description accurate and safe to display to non-technical users? Answer yes/no and explain briefly: "{description}".
```

Save the best prompts you used in `ai_usage_note.md`.
