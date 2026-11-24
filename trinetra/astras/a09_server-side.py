# AUTO-DRAFTED by Trinetra third eye (brain=template) from feed entry FEED-2026-SSTI.
# Technique: Server-Side Template Injection in Flask render_template_string
# REVIEW before approving — generated code, not yet trusted.
ID = 'A09'
NAME = 'Server-Side Template Injection (SSTI)'
SEVERITY = 'CRITICAL'
CWE = 'CWE-1336'
EYE = "attack"
FIX = 'Never render user input as a template. Pass it as data to a static template with autoescaping.'

_ENDPOINTS = ['/greet', '/hello', '/welcome']
_PARAM = 'name'
_PAYLOAD = '{{7*7}}'
_EXPECT = '49'


def run(ctx):
    s = ctx.session()
    for ep in _ENDPOINTS:
        try:
            r = s.get(ctx.base_url + ep, params={_PARAM: _PAYLOAD})
        except Exception:
            continue
        if _EXPECT in r.text:
            return True, f"GET {ep}?{_PARAM}={_PAYLOAD} -> response contained {_EXPECT!r} (payload executed)"
    return False, "not vulnerable"
