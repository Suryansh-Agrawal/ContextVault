from typing import Dict
from app.core.schema import ContextSchema


# Simple in-memory store (can be swapped later)
CONTEXT_STORE: Dict[str, ContextSchema] = {}
LAST_TURN_STORE: Dict[str, int] = {}
