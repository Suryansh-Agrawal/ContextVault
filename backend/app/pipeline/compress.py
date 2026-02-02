from typing import List, Dict
from app.model.inference import run_inference


def compress(chunks: List[List[Dict]]):
    return run_inference(chunks)
