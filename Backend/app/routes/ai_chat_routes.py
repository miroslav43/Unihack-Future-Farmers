"""AI Chat routes using OpenRouter"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..config.database import get_db
from ..services.ai_agent_service import AIAgentService


router = APIRouter(prefix="/ai-chat", tags=["ai-chat"])


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # user, assistant, system
    content: str


class ChatRequest(BaseModel):
    """Chat request with conversation history"""
    farmer_id: str
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    """Chat response"""
    answer: str
    data: Optional[Any] = None
    function_called: Optional[str] = None
    success: bool
    error: Optional[str] = None


@router.post("/query", response_model=ChatResponse)
async def process_chat_query(
    request: ChatRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Process natural language query using AI (OpenRouter - Gemini 2.5 Flash)
    
    Exemple de întrebări:
    - "Ce comenzi am astăzi?"
    - "Câte comenzi am făcut în ultima lună și cât am câștigat?"
    - "Ce task-uri am de făcut?"
    - "Spune-mi despre inventarul meu"
    - "Când trebuie să recoltez?"
    - "Ce culturi am plantate?"
    """
    ai_service = AIAgentService(db)
    
    result = await ai_service.process_query(
        farmer_id=request.farmer_id,
        query=request.message,
        conversation_history=request.conversation_history
    )
    
    return ChatResponse(**result)


@router.get("/test")
async def test_ai_connection():
    """Test OpenRouter connection"""
    return {
        "status": "ok",
        "message": "AI Chat API is ready",
        "model": AIAgentService.MODEL,
        "features": [
            "Natural language understanding",
            "Function calling pentru date reale",
            "Context awareness",
            "Răspunsuri în română"
        ]
    }
