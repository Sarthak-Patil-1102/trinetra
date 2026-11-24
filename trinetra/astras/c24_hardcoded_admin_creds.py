import re
from trinetra.core.sast import rel, walk_code

ID = "C24"
NAME = "Hardcoded admin credentials in logic"
SEVERITY = "HIGH"
CWE = "CWE-798"
EYE = "code"
FIX = "Never compare against literal credentials in code. Check a salted hash from your user store instead."

# e.g.  if username == "admin" and password == "admin123":
CRED = re.compile(r'(user(name)?|login|pass(word|wd)?|pwd|secret)\s*==\s*[\'"][^\'"]{2,}[\'"]', re.I)
GATE = re.compile(r'(admin|root|superuser|==\s*[\'"]admin)', re.I)


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        for i, l in enumerate(t.splitlines(), 1):
            if CRED.search(l) and GATE.search(l):
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "credential compared against a literal at " + ", ".join(hits[:4])
    return False, "none found"
