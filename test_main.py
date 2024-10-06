import sys
import os
import site
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io
from main import app, PDFDocument
from pdf_processor import extract_text_from_pdf, preprocess_text

client = TestClient(app)

# Unit tests

def test_preprocess_text():
    text = "This is a TEST sentence with NUMBERS 123 and SPECIAL characters !@#."
    processed_text = preprocess_text(text)
    assert processed_text == "this is a test sentence with numbers 123 and special characters !@#."

@patch('pdf_processor.PdfReader')
def test_extract_text_from_pdf(mock_pdf_reader):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "This is a test page."
    mock_pdf_reader.return_value.pages = [mock_page, mock_page]
    
    file_content = b"Mock PDF content"
    text, page_count = extract_text_from_pdf(file_content)
    
    assert text == "This is a test page.This is a test page."
    assert page_count == 2

# Integration tests

@patch('main.extract_text_from_pdf')
def test_upload_pdf(mock_extract_text):
    mock_extract_text.return_value = ("Sample text", 1)
    
    mock_file = io.BytesIO(b"Mock PDF content")
    mock_file.name = "test.pdf"
    
    response = client.post("/v1/pdf", files={"file": ("test.pdf", mock_file, "application/pdf")})
    
    assert response.status_code == 201
    assert "pdf_id" in response.json()

def test_upload_invalid_file():
    mock_file = io.BytesIO(b"Mock text content")
    mock_file.name = "test.txt"
    
    response = client.post("/v1/pdf", files={"file": ("test.txt", mock_file, "text/plain")})
    
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")
    print(f"Response headers: {response.headers}")
    print(f"Response text: {response.text}")
    
    assert response.status_code == 400
    assert response.json()["detail"] == "400: Only PDF files are allowed"

@patch('main.genai.GenerativeModel')
@patch('main.pdf_storage')
def test_chat_with_pdf(mock_pdf_storage, mock_generative_model):
    pdf_id = "test_id"
    mock_pdf = MagicMock()
    mock_pdf.content = "Test content"
    mock_chat = MagicMock()
    mock_chat.send_message.return_value.text = "This is a test response."
    
    mock_pdf_storage.__getitem__.return_value = mock_pdf
    mock_pdf_storage.__contains__.return_value = True
    mock_generative_model.return_value.start_chat.return_value = mock_chat
    
    response = client.post(f"/v1/chat/{pdf_id}", json={"message": "What is this PDF about?"})
    
    assert response.status_code == 200
    assert response.json()["response"] == "This is a test response."
    mock_chat.send_message.assert_called_once()

def test_chat_with_nonexistent_pdf():
    response = client.post("/v1/chat/nonexistent_id", json={"message": "What is this PDF about?"})
    assert response.status_code == 404

# Run the tests
if __name__ == "__main__":
    pytest.main([__file__])