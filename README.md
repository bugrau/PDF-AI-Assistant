# PDF AI Assistant

## Project Overview

The PDF AI Assistant is a FastAPI-based application that allows users to upload PDF documents, extract text content, and interact with the content using AI-powered chat functionality. The application leverages Google's Gemini API for generating context-aware responses based on the PDF content and user queries.

## Features

- PDF upload and processing with size limit checks
- Text extraction and preprocessing from PDFs
- AI-powered chat functionality using Google's Gemini API
- Comprehensive error handling and structured logging
- Efficient in-memory document storage for quick retrieval
- RESTful API design with clear endpoint documentation

## Technology Stack

- FastAPI: High-performance web framework for building APIs
- Google Generative AI (Gemini): For generating human-like responses
- PyPDF: For robust PDF text extraction
- Pydantic: For data validation and settings management
- pytest: For comprehensive unit and integration testing

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Environment Configuration

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pdf-ai-assistant.git
   cd pdf-ai-assistant
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

### Running the Application

1. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

2. The API will be available at `http://localhost:8000`
3. Access the interactive API documentation at `http://localhost:8000/docs`

## API Endpoints

### 1. Upload PDF
- **POST** `/v1/pdf`
- Upload a PDF file (max 10MB) for processing

### 2. Chat with PDF
- **POST** `/v1/chat/{pdf_id}`
- Interact with the content of a specific PDF

### 3. Get PDF Information
- **GET** `/v1/pdf/{pdf_id}`
- Retrieve metadata about a specific PDF

### 4. List PDFs
- **GET** `/v1/pdfs`
- List all uploaded PDFs

### 5. Delete PDF
- **DELETE** `/v1/pdf/{pdf_id}`
- Remove a specific PDF from storage

## Testing

Run the comprehensive test suite with: