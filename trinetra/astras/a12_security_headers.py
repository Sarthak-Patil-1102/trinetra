ID = "A12"
NAME = "Missing security headers"
SEVERITY = "LOW"
CWE = "CWE-693"
EYE = "attack"
FIX = "Set X-Frame-Options, Content-Security-Policy, X-Content-Type-Options, and HSTS on responses."

WANT = ["X-Frame-Options", "Content-Security-Policy", "X-Content-Type-Options"]


def run(ctx):
    try:
        r = ctx.session().get(ctx.base_url + "/search", params={"q": "x"})
    except Exception:
        return False, "target unreachable"
    missing = [h for h in WANT if h not in r.headers]
    if len(missing) >= 2:
        return True, "response is missing: " + ", ".join(missing)
    return False, "headers present"
