import re
from trinetra.core.sast import rel, walk_code

ID = "C25"
NAME = "JWT signature not verified / 'none' algorithm"
SEVERITY = "HIGH"
CWE = "CWE-347"
EYE = "code"
FIX = "Always verify JWT signatures with a strong algorithm (RS256/HS256) and a real key; never use alg 'none' or verify=False."

ALGNONE = re.compile(r'alg(orithm)?s?\s*=\s*\[?\s*[\'"]none[\'"]', re.I)
NOVERIFY = re.compile(r'(verify\s*=\s*False|verify_signature[\'"]?\s*:\s*False)', re.I)
JWT = re.compile(r'\bjwt\b|decode\(|encode\(', re.I)


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        for i, l in enumerate(t.splitlines(), 1):
            if ALGNONE.search(l) or (NOVERIFY.search(l) and JWT.search(l)):
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "unverified/weak JWT at " + ", ".join(hits[:4])
    return False, "none found"
