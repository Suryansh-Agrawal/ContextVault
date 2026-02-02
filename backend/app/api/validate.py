from fastapi import APIRouter, HTTPException
from app.core.schema import ContextSchema
from pydantic import ValidationError

router = APIRouter()


@router.post("/validate")
def validate_context(payload: dict):
    try:
        context = ContextSchema(**payload)
        return {
            "valid": True,
            "data": context.dict()
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=e.errors()
        )
