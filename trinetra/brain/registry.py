"""Brain registry — the pluggable 'minds' that turn a disclosure into an astra.

Trinetra is brain-agnostic on purpose: a vibecoder can run a free local model,
a big team can point it at Claude/Fable. The brain only has ONE job — read a
disclosure entry and return astra source code (a string).

╔══════════════════════════════════════════════════════════════════════════╗
║  ADD A NEW BRAIN HERE                                                     ║
║  1. Write a class with `.name` and `.draft_astra(entry) -> str`          ║
║     (subclass trinetra.brain.base.Brain). See template_brain.py.         ║
║  2. Add one line to the BRAINS map below: "yourname": YourBrain          ║
║  That's the only wiring needed — `trinetra feed --brain yourname` works. ║
╚══════════════════════════════════════════════════════════════════════════╝
"""
from .claude_brain import ClaudeBrain
from .ollama_brain import OllamaBrain
from .template_brain import TemplateBrain

# ─────────────────────────── BRAINS (the registry) ───────────────────────────
BRAINS = {
    "template": TemplateBrain,   # offline, deterministic — the default, no model needed
    "ollama": OllamaBrain,       # local model (private/free) — needs Ollama running
    "claude": ClaudeBrain,       # Anthropic API (higher quality) — needs ANTHROPIC_API_KEY
    # "fable":  FableBrain,      # <- add here
}
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT = "template"


def get_brain(name=None):
    name = name or DEFAULT
    if name not in BRAINS:
        raise ValueError(f"unknown brain '{name}'. available: {', '.join(BRAINS)}")
    return BRAINS[name]()


def available():
    return list(BRAINS)
