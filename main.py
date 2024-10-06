from fastapi import FastAPI, HTTPException, File, UploadFile, status, Body, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from pdf_processor import extract_text_from_pdf
import numpy as np
from datetime import datetime
import uuid
import re
import os
import logging
import json
from middleware import CustomLoggingMiddleware, validation_exception_handler, http_exception_handler, general_exception_handler
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)

app = FastAPI()

# Add middleware
app.add_middleware(CustomLoggingMiddleware)

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Load API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logging.error(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "level": "ERROR",
        "message": "GEMINI_API_KEY environment variable is not set"
    }))
    raise ValueError("GEMINI_API_KEY environment variable is not set")

genai.configure(api_key=GEMINI_API_KEY)

# Data structure to store PDFs
pdf_storage: Dict[str, 'PDFDocument'] = {}

class PDFDocument(BaseModel):
    id: str = Field(..., description="Unique identifier for the PDF")
    filename: str = Field(..., description="Original filename of the PDF")
    content: str = Field(..., description="Extracted and preprocessed text content")
    size: int = Field(..., description="File size in bytes")
    page_count: int = Field(..., description="Number of pages in the PDF")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of upload")
    last_accessed: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of last access")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )

@app.post("/v1/pdf", status_code=status.HTTP_201_CREATED)
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="400: Only PDF files are allowed")
        
        file_content = await file.read()
        if len(file_content) > 10_000_000:
            raise HTTPException(status_code=400, detail="File size exceeds the 10 MB limit")

        pdf_id = str(uuid.uuid4())
        text, page_count = extract_text_from_pdf(file_content)

        pdf_document = PDFDocument(
            id=pdf_id,
            filename=file.filename,
            content=text,
            size=len(file_content),
            page_count=page_count,
        )

        # Store the PDF document
        pdf_storage[pdf_id] = pdf_document

        logging.info(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": f"PDF uploaded successfully",
            "pdf_id": pdf_id,
            "filename": file.filename,
            "size": len(file_content),
            "page_count": page_count
        }))

        return {"pdf_id": pdf_id}
    except HTTPException as e:
        logging.error(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "message": str(e.detail),
            "status_code": e.status_code
        }))
        raise e
    except Exception as e:
        logging.error(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "message": f"Error uploading PDF: {str(e)}",
            "filename": file.filename if file else "Unknown"
        }))
        raise HTTPException(status_code=500, detail="An error occurred while processing the PDF")

@app.post("/v1/chat/{pdf_id}", response_model=ChatResponse)
async def chat_with_pdf(pdf_id: str, chat_request: ChatRequest):
    try:
        if pdf_id not in pdf_storage:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        pdf_document = pdf_storage[pdf_id]
        pdf_document.last_accessed = datetime.utcnow()

        model = genai.GenerativeModel('gemini-pro')
        chat = model.start_chat(history=[])
        
        prompt = f"""
        Based on the following PDF content, please answer the user's question.
        
        PDF Content:
        {pdf_document.content[:4000]}  # Limiting to 4000 characters for this example
        
        User Question: {chat_request.message}
        
        Please provide a concise and relevant answer based solely on the information given in the PDF content.
        """
        
        response = chat.send_message(prompt)

        logging.info(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "message": "Chat response generated successfully",
            "pdf_id": pdf_id,
            "query": chat_request.message[:50]
        }))

        return ChatResponse(response=response.text)
    except HTTPException as e:
        raise
    except Exception as e:
        logging.error(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "message": f"Error generating chat response: {str(e)}",
            "pdf_id": pdf_id,
            "query": chat_request.message[:50]
        }))
        raise HTTPException(status_code=500, detail="An error occurred while generating the response")

# ... (rest of the endpoints remain the same)