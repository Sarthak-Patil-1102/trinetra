ID = "A20"
NAME = "Insecure session cookie (missing flags)"
SEVERITY = "MEDIUM"
CWE = "CWE-614"
EYE = "attack"
FIX = "Set Secure, HttpOnly and SameSite on session cookies so they can't be stolen over HTTP or via JS."


def run(ctx):
    try:
        r = ctx.session().post(ctx.base_url + "/login", data={"username": "alice", "password": "alicepass"})
    except Exception:
        return False, "target unreachable"
    sc = r.headers.get("Set-Cookie", "")
    if "session" not in sc.lower():
        return False, "no session cookie set"
    missing = [f for f in ("Secure", "HttpOnly", "SameSite") if f.lower() not in sc.lower()]
    if missing:
        return True, f"session cookie is missing: {', '.join(missing)}  (Set-Cookie: {sc[:60]}…)"
    return False, "cookie flags present"
