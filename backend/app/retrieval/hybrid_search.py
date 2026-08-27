import re

import faiss
import numpy as np
from rank_bm25 import BM25Okapi

from app.database.mongodb import get_database


_db = None
_chunks = None
_documents = None
_document_tokens = None
_bm25 = None
_index = None
_embedding_function = None


# =========================================================
# INITIALIZATION
# =========================================================

def _initialize():

    global _db
    global _chunks
    global _documents
    global _document_tokens
    global _bm25
    global _index
    global _embedding_function

    if (
        _chunks is not None
        and _bm25 is not None
        and _index is not None
        and _embedding_function is not None
    ):
        return

    print(
        "[RAG] Initializing retrieval system...",
        flush=True
    )

    from app.embeddings.embedding_service import generate_embedding

    _embedding_function = generate_embedding

    _db = get_database()

    print(
        "[RAG] Loading MongoDB chunks...",
        flush=True
    )

    _chunks = list(
        _db.chunks.find(
            {},
            {"_id": 0}
        )
    )

    print(
        f"[RAG] Loaded {len(_chunks)} chunks",
        flush=True
    )

    _documents = [
        str(
            chunk.get(
                "chunk_text",
                ""
            )
        )
        for chunk in _chunks
    ]

    # ---------------------------------------------------------
    # TOKENIZATION
    # ---------------------------------------------------------

    _document_tokens = [
        set(
            _tokenize(document)
        )
        for document in _documents
    ]

    tokenized_documents = [
        list(tokens)
        for tokens in _document_tokens
    ]

    # ---------------------------------------------------------
    # BM25
    # ---------------------------------------------------------

    print(
        "[RAG] Building BM25 index...",
        flush=True
    )

    _bm25 = BM25Okapi(
        tokenized_documents
    )

    # ---------------------------------------------------------
    # FAISS
    # ---------------------------------------------------------

    print(
        "[RAG] Loading FAISS index...",
        flush=True
    )

    _index = faiss.read_index(
        "vector_index.faiss"
    )

    print(
        "[RAG] Retrieval system ready.",
        flush=True
    )


# =========================================================
# TEXT HELPERS
# =========================================================

def _tokenize(text):

    if not text:
        return []

    return re.findall(
        r"[a-z0-9]+",
        str(text).lower()
    )


def _normalize(text):

    if not text:
        return ""

    return " ".join(
        str(text)
        .lower()
        .split()
    )


def _query_terms(query):

    stop_words = {
        "what",
        "who",
        "when",
        "where",
        "why",
        "how",
        "did",
        "does",
        "do",
        "was",
        "were",
        "is",
        "are",
        "the",
        "a",
        "an",
        "to",
        "of",
        "in",
        "on",
        "for",
        "and",
        "or",
        "with",
        "from",
        "between",
        "about",
        "regarding",
        "which",
        "that",
        "this",
        "these",
        "those",
        "me",
        "show",
        "find",
        "give",
        "tell"
    }

    return [
        term
        for term in _tokenize(query)
        if term not in stop_words
    ]


# =========================================================
# SEARCH
# =========================================================

