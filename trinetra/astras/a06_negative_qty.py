ID = "A06"
NAME = "Negative quantity (credit abuse)"
SEVERITY = "MEDIUM"
CWE = "CWE-20"
EYE = "attack"
FIX = "Validate that quantity is a positive integer server-side before computing any total."


def run(ctx):
    r = ctx.session().post(ctx.base_url + "/checkout", data={"price": "500", "qty": "-3"})
    try:
        j = r.json()
    except Exception:
        return False, "no JSON response"
    total = j.get("total")
    if isinstance(total, (int, float)) and total < 0:
        return True, f"POST /checkout qty=-3 → total={total} (negative, i.e. a credit)"
    return False, "not vulnerable"
