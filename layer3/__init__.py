"""
layer3/__init__.py

Layer 3 LLM detection using Qwen2.5-Coder-1.5B-Instruct
via HuggingFace transformers — no Ollama required.

Flow:
  - Layer 1 is ambiguous  →  call Qwen2.5-Coder-1.5B-Instruct
  - Layer 3 answer always prevails
  - Only ask user when Layer 3 itself says confidence "low"

Usage:
    from layer3 import detect_with_llm

    merged = detect_with_llm(code, layer1_scores)
    print(merged.detected)     # "Vue"
    print(merged.confidence)   # "high"
    print(merged.ask_user)     # False
    print(merged.summary())
"""

from layer3.prompt_builder  import build_messages
from layer3.response_parser import parse_response
from layer3.cache           import DetectionCache
from layer3.score_merger    import merge_results, MergedResult

# Shared cache — no model loaded yet
_cache  = DetectionCache()
_client = None   # lazy-loaded on first call to avoid import errors


def _get_client():
    """Lazy-load HFClient so torch import only happens when actually needed."""
    global _client
    if _client is None:
        from hf_client import HFClient
        _client = HFClient()
    return _client


def detect_with_llm(
    code: str,
    layer1_scores: dict[str, int],
) -> MergedResult:
    """
    Full Layer 3 detection pipeline using Qwen2.5-Coder-1.5B-Instruct.

    1. Check cache        → return instantly if seen before
    2. Build prompt
    3. Call Qwen model    → runs on your RTX 3050 via HuggingFace
    4. Parse JSON response
    5. Cache result
    6. Return MergedResult — Layer 3 answer is final

    Args:
        code          : Ambiguous source code string
        layer1_scores : Raw scores from Layer 1 (for display only)

    Returns:
        MergedResult where detected is always Layer 3's answer.
        ask_user is True only when Layer 3 confidence is "low".
    """

    # ── Step 1: Cache check ──────────────────────────────────────────────
    cached = _cache.get(code)
    if cached:
        return merge_results(layer1_scores, cached)

    # ── Step 2: Check model is available ─────────────────────────────────
    client = _get_client()
    if not client.is_available():
        raise ImportError(
            "transformers or torch not installed.\n"
            "Run: pip install transformers torch accelerate"
        )

    # ── Step 3: Build prompt ─────────────────────────────────────────────
    messages = build_messages(code)

    # ── Step 4: Call Qwen2.5-Coder-1.5B-Instruct ───────────────────────
    raw_response = client.chat(
        messages,
        max_new_tokens = 150,    # detection response is tiny
        temperature    = 0.1,
    )

    # ── Step 5: Parse response ───────────────────────────────────────────
    parsed = parse_response(raw_response)

    # ── Step 6: Cache result ─────────────────────────────────────────────
    _cache.set(code, parsed)

    # ── Step 7: Return — Layer 3 prevails ───────────────────────────────
    return merge_results(layer1_scores, parsed)


__all__ = [
    "detect_with_llm",
    "MergedResult",
]