import uuid

ID = "A04"
NAME = "Mass assignment (privilege escalation)"
SEVERITY = "HIGH"
CWE = "CWE-915"
EYE = "attack"
FIX = "Never accept privileged fields (role, is_admin) from client input; set them server-side from a fixed default."


def run(ctx):
    u = "t_" + uuid.uuid4().hex[:6]
    r = ctx.session().post(ctx.base_url + "/signup", data={"username": u, "password": "x", "role": "admin"})
    try:
        j = r.json()
    except Exception:
        return False, "no JSON response"
    if j.get("role") == "admin":
        return True, f"POST /signup role=admin → account '{u}' created with admin privileges"
    return False, "not vulnerable"
