"""Fingerprint a repo: detect its stack so Trinetra personalizes what it runs."""
import os
import re

from .sast import walk_code

# Python frameworks are detected by a real import statement (high precision),
# not a bare word anywhere in the code.
PY_IMPORT_RE = {
    fw: re.compile(rf"^\s*(?:import|from)\s+{fw}\b", re.M)
    for fw in ("flask", "fastapi", "django", "streamlit")
}
# JS frameworks are detected only from declared dependencies (package.json).
JS_DEP_FRAMEWORKS = ("express", "next")
WEB_FRAMEWORKS = ("flask", "fastapi", "django", "express", "next")
REQ_FILES = ("requirements.txt", "pyproject.toml", "Pipfile", "pip modules.txt", "package.json")


def _read_deps(root):
    deps = set()
    for name in REQ_FILES:
        p = os.path.join(root, name)
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    tok = re.split(r"[=<>~!\[\]\" :,]", line.strip())[0].lower().lstrip('"')
                    if tok and not tok.startswith("#"):
                        deps.add(tok)
        except OSError:
            continue
    return deps


def fingerprint(root):
    deps = _read_deps(root)
    found = set()
    # JS frameworks: dependency declaration only
    for fw in JS_DEP_FRAMEWORKS:
        if fw in deps:
            found.add(fw)
    # Python frameworks: dep OR a real import statement
    found |= {fw for fw in PY_IMPORT_RE if fw in deps}
    langs = set()
    for p, t in walk_code(root, exts=(".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css")):
        langs.add(os.path.splitext(p)[1])
        if p.endswith(".py"):
            for fw, rx in PY_IMPORT_RE.items():
                if fw not in found and rx.search(t):
                    found.add(fw)
    frameworks = sorted(found)
    web_app = any(f in frameworks for f in WEB_FRAMEWORKS)
    stack = frameworks + (["jinja2"] if "flask" in frameworks else [])
    return {
        "frameworks": frameworks,
        "web_app": web_app,
        "stack": stack or ["python"],
        "languages": sorted(langs),
        "dep_count": len(deps),
    }
