from typing import List, Dict


ALLOWED_ROLES = {"user", "assistant", "system"}


def normalize_chat_turns(raw_turns: List[Dict]) -> List[Dict]:
    normalized = []

    for i, turn in enumerate(raw_turns):
        role = str(turn.get("role", "unknown")).lower()
        if role not in ALLOWED_ROLES:
            role = "user"

        content = str(turn.get("content", "")).strip()
        if not content:
            continue

        timestamp = turn.get("timestamp", i)

        normalized.append(
            {
                "role": role,
                "content": content,
                "timestamp": timestamp
            }
        )

    # Sort deterministically
    normalized.sort(key=lambda x: x["timestamp"])

    return normalized
