ID = "A17"
NAME = "Verbose error / stack-trace disclosure"
SEVERITY = "MEDIUM"
CWE = "CWE-209"
EYE = "attack"
FIX = "Disable debug in production; return a generic error page; log stack traces server-side only."


def run(ctx):
    try:
        r = ctx.session().get(ctx.base_url + "/crash", params={"n": "0"})
    except Exception:
        return False, "no /crash endpoint"
    if "Traceback (most recent call last)" in r.text or "ZeroDivisionError" in r.text:
        return True, "GET /crash?n=0 leaked a full Python traceback to the client"
    return False, "not vulnerable"
