import re
from trinetra.core.sast import rel, walk_code

ID = "C26"
NAME = "CORS allows credentials with wildcard origin"
SEVERITY = "HIGH"
CWE = "CWE-942"
EYE = "code"
FIX = "Never combine a wildcard origin with credentials. Echo an allow-list of exact origins when credentials are allowed."

WILD = re.compile(r'Allow-Origin[\'"]?\s*[:,]\s*[\'"]\*[\'"]|origins\s*=\s*[\'"]\*[\'"]', re.I)
CREDS = re.compile(r'Allow-Credentials[\'"]?\s*[:,]\s*[\'"]?true|supports_credentials\s*=\s*True', re.I)


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        lines = t.splitlines()
        for i, l in enumerate(lines):
            window = "\n".join(lines[max(0, i - 3):i + 4])
            if WILD.search(l) and CREDS.search(window):
                hits.append(f"{rel(ctx.source_root, p)}:{i+1}")
    if hits:
        return True, "wildcard origin + credentials at " + ", ".join(hits[:4])
    return False, "none found"
