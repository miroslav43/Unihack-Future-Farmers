"""Helper utility functions"""
from datetime import datetime
from typing import Any, Dict
import json


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string"""
    return dt.isoformat()


def parse_datetime(dt_str: str) -> datetime:
    """Parse ISO datetime string"""
    return datetime.fromisoformat(dt_str)


def convert_objectid_to_str(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert MongoDB ObjectId to string in dictionaries
    Recursively handles nested dictionaries and lists
    """
    if isinstance(data, dict):
        return {
            key: (str(value) if key == '_id' else convert_objectid_to_str(value))
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    else:
        return data


def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage safely"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def serialize_to_json(data: Any) -> str:
    """
    Serialize data to JSON string with datetime handling
    """
    def default_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    return json.dumps(data, default=default_serializer)


def bytes_to_mb(bytes_value: int) -> float:
    """Convert bytes to megabytes"""
    return round(bytes_value / (1024 * 1024), 2)


def generate_pagination_metadata(
    total: int,
    skip: int,
    limit: int
) -> Dict[str, Any]:
    """Generate pagination metadata"""
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    current_page = (skip // limit) + 1 if limit > 0 else 1
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "total_pages": total_pages,
        "current_page": current_page,
        "has_next": skip + limit < total,
        "has_previous": skip > 0
    }
