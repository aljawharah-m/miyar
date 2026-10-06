"""Local multilingual semantic-AI layer for Mi'yar.

The model is an independent semantic-drift signal. It never decides religious
correctness and never counts as a standalone meaning gap.
"""
from __future__ import annotations
import os, threading

DEFAULT_MODEL="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_MODEL=None
_MODEL_ID=None
_MODEL_ERROR=None
_MODEL_LOCK=threading.Lock()
_WARM_THREAD=None


def interpret_similarity(score: float):
    """Conservative engineering thresholds, not calibrated probabilities."""
    score=float(score)
    if score < 0.42:
        return {"state":"fail","severity":"high","label":"انجراف دلالي مرتفع","detail":"التشابه الدلالي العام منخفض بصورة تستحق المراجعة."}
    if score < 0.58:
        return {"state":"review","severity":"medium","label":"انجراف دلالي محتمل","detail":"يوجد تفاوت دلالي يحتاج دعماً من بقية طبقات مِعيار."}
    return {"state":"pass","severity":None,"label":"تقارب دلالي عام","detail":"التشابه العام مرتفع نسبيًا، لكنه لا يثبت حفظ القيود الدقيقة."}


def _load_model(model_id: str):
    global _MODEL,_MODEL_ID,_MODEL_ERROR
    if _MODEL is not None and _MODEL_ID==model_id:
        return _MODEL,None
    with _MODEL_LOCK:
        if _MODEL is not None and _MODEL_ID==model_id:
            return _MODEL,None
        try:
            from sentence_transformers import SentenceTransformer
            kwargs={}
            if os.getenv("MIYAR_MODEL_LOCAL_ONLY","0").strip().lower() in {"1","true","yes"}:
                kwargs["local_files_only"]=True
            _MODEL=SentenceTransformer(model_id, **kwargs)
            _MODEL_ID=model_id
            _MODEL_ERROR=None
            return _MODEL,None
        except Exception as exc:
            _MODEL=None
            _MODEL_ID=model_id
            _MODEL_ERROR=f"{type(exc).__name__}: {exc}"
            return None,_MODEL_ERROR


def start_background_warmup(model_id: str|None=None):
    """Load the model while the user reads/types, before the first Analyze click."""
    global _WARM_THREAD
    model_id=model_id or os.getenv("MIYAR_SEMANTIC_MODEL",DEFAULT_MODEL)
    if _MODEL is not None and _MODEL_ID==model_id:
        return "ready"
    if _WARM_THREAD is not None and _WARM_THREAD.is_alive():
        return "warming"
    def _warm():
        _load_model(model_id)
    _WARM_THREAD=threading.Thread(target=_warm,name="miyar-semantic-warmup",daemon=True)
    _WARM_THREAD.start()
    return "warming"


def model_state():
    if _MODEL is not None:
        return {"state":"ready","model":_MODEL_ID,"error":None}
    if _WARM_THREAD is not None and _WARM_THREAD.is_alive():
        return {"state":"warming","model":_MODEL_ID or DEFAULT_MODEL,"error":None}
    return {"state":"error" if _MODEL_ERROR else "idle","model":_MODEL_ID or DEFAULT_MODEL,"error":_MODEL_ERROR}




def _chunk_text(text: str, max_chars: int=600, max_chunks: int|None=None):
    """Split long text without silently dropping later passages.

    ``max_chunks`` is kept for backward compatibility but is intentionally not
    used to merge chunks into oversized blocks. The public UI bounds each side
    to 12,000 characters, so normal requests remain small while every passage
    reaches the embedding model.
    """
    import re
    text=(text or "").strip()
    if not text:
        return [""]
    parts=[p.strip() for p in re.split(r"(?<=[.!?؟؛\n])\s+|\n+", text) if p.strip()]
    if not parts:
        parts=[text]
    chunks=[]; current=""
    for part in parts:
        hard=[part[i:i+max_chars] for i in range(0,len(part),max_chars)] if len(part)>max_chars else [part]
        for piece in hard:
            candidate=(current+" "+piece).strip() if current else piece
            if current and len(candidate)>max_chars:
                chunks.append(current)
                current=piece
            else:
                current=candidate
    if current:
        chunks.append(current)
    return chunks


def run_semantic_ai(ar_text: str, en_text: str, enabled: bool=True, model_id: str|None=None):
    if not enabled or os.getenv("MIYAR_DISABLE_LOCAL_AI","0").strip().lower() in {"1","true","yes"}:
        return {"available":False,"status":"off","model":None,"similarity":None,"signal":None,"issue":None,"detail":"تم تعطيل طبقة الذكاء الدلالي محليًا."}
    model_id=model_id or os.getenv("MIYAR_SEMANTIC_MODEL",DEFAULT_MODEL)
    model,err=_load_model(model_id)
    if model is None:
        return {"available":False,"status":"unavailable","model":model_id,"similarity":None,"signal":None,"issue":None,"detail":"تعذر تحميل نموذج التمثيلات الدلالية. يستمر المحرك بطبقات الحماية الأخرى.","error":err}
    try:
        import numpy as np
        ar_chunks=_chunk_text(ar_text)
        en_chunks=_chunk_text(en_text)
        texts=ar_chunks+en_chunks
        emb=model.encode(texts,normalize_embeddings=True,show_progress_bar=False,convert_to_numpy=True)
        ar_vec=np.asarray(emb[:len(ar_chunks)]).mean(axis=0)
        en_vec=np.asarray(emb[len(ar_chunks):]).mean(axis=0)
        ar_norm=float(np.linalg.norm(ar_vec)); en_norm=float(np.linalg.norm(en_vec))
        if ar_norm:
            ar_vec=ar_vec/ar_norm
        if en_norm:
            en_vec=en_vec/en_norm
        score=float(ar_vec @ en_vec)
        signal=interpret_similarity(score)
        # Policy: similarity is SUPPORTING AI EVIDENCE, not a standalone error.
        return {"available":True,"status":signal["state"],"model":model_id,"similarity":score,"signal":signal,"issue":None,"detail":signal["detail"]}
    except Exception as exc:
        return {"available":False,"status":"unavailable","model":model_id,"similarity":None,"signal":None,"issue":None,"detail":"تعذر تنفيذ المقارنة الدلالية؛ استمر المحرك بالطبقات الأخرى.","error":f"{type(exc).__name__}: {exc}"}
