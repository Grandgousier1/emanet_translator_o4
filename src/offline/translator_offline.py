from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

try:
    import torch
except Exception:  # pragma: no cover - optional dependency
    torch = None  # type: ignore

from ..config import settings
from ..logger import logger

_tok = None
_model = None


def get_translator():
    global _tok, _model
    if _tok is None:
        logger.info("nllb.load", model=settings.nllb_model)
        _tok = AutoTokenizer.from_pretrained(settings.nllb_model)
        quant_args = {}
        # Prefer 8-bit quantization if bitsandbytes is available
        try:
            import bitsandbytes  # noqa: F401

            quant_args["load_in_8bit"] = True
        except Exception:
            if torch is not None:
                quant_args["torch_dtype"] = torch.float16
        _model = AutoModelForSeq2SeqLM.from_pretrained(
            settings.nllb_model,
            device_map="auto",
            **quant_args,
        )
    return _tok, _model


def translate_segments(segments):
    if not segments:
        return []
    tok, mdl = get_translator()
    out = []
    batch = []
    max_batch_chars = 1200

    def flush():
        if not batch:
            return
        texts = [s["text"] for s in batch]
        inputs = tok(texts, return_tensors="pt", padding=True, truncation=True)
        gen = mdl.generate(**inputs, max_length=512)
        decoded = tok.batch_decode(gen, skip_special_tokens=True)
        for src, tgt in zip(batch, decoded):
            out.append({**src, "text_fr": tgt})
        batch.clear()

    for seg in segments:
        if sum(len(s["text"]) for s in batch) + len(seg["text"]) > max_batch_chars:
            flush()
        batch.append(seg)
    flush()
    return out
