from fastapi import APIRouter, HTTPException
from typing import Dict

from app.pipeline.normalize import normalize_chat_turns
from app.pipeline.chunk import chunk_chat
from app.pipeline.safe_compress import safe_compress
from app.core.state import CONTEXT_STORE, LAST_TURN_STORE
from app.core.schema import ContextSchema

router = APIRouter()


@router.post("/context/extract_delta")
def extract_delta(payload: Dict):

    conversation_id = payload.get("conversation_id")
    new_turns = payload.get("new_turns", [])

    if not conversation_id:
        raise HTTPException(400, "conversation_id required")

    if not new_turns:
        raise HTTPException(400, "no new turns provided")

    normalized = normalize_chat_turns(new_turns)
    chunks = chunk_chat(normalized)

    delta_context, meta = safe_compress(chunks)

    # Merge with existing context
    previous = CONTEXT_STORE.get(conversation_id)

    if previous:
        merged = ContextSchema(
            conversation_goal=previous.conversation_goal,
            key_facts=previous.key_facts + delta_context.key_facts,
            key_decisions=previous.key_decisions + delta_context.key_decisions,
            open_questions=previous.open_questions + delta_context.open_questions,
            constraints=previous.constraints + delta_context.constraints,
            entities=previous.entities + delta_context.entities,
            compressed_summary=previous.compressed_summary
            + " "
            + delta_context.compressed_summary,
        )
    else:
        merged = delta_context

    CONTEXT_STORE[conversation_id] = merged

    return {
        "context": merged.dict(),
        "meta": meta.dict(),
    }
