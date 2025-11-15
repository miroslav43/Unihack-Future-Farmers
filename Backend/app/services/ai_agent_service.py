"""Simplified AI Agent - fără function calling pentru început"""
import httpx
import json
from typing import Dict, Any, List, Optional

from ..services.order_service import OrderService
from ..services.inventory_service import InventoryService
from ..services.crop_service import CropService
from ..services.task_service import TaskService


class AIAgentService:
    """AI Agent that processes natural language queries using OpenRouter"""
    
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_API_KEY = "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"
    MODEL = "openai/gpt-4o-mini"
    
    def __init__(self, db):
        self.db = db
        self.order_service = OrderService(db)
        self.inventory_service = InventoryService(db)
        self.crop_service = CropService(db)
        self.task_service = TaskService(db)
    
    async def _get_farmer_data(self, farmer_id: str) -> Dict[str, Any]:
        """Get all relevant farmer data at once"""
        data = {}
        
        try:
            # Orders
            today_orders = await self.order_service.get_today_orders(farmer_id)
            orders_stats = await self.order_service.get_orders_statistics(farmer_id)
            data["comenzi_astazi"] = len(today_orders)
            data["venit_total"] = orders_stats.get("total_revenue", 0)
            data["numar_comenzi_total"] = orders_stats.get("total_orders", 0)
            
            # Inventory
            inv_value = await self.inventory_service.get_inventory_value(farmer_id)
            inv_items = await self.inventory_service.list_farmer_inventory(farmer_id)
            data["valoare_inventar"] = inv_value
            data["numar_produse"] = len(inv_items)
            
            # Tasks
            today_tasks = await self.task_service.get_today_tasks(farmer_id)
            overdue_tasks = await self.task_service.get_overdue_tasks(farmer_id)
            data["taskuri_astazi"] = len(today_tasks)
            data["taskuri_intarziate"] = len(overdue_tasks)
            
            # Crops
            crops = await self.crop_service.list_farmer_crops(farmer_id)
            data["numar_culturi"] = len(crops)
            
        except Exception as e:
            print(f"Error getting farmer data: {e}")
        
        return data
    
    async def process_query(self, farmer_id: str, query: str, conversation_history: Optional[List] = None) -> Dict[str, Any]:
        """Process natural language query using AI"""
        
        # Get farmer data
        farmer_data = await self._get_farmer_data(farmer_id)
        
        # Prepare system message with data
        system_message = f"""Ești un asistent AI pentru fermieri în România.

DATE FERMA (ID: {farmer_id}):
- Comenzi astăzi: {farmer_data.get('comenzi_astazi', 0)}
- Venit total: {farmer_data.get('venit_total', 0)} RON
- Total comenzi: {farmer_data.get('numar_comenzi_total', 0)}
- Valoare inventar: {farmer_data.get('valoare_inventar', 0)} RON
- Produse în stoc: {farmer_data.get('numar_produse', 0)}
- Task-uri astăzi: {farmer_data.get('taskuri_astazi', 0)}
- Task-uri întârziate: {farmer_data.get('taskuri_intarziate', 0)}
- Număr culturi: {farmer_data.get('numar_culturi', 0)}

Răspunde ÎNTOTDEAUNA în limba română, natural și prietenos.
Folosește datele de mai sus pentru a răspunde la întrebări despre fermă.
Fii concis dar util."""

        messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.OPENROUTER_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "Farmer Assistant"
                    },
                    json={
                        "model": self.MODEL,
                        "messages": messages
                    }
                )
                
                response.raise_for_status()
                ai_response = response.json()
                
                answer = ai_response["choices"][0]["message"]["content"]
                
                return {
                    "answer": answer,
                    "data": farmer_data,
                    "function_called": None,
                    "success": True
                }
                
        except Exception as e:
            return {
                "answer": f"Eroare la procesarea întrebării: {str(e)}",
                "data": None,
                "function_called": None,
                "success": False,
                "error": str(e)
            }
