import io
import uuid

ID = "A10"
NAME = "Unrestricted file upload"
SEVERITY = "HIGH"
CWE = "CWE-434"
EYE = "attack"
FIX = "Validate file type/extension and content; store uploads outside the web root; never trust the filename."


def run(ctx):
    name = f"trinetra_{uuid.uuid4().hex[:6]}.py"
    files = {"file": (name, io.BytesIO(b"print('pwned')"), "text/x-python")}
    try:
        r = ctx.session().post(ctx.base_url + "/upload", files=files)
        j = r.json()
    except Exception:
        return False, "no usable /upload endpoint"
    if j.get("ok") and j.get("saved") == name:
        return True, f"uploaded executable-looking file '{name}' — no type/extension check"
    return False, "not vulnerable"
