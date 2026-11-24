import re

from trinetra.core.sast import rel, walk_code

ID = "C13"
NAME = "Private key committed to repo"
SEVERITY = "CRITICAL"
CWE = "CWE-312"
EYE = "code"
FIX = "Never commit private keys. Remove it, rotate the key, and keep key material out of the repo entirely."

RX = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----')


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    for p, t in walk_code(ctx.source_root, exts=(".py", ".pem", ".key", ".txt", ".env", ".json", ".yaml", ".yml")):
        if RX.search(t):
            return True, f"private key material found in {rel(ctx.source_root, p)}"
    return False, "none found"
