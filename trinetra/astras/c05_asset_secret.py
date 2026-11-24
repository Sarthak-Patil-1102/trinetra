import os
import re

from trinetra.core.sast import rel, walk_code

ID = "C05"
NAME = "Secret in web asset / .env"
SEVERITY = "HIGH"
CWE = "CWE-798"
EYE = "code"
FIX = "Keep secrets server-side in env vars; never ship keys in JS bundles, .env, or committed config."

PATS = [
    re.compile(r'sk_live_[A-Za-z0-9]{6,}'),
    re.compile(r'AKIA[0-9A-Z]{12,}'),
    re.compile(r'(api[_-]?key|secret|token)\s*[:=]\s*["\'][^"\']{8,}', re.I),
]
ASSET_EXTS = (".js", ".ts", ".json", ".env", ".yaml", ".yml", ".html", ".txt")


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = set()
    for p, t in walk_code(ctx.source_root, exts=ASSET_EXTS):
        for ln, line in enumerate(t.splitlines(), 1):
            for rx in PATS:
                if rx.search(line):
                    hits.add(f"{rel(ctx.source_root, p)}:{ln}")
    if os.path.exists(os.path.join(ctx.source_root, ".env")):
        hits.add(".env committed to the repo")
    if hits:
        hits = sorted(hits)
        extra = f" (+{len(hits) - 4} more)" if len(hits) > 4 else ""
        return True, "; ".join(hits[:4]) + extra
    return False, "none found"
