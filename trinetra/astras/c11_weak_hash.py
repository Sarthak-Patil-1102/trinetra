import re

from trinetra.core.sast import rel, walk_code

ID = "C11"
NAME = "Weak password hashing (MD5/SHA1)"
SEVERITY = "HIGH"
CWE = "CWE-916"
EYE = "code"
FIX = "Hash passwords with a slow, salted algorithm (bcrypt, scrypt, or argon2) — never MD5/SHA1."

RX = re.compile(r'hashlib\.(md5|sha1)\s*\(')
CTX = re.compile(r'(pass|pwd|secret|token|cred)', re.I)


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        lines = t.splitlines()
        for i, l in enumerate(lines, 1):
            if RX.search(l):
                window = " ".join(lines[max(0, i - 3):i + 2])
                if CTX.search(window) or CTX.search(l):
                    hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "weak hash used for a credential at " + ", ".join(hits[:4])
    return False, "none found"
