ID = "A11"
NAME = "Open redirect"
SEVERITY = "MEDIUM"
CWE = "CWE-601"
EYE = "attack"
FIX = "Only redirect to allow-listed internal paths; reject absolute/external URLs."


def run(ctx):
    evil = "http://evil.example.com/phish"
    try:
        r = ctx.session().get(ctx.base_url + "/go", params={"url": evil}, allow_redirects=False)
    except Exception:
        return False, "no /go endpoint"
    loc = r.headers.get("Location", "")
    if r.status_code in (301, 302, 303, 307, 308) and evil in loc:
        return True, f"GET /go?url={evil} → {r.status_code} Location: {loc}"
    return False, "not vulnerable"
