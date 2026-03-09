"""
rules/__init__.py

Makes `rules` a Python package and exposes all rule lists
and shared types from a single import point.

Usage (import everything at once):
    from rules import REACT_RULES, VUE_RULES, ANGULAR_RULES, HTML_RULES
    from rules import Rule, FiredRule

Usage (import individual framework):
    from rules.react_rules import REACT_RULES
    from rules.vue_rules import VUE_RULES
    from rules.angular_rules import ANGULAR_RULES
    from rules.html_rules import HTML_RULES
"""

from rules.base import Rule, FiredRule
from rules.react_rules import REACT_RULES
from rules.vue_rules import VUE_RULES
from rules.angular_rules import ANGULAR_RULES
from rules.html_rules import HTML_RULES

__all__ = [
    "Rule",
    "FiredRule",
    "REACT_RULES",
    "VUE_RULES",
    "ANGULAR_RULES",
    "HTML_RULES",
]
