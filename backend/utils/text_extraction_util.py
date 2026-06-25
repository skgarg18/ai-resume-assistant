from io import BytesIO
from pathlib import Path

import fitz
from docx import Document


def extract_text_from_file(
    file_bytes: bytes,
    filename: str,
) -> str:

    extension = Path(filename).suffix.lower()

    # ---------------- PDF ----------------
    if extension == ".pdf":

        doc = fitz.open(
            stream=file_bytes,
            filetype="pdf"
        )

        text = ""

        for page in doc:
            text += page.get_text()

        doc.close()

        return text

    # ---------------- DOCX ----------------
    elif extension == ".docx":

        document = Document(
            BytesIO(file_bytes)
        )

        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

        return text

    # ---------------- Unsupported ----------------
    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )