"""TF-IDF retrieval over knowledge/metrics_glossary.md for ai-engineer.

Deliberately not an embedding-API-based RAG pipeline — this needs to work with
zero external API keys, and TF-IDF is more than adequate for grounding a handful
of short, keyword-distinct glossary entries. Swap in a real embedding model here
if the knowledge base grows large enough that keyword overlap stops being a
reliable enough retrieval signal.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

GLOSSARY_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "metrics_glossary.md"


@dataclass
class RetrievedChunk:
    term: str
    text: str
    score: float


def _load_chunks(path: Path = GLOSSARY_PATH) -> list[tuple[str, str]]:
    """Split the glossary into (term, body) chunks on '## ' headers."""
    content = path.read_text(encoding="utf-8")
    sections = re.split(r"^## ", content, flags=re.MULTILINE)[1:]  # drop the H1 preamble
    chunks = []
    for section in sections:
        term, _, body = section.partition("\n")
        chunks.append((term.strip(), body.strip()))
    return chunks


def retrieve(query: str, top_k: int = 1, min_score: float = 0.05) -> list[RetrievedChunk]:
    """Return the top_k glossary chunks most relevant to `query`, or an empty
    list if nothing clears `min_score` — callers must treat an empty result as
    'not covered by the glossary,' not silently fall back to an invented
    definition.
    """
    chunks = _load_chunks()
    corpus = [f"{term} {body}" for term, body in chunks]

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(corpus + [query])
    query_vec = matrix[-1]
    doc_vecs = matrix[:-1]

    scores = cosine_similarity(query_vec, doc_vecs)[0]
    ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)

    return [
        RetrievedChunk(term=term, text=body, score=round(float(score), 4))
        for (term, body), score in ranked[:top_k]
        if score >= min_score
    ]


if __name__ == "__main__":
    for q in ["what counts as an active user", "what does net revenue retention mean", "difference between expansion and activation"]:
        print(f"\nQuery: {q!r}")
        results = retrieve(q, top_k=1)
        if not results:
            print("  No glossary entry cleared the relevance threshold.")
        for r in results:
            print(f"  [{r.score}] {r.term}: {r.text[:120]}...")
