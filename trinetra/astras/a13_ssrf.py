ID = "A13"
NAME = "Server-Side Request Forgery (SSRF)"
SEVERITY = "HIGH"
CWE = "CWE-918"
EYE = "attack"
FIX = "Do not fetch user-supplied URLs; if you must, allow-list hosts and block internal/metadata addresses."


def run(ctx):
    internal = ctx.base_url + "/admin"
    try:
        r = ctx.session().get(ctx.base_url + "/fetch", params={"url": internal})
    except Exception:
        return False, "no /fetch endpoint"
    if r.status_code == 200 and "api_key" in r.text:
        return True, f"/fetch?url={internal} made the server pull an internal resource (api keys leaked)"
    return False, "not vulnerable"
