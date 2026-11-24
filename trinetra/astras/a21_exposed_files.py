ID = "A21"
NAME = "Exposed sensitive file over HTTP"
SEVERITY = "HIGH"
CWE = "CWE-538"
EYE = "attack"
FIX = "Never serve .env, .git, or config files; block dotfiles at the web server and keep secrets out of the web root."

PATHS = ["/.env", "/.git/config", "/config.json", "/.env.local", "/settings.py"]
MARKERS = ("SECRET", "KEY=", "PASSWORD", "[core]", "token")


def run(ctx):
    s = ctx.session()
    for path in PATHS:
        try:
            r = s.get(ctx.base_url + path)
        except Exception:
            continue
        if r.status_code == 200 and any(m in r.text for m in MARKERS):
            return True, f"GET {path} returned sensitive config over HTTP ({r.text[:50].strip()}…)"
    return False, "not vulnerable"
