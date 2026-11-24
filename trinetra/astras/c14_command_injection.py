import re

from trinetra.core.sast import rel, walk_code

ID = "C14"
NAME = "OS command execution"
SEVERITY = "HIGH"
CWE = "CWE-78"
EYE = "code"
FIX = "Avoid os.system / shell=True; use subprocess with an argument list and never pass user input to a shell."

RX = re.compile(r'(os\.system\s*\(|os\.popen\s*\(|subprocess\.[A-Za-z_]+\([^)]*shell\s*=\s*True|commands\.getoutput)')


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
        return True, "shell/command execution at " + ", ".join(hits[:4])
    return False, "none found"
