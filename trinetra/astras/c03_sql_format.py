import re

from trinetra.core.sast import rel, walk_code

ID = "C03"
NAME = "SQL built from string formatting"
SEVERITY = "HIGH"
CWE = "CWE-89"
EYE = "code"
FIX = "Use parameterized queries; pass values as params to execute(), never format them into the SQL string."

SQLWORD = re.compile(r'\b(select|insert|update|delete)\b', re.I)
FMT = re.compile(r'(%\s*[\(sdr]|\.format\(|f["\'])')


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        for i, l in enumerate(t.splitlines(), 1):
            if SQLWORD.search(l) and FMT.search(l) and ('"' in l or "'" in l):
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "query built by formatting at " + ", ".join(hits[:4])
    return False, "none found"
