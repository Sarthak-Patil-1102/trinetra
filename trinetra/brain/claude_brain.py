"""ClaudeBrain — drafts an astra with the Anthropic API (higher quality).

Real code; needs ANTHROPIC_API_KEY in the environment. For the 'big builder'
tier. In this sandbox (network off, no key) it can't run, but on a laptop it does.
"""
import json
import os
import urllib.request

from .base import Brain, DRAFT_PROMPT, extract_code


class ClaudeBrain(Brain):
    name = "claude"

    def __init__(self, model="claude-opus-4-8", key=None):
        self.model = model
        self.key = key or os.environ.get("ANTHROPIC_API_KEY", "")

    def draft_astra(self, entry) -> str:
        if not self.key:
            raise RuntimeError("set ANTHROPIC_API_KEY to use the claude brain")
        disclosure = entry.get("raw_text") or json.dumps(entry, indent=2)
        body = {
            "model": self.model,
            "max_tokens": 1500,
            "messages": [{"role": "user", "content": DRAFT_PROMPT.format(disclosure=disclosure)}],
        }
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(body).encode(),
            headers={
                "content-type": "application/json",
                "x-api-key": self.key,
                "anthropic-version": "2023-06-01",
            },
        )
        with urllib.request.urlopen(req, timeout=120) as r:  # noqa: S310
            data = json.loads(r.read())
        return extract_code(data["content"][0]["text"])
