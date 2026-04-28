"""
translation/response_cleaner.py

Extracts clean translated code from Ollama's raw response.

Ollama responses for code generation tasks frequently contain:
  - Markdown fences: ```jsx ... ``` or ```vue ... ```
  - <think>...</think> reasoning blocks (Qwen3 models)
  - Preamble text before the code
  - Postamble explanation after the code
  - Mixed language labels on fences: ```typescript, ```html etc.

Three extraction strategies in order:
  1. Fenced block   — extract content between ``` markers
  2. Tag block      — extract content between <template> or <!DOCTYPE markers
  3. Strip fallback — remove known non-code lines, return what remains

The cleaner never modifies the code content itself — it only removes
wrapper text. Indentation, newlines, and logic are preserved exactly.
"""

import re


_FENCE_LANGUAGES = {
    "react", "vue", "angular", "html", "javascript", "typescript",
    "js", "ts", "jsx", "tsx", "svelte", "css", "scss",
}


def _strip_think_blocks(raw: str) -> str:
    return re.sub(r'<think>[\s\S]*?</think>', '', raw).strip()


def _extract_fenced_block(raw: str) -> str | None:
    pattern = re.compile(
        r'```(?:' + '|'.join(_FENCE_LANGUAGES) + r')?\s*\n([\s\S]*?)```',
        re.IGNORECASE,
    )
    matches = pattern.findall(raw)
    if matches:
        return max(matches, key=len).strip()
    return None


def _extract_by_marker(raw: str, target_framework: str) -> str | None:
    if target_framework == "HTML":
        m = re.search(r'(<!DOCTYPE[\s\S]+)', raw, re.IGNORECASE)
        if m:
            return m.group(1).strip()

    if target_framework == "Vue":
        m = re.search(r'(<template>[\s\S]+)', raw)
        if m:
            return m.group(1).strip()

    if target_framework in ("React", "Angular"):
        m = re.search(r'(import\s+[\s\S]+)', raw)
        if m:
            return m.group(1).strip()

    return None


def _strip_fallback(raw: str) -> str:
    lines    = raw.splitlines()
    cleaned  = []
    skip_prefixes = (
        "here is", "here's", "the translated", "translating",
        "below is", "output:", "result:", "translation:",
        "i've translated", "i have translated",
    )

    for line in lines:
        stripped = line.strip().lower()
        if any(stripped.startswith(p) for p in skip_prefixes):
            continue
        cleaned.append(line)

    return "\n".join(cleaned).strip()


def clean(raw: str, target_framework: str) -> str:
    """
    Extract clean translated code from a raw Ollama response.

    Attempts three strategies in order, returning the first success.
    Falls back to the stripped raw response if all strategies fail.

    Args:
        raw              : Raw string from Phi3Client.chat()
        target_framework : One of React | Vue | Angular | HTML
                           Used to guide marker-based extraction

    Returns:
        Clean code string with no markdown, fences, or preamble
    """
    if not raw or not raw.strip():
        raise ValueError("Empty response from model — nothing to clean")

    text = _strip_think_blocks(raw)

    fenced = _extract_fenced_block(text)
    if fenced:
        return fenced

    by_marker = _extract_by_marker(text, target_framework)
    if by_marker:
        return by_marker

    return _strip_fallback(text)
