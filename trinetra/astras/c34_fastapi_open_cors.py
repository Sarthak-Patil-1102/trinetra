import re
from trinetra.core.sast import rel, walk_code

ID = "C34"
NAME = "FastAPI/Starlette open CORS middleware"
SEVERITY = "HIGH"
CWE = "CWE-942"
EYE = "code"
FIX = "Set allow_origins to an explicit list; a wildcard with allow_credentials=True lets any site act as the user."

MW = re.compile(r'CORSMiddleware')
WILD = re.compile(r'allow_origins\s*=\s*\[[^\]]*[\'"]\*[\'"]')


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        if not MW.search(t):
            continue
        lines = t.splitlines()
        for i, l in enumerate(lines, 1):
            if WILD.search(l):
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "wildcard CORS origins at " + ", ".join(hits[:4])
    return False, "none found"
