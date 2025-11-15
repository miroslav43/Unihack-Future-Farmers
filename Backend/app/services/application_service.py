"""Application service - business logic for CHM generation"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import uuid

from ..models.application import (
    Application, ApplicationCreate, ApplicationResponse,
    ApplicationType, ApplicationStatus
)
from .farmer_service import FarmerService
from .assessment_service import AssessmentService
from ..config.settings import settings


class ApplicationService:
    """Service for managing applications and CHM generation"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.applications
        self.farmer_service = FarmerService(db)
        self.assessment_service = AssessmentService(db)
        self.output_dir = Path("applications")
        self.output_dir.mkdir(exist_ok=True)
    
    async def create_application(
        self, 
        application_data: ApplicationCreate
    ) -> ApplicationResponse:
        """Create a new application/CHM"""
        # Validate farmer exists
        farmer = await self.farmer_service.get_farmer(application_data.farmer_id)
        if not farmer:
            raise ValueError(f"Farmer not found: {application_data.farmer_id}")
        
        # Validate assessment exists
        assessment = await self.assessment_service.get_assessment(application_data.assessment_id)
        if not assessment:
            raise ValueError(f"Assessment not found: {application_data.assessment_id}")
        
        # Check eligibility
        eligibility_check = self._check_eligibility(farmer, assessment, application_data)
        
        # Generate application number
        application_number = self._generate_application_number(application_data.application_type)
        
        # Create application document
        application_dict = application_data.model_dump()
        application_dict["status"] = ApplicationStatus.DRAFT
        application_dict["application_number"] = application_number
        application_dict["eligibility_check"] = eligibility_check
        application_dict["supporting_docs"] = []
        application_dict["created_at"] = datetime.utcnow()
        application_dict["updated_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(application_dict)
        
        created_app = await self.collection.find_one({"_id": result.inserted_id})
        created_app["_id"] = str(created_app["_id"])
        
        return ApplicationResponse(**created_app)
    
    async def get_application(self, application_id: str) -> Optional[ApplicationResponse]:
        """Get application by ID"""
        if not ObjectId.is_valid(application_id):
            return None
        
        app = await self.collection.find_one({"_id": ObjectId(application_id)})
        if not app:
            return None
        
        app["_id"] = str(app["_id"])
        return ApplicationResponse(**app)
    
    async def list_farmer_applications(
        self, 
        farmer_id: str,
        status: Optional[ApplicationStatus] = None
    ) -> List[ApplicationResponse]:
        """List all applications for a farmer"""
        query = {"farmer_id": farmer_id}
        if status:
            query["status"] = status
        
        cursor = self.collection.find(query).sort("created_at", -1)
        applications = []
        
        async for app in cursor:
            app["_id"] = str(app["_id"])
            applications.append(ApplicationResponse(**app))
        
        return applications
    
    async def generate_chm_document(self, application_id: str) -> Optional[ApplicationResponse]:
        """Generate CHM document for application"""
        app = await self.get_application(application_id)
        if not app:
            return None
        
        # Get farmer and assessment data
        farmer = await self.farmer_service.get_farmer(app.farmer_id)
        assessment = await self.assessment_service.get_assessment(app.assessment_id)
        
        if not farmer or not assessment:
            return None
        
        # Generate CHM file (placeholder - will be implemented with AI module)
        chm_filename = f"{app.application_number}.pdf"
        chm_path = self.output_dir / chm_filename
        
        # Update application status
        update_data = {
            "status": ApplicationStatus.GENERATED,
            "chm_file_path": str(chm_path),
            "generated_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.collection.update_one(
            {"_id": ObjectId(application_id)},
            {"$set": update_data}
        )
        
        return await self.get_application(application_id)
    
    async def submit_application(self, application_id: str) -> Optional[ApplicationResponse]:
        """Submit application"""
        app = await self.get_application(application_id)
        if not app:
            return None
        
        if app.status != ApplicationStatus.GENERATED:
            raise ValueError("Application must be generated before submission")
        
        update_data = {
            "status": ApplicationStatus.SUBMITTED,
            "submitted_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.collection.update_one(
            {"_id": ObjectId(application_id)},
            {"$set": update_data}
        )
        
        return await self.get_application(application_id)
    
    async def update_application_status(
        self,
        application_id: str,
        status: ApplicationStatus
    ) -> Optional[ApplicationResponse]:
        """Update application status"""
        if not ObjectId.is_valid(application_id):
            return None
        
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        result = await self.collection.update_one(
            {"_id": ObjectId(application_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return None
        
        return await self.get_application(application_id)
    
    def _check_eligibility(self, farmer, assessment, application_data) -> dict:
        """Check application eligibility"""
        eligible = True
        criteria_met = []
        criteria_failed = []
        
        # Basic eligibility criteria
        if assessment.eligibility_score >= 50:
            criteria_met.append("minimum_score")
        else:
            eligible = False
            criteria_failed.append("minimum_score")
        
        # Age criteria for young farmer programs
        if application_data.application_type == ApplicationType.YOUNG_FARMER:
            if farmer.age <= 40:
                criteria_met.append("age_requirement")
            else:
                eligible = False
                criteria_failed.append("age_requirement")
        
        # Experience criteria
        if farmer.experience_years >= 2:
            criteria_met.append("experience")
        else:
            criteria_failed.append("experience")
        
        # Land ownership
        if farmer.total_parcels > 0:
            criteria_met.append("land_ownership")
        else:
            eligible = False
            criteria_failed.append("land_ownership")
        
        return {
            "eligible": eligible,
            "score": assessment.eligibility_score,
            "criteria_met": criteria_met,
            "criteria_failed": criteria_failed
        }
    
    def _generate_application_number(self, app_type: ApplicationType) -> str:
        """Generate unique application number"""
        prefix_map = {
            ApplicationType.SUBSIDIES: "SUB",
            ApplicationType.DEVELOPMENT_FUNDS: "DEV",
            ApplicationType.YOUNG_FARMER: "YNG",
            ApplicationType.ECOLOGICAL: "ECO",
            ApplicationType.EQUIPMENT: "EQP",
            ApplicationType.OTHER: "OTH"
        }
        
        prefix = prefix_map.get(app_type, "CHM")
        year = datetime.utcnow().year
        unique_id = str(uuid.uuid4())[:8].upper()
        
        return f"{prefix}-{year}-{unique_id}"
    
    async def get_application_statistics(self, farmer_id: Optional[str] = None) -> dict:
        """Get application statistics"""
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
                "_id": "$application_type",
                "count": {"$sum": 1},
                "total_amount": {"$sum": "$requested_amount"}
            }}
        ]
        
        type_dist = {}
        async for doc in self.collection.aggregate(type_pipeline):
            type_dist[doc["_id"]] = {
                "count": doc["count"],
                "total_amount": doc["total_amount"]
            }
        
        return {
            "total_applications": total,
            "status_distribution": status_dist,
            "type_distribution": type_dist
        }
