"""Assessment service - business logic for scoring and assessment"""
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List
from datetime import datetime
import math

from ..models.assessment import (
    Assessment, AssessmentCreate, AssessmentResponse,
    BonitateScore, FarmerScore, RiskAssessment
)
from ..models.farmer import FarmerResponse
from .farmer_service import FarmerService


class AssessmentService:
    """Service for farmer assessment and scoring"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.assessments
        self.farmer_service = FarmerService(db)
    
    async def create_assessment(
        self, 
        assessment_data: AssessmentCreate
    ) -> AssessmentResponse:
        """Create and calculate assessment for a farmer"""
        # Get farmer data
        farmer = await self.farmer_service.get_farmer(assessment_data.farmer_id)
        if not farmer:
            raise ValueError(f"Farmer not found: {assessment_data.farmer_id}")
        
        # Calculate scores
        bonitate_score = await self._calculate_bonitate_score(farmer)
        farmer_score = await self._calculate_farmer_score(farmer)
        risk_assessment = await self._calculate_risk_assessment(farmer, bonitate_score, farmer_score)
        
        # Calculate overall rating and eligibility
        eligibility_score = self._calculate_eligibility_score(bonitate_score, farmer_score)
        overall_rating = self._get_overall_rating(eligibility_score)
        recommendations = self._generate_recommendations(farmer, bonitate_score, farmer_score, risk_assessment)
        
        # Create assessment document
        assessment_dict = {
            "farmer_id": assessment_data.farmer_id,
            "bonitate_score": bonitate_score.model_dump(),
            "farmer_score": farmer_score.model_dump(),
            "risk_assessment": risk_assessment.model_dump(),
            "overall_rating": overall_rating,
            "eligibility_score": eligibility_score,
            "recommendations": recommendations,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.collection.insert_one(assessment_dict)
        
        created_assessment = await self.collection.find_one({"_id": result.inserted_id})
        created_assessment["_id"] = str(created_assessment["_id"])
        
        return AssessmentResponse(**created_assessment)
    
    async def get_assessment(self, assessment_id: str) -> Optional[AssessmentResponse]:
        """Get assessment by ID"""
        if not ObjectId.is_valid(assessment_id):
            return None
        
        assessment = await self.collection.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            return None
        
        assessment["_id"] = str(assessment["_id"])
        return AssessmentResponse(**assessment)
    
    async def get_farmer_latest_assessment(self, farmer_id: str) -> Optional[AssessmentResponse]:
        """Get most recent assessment for a farmer"""
        assessment = await self.collection.find_one(
            {"farmer_id": farmer_id},
            sort=[("created_at", -1)]
        )
        
        if not assessment:
            return None
        
        assessment["_id"] = str(assessment["_id"])
        return AssessmentResponse(**assessment)
    
    async def list_farmer_assessments(self, farmer_id: str) -> List[AssessmentResponse]:
        """List all assessments for a farmer"""
        cursor = self.collection.find({"farmer_id": farmer_id}).sort("created_at", -1)
        assessments = []
        
        async for assessment in cursor:
            assessment["_id"] = str(assessment["_id"])
            assessments.append(AssessmentResponse(**assessment))
        
        return assessments
    
    async def _calculate_bonitate_score(self, farmer: FarmerResponse) -> BonitateScore:
        """Calculate land quality (bonitate) score"""
        # Soil quality based on land area and location
        soil_quality = min(100, int(farmer.total_land_area * 2 + 50))
        
        # Irrigation access
        irrigation_access = 90 if farmer.has_irrigation else 40
        
        # Location score - urban proximity
        location_score = 75  # Base score, could be enhanced with geolocation data
        
        # Infrastructure score
        infrastructure_score = 0
        if farmer.has_equipment:
            infrastructure_score += 35
        if farmer.has_storage:
            infrastructure_score += 35
        if farmer.has_irrigation:
            infrastructure_score += 30
        
        # Overall bonitate score
        overall_score = int(
            soil_quality * 0.3 +
            irrigation_access * 0.3 +
            location_score * 0.2 +
            infrastructure_score * 0.2
        )
        
        return BonitateScore(
            soil_quality=soil_quality,
            irrigation_access=irrigation_access,
            location_score=location_score,
            infrastructure_score=infrastructure_score,
            overall_score=overall_score
        )
    
    async def _calculate_farmer_score(self, farmer: FarmerResponse) -> FarmerScore:
        """Calculate farmer capability score"""
        # Experience score
        experience_score = min(100, int(farmer.experience_years * 3))
        
        # Education/training score based on experience level
        education_mapping = {
            "beginner": 30,
            "intermediate": 60,
            "advanced": 85,
            "expert": 95
        }
        education_score = education_mapping.get(farmer.experience_level, 30)
        
        # Equipment score
        equipment_score = 80 if farmer.has_equipment else 30
        
        # Financial capability score (based on land area and resources)
        financial_score = min(100, int(
            farmer.total_land_area * 3 +
            (20 if farmer.has_equipment else 0) +
            (20 if farmer.has_storage else 0)
        ))
        
        # Overall farmer score
        overall_score = int(
            experience_score * 0.3 +
            education_score * 0.25 +
            equipment_score * 0.25 +
            financial_score * 0.2
        )
        
        return FarmerScore(
            experience_score=experience_score,
            education_score=education_score,
            equipment_score=equipment_score,
            financial_score=financial_score,
            overall_score=overall_score
        )
    
    async def _calculate_risk_assessment(
        self,
        farmer: FarmerResponse,
        bonitate: BonitateScore,
        farmer_score: FarmerScore
    ) -> RiskAssessment:
        """Calculate risk assessment"""
        risk_factors = []
        mitigation_suggestions = []
        
        # Analyze risk factors
        if farmer.experience_years < 5:
            risk_factors.append("Limited farming experience")
            mitigation_suggestions.append("Consider mentorship or training programs")
        
        if not farmer.has_irrigation:
            risk_factors.append("No irrigation system")
            mitigation_suggestions.append("Invest in irrigation infrastructure")
        
        if not farmer.has_equipment:
            risk_factors.append("Insufficient equipment")
            mitigation_suggestions.append("Consider equipment leasing or purchase")
        
        if farmer.total_land_area < 5:
            risk_factors.append("Small land area")
            mitigation_suggestions.append("Consider land consolidation or cooperative farming")
        
        # Determine risk level
        avg_score = (bonitate.overall_score + farmer_score.overall_score) / 2
        if avg_score >= 75:
            risk_level = "low"
        elif avg_score >= 50:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        # Calculate confidence based on available data
        confidence = 0.85  # Base confidence
        
        return RiskAssessment(
            risk_level=risk_level,
            risk_factors=risk_factors,
            mitigation_suggestions=mitigation_suggestions,
            confidence_score=confidence
        )
    
    def _calculate_eligibility_score(
        self,
        bonitate: BonitateScore,
        farmer_score: FarmerScore
    ) -> int:
        """Calculate overall eligibility score"""
        return int((bonitate.overall_score + farmer_score.overall_score) / 2)
    
    def _get_overall_rating(self, eligibility_score: int) -> str:
        """Get overall rating category"""
        if eligibility_score >= 85:
            return "excellent"
        elif eligibility_score >= 70:
            return "good"
        elif eligibility_score >= 50:
            return "average"
        else:
            return "poor"
    
    def _generate_recommendations(
        self,
        farmer: FarmerResponse,
        bonitate: BonitateScore,
        farmer_score: FarmerScore,
        risk: RiskAssessment
    ) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        eligibility_score = self._calculate_eligibility_score(bonitate, farmer_score)
        
        # Funding eligibility
        if eligibility_score >= 70:
            recommendations.append("Eligible for agricultural subsidies and development funds")
        
        if eligibility_score >= 80 and farmer.age < 40:
            recommendations.append("Eligible for young farmer programs")
        
        # Infrastructure improvements
        if not farmer.has_irrigation and bonitate.soil_quality > 70:
            recommendations.append("High priority: Install irrigation system to maximize land potential")
        
        if not farmer.has_storage:
            recommendations.append("Consider building storage facilities to reduce post-harvest losses")
        
        # Business development
        if farmer.total_land_area > 10 and farmer_score.experience_score > 70:
            recommendations.append("Consider diversifying crops or expanding production")
        
        # Risk mitigation
        if risk.risk_level in ["medium", "high"]:
            recommendations.append("Recommended: Agricultural insurance to mitigate risks")
        
        return recommendations
