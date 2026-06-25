import tempfile
import shutil
from pathlib import Path
from docx2pdf import convert


def convert_docx_to_pdf(
    file_bytes: bytes,
    filename: str,
) -> bytes:

    temp_dir = tempfile.mkdtemp()

    try:

        docx_path = Path(temp_dir) / filename

        with open(docx_path, "wb") as f:
            f.write(file_bytes)

        pdf_path = docx_path.with_suffix(".pdf")

        convert(str(docx_path), str(pdf_path))

        with open(pdf_path, "rb") as f:
            return f.read()

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)