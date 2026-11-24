import re
from trinetra.core.sast import rel, walk_code

ID = "C29"
NAME = "World-writable file permissions"
SEVERITY = "MEDIUM"
CWE = "CWE-732"
EYE = "code"
FIX = "Never chmod 0o777 / 0o666. Grant the narrowest permissions the file actually needs (e.g. 0o600)."

PERM = re.compile(r'chmod\s*\([^)]*0o?7[0-7]7|chmod\s*\([^)]*0o?666|chmod\s+(-R\s+)?777')


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        for i, l in enumerate(t.splitlines(), 1):
            if PERM.search(l):
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "world-writable chmod at " + ", ".join(hits[:4])
    return False, "none found"
