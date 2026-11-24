"""TemplateBrain — the offline, no-LLM fallback brain.

Deterministic: it fills an astra template from a *structured* feed entry. With a
real LLM brain (Ollama/Claude) the entry would be freeform disclosure text and
the model would write the astra itself. This one needs the probe spelled out,
which is the honest limit of running with no model.
"""
from .base import Brain

ASTRA_TPL = '''# AUTO-DRAFTED by Trinetra third eye (brain={brain}) from feed entry {feed_id}.
# Technique: {title}
# REVIEW before approving — generated code, not yet trusted.
ID = {aid!r}
NAME = {name!r}
SEVERITY = {severity!r}
CWE = {cwe!r}
EYE = "attack"
FIX = {fix!r}

_ENDPOINTS = {endpoints!r}
_PARAM = {param!r}
_PAYLOAD = {payload!r}
_EXPECT = {expect!r}


def run(ctx):
    s = ctx.session()
    for ep in _ENDPOINTS:
        try:
            r = s.get(ctx.base_url + ep, params={{_PARAM: _PAYLOAD}})
        except Exception:
            continue
        if _EXPECT in r.text:
            return True, f"GET {{ep}}?{{_PARAM}}={{_PAYLOAD}} -> response contained {{_EXPECT!r}} (payload executed)"
    return False, "not vulnerable"
'''


class TemplateBrain(Brain):
    name = "template"

    def draft_astra(self, entry) -> str:
        a = entry["astra"]
        return ASTRA_TPL.format(
            brain=self.name, feed_id=entry["id"], title=entry["title"],
            aid=a["id"], name=a["name"], severity=entry.get("severity", "HIGH"),
            cwe=entry.get("cwe", "CWE-000"), fix=a["fix"], endpoints=a["endpoints"],
            param=a["param"], payload=a["payload"], expect=a["expect_contains"],
        )
