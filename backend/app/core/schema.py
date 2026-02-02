from typing import List
from pydantic import BaseModel, Field, validator


class ContextSchema(BaseModel):
    conversation_goal: str = Field(
        ..., max_length=300, description="Primary goal of the conversation"
    )

    key_facts: List[str] = Field(
        default_factory=list, max_items=10
    )

    key_decisions: List[str] = Field(
        default_factory=list, max_items=10
    )

    open_questions: List[str] = Field(
        default_factory=list, max_items=10
    )

    constraints: List[str] = Field(
        default_factory=list, max_items=10
    )

    entities: List[str] = Field(
        default_factory=list, max_items=15
    )

    compressed_summary: str = Field(
        ..., max_length=1000, description="Compressed transferable context"
    )

    @validator(
        "key_facts",
        "key_decisions",
        "open_questions",
        "constraints",
        "entities",
        each_item=True
    )
    def no_empty_strings(cls, v: str):
        if not v or not v.strip():
            raise ValueError("Empty strings are not allowed")
        return v.strip()
