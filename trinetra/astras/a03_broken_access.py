ID = "A03"
NAME = "Broken access control (admin panel)"
SEVERITY = "CRITICAL"
CWE = "CWE-284"
EYE = "attack"
FIX = "Require authentication + an admin-role check on every admin route (e.g. an @admin_required decorator)."


def run(ctx):
    r = ctx.session().get(ctx.base_url + "/admin")
    if r.status_code == 200 and "api_key" in r.text:
        return True, "anonymous GET /admin returned the admin panel including user api keys"
    return False, "not vulnerable"
