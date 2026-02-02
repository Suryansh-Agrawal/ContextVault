from typing import List, Dict, Tuple

from app.pipeline.compress import compress   # real LLM inference
from app.core.schema import ContextSchema
from app.core.result_meta import ExtractionMeta


def safe_compress(
    chunks: List[List[Dict]],
    max_retries: int = 1
) -> Tuple[ContextSchema, ExtractionMeta]:
    """
    Reliability wrapper around LLM inference.

    Guarantees:
    - Never raises due to model failure
    - Always returns a valid ContextSchema
    - Explicitly signals result quality
    """

    attempt = 0
    last_error = None

    # -------------------------
    # Try model inference
    # -------------------------
    while attempt <= max_retries:
        try:
            context = compress(chunks)
            return context, ExtractionMeta(
                source="model" if attempt == 0 else "retry",
                retries=attempt
            )
        except Exception as e:
            last_error = e
            attempt += 1

    # -------------------------
    # Inline deterministic fallback
    # -------------------------
    all_text = []
    for chunk in chunks:
        for turn in chunk:
            all_text.append(f"{turn['role']}: {turn['content']}")

    joined = " ".join(all_text)

    fallback_context = ContextSchema(
        conversation_goal="Transfer conversation context to another LLM",
        key_facts=[],
        key_decisions=[],
        open_questions=[],
        constraints=[],
        entities=[],
        compressed_summary=joined[:800]
    )

    return fallback_context, ExtractionMeta(
        source="fallback",
        retries=max_retries
    )
