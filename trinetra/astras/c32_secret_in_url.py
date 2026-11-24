import re
from trinetra.core.sast import rel, walk_code

ID = "C32"
NAME = "Secret passed in URL query string"
SEVERITY = "MEDIUM"
CWE = "CWE-598"
EYE = "code"
FIX = "Never put passwords/tokens/keys in a URL — they leak into logs, history and referrers. Use headers or a POST body."

Q = re.compile(r'[?&](password|passwd|pwd|token|api[_-]?key|access[_-]?token|secret)=', re.I)


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        for i, l in enumerate(t.splitlines(), 1):
            if Q.search(l):
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "secret in query string at " + ", ".join(hits[:4])
    return False, "none found"
