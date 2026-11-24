ID = "A16"
NAME = "Path traversal"
SEVERITY = "HIGH"
CWE = "CWE-22"
EYE = "attack"
FIX = "Never join user input into a filesystem path. Resolve the path and confirm it stays inside an allow-listed directory."


def run(ctx):
    try:
        r = ctx.session().get(ctx.base_url + "/download", params={"file": "../app.py"})
    except Exception:
        return False, "no /download endpoint"
    if r.status_code == 200 and ("secret_key" in r.text.lower() or "VULN" in r.text):
        return True, "GET /download?file=../app.py returned the server's own source code"
    return False, "not vulnerable"
