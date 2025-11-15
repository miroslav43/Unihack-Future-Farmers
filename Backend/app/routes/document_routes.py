"""Document API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from typing import List, Optional
import os
from pathlib import Path
import uuid

from ..models.document import (
    DocumentCreate, DocumentResponse, DocumentType, DocumentStatus
)
from ..services.document_service import DocumentService
from ..config.database import get_db
from ..config.settings import settings
from motor.motor_asyncio import AsyncIOMotorDatabase


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    farmer_id: str = Form(...),
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Upload a document for a farmer"""
    service = DocumentService(db)
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
        )
    
    # Create farmer directory
    farmer_dir = service.get_farmer_upload_dir(farmer_id)
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = farmer_dir / unique_filename
    
    # Save file
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Create document record
    document_data = DocumentCreate(
        farmer_id=farmer_id,
        document_type=document_type,
        filename=file.filename,
        file_path=str(file_path),
        file_size=file_size,
        mime_type=file.content_type or "application/octet-stream"
    )
    
    try:
        return await service.create_document(document_data)
    except Exception as e:
        # Clean up file if document creation fails
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create document record: {str(e)}"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get document by ID"""
    service = DocumentService(db)
    document = await service.get_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    return document


@router.get("/farmer/{farmer_id}", response_model=List[DocumentResponse])
async def list_farmer_documents(
    farmer_id: str,
    document_type: Optional[DocumentType] = None,
    status: Optional[DocumentStatus] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """List all documents for a farmer"""
    service = DocumentService(db)
    return await service.list_farmer_documents(
        farmer_id=farmer_id,
        document_type=document_type,
        status=status
    )


@router.patch("/{document_id}/status", response_model=DocumentResponse)
async def update_document_status(
    document_id: str,
    status: DocumentStatus,
    extracted_data: Optional[dict] = None,
    ocr_confidence: Optional[float] = None,
    error_message: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update document processing status"""
    service = DocumentService(db)
    updated_doc = await service.update_document_status(
        document_id=document_id,
        status=status,
        extracted_data=extracted_data,
        ocr_confidence=ocr_confidence,
        error_message=error_message
    )
    if not updated_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    return updated_doc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Delete document"""
    service = DocumentService(db)
    deleted = await service.delete_document(document_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )


@router.get("/statistics/overview")
async def get_document_statistics(
    farmer_id: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Get document statistics"""
    service = DocumentService(db)
    return await service.get_document_statistics(farmer_id=farmer_id)
