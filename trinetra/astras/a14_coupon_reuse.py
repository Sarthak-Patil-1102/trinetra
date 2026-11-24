ID = "A14"
NAME = "Coupon reuse (no single-use)"
SEVERITY = "MEDIUM"
CWE = "CWE-837"
EYE = "attack"
FIX = "Enforce single-use per coupon/user server-side; record redemptions and reject repeats."


def run(ctx):
    s = ctx.session()
    try:
        r1 = s.post(ctx.base_url + "/redeem", data={"code": "SAVE50"})
        r2 = s.post(ctx.base_url + "/redeem", data={"code": "SAVE50"})
        if r1.json().get("ok") and r2.json().get("ok"):
            return True, "redeemed coupon SAVE50 twice in a row — no single-use enforcement"
    except Exception:
        return False, "no usable /redeem endpoint"
    return False, "not vulnerable"
