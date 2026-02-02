from typing import List, Dict


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def chunk_chat(
    turns: List[Dict],
    max_tokens: int = 512
) -> List[List[Dict]]:
    chunks = []
    current_chunk = []
    current_tokens = 0

    for turn in turns:
        text = f"{turn['role']}: {turn['content']}"
        tokens = estimate_tokens(text)

        # Single message too large → force split
        if tokens > max_tokens:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
                current_tokens = 0

            chunks.append([turn])
            continue

        if current_tokens + tokens > max_tokens:
            chunks.append(current_chunk)
            current_chunk = []
            current_tokens = 0

        current_chunk.append(turn)
        current_tokens += tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
