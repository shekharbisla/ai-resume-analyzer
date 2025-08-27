from typing import Tuple
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
    document = Document(BytesIO(file_bytes))
    return "\n".join(p.text for p in document.paragraphs)

def extract_text(file_name: str, file_bytes: bytes) -> Tuple[str, str]:
    name = file_name.lower()
    if name.endswith(".pdf"):
        return read_pdf(file_bytes), "pdf"
    if name.endswith(".docx"):
        return read_docx(file_bytes), "docx"
    if name.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore"), "txt"
    raise ValueError("Unsupported file type. Upload PDF, DOCX, or TXT.")
