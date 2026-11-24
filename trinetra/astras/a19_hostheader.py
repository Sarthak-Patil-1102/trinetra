# DRAFTED by Trinetra third eye (brain=claude, standing in) from disclosure_hostheader.txt
# Technique: Host Header Injection in password reset.
# REVIEW + sandbox-validate before approving — generated from a freeform disclosure.
ID = "A19"
NAME = "Host header injection (reset-link poisoning)"
SEVERITY = "HIGH"
CWE = "CWE-644"
EYE = "attack"
FIX = "Never build links from the Host header; use a configured canonical domain for reset/verification URLs."


def run(ctx):
    evil = "evil.example.com"
    try:
        r = ctx.session().get(ctx.base_url + "/reset", headers={"Host": evil})
        reply = r.text
    except Exception as e:
        return False, f"error: {e}"
    if evil in reply:
        return True, f"GET /reset with Host: {evil} produced a reset link pointing at the attacker — {reply[:80]}"
    return False, "not vulnerable"
