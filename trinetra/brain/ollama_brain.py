"""OllamaBrain — drafts an astra with a local model (private, free).

Real code; it needs a running Ollama on the user's machine:
    ollama pull qwen2.5-coder:7b   # one time
    ollama serve                   # usually already running
In this sandbox (network off, no Ollama) it can't run, but on a laptop it does.
"""
import json
import urllib.request

from .base import Brain, DRAFT_PROMPT, extract_code


class OllamaBrain(Brain):
    name = "ollama"

    def __init__(self, model="qwen2.5-coder:7b", host="http://localhost:11434"):
        self.model = model
        self.host = host

    def draft_astra(self, entry) -> str:
        disclosure = entry.get("raw_text") or json.dumps(entry, indent=2)
        payload = {
            "model": self.model,
            "prompt": DRAFT_PROMPT.format(disclosure=disclosure),
            "stream": False,
        }
        req = urllib.request.Request(
            self.host + "/api/generate",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=180) as r:  # noqa: S310 (local only)
            return extract_code(json.loads(r.read())["response"])
