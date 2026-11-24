import re
from trinetra.core.sast import rel, walk_code

ID = "C31"
NAME = "Credentials sent over cleartext HTTP"
SEVERITY = "MEDIUM"
CWE = "CWE-319"
EYE = "code"
FIX = "Call auth/token/payment endpoints over https:// only — http:// exposes credentials and tokens on the wire."

URL = re.compile(r'[\'"]http://[^\'"]*(login|auth|token|oauth|signin|account|pay|api)[^\'"]*[\'"]', re.I)


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        for i, l in enumerate(t.splitlines(), 1):
            if URL.search(l):
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "sensitive endpoint over http:// at " + ", ".join(hits[:4])
    return False, "none found"
