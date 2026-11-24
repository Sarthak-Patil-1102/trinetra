import re

from trinetra.core.sast import rel, walk_code

ID = "C08"
NAME = "Unverified TLS / disabled certificate check"
SEVERITY = "HIGH"
CWE = "CWE-295"
EYE = "code"
FIX = "Never disable TLS verification; keep certificate validation on for all outbound HTTPS calls."

RX = re.compile(r'(verify\s*=\s*False|ssl\._create_unverified_context|CERT_NONE|check_hostname\s*=\s*False)')


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
        return True, "TLS verification disabled at " + ", ".join(hits[:4])
    return False, "none found"
