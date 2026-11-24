import re

from trinetra.core.sast import rel, walk_code

ID = "C22"
NAME = "Sensitive data in logs"
SEVERITY = "MEDIUM"
CWE = "CWE-532"
EYE = "code"
FIX = "Never log passwords, tokens, or keys; redact sensitive fields before logging."

LOGCALL = re.compile(r'(logger?\.|logging\.)(info|debug|warning|error|exception|critical)\s*\(')
SENS = re.compile(r'(password|passwd|secret|token|api[_-]?key|credit|cvv)', re.I)


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        for i, l in enumerate(t.splitlines(), 1):
            if LOGCALL.search(l) and SENS.search(l):
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "sensitive value logged at " + ", ".join(hits[:4])
    return False, "none found"
