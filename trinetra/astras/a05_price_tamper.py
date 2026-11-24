ID = "A05"
NAME = "Price tampering"
SEVERITY = "HIGH"
CWE = "CWE-602"
EYE = "attack"
FIX = "Never trust a client-sent price. Look up the price server-side by product id at checkout."


def run(ctx):
    r = ctx.session().post(ctx.base_url + "/checkout", data={"price": "1", "qty": "1"})
    try:
        j = r.json()
    except Exception:
        return False, "no JSON response"
    if j.get("total") == 1.0:
        return True, "POST /checkout price=1 accepted → total=1 for a priced item"
    return False, "not vulnerable"
