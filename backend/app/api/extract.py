from fastapi import APIRouter, HTTPException
from typing import List, Dict

from app.pipeline.normalize import normalize_chat_turns
from app.pipeline.chunk import chunk_chat
from app.pipeline.compress import compress
from app.pipeline.safe_compress import safe_compress

router = APIRouter()


@router.post("/context/extract")
def extract_context(payload: List[Dict]):
    if not isinstance(payload, list):
        raise HTTPException(status_code=400, detail="Payload must be a list of chat turns")

    normalized = normalize_chat_turns(payload)
    if not normalized:
        raise HTTPException(status_code=400, detail="No valid chat content")

    chunks = chunk_chat(normalized)
    context, meta = safe_compress(chunks)

    return {
    "context": context.dict(),
    "meta": meta.dict()
    }
