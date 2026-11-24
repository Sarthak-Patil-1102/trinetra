import re
from trinetra.core.sast import rel, walk_code

ID = "C27"
NAME = "Security check done with assert"
SEVERITY = "MEDIUM"
CWE = "CWE-617"
EYE = "code"
FIX = "Never enforce auth/permissions with assert — Python strips asserts under -O. Use an explicit if/raise."

ASRT = re.compile(r'^\s*assert\b', )
CTX = re.compile(r'(is_admin|is_authenticated|permission|role|authori[sz]|owner|allowed|logged_in|current_user)', re.I)


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        for i, l in enumerate(t.splitlines(), 1):
            if ASRT.search(l) and CTX.search(l):
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "assert used as a security gate at " + ", ".join(hits[:4])
    return False, "none found"
