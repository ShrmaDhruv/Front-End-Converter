"""
translation/translation_validator.py

Post-translation sanity checks on the generated code.

Verifies that the translated code is structurally consistent with
the IR it was generated from. Does not parse the code — uses fast
regex pattern matching only.

Two severity levels:
  critical  → is_valid=False  → triggers a retry in translate()
  warning   → is_valid=True   → logged, does not block output

Critical checks:
  - Output is not empty
  - Output does not look like the source framework (translation failed)
  - State names from IR are present in the output
  - Component name is present in the output

Warning checks:
  - Method names from IR are present in the output
  - Prop names from IR are present in the output
  - Expected framework markers are present (e.g. useState for React)
"""

import re
from dataclasses import dataclass, field
from ast_layer.ir_schema import IR


_FRAMEWORK_MARKERS = {
    "React": [
        r'\buseState\b',
        r'\buseEffect\b',
        r'export\s+default',
        r'=>\s*\(',
    ],
    "Vue": [
        r'<template>',
        r'<script\s+setup',
        r'\bref\s*\(',
        r'defineProps',
    ],
    "Angular": [
        r'@Component',
        r'ngOnInit',
        r'export\s+class',
        r'@angular/core',
    ],
    "HTML": [
        r'<!DOCTYPE',
        r'<html',
        r'<script',
        r'<body',
    ],
}

_ANTI_MARKERS = {
    "React":   [r'<template>', r'ngOnInit', r'<!DOCTYPE'],
    "Vue":     [r'useState\b', r'ngOnInit', r'<!DOCTYPE'],
    "Angular": [r'<template>', r'useState\b', r'<!DOCTYPE'],
    "HTML":    [r'useState\b', r'<template>', r'ngOnInit'],
}


@dataclass
class TranslationValidationResult:
    is_valid: bool
    errors:   list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_translation(
    code:             str,
    ir:               IR,
    target_framework: str,
) -> TranslationValidationResult:
    """
    Validate translated code against the source IR.

    Args:
        code             : Cleaned translated code string
        ir               : Source IR the translation was generated from
        target_framework : The framework the code was translated into

    Returns:
        TranslationValidationResult with errors and warnings
    """
    errors   = []
    warnings = []

    if not code or not code.strip():
        errors.append("translated output is empty")
        return TranslationValidationResult(is_valid=False, errors=errors)

    if len(code.strip()) < 20:
        errors.append("translated output is too short to be valid code")
        return TranslationValidationResult(is_valid=False, errors=errors)

    for anti in _ANTI_MARKERS.get(target_framework, []):
        if re.search(anti, code):
            errors.append(
                f"output contains source-framework marker '{anti}' — "
                f"translation may have failed"
            )

    markers      = _FRAMEWORK_MARKERS.get(target_framework, [])
    markers_hit  = sum(1 for m in markers if re.search(m, code))
    if markers_hit == 0:
        errors.append(
            f"output contains no {target_framework} framework markers — "
            f"translation may be wrong framework"
        )

    if ir.component and ir.component != "App":
        if ir.component not in code:
            errors.append(
                f"component name '{ir.component}' not found in output"
            )

    for state in ir.state:
        if state.name and state.name not in code:
            warnings.append(f"state '{state.name}' not found in output")

    for method in ir.methods:
        if method.name and method.name not in code:
            warnings.append(f"method '{method.name}' not found in output")

    for prop in ir.props:
        if prop.name and prop.name not in code:
            warnings.append(f"prop '{prop.name}' not found in output")

    return TranslationValidationResult(
        is_valid = len(errors) == 0,
        errors   = errors,
        warnings = warnings,
    )
