import re


class Brain:
    """A brain reads a disclosure entry and returns astra source code (str).

    `entry` may be a structured dict OR carry freeform text in entry["raw_text"].
    """
    name = "base"

    def draft_astra(self, entry) -> str:
        raise NotImplementedError


def extract_code(text: str) -> str:
    """Pull Python out of an LLM reply — strip ```python ... ``` fences if present."""
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.S)
    return (m.group(1) if m else text).strip()


# The instruction every real-model brain sends. Kept here so Ollama/Claude share it.
DRAFT_PROMPT = """You are Trinetra's security-astra writer. Turn the vulnerability
disclosure below into ONE Python astra plugin. Output ONLY Python code, no prose.

The astra must define these module-level names:
  ID       (e.g. "A20")
  NAME     (short human name)
  SEVERITY ("CRITICAL" | "HIGH" | "MEDIUM" | "LOW")
  CWE      (e.g. "CWE-20")
  EYE      = "attack"
  FIX      (one sentence)
and a function run(ctx) that uses ctx.session() (a requests.Session) and
ctx.base_url to probe the target, returning (True, "evidence string") if the
exploit lands, or (False, "reason") otherwise. Never raise — catch exceptions
and return (False, ...).

DISCLOSURE:
{disclosure}
"""
