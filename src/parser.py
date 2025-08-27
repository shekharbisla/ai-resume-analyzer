# src/parser.py
from io import BytesIO
import PyPDF2
from docx import Document

def read_pdf(file_bytes: bytes) -> str:
    text_parts = []
    reader = PyPDF2.PdfReader(BytesIO(file_bytes))
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)

def read_docx(file_bytes: bytes) -> str:
    doc = Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)
