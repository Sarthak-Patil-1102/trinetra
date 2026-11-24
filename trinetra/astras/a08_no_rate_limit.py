ID = "A08"
NAME = "No rate limiting on login"
SEVERITY = "MEDIUM"
CWE = "CWE-307"
EYE = "attack"
FIX = "Throttle auth attempts (per-IP / account lockout or exponential backoff); return 429 when exceeded."


def run(ctx):
    s = ctx.session()
    codes = [
        s.post(ctx.base_url + "/login", data={"username": "x", "password": "y"}).status_code
        for _ in range(15)
    ]
    if all(c != 429 for c in codes):
        return True, f"15 rapid /login attempts, none throttled (no 429; statuses={sorted(set(codes))})"
    return False, "rate limited"
