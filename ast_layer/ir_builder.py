"""
ir_builder.py

Converts a pre-parsed summary dict into a validated IR instance.

Takes the output of pre_parser.py, builds an Ollama prompt that
combines the structured summary with the raw script block, calls
Qwen2.5-Coder-3B via OLClient, parses the JSON response into an
IR dataclass, and validates it with ir_validator.

Two-attempt strategy:
    Attempt 1 — full prompt with summary + script block
    Attempt 2 — if validator returns critical errors, retry with a
                stricter prompt that explicitly lists what was wrong

The model never sees raw code alone — it always sees the pre-parsed
summary alongside the script block so it fills gaps rather than
extracting from scratch.

Flow:
    summary dict  (from pre_parser.py)
        ↓
    build_prompt()
        ↓
    OLClient.chat()     → raw JSON string
        ↓
    _parse_json()       → dict
        ↓
    IR.from_dict()      → IR instance
        ↓
    ir_validator        → ValidationResult
        ↓
    return IR           (or retry once on critical failure)
"""

import json
import re
from ast_layer.ir_schema    import IR
from ast_layer.ir_validator import validate

MAX_TOKENS = 1500
TEMPERATURE = 0.1

_SYSTEM_PROMPT = """You are a frontend code analyser.
You will receive a pre-parsed structural summary of a frontend component
alongside its raw script block.

Your job is to fill in the following IR schema as a JSON object.
Use the summary hints as a starting point and correct or extend them
using the raw script block.

IR schema:
{
  "framework":  string,               // source framework as detected
  "component":  string,               // component name
  "props":      [{ "name": string, "type": string, "required": bool, "default": string|null }],
  "state":      [{ "name": string, "init": string|null, "type": string }],
  "computed":   [{ "name": string, "expression": string, "deps": [string] }],
  "lifecycle":  [{ "hook": string, "body": string }],
  "methods":    [{ "name": string, "params": [string], "body": string }],
  "imports":    [{ "source": string, "specifiers": [string], "default": string|null }],
  "styles":     string
}

Lifecycle hook names to use:
  onMount | onDestroy | onBeforeMount | onBeforeDestroy | onUpdate |
  onBeforeUpdate | onCreate | onAfterViewInit | onChanges | onEveryRender

Rules:
  - className   → use "class" in attrs
  - onClick     → use "events.click"
  - useState    → state entry
  - useEffect with [] deps → lifecycle hook "onMount"
  - ref()       → state entry  (Vue 3)
  - computed()  → computed entry  (Vue 3)
  - ngOnInit    → lifecycle hook "onMount"
  - ngOnDestroy → lifecycle hook "onDestroy"

Return ONLY valid JSON. No markdown fences. No explanation. No preamble."""


def _build_prompt(summary: dict) -> list[dict]:
    summary_text = json.dumps({
        k: v for k, v in summary.items()
        if k not in ("script_block", "styles", "markup")
    }, indent=2)

    user_content = (
        f"Framework: {summary['framework']}\n\n"
        f"Pre-parsed summary:\n{summary_text}\n\n"
        f"Raw script block:\n```\n{summary.get('script_block', '')}\n```\n\n"
        "Fill the IR schema from the above. Return only JSON."
    )

    return [
        { "role": "system",  "content": _SYSTEM_PROMPT },
        { "role": "user",    "content": user_content },
    ]


def _build_retry_prompt(summary: dict, errors: list[str]) -> list[dict]:
    base     = _build_prompt(summary)
    error_str = "\n".join(f"  - {e}" for e in errors)

    base.append({
        "role": "assistant",
        "content": "[previous attempt had errors]",
    })
    base.append({
        "role": "user",
        "content": (
            f"Your previous response had these critical errors:\n{error_str}\n\n"
            "Please fix them and return corrected JSON only."
        ),
    })
    return base


def _strip_fences(raw: str) -> str:
    raw = re.sub(r'^```(?:json)?\s*', '', raw.strip())
    raw = re.sub(r'\s*```$',          '', raw)
    raw = re.sub(r'<think>[\s\S]*?</think>', '', raw)
    return raw.strip()


def _parse_json(raw: str) -> dict:
    cleaned = _strip_fences(raw)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        brace = cleaned.find("{")
        last  = cleaned.rfind("}")
        if brace != -1 and last != -1:
            try:
                return json.loads(cleaned[brace:last + 1])
            except json.JSONDecodeError:
                pass

    raise ValueError(f"Could not parse IR JSON from model response:\n{raw[:300]}")


def _get_client():
    from ollama_client import OLClient
    return OLClient()


def build_ir(summary: dict) -> IR:
    """
    Convert a pre-parsed summary dict into a validated IR instance.

    Args:
        summary : Output of pre_parser.parse()

    Returns:
        IR instance — validated, ready for translation prompt

    Raises:
        RuntimeError  if Ollama is unreachable
        ValueError    if IR cannot be parsed after two attempts
    """
    client = _get_client()

    if not client.is_available():
        raise RuntimeError(
            "Ollama is not reachable at localhost:11434.\n"
            "Run: ollama serve"
        )

    messages  = _build_prompt(summary)
    raw       = client.chat(messages, max_new_tokens=MAX_TOKENS, temperature=TEMPERATURE)
    data      = _parse_json(raw)
    ir        = IR.from_dict(data)
    result    = validate(ir)

    if not result.is_valid:
        messages  = _build_retry_prompt(summary, result.errors)
        raw       = client.chat(messages, max_new_tokens=MAX_TOKENS, temperature=TEMPERATURE)
        data      = _parse_json(raw)
        ir        = IR.from_dict(data)
        result    = validate(ir)

        if not result.is_valid:
            raise ValueError(
                f"IR extraction failed after two attempts.\n"
                f"Errors: {result.errors}"
            )

    return ir
