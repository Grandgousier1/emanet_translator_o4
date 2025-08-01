from transformers import AutoTokenizer, AutoModelForCausalLM

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
        logger.info("mistral.load", model=settings.mistral_model)
        _tok = AutoTokenizer.from_pretrained(settings.mistral_model)
        quant_args = {}
        # Prefer 8-bit quantization if bitsandbytes is available
        try:
            import bitsandbytes  # noqa: F401
            quant_args["load_in_8bit"] = True
        except Exception:
            if torch is not None:
                quant_args["torch_dtype"] = torch.float16
        device_map = "auto" if settings.mistral_device == "auto" else None
        _model = AutoModelForCausalLM.from_pretrained(
            settings.mistral_model,
            device_map=device_map,
            **quant_args,
        )
        if settings.mistral_device != "auto":
            _model.to(settings.mistral_device)
    return _tok, _model


def translate_segments(segments):
    if not segments:
        return []
    tok, mdl = get_translator()
    out = []
    for seg in segments:
        prompt = (
            "Traduire le texte suivant du turc vers le français:\n"
            f"{seg['text']}\n"
            "Traduction:"
        )
        inputs = tok(prompt, return_tensors="pt").to(mdl.device)
        gen = mdl.generate(**inputs, max_new_tokens=256)
        text_fr = tok.decode(gen[0], skip_special_tokens=True)
        out.append({**seg, "text_fr": text_fr.strip()})
    return out
