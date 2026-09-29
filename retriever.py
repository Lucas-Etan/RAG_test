import json

from pathlib import Path
from embedding_vector import cosine, embed_text

SCORE_THRESHOLD = 0.55
_CHUNK_CACHE: list[dict] | None = None

def load_chunks(path: str = "index/chunks.json") -> list[dict]:
    global _CHUNK_CACHE
    if _CHUNK_CACHE is not None:
        return _CHUNK_CACHE

    chunks = json.loads(Path(path).read_text().encode("utf-8"))

    for chunk in chunks:
        chunk["vector"] = embed_text(chunk["text"])

    _CHUNK_CACHE = chunks
    return chunks

def retrieve(question: str, top_k: int = 3) -> list[dict]:
    query_vec = embed_text(question)

    scored = []
    for chunk in load_chunks():
        score = cosine(query_vec, chunk["vector"])
        scored.append({**chunk, "score": round(score, 4)})

    scored.sort(key=lambda x: x["score"], reverse=True)

    return [item for item in scored[:top_k] if item["score"] > SCORE_THRESHOLD]