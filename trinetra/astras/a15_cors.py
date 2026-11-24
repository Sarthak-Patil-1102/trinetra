ID = "A15"
NAME = "CORS misconfiguration"
SEVERITY = "HIGH"
CWE = "CWE-942"
EYE = "attack"
FIX = "Never use Access-Control-Allow-Origin: * together with Allow-Credentials: true. Allow-list specific origins."


def run(ctx):
    try:
        r = ctx.session().get(ctx.base_url + "/search", params={"q": "x"})
    except Exception:
        return False, "target unreachable"
    acao = r.headers.get("Access-Control-Allow-Origin", "")
    acac = r.headers.get("Access-Control-Allow-Credentials", "").lower()
    if acao == "*" and acac == "true":
        return True, "Access-Control-Allow-Origin: * with Allow-Credentials: true — any site can read authenticated responses"
    return False, "not vulnerable"
