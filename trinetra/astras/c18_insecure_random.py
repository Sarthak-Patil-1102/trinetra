import re

from trinetra.core.sast import rel, walk_code

ID = "C18"
NAME = "Insecure randomness for secrets"
SEVERITY = "MEDIUM"
CWE = "CWE-330"
EYE = "code"
FIX = "Use the `secrets` module (or os.urandom) for tokens, passwords, OTPs and keys — never `random`."

RAND = re.compile(r'\brandom\.(random|randint|choice|randrange|getrandbits|sample|shuffle)\b')
CTX = re.compile(r'(token|secret|password|otp|nonce|session|api[_-]?key|reset|salt)', re.I)


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        for i, l in enumerate(t.splitlines(), 1):
            if RAND.search(l) and CTX.search(l):
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "weak randomness for a secret at " + ", ".join(hits[:4])
    return False, "none found"
