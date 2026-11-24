import re

from trinetra.core.sast import rel, walk_code

ID = "C15"
NAME = "Template injection risk (render_template_string)"
SEVERITY = "HIGH"
CWE = "CWE-1336"
EYE = "code"
FIX = "Never pass user input to render_template_string; render a fixed template and pass the input as data."

# render_template_string( not immediately followed by a plain quoted literal
RX = re.compile(r'render_template_string\s*\(\s*(?![\'"])')


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
        return True, "render_template_string on a non-literal at " + ", ".join(hits[:4])
    return False, "none found"
