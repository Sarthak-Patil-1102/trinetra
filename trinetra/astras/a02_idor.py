ID = "A02"
NAME = "IDOR (broken object-level access)"
SEVERITY = "HIGH"
CWE = "CWE-639"
EYE = "attack"
FIX = "Check ownership on every object fetch: verify the record's user_id matches the session user before returning it."


def run(ctx):
    s = ctx.session()
    s.post(ctx.base_url + "/login", data={"username": "alice", "password": "alicepass"})
    r = s.get(ctx.base_url + "/order/1002")
    if r.status_code == 200:
        try:
            j = r.json()
        except Exception:
            return False, "no JSON response"
        if j.get("user_id") and j.get("user_id") != 1:
            return True, f"as alice (id 1) fetched /order/1002 owned by user_id={j['user_id']}: {j.get('item')}"
    return False, "not vulnerable"
