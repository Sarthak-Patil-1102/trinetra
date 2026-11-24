"""Helpers for the code-reading eye: walk a source tree, read files safely."""
import os

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".trinetra", "dist", "build", "uploads"}


def walk_code(root, exts=(".py",)):
    """Yield (path, text) for every source file under root, skipping junk dirs."""
    if not root or not os.path.isdir(root):
        return
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            if fn.endswith(exts):
                p = os.path.join(dp, fn)
                try:
                    with open(p, encoding="utf-8", errors="ignore") as fh:
                        yield p, fh.read()
                except OSError:
                    continue


def rel(root, p):
    try:
        return os.path.relpath(p, root)
    except ValueError:
        return p
