from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path

_PATH=Path(__file__).resolve().parents[1]/'data'/'terminology_provenance.json'

@lru_cache(maxsize=1)
def _rows():
    try:
        return json.loads(_PATH.read_text(encoding='utf-8'))
    except Exception:
        return []

@lru_cache(maxsize=1)
def _index():
    return {r.get('term'):r for r in _rows() if r.get('term')}

def provenance_for(term: str):
    return _index().get(term)
