import json
import re
from typing import List, Dict

from app.model.loader import load_model
from app.core.schema import ContextSchema


# =========================
# Prompt (FLAN-T5 friendly)
# =========================

TASK_PROMPT = """Extract transferable context from the following conversation.

Return ONLY valid JSON with this schema:
{
  "conversation_goal": string,
  "key_facts": [string],
  "key_decisions": [string],
  "open_questions": [string],
  "constraints": [string],
  "entities": [string],
  "compressed_summary": string
}

Rules:
- All fields are REQUIRED
- Do not add explanations
- Do not add extra keys
- If information is missing, infer conservatively
"""


# =========================
# Prompt builder
# =========================

def build_input(chunks: List[List[Dict]]) -> str:
    lines: List[str] = []

    for chunk in chunks:
        for turn in chunk:
            lines.append(f"{turn['role']}: {turn['content']}")

    conversation = "\n".join(lines)

    # IMPORTANT:
    # We explicitly anchor the output and inject `{`
    # to force valid JSON generation.
    return (
        TASK_PROMPT
        + "\n\nInput Conversation:\n"
        + conversation
        + "\n\nOutput JSON (start with `{`):\n{"
    )


# =========================
# JSON extraction & repair
# =========================

def extract_json(text: str) -> dict:
    """
    Extract and repair JSON from model output.
    Designed to tolerate partial / malformed generations.
    """
    text = text.strip()

    # Try to extract JSON block if model added extra text
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        candidate = match.group(0)
    else:
        # Model may have omitted braces
        candidate = text

    candidate = candidate.strip()

    if not candidate.startswith("{"):
        candidate = "{" + candidate
    if not candidate.endswith("}"):
        candidate = candidate + "}"

    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON after recovery:\n{candidate}") from e


# =========================
# Inference entrypoint
# =========================

def run_inference(chunks: List[List[Dict]]) -> ContextSchema:
    model, tokenizer = load_model()

    prompt = build_input(chunks)

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024,
    )

    output_ids = model.generate(
        **inputs,
        max_new_tokens=768,
        do_sample=False,
        num_beams=2,
        early_stopping=True,
        repetition_penalty=1.1,
        eos_token_id=tokenizer.eos_token_id,
    )

    raw_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    data = extract_json(raw_text)

    # =========================
    # Safety defaults (CRITICAL)
    # =========================

    data.setdefault(
        "conversation_goal",
        "Transfer context from one LLM conversation to another",
    )
    data.setdefault(
        "compressed_summary",
        "Compressed representation of the conversation for transfer to another LLM.",
    )

    data.setdefault("key_facts", [])
    data.setdefault("key_decisions", [])
    data.setdefault("open_questions", [])
    data.setdefault("constraints", [])
    data.setdefault("entities", [])

    # Final, strict validation
    return ContextSchema(**data)
