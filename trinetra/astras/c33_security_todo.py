import re
from trinetra.core.sast import rel, walk_code

ID = "C33"
NAME = "Unfinished security code (TODO/FIXME)"
SEVERITY = "LOW"
CWE = "CWE-546"
EYE = "code"
FIX = "Resolve security TODO/FIXME/HACK notes before shipping — they mark gaps an attacker will find first."

MARK = re.compile(r'#.*\b(TODO|FIXME|HACK|XXX)\b', re.I)
SEC = re.compile(r'(auth|secur|insecure|sanitiz|validat|permission|escap|encrypt|vuln|password|token|csrf|inject)', re.I)


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        for i, l in enumerate(t.splitlines(), 1):
            if MARK.search(l) and SEC.search(l):
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "unfinished security note at " + ", ".join(hits[:4])
    return False, "none found"