def search(
    query,
    top_k=5
):

    _initialize()

    if not _chunks:
        return []

    query = str(
        query
    ).strip()

    if not query:
        return []

    print(
        f"[RAG] Searching: {query}",
        flush=True
    )

    # ---------------------------------------------------------
    # QUERY TERMS
    # ---------------------------------------------------------

    query_terms = _query_terms(
        query
    )

    query_normalized = _normalize(
        query
    )

    # ---------------------------------------------------------
    # SEMANTIC SEARCH
    # ---------------------------------------------------------

    query_embedding = np.array(
        [
            _embedding_function(query)
        ],
        dtype="float32"
    )

    semantic_k = min(
        max(top_k * 4, 20),
        len(_chunks)
    )

    distances, indices = _index.search(
        query_embedding,
        semantic_k
    )

    # ---------------------------------------------------------
    # NORMALIZE FAISS SCORES
    # ---------------------------------------------------------

    semantic_scores = {}

    valid_distances = []

    for distance, index_position in zip(
        distances[0],
        indices[0]
    ):

        if (
            index_position < 0
            or index_position >= len(_chunks)
        ):
            continue

        valid_distances.append(
            float(distance)
        )

    # ---------------------------------------------------------
    # DETERMINE FAISS INDEX TYPE
    # ---------------------------------------------------------

    metric_type = getattr(
        _index,
        "metric_type",
        None
    )

    # ---------------------------------------------------------
    # INNER PRODUCT
    # ---------------------------------------------------------

    if (
        metric_type == faiss.METRIC_INNER_PRODUCT
        and valid_distances
    ):

        min_score = min(
            valid_distances
        )

        max_score = max(
            valid_distances
        )

        score_range = (
            max_score
            - min_score
        )

        for distance, index_position in zip(
            distances[0],
            indices[0]
        ):

            if (
                index_position < 0
                or index_position >= len(_chunks)
            ):
                continue

            value = float(
                distance
            )

            if score_range > 0:

                normalized = (
                    value - min_score
                ) / score_range

            else:

                normalized = 1.0

            semantic_scores[
                index_position
            ] = max(
                0.0,
                min(
                    normalized,
                    1.0
                )
            )

    # ---------------------------------------------------------
    # L2 DISTANCE
    # ---------------------------------------------------------

    else:

        # Smaller L2 distance = more similar.
        #
        # Convert distance into a similarity-like value.

        for distance, index_position in zip(
            distances[0],
            indices[0]
        ):

            if (
                index_position < 0
                or index_position >= len(_chunks)
            ):
                continue

            distance = float(
                distance
            )

            semantic_scores[
                index_position
            ] = 1.0 / (
                1.0 + max(
                    distance,
                    0.0
                )
            )

    # ---------------------------------------------------------
    # BM25
    # ---------------------------------------------------------

    keyword_scores = _bm25.get_scores(
        query_terms
    )

    keyword_k = min(
        max(top_k * 4, 20),
        len(_chunks)
    )

    if len(keyword_scores):

        keyword_indices = np.argsort(
            keyword_scores
        )[-keyword_k:][::-1]

    else:

        keyword_indices = []

    # ---------------------------------------------------------
    # NORMALIZE BM25
    # ---------------------------------------------------------

    max_bm25 = (
        float(
            np.max(
                keyword_scores
            )
        )
        if len(keyword_scores)
        else 0.0
    )

    if max_bm25 <= 0:

        max_bm25 = 1.0

    # ---------------------------------------------------------
    # CANDIDATES
    # ---------------------------------------------------------

    candidates = set(
        semantic_scores.keys()
    )

    candidates.update(
        keyword_indices.tolist()
        if hasattr(
            keyword_indices,
            "tolist"
        )
        else keyword_indices
    )

    ranked = []

    # ---------------------------------------------------------
    # SCORE CANDIDATES
    # ---------------------------------------------------------

    for index_position in candidates:

        document = _documents[
            index_position
        ]

        document_normalized = _normalize(
            document
        )

        document_tokens = _document_tokens[
            index_position
        ]

        # -----------------------------------------------------
        # SEMANTIC SCORE
        # -----------------------------------------------------

        semantic_score = semantic_scores.get(
            index_position,
            0.0
        )

        # -----------------------------------------------------
        # BM25 SCORE
        # -----------------------------------------------------

        bm25_score = float(
            keyword_scores[
                index_position
            ]
        )

        normalized_bm25 = (
            bm25_score
            /
            max_bm25
        )

        normalized_bm25 = max(
            0.0,
            min(
                normalized_bm25,
                1.0
            )
        )

        # -----------------------------------------------------
        # TERM MATCHING
        # -----------------------------------------------------

        matched_terms = sum(
            1
            for term in query_terms
            if term in document_tokens
        )

        if query_terms:

            term_match_score = (
                matched_terms
                /
                len(query_terms)
            )

        else:

            term_match_score = 0.0

        # -----------------------------------------------------
        # EXACT PHRASE
        # -----------------------------------------------------

        phrase_score = (
            1.0
            if (
                query_normalized
                in document_normalized
            )
            else 0.0
        )

        # -----------------------------------------------------
        # IMPORTANT QUERY PHRASES
        # -----------------------------------------------------

        phrase_boost = 0.0

        query_words = _tokenize(
            query
        )

        if len(query_words) >= 2:

            for size in (3, 2):

                if len(query_words) < size:
                    continue

                for start in range(
                    len(query_words) - size + 1
                ):

                    phrase = " ".join(
                        query_words[
                            start:
                            start + size
                        ]
                    )

                    # Ignore very generic phrases.

                    if phrase in {
                        "what were the",
                        "what are the",
                        "who were the",
                        "who are the",
                        "find emails related",
                        "emails related to",
                        "main topics in",
                        "people in the",
                        "related to the"
                    }:
                        continue

                    if (
                        phrase in document_normalized
                    ):

                        phrase_boost += 0.08

        phrase_boost = min(
            phrase_boost,
            0.24
        )

        # -----------------------------------------------------
        # FINAL SCORE
        # -----------------------------------------------------

        final_score = (
            0.35 * semantic_score
            + 0.35 * normalized_bm25
            + 0.20 * term_match_score
            + 0.05 * phrase_score
            + 0.05 * phrase_boost
        )

        ranked.append(
            (
                float(
                    final_score
                ),
                index_position
            )
        )

    # ---------------------------------------------------------
    # SORT
    # ---------------------------------------------------------

    ranked.sort(
        key=lambda item: item[0],
        reverse=True
    )

    # ---------------------------------------------------------
    # REMOVE DUPLICATES
    # ---------------------------------------------------------

    results = []

    seen_chunk_ids = set()
    seen_text = set()

    for score, index_position in ranked:

        chunk = dict(
            _chunks[
                index_position
            ]
        )

        chunk_id = chunk.get(
            "chunk_id"
        )

        text = _normalize(
            chunk.get(
                "chunk_text",
                ""
            )
        )

        # -----------------------------------------------------
        # CHUNK ID DEDUPLICATION
        # -----------------------------------------------------

        if chunk_id:

            if chunk_id in seen_chunk_ids:
                continue

            seen_chunk_ids.add(
                chunk_id
            )

        # -----------------------------------------------------
        # TEXT DEDUPLICATION
        # -----------------------------------------------------

        if text:

            if text in seen_text:
                continue

            seen_text.add(
                text
            )

        # -----------------------------------------------------
        # STORE SCORE
        # -----------------------------------------------------

        chunk[
            "_retrieval_score"
        ] = round(
            float(score),
            6
        )

        results.append(
            chunk
        )

        if len(results) >= top_k:
            break

    # ---------------------------------------------------------
    # DEBUG
    # ---------------------------------------------------------

    print(
        "[RAG] Top results:",
        flush=True
    )

    for i, result in enumerate(
        results,
        start=1
    ):

        print(
            f"  {i}. "
            f"score="
            f"{result.get('_retrieval_score', 0):.4f}",
            flush=True
        )

        print(
            f"     chunk_id="
            f"{result.get('chunk_id')}",
            flush=True
        )

        print(
            f"     email_id="
            f"{result.get('email_id')}",
            flush=True
        )

        print(
            "     text="
            f"{str(result.get('chunk_text', ''))[:500]}",
            flush=True
        )

    return results