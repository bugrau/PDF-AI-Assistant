from pypdf import PdfReader
import io

def extract_text_from_pdf(file_content: bytes) -> tuple[str, int]:
    try:
        pdf_reader = PdfReader(io.BytesIO(file_content))
        text = ""
        page_count = len(pdf_reader.pages)
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text, page_count
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {str(e)}")

def preprocess_text(text: str) -> str:
    # Add any text preprocessing steps here
    # For example, removing extra whitespace, lowercasing, etc.
    return text.strip().lower()