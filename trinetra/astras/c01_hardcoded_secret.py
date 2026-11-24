import re

from trinetra.core.sast import rel, walk_code

ID = "C01"
NAME = "Hardcoded secret in source"
SEVERITY = "HIGH"
CWE = "CWE-798"
EYE = "code"
FIX = "Move secrets to environment variables or a secrets manager; never commit them to source."

PATTERNS = [
    (re.compile(r'(secret_key|SECRET_KEY)\s*=\s*["\'][^"\']{6,}'), "hardcoded secret_key"),
    (re.compile(r'sk_live_[A-Za-z0-9]{6,}'), "Stripe-style live key"),
    (re.compile(r'AKIA[0-9A-Z]{12,}'), "AWS access key id"),
    (re.compile(r'(api_key|API_KEY|aws_secret|token|password)\s*=\s*["\'][^"\']{6,}["\']'), "hardcoded credential"),
]


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = set()
    for path, text in walk_code(ctx.source_root):
        for ln, line in enumerate(text.splitlines(), 1):
            for rx, label in PATTERNS:
                if rx.search(line):
                    hits.add(f"{rel(ctx.source_root, path)}:{ln} ({label})")
    if hits:
        hits = sorted(hits)
        extra = f" (+{len(hits) - 4} more)" if len(hits) > 4 else ""
        return True, "; ".join(hits[:4]) + extra
    return False, "none found"
