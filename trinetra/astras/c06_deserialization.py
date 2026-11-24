import re

from trinetra.core.sast import rel, walk_code

ID = "C06"
NAME = "Insecure deserialization"
SEVERITY = "HIGH"
CWE = "CWE-502"
EYE = "code"
FIX = "Never unpickle or yaml.load untrusted data. Use json, or yaml.safe_load, and validate the result."

RX = re.compile(r'(pickle\.loads|pickle\.load|cPickle\.loads|yaml\.load\s*\()')


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        for i, l in enumerate(t.splitlines(), 1):
            if RX.search(l) and "SafeLoader" not in l:
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "unsafe deserialization at " + ", ".join(hits[:4])
    return False, "none found"
