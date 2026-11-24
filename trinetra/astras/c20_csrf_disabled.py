import re

from trinetra.core.sast import rel, walk_code

ID = "C20"
NAME = "CSRF protection disabled"
SEVERITY = "HIGH"
CWE = "CWE-352"
EYE = "code"
FIX = "Keep CSRF protection on for all state-changing routes; don't globally disable it or blanket-exempt views."

RX = re.compile(r'(WTF_CSRF_ENABLED\s*=\s*False|csrf_exempt|@csrf\.exempt|CSRF_ENABLED\s*=\s*False|csrf_protect\s*=\s*False)')


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
        return True, "CSRF disabled/exempt at " + ", ".join(hits[:4])
    return False, "none found"
