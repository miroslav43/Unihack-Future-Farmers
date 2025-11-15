"""Document service - business logic for document operations"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List
from datetime import datetime
import os
from pathlib import Path

from ..models.document import (
    Document, DocumentCreate, DocumentResponse, 
    DocumentType, DocumentStatus
)
from ..config.settings import settings


class DocumentService:
    """Service for managing document data and files"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.documents
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
    
    async def create_document(
        self, 
        document_data: DocumentCreate
    ) -> DocumentResponse:
        """Create a new document record"""
        document_dict = document_data.model_dump()
        document_dict["status"] = DocumentStatus.UPLOADED
        document_dict["created_at"] = datetime.utcnow()
        document_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(document_dict)
        
        created_doc = await self.collection.find_one({"_id": result.inserted_id})
        created_doc["_id"] = str(created_doc["_id"])
        
        return DocumentResponse(**created_doc)
    
    async def get_document(self, document_id: str) -> Optional[DocumentResponse]:
        """Get document by ID"""
        if not ObjectId.is_valid(document_id):
            return None
        
        doc = await self.collection.find_one({"_id": ObjectId(document_id)})
        if not doc:
            return None
        
        doc["_id"] = str(doc["_id"])
        return DocumentResponse(**doc)
    
    async def list_farmer_documents(
        self, 
        farmer_id: str,
        document_type: Optional[DocumentType] = None,
        status: Optional[DocumentStatus] = None
    ) -> List[DocumentResponse]:
        """List all documents for a farmer"""
        query = {"farmer_id": farmer_id}
        
        if document_type:
            query["document_type"] = document_type
        if status:
            query["status"] = status
        
        cursor = self.collection.find(query).sort("created_at", -1)
        documents = []
        
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            documents.append(DocumentResponse(**doc))
        
        return documents
    
    async def update_document_status(
        self,
        document_id: str,
        status: DocumentStatus,
        extracted_data: Optional[dict] = None,
        ocr_confidence: Optional[float] = None,
        error_message: Optional[str] = None
    ) -> Optional[DocumentResponse]:
        """Update document processing status and data"""
        if not ObjectId.is_valid(document_id):
            return None
        
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if status in [DocumentStatus.PROCESSED, DocumentStatus.VERIFIED]:
            update_data["processed_at"] = datetime.utcnow()
        
        if extracted_data is not None:
            update_data["extracted_data"] = extracted_data
        
        if ocr_confidence is not None:
            update_data["ocr_confidence"] = ocr_confidence
        
        if error_message is not None:
            update_data["processing_error"] = error_message
        
        result = await self.collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return await self.get_document(document_id)
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document record and file"""
        if not ObjectId.is_valid(document_id):
            return False
        
        # Get document to delete file
        doc = await self.get_document(document_id)
        if not doc:
            return False
        
        # Delete file if exists
        if doc.file_path and os.path.exists(doc.file_path):
            try:
                os.remove(doc.file_path)
            except Exception:
                pass  # Continue even if file deletion fails
        
        result = await self.collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0
    
    def get_farmer_upload_dir(self, farmer_id: str) -> Path:
        """Get or create upload directory for farmer"""
        farmer_dir = self.upload_dir / farmer_id
        farmer_dir.mkdir(parents=True, exist_ok=True)
        return farmer_dir
    
    async def get_document_statistics(self, farmer_id: Optional[str] = None) -> dict:
        """Get document statistics"""
        query = {"farmer_id": farmer_id} if farmer_id else {}
        
        total = await self.collection.count_documents(query)
        
        # Status distribution
        pipeline = [
            {"$match": query} if query else {"$match": {}},
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }}
        ]
        
        status_dist = {}
        async for doc in self.collection.aggregate(pipeline):
            status_dist[doc["_id"]] = doc["count"]
        
        # Type distribution
        type_pipeline = [
            {"$match": query} if query else {"$match": {}},
            {"$group": {
                "_id": "$document_type",
                "count": {"$sum": 1}
            }}
        ]
        
        type_dist = {}
        async for doc in self.collection.aggregate(type_pipeline):
            type_dist[doc["_id"]] = doc["count"]
        
        return {
            "total_documents": total,
            "status_distribution": status_dist,
            "type_distribution": type_dist
        }
