from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

_MODEL = None
_TOKENIZER = None


def load_model():
    global _MODEL, _TOKENIZER

    if _MODEL is None or _TOKENIZER is None:
        model_name = "google/flan-t5-base"

        _TOKENIZER = AutoTokenizer.from_pretrained(model_name)
        _MODEL = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        _MODEL.eval()
        torch.set_grad_enabled(False)

    return _MODEL, _TOKENIZER
