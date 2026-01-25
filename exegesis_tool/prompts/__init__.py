"""Perspective prompt modules for exegesis analysis."""

from typing import Dict, Any
import importlib

PERSPECTIVES = [
    "historian",
    "linguist",
    "author",
    "theologian",
    "disciple",
    "shepherd",
]

def get_prompt_module(perspective: str):
    """Load a perspective prompt module by name."""
    if perspective not in PERSPECTIVES:
        raise ValueError(f"Unknown perspective: {perspective}. Must be one of {PERSPECTIVES}")
    return importlib.import_module(f".{perspective}", package=__name__)

def get_all_prompts() -> Dict[str, Any]:
    """Load all perspective prompt modules."""
    return {p: get_prompt_module(p) for p in PERSPECTIVES}
