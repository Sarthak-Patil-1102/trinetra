import re

from trinetra.core.sast import rel, walk_code

ID = "C02"
NAME = "Debug mode enabled"
SEVERITY = "HIGH"
CWE = "CWE-489"
EYE = "code"
FIX = "Never run with debug=True in production — it exposes an interactive console (RCE). Gate it behind an env var."

RX = re.compile(r'debug\s*=\s*True')


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = [
        f"{rel(ctx.source_root, p)}:{i}"
        for p, t in walk_code(ctx.source_root)
        for i, l in enumerate(t.splitlines(), 1)
        if RX.search(l)
    ]
    if hits:
        return True, "debug=True at " + ", ".join(hits[:4])
    return False, "none found"
