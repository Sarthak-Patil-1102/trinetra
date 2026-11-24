import re

from trinetra.core.sast import rel, walk_code

ID = "C19"
NAME = "Server binds to all network interfaces"
SEVERITY = "MEDIUM"
CWE = "CWE-1327"
EYE = "code"
FIX = "Bind to 127.0.0.1 in development; expose publicly only behind a reverse proxy with auth/TLS."

RX = re.compile(r'host\s*=\s*[\'"]0\.0\.0\.0[\'"]')


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
        return True, "binds host 0.0.0.0 at " + ", ".join(hits[:4])
    return False, "none found"
