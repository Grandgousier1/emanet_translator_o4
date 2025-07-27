from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from ..config import settings
from ..logger import logger

_tok = None
_model = None

def get_translator():
    global _tok, _model
    if _tok is None:
        logger.info('nllb.load', model=settings.nllb_model)
        _tok = AutoTokenizer.from_pretrained(settings.nllb_model)
        _model = AutoModelForSeq2SeqLM.from_pretrained(settings.nllb_model)
    return _tok, _model

def translate_segments(segments):
    if not segments:
        return []
    tok, mdl = get_translator()
    tok.src_lang = "tur_Latn"
    out = []
    batch = []
    max_batch_chars = 1200
    def flush():
        if not batch: return
        texts = [s['text'] for s in batch]
        inputs = tok(texts, return_tensors='pt', padding=True, truncation=True)
        gen = mdl.generate(
            **inputs,
            max_length=512,
            forced_bos_token_id=tok.lang_code_to_id.get("fra_Latn"),
        )
        decoded = tok.batch_decode(gen, skip_special_tokens=True)
        for src, tgt in zip(batch, decoded):
            out.append({**src, 'text_fr': tgt})
        batch.clear()
    for seg in segments:
        if sum(len(s['text']) for s in batch) + len(seg['text']) > max_batch_chars:
            flush()
        batch.append(seg)
    flush()
    return out

