from pydantic import BaseModel


class ExtractionMeta(BaseModel):
    source: str  # "model" | "retry" | "fallback"
    retries: int
