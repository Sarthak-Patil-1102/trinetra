import re

from trinetra.core.sast import rel, walk_code

ID = "C21"
NAME = "XML parsing without XXE protection"
SEVERITY = "MEDIUM"
CWE = "CWE-611"
EYE = "code"
FIX = "Parse untrusted XML with defusedxml (or disable external entities); don't use the stdlib XML parsers directly."

PARSE = re.compile(r'(etree\.(parse|fromstring|XML)|minidom\.parse|xml\.sax\.|xmlrpc)')


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        if "defusedxml" in t:
            continue  # already using the safe parser
        for i, l in enumerate(t.splitlines(), 1):
            if PARSE.search(l):
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "unprotected XML parsing at " + ", ".join(hits[:4])
    return False, "none found"
