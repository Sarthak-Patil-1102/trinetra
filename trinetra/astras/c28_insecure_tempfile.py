import re
from trinetra.core.sast import rel, walk_code

ID = "C28"
NAME = "Insecure temp file (predictable name)"
SEVERITY = "MEDIUM"
CWE = "CWE-377"
EYE = "code"
FIX = "Use tempfile.NamedTemporaryFile/mkstemp (atomic, unpredictable); never tempfile.mktemp or a hardcoded /tmp path."

MKTEMP = re.compile(r'tempfile\.mktemp\s*\(')
HARDTMP = re.compile(r'open\s*\(\s*[\'"]/tmp/[^\'"]+[\'"]')


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        for i, l in enumerate(t.splitlines(), 1):
            if MKTEMP.search(l) or HARDTMP.search(l):
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "predictable temp file at " + ", ".join(hits[:4])
    return False, "none found"
