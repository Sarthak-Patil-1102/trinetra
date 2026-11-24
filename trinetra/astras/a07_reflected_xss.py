import uuid

ID = "A07"
NAME = "Reflected XSS"
SEVERITY = "MEDIUM"
CWE = "CWE-79"
EYE = "attack"
FIX = "Escape user input before rendering (use autoescaping templates; never build HTML by string concatenation)."


def run(ctx):
    marker = f"<script>__{uuid.uuid4().hex[:6]}__</script>"
    r = ctx.session().get(ctx.base_url + "/search", params={"q": marker})
    if marker in r.text:
        return True, f"GET /search?q={marker} reflected the <script> payload unescaped"
    return False, "not vulnerable"
