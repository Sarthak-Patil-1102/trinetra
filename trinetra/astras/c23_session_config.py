import re

from trinetra.core.sast import rel, walk_code

ID = "C23"
NAME = "Insecure session/cookie config"
SEVERITY = "MEDIUM"
CWE = "CWE-614"
EYE = "code"
FIX = "Set SESSION_COOKIE_SECURE/HTTPONLY/SAMESITE to secure values and use a strong, non-default SECRET_KEY."

RX = re.compile(r'(SESSION_COOKIE_SECURE\s*=\s*False|SESSION_COOKIE_HTTPONLY\s*=\s*False|SECRET_KEY\s*=\s*[\'"](dev|secret|changeme|test|)[\'"])')


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
        return True, "insecure session/cookie config at " + ", ".join(hits[:4])
    return False, "none found"
