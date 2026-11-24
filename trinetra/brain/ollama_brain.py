"""OllamaBrain — drafts an astra with a local model (private, free).

Real code; it just needs a running Ollama on the user's machine. In this
sandbox (network off) we use TemplateBrain instead, but this is the path a
'big builder' would wire to Claude/Fable and a vibecoder to a local model.
"""
import json
import urllib.request

from .base import Brain

PROMPT = """You are Trinetra's security-astra writer. Turn the vulnerability
disclosure below into a Python astra plugin. Output ONLY the code.

An astra defines: ID, NAME, SEVERITY, CWE, EYE="attack", FIX, and a
run(ctx) function that uses ctx.session() (a requests.Session) and
ctx.base_url to probe the target, returning (True, evidence) if the exploit
lands or (False, reason) otherwise.

DISCLOSURE:
{disclosure}
"""


class OllamaBrain(Brain):
    name = "ollama"

    def __init__(self, model="qwen2.5-coder:7b", host="http://localhost:11434"):
        self.model = model
        self.host = host

    def draft_astra(self, entry) -> str:
        disclosure = entry.get("raw_text") or json.dumps(entry, indent=2)
        payload = {"model": self.model, "prompt": PROMPT.format(disclosure=disclosure), "stream": False}
        req = urllib.request.Request(
            self.host + "/api/generate",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=180) as r:  # noqa: S310 (local only)
            return json.loads(r.read())["response"]
