import re

from trinetra.core.sast import rel, walk_code

ID = "C16"
NAME = "Path traversal in file handling"
SEVERITY = "HIGH"
CWE = "CWE-22"
EYE = "code"
FIX = "Never build a filesystem path from request data; resolve and confirm it stays inside an allow-listed directory."

RX = re.compile(r'(open\s*\(\s*request\.|send_file\s*\(\s*request\.|send_from_directory\s*\([^)]*request\.|os\.path\.join\([^)]*request\.)')


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = [
        f"{rel(ctx.source_root, p)}:{i}"
        for p, t in walk_code(ctx.source_root)
        for i, l in enumerate(t.splitlines(), 1)
        if RX.search(l)
    ]
    if hits:
        return True, "request data used in a file path at " + ", ".join(hits[:4])
    return False, "none found"
