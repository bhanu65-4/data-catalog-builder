import subprocess
import sys

for mod in ['fitz', 'pdfminer', 'pdfminer.high_level', 'docx']:
    try:
        __import__(mod)
        print(f'{mod} is available')
    except ImportError:
        print(f'{mod} is NOT available')