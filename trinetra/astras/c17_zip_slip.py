import re

from trinetra.core.sast import rel, walk_code

ID = "C17"
NAME = "Unsafe archive extraction (zip slip)"
SEVERITY = "MEDIUM"
CWE = "CWE-22"
EYE = "code"
FIX = "Don't call extractall on untrusted archives; validate each member path stays inside the target directory."

RX = re.compile(r'\.extractall\s*\(')


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
        return True, "archive extractall at " + ", ".join(hits[:4])
    return False, "none found"
