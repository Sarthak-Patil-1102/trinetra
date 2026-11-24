import re

from trinetra.core.sast import rel, walk_code

ID = "C10"
NAME = "Silent exception swallowing"
SEVERITY = "LOW"
CWE = "CWE-703"
EYE = "code"
FIX = "Don't swallow errors with bare `except: pass`; catch specific exceptions and log them so failures are visible."

EXCEPT_LINE = re.compile(r'^\s*except\b.*:\s*$')
EXCEPT_INLINE_PASS = re.compile(r'^\s*except\b.*:\s*pass\s*$')


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        lines = t.splitlines()
        for i, l in enumerate(lines):
            if EXCEPT_INLINE_PASS.match(l):
                hits.append(f"{rel(ctx.source_root, p)}:{i + 1}")
            elif EXCEPT_LINE.match(l):
                nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
                if nxt == "pass":
                    hits.append(f"{rel(ctx.source_root, p)}:{i + 1}")
    if hits:
        return True, "silent except: pass at " + ", ".join(hits[:4])
    return False, "none found"
