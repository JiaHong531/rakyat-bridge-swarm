import json
import os
import re
from rank_bm25 import BM25Okapi

# Define the paths to your local data sandbox
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DICTIONARY_PATH = os.path.join(DATA_DIR, 'dialect_glossary.json')
POLICY_PATH = os.path.join(DATA_DIR, 'unstructured_policies.txt')

# =====================================================================
# BM25 INDEX — built once at import time, reused for every search
# This is the RAG retrieval layer over unstructured_policies.txt
# Production upgrade path: swap BM25Okapi for Qdrant + Gemma embeddings
# =====================================================================

def _build_bm25_index():
    """
    Loads unstructured_policies.txt, splits into paragraphs,
    tokenizes each paragraph, and builds a BM25Okapi index.
    Returns (corpus_paragraphs, bm25_index).
    """
    try:
        with open(POLICY_PATH, 'r', encoding='utf-8') as f:
            raw = f.read()

        # Split into paragraphs (double newline as separator)
        paragraphs = [p.strip() for p in raw.split('\n\n') if p.strip()]

        # Tokenize: lowercase + split on whitespace/punctuation
        tokenized = [re.findall(r'\w+', p.lower()) for p in paragraphs]

        index = BM25Okapi(tokenized)
        print(f"[MCP BM25] Index built: {len(paragraphs)} paragraphs indexed.")
        return paragraphs, index

    except FileNotFoundError:
        print(f"[MCP BM25] ⚠️ Policy file not found: {POLICY_PATH}")
        return [], None
    except Exception as e:
        print(f"[MCP BM25] ⚠️ Failed to build index: {str(e)}")
        return [], None


# Build index once on import
_CORPUS, _BM25_INDEX = _build_bm25_index()


def tool_dictionary_lookup(slang_word: str) -> str:
    """
    MCP Tool: Looks up an unknown dialect or slang word in the local JSON glossary.
    Use this tool ONLY when confidence in translation is low.
    """
    try:
        with open(DICTIONARY_PATH, 'r', encoding='utf-8') as file:
            glossary = json.load(file)

        term = slang_word.lower().strip()

        # Exact match first
        if term in glossary:
            return f"[MCP Dictionary Success] '{term}' translates to '{glossary[term]}'"

        # Fuzzy partial match fallback
        partial_matches = {k: v for k, v in glossary.items() if term in k or k in term}
        if partial_matches:
            results = "; ".join([f"'{k}' → '{v}'" for k, v in list(partial_matches.items())[:3]])
            return f"[MCP Dictionary Partial Match] Closest results: {results}"

        return f"[MCP Dictionary Error] Term '{term}' not found in local database."

    except FileNotFoundError:
        return f"[System Error] Dictionary file not found at: {DICTIONARY_PATH}"
    except json.JSONDecodeError:
        return f"[System Error] Dictionary file is corrupted or invalid JSON."
    except Exception as e:
        return f"[System Error] Failed to access dictionary: {str(e)}"


def tool_policy_search(keyword: str) -> str:
    """
    MCP Tool: Uses BM25 probabilistic retrieval to search the unstructured
    government policy corpus for the most relevant paragraphs.

    BM25 (Best Match 25) scores each paragraph based on term frequency
    and inverse document frequency — far more accurate than string matching.

    Production upgrade path: Qdrant vector DB + Gemma embeddings.
    """
    if _BM25_INDEX is None or not _CORPUS:
        return f"[System Error] BM25 index not available. Check policy file path."

    try:
        # Tokenize the query the same way as the corpus
        query_tokens = re.findall(r'\w+', keyword.lower())

        if not query_tokens:
            return f"[MCP Search Error] Empty query after tokenization: '{keyword}'"

        # BM25 scoring — returns score for every paragraph
        scores = _BM25_INDEX.get_scores(query_tokens)

        # Rank paragraphs by score, take top 3
        ranked = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True
        )

        # Filter out zero-score results (no relevance at all)
        top_results = [(i, s) for i, s in ranked[:5] if s > 0]

        if not top_results:
            return f"[MCP Search Error] No relevant policy found for keyword: '{keyword}'"

        # Build result string with relevance scores for transparency
        output_parts = [f"[MCP BM25 Search] Top results for '{keyword}':\n"]
        for rank, (idx, score) in enumerate(top_results[:3], 1):
            output_parts.append(
                f"--- Result {rank} (BM25 Score: {score:.2f}) ---\n{_CORPUS[idx]}"
            )

        print(f"[MCP BM25] Query: '{keyword}' | Top score: {top_results[0][1]:.2f} | {len(top_results)} results found")
        return "\n\n".join(output_parts)

    except Exception as e:
        return f"[System Error] BM25 search failed: {str(e)}"


# Exposes the tools to Google Gemini Agents
swarm_tools = [tool_dictionary_lookup, tool_policy_search]