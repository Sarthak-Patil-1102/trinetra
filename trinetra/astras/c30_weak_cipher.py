import re
from trinetra.core.sast import rel, walk_code

ID = "C30"
NAME = "Weak cipher / ECB mode"
SEVERITY = "HIGH"
CWE = "CWE-327"
EYE = "code"
FIX = "Use AES-GCM (or ChaCha20-Poly1305) with a random nonce. Never DES/3DES/RC4/ARC4 or ECB mode."

WEAK = re.compile(r'\b(DES|TripleDES|ARC4|RC4|Blowfish)\.new\b|MODE_ECB\b|\bDES3\.new\b')


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        for i, l in enumerate(t.splitlines(), 1):
            if WEAK.search(l):
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "weak cipher/mode at " + ", ".join(hits[:4])
    return False, "none found"
