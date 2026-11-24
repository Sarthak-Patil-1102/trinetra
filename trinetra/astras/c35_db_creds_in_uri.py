import re
from trinetra.core.sast import rel, walk_code

ID = "C35"
NAME = "Database password embedded in connection string"
SEVERITY = "HIGH"
CWE = "CWE-798"
EYE = "code"
FIX = "Load DB credentials from env vars / a secrets manager; never hardcode user:password@host in a connection URI."

URI = re.compile(r'(postgres(ql)?|mysql|mariadb|mongodb(\+srv)?|redis|amqp)://[^\s:/\'"]+:[^\s@\'"]+@', re.I)


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    hits = []
    for p, t in walk_code(ctx.source_root):
        for i, l in enumerate(t.splitlines(), 1):
            if URI.search(l):
                hits.append(f"{rel(ctx.source_root, p)}:{i}")
    if hits:
        return True, "credentials in DB connection string at " + ", ".join(hits[:4])
    return False, "none found"
