import re

from trinetra.core.sast import rel, walk_code

ID = "C12"
NAME = "Hardcoded cloud / API token"
SEVERITY = "CRITICAL"
CWE = "CWE-798"
EYE = "code"
FIX = "Move provider tokens to environment variables or a secrets manager; rotate any that were committed."

PATS = [
    (re.compile(r'ghp_[A-Za-z0-9]{20,}'), "GitHub token"),
    (re.compile(r'gho_[A-Za-z0-9]{20,}'), "GitHub OAuth token"),
    (re.compile(r'xox[baprs]-[A-Za-z0-9-]{10,}'), "Slack token"),
    (re.compile(r'AIza[0-9A-Za-z\-_]{30,}'), "Google API key"),
    (re.compile(r'SG\.[A-Za-z0-9_\-.]{20,}'), "SendGrid key"),
    (re.compile(r'glpat-[A-Za-z0-9_\-]{18,}'), "GitLab token"),
    (re.compile(r'sk-[A-Za-z0-9]{32,}'), "OpenAI-style key"),
]


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root, exts=(".py", ".js", ".ts", ".json", ".env", ".yaml", ".yml", ".txt")):
        for i, l in enumerate(t.splitlines(), 1):
            for rx, label in PATS:
                if rx.search(l):
                    hits.append(f"{rel(ctx.source_root, p)}:{i} ({label})")
    if hits:
        return True, "; ".join(sorted(set(hits))[:4])
    return False, "none found"
