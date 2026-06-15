"""Test the improved AI question answering engine."""
import json
from llm_enrich import _answer_question_from_catalog

c = json.load(open('catalog.json'))

questions = [
    'What columns exist in orders?',
    'How many departments exist?',
    'Which table contains emails?',
    'What relationships exist?',
    'How many rows are in products?',
    'What tables are available?',
    'What columns does customers have?',
    'tell me about orders table',
]

for q in questions:
    print(f'Q: {q}')
    print(f'A: {_answer_question_from_catalog(c, q)}')
    print()