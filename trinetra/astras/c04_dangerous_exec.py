import re

from trinetra.core.sast import rel, walk_code

ID = "C04"
NAME = "Dangerous eval/exec/shell call"
SEVERITY = "HIGH"
CWE = "CWE-95"
EYE = "code"
FIX = "Avoid eval/exec/os.system on any input-derived data; use safe parsers and subprocess with an argument list (no shell=True)."

RX = re.compile(r'(\beval\s*\(|\bexec\s*\(|os\.system\s*\(|shell\s*=\s*True)')


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
        return True, "dangerous call at " + ", ".join(hits[:4])
    return False, "none found"
