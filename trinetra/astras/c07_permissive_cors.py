from trinetra.core.sast import rel, walk_code

ID = "C07"
NAME = "Permissive CORS in source"
SEVERITY = "MEDIUM"
CWE = "CWE-942"
EYE = "code"
FIX = "Allow-list specific origins; never reflect the request origin or allow '*' together with credentials."


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        for i, l in enumerate(t.splitlines(), 1):
            if ("Access-Control-Allow-Origin" in l and ('"*"' in l or "'*'" in l)) or "CORS(app" in l:
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "wildcard/permissive CORS at " + ", ".join(hits[:4])
    return False, "none found"
