"""Conversational API routes for AI agents"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..config.database import get_db
from ..services.order_service import OrderService
from ..services.farmer_service import FarmerService
from ..services.crop_service import CropService
from ..services.task_service import TaskService


router = APIRouter(prefix="/conversational", tags=["conversational"])


class QueryRequest(BaseModel):
    """Natural language query request"""
    farmer_id: str
    query: str
    context: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Query response with structured data"""
    answer: str
    data: Optional[Dict[str, Any]] = None
    intent: str
    confidence: float


@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Process natural language queries
    
    Examples:
    - "ce comenzi am astazi?"
    - "cate comenzi am facut in ultima luna?"
    - "care sunt comenzile mele?"
    - "cat am vandut saptamana asta?"
    """
    query_lower = request.query.lower()
    
    # Intent detection (simple keyword matching - poate fi înlocuit cu AI)
    if any(word in query_lower for word in ['comenzi', 'orders', 'vanzari']):
        return await _handle_order_query(request, db)
    
    elif any(word in query_lower for word in ['inventar', 'stoc', 'inventory']):
        return await _handle_inventory_query(request, db)
    
    elif any(word in query_lower for word in ['venit', 'revenue', 'bani', 'vandut']):
        return await _handle_revenue_query(request, db)
    
    elif any(word in query_lower for word in ['culturi', 'crops', 'recolt', 'plantat']):
        return await _handle_crop_query(request, db)
    
    elif any(word in query_lower for word in ['task', 'treaba', 'de facut', 'lucru', 'trebuie', 'fac astazi', 'sarcinile']):
        return await _handle_task_query(request, db)
    
    else:
        return QueryResponse(
            answer="Nu am înțeles întrebarea. Încearcă să întrebi despre comenzi, inventar, venituri, culturi sau task-uri.",
            data=None,
            intent="unknown",
            confidence=0.0
        )


async def _handle_order_query(request: QueryRequest, db: AsyncIOMotorDatabase) -> QueryResponse:
    """Handle queries about orders"""
    query_lower = request.query.lower()
    order_service = OrderService(db)
    
    # Today's orders
    if 'astazi' in query_lower or 'today' in query_lower:
        orders = await order_service.get_today_orders(request.farmer_id)
        count = len(orders)
        
        return QueryResponse(
            answer=f"Ai {count} {'comandă' if count == 1 else 'comenzi'} astăzi.",
            data={
                "count": count,
                "orders": [
                    {
                        "order_number": o.order_number,
                        "customer": o.customer_name,
                        "amount": o.total_amount,
                        "status": o.status
                    }
                    for o in orders
                ]
            },
            intent="orders_today",
            confidence=0.95
        )
    
    # This week
    elif 'saptamana' in query_lower or 'week' in query_lower:
        start_date = datetime.utcnow() - timedelta(days=7)
        count = await order_service.get_orders_count(
            farmer_id=request.farmer_id,
            start_date=start_date
        )
        
        return QueryResponse(
            answer=f"Ai avut {count} {'comandă' if count == 1 else 'comenzi'} în ultima săptămână.",
            data={"count": count, "period": "last_week"},
            intent="orders_week",
            confidence=0.9
        )
    
    # Last month
    elif 'luna' in query_lower or 'month' in query_lower:
        start_date = datetime.utcnow() - timedelta(days=30)
        count = await order_service.get_orders_count(
            farmer_id=request.farmer_id,
            start_date=start_date
        )
        stats = await order_service.get_orders_statistics(
            farmer_id=request.farmer_id,
            start_date=start_date
        )
        
        return QueryResponse(
            answer=f"În ultima lună ai avut {count} {'comandă' if count == 1 else 'comenzi'}, "
                   f"cu venituri totale de {stats['total_revenue']:.2f} RON.",
            data={
                "count": count,
                "period": "last_month",
                "revenue": stats['total_revenue'],
                "avg_order": stats['avg_order_value']
            },
            intent="orders_month",
            confidence=0.9
        )
    
    # All orders
    else:
        orders = await order_service.list_farmer_orders(
            farmer_id=request.farmer_id,
            limit=10
        )
        count = len(orders)
        
        return QueryResponse(
            answer=f"Ai {count} {'comandă recentă' if count == 1 else 'comenzi recente'}.",
            data={
                "count": count,
                "orders": [
                    {
                        "order_number": o.order_number,
                        "customer": o.customer_name,
                        "amount": o.total_amount,
                        "date": o.created_at.isoformat()
                    }
                    for o in orders[:5]  # Top 5
                ]
            },
            intent="orders_recent",
            confidence=0.85
        )


async def _handle_inventory_query(request: QueryRequest, db: AsyncIOMotorDatabase) -> QueryResponse:
    """Handle queries about inventory"""
    # TODO: Implement inventory queries
    return QueryResponse(
        answer="Funcționalitatea de inventar va fi disponibilă în curând.",
        data=None,
        intent="inventory",
        confidence=0.7
    )


async def _handle_revenue_query(request: QueryRequest, db: AsyncIOMotorDatabase) -> QueryResponse:
    """Handle queries about revenue"""
    query_lower = request.query.lower()
    order_service = OrderService(db)
    
    # Determine time period
    if 'astazi' in query_lower:
        start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        period_name = "astăzi"
    elif 'saptamana' in query_lower or 'week' in query_lower:
        start_date = datetime.utcnow() - timedelta(days=7)
        period_name = "în ultima săptămână"
    elif 'luna' in query_lower or 'month' in query_lower:
        start_date = datetime.utcnow() - timedelta(days=30)
        period_name = "în ultima lună"
    else:
        start_date = None
        period_name = "total"
    
    stats = await order_service.get_orders_statistics(
        farmer_id=request.farmer_id,
        start_date=start_date
    )
    
    return QueryResponse(
        answer=f"Ai vândut {stats['total_revenue']:.2f} RON {period_name}, "
               f"din {stats['total_orders']} {'comandă' if stats['total_orders'] == 1 else 'comenzi'}.",
        data={
            "revenue": stats['total_revenue'],
            "orders": stats['total_orders'],
            "avg_order": stats['avg_order_value'],
            "period": period_name
        },
        intent="revenue",
        confidence=0.9
    )


async def _handle_crop_query(request: QueryRequest, db: AsyncIOMotorDatabase) -> QueryResponse:
    """Handle queries about crops"""
    query_lower = request.query.lower()
    crop_service = CropService(db)
    
    # Ready for harvest
    if 'gata' in query_lower or 'ready' in query_lower or 'recolt' in query_lower:
        crops = await crop_service.get_harvest_ready(request.farmer_id)
        count = len(crops)
        
        if count == 0:
            return QueryResponse(
                answer="Nu ai culturi gata de recoltat în acest moment.",
                data={"count": 0, "crops": []},
                intent="crops_harvest_ready",
                confidence=0.95
            )
        
        return QueryResponse(
            answer=f"Ai {count} {'cultură' if count == 1 else 'culturi'} gata de recoltat.",
            data={
                "count": count,
                "crops": [
                    {
                        "crop_name": c.crop_name,
                        "area": c.area_hectares,
                        "days_overdue": abs(c.days_until_harvest) if c.days_until_harvest and c.days_until_harvest < 0 else 0
                    }
                    for c in crops
                ]
            },
            intent="crops_harvest_ready",
            confidence=0.95
        )
    
    # Active crops
    elif 'active' in query_lower or 'plantat' in query_lower or 'cresc' in query_lower:
        crops = await crop_service.get_active_crops(request.farmer_id)
        count = len(crops)
        
        return QueryResponse(
            answer=f"Ai {count} {'cultură activă' if count == 1 else 'culturi active'}.",
            data={
                "count": count,
                "crops": [
                    {
                        "crop_name": c.crop_name,
                        "area": c.area_hectares,
                        "status": c.status,
                        "days_until_harvest": c.days_until_harvest
                    }
                    for c in crops[:5]
                ]
            },
            intent="crops_active",
            confidence=0.9
        )
    
    # All crops
    else:
        crops = await crop_service.list_farmer_crops(request.farmer_id)
        count = len(crops)
        
        return QueryResponse(
            answer=f"Ai un total de {count} {'cultură' if count == 1 else 'culturi'} înregistrată.",
            data={
                "count": count,
                "crops": [
                    {
                        "crop_name": c.crop_name,
                        "area": c.area_hectares,
                        "status": c.status
                    }
                    for c in crops[:5]
                ]
            },
            intent="crops_all",
            confidence=0.85
        )


async def _handle_task_query(request: QueryRequest, db: AsyncIOMotorDatabase) -> QueryResponse:
    """Handle queries about tasks"""
    query_lower = request.query.lower()
    task_service = TaskService(db)
    
    # Today's tasks
    if 'astazi' in query_lower or 'azi' in query_lower or 'today' in query_lower:
        tasks = await task_service.get_today_tasks(request.farmer_id)
        count = len(tasks)
        
        if count == 0:
            return QueryResponse(
                answer="Nu ai task-uri programate pentru astăzi.",
                data={"count": 0, "tasks": []},
                intent="tasks_today",
                confidence=0.95
            )
        
        return QueryResponse(
            answer=f"Ai {count} {'task' if count == 1 else 'task-uri'} de făcut astăzi.",
            data={
                "count": count,
                "tasks": [
                    {
                        "title": t.title,
                        "priority": t.priority,
                        "status": t.status
                    }
                    for t in tasks
                ]
            },
            intent="tasks_today",
            confidence=0.95
        )
    
    # Overdue tasks
    elif 'intarziat' in query_lower or 'overdue' in query_lower or 'trecut' in query_lower:
        tasks = await task_service.get_overdue_tasks(request.farmer_id)
        count = len(tasks)
        
        if count == 0:
            return QueryResponse(
                answer="Nu ai task-uri întârziate. Bravo!",
                data={"count": 0, "tasks": []},
                intent="tasks_overdue",
                confidence=0.95
            )
        
        return QueryResponse(
            answer=f"Ai {count} {'task întârziat' if count == 1 else 'task-uri întârziate'}.",
            data={
                "count": count,
                "tasks": [
                    {
                        "title": t.title,
                        "due_date": t.due_date.isoformat() if t.due_date else None,
                        "priority": t.priority
                    }
                    for t in tasks
                ]
            },
            intent="tasks_overdue",
            confidence=0.95
        )
    
    # Pending tasks
    else:
        tasks = await task_service.get_pending_tasks(request.farmer_id)
        count = len(tasks)
        
        return QueryResponse(
            answer=f"Ai {count} {'task în așteptare' if count == 1 else 'task-uri în așteptare'}.",
            data={
                "count": count,
                "tasks": [
                    {
                        "title": t.title,
                        "priority": t.priority,
                        "due_date": t.due_date.isoformat() if t.due_date else None,
                        "status": t.status
                    }
                    for t in tasks[:10]
                ]
            },
            intent="tasks_pending",
            confidence=0.9
        )


@router.get("/intents")
async def get_available_intents():
    """Get list of available query intents for AI agents"""
    return {
        "intents": [
            {
                "name": "orders_today",
                "examples": [
                    "ce comenzi am astazi?",
                    "cate comenzi am azi?",
                    "what orders do I have today?"
                ]
            },
            {
                "name": "orders_week",
                "examples": [
                    "cate comenzi am avut saptamana asta?",
                    "comenzi ultima saptamana"
                ]
            },
            {
                "name": "orders_month",
                "examples": [
                    "cate comenzi am facut in ultima luna?",
                    "orders last month"
                ]
            },
            {
                "name": "revenue",
                "examples": [
                    "cat am vandut astazi?",
                    "venituri luna asta",
                    "how much revenue this week?"
                ]
            }
        ]
    }
