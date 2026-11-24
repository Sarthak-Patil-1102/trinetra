"""Trinetra command line. P1: `trinetra scan`."""
import argparse
import os
import socket
import subprocess
import sys
import time

from trinetra.core.astra import Context
from trinetra.core.loader import load_astras
from trinetra.core.orchestrator import run_scan
from trinetra.core.report import terminal_report, json_report, html_report
from trinetra.core import memory

CHAICART = os.path.join(os.path.dirname(__file__), "..", "targets", "chaicart", "app.py")
PKG_PARENT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # dir to put on PYTHONPATH


def _wait_port(host, port, timeout=8.0):
    end = time.time() + timeout
    while time.time() < end:
        try:
            with socket.create_connection((host, port), 0.3):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def cmd_scan(args):
    proc = None
    url = args.url
    source = args.source
    if args.launch == "chaicart":
        proc = subprocess.Popen(
            [sys.executable, os.path.abspath(CHAICART)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        url = "http://127.0.0.1:5001"
        if source is None:
            source = os.path.abspath(os.path.join(os.path.dirname(CHAICART)))
        if not _wait_port("127.0.0.1", 5001):
            print("  target did not start")
            proc.terminate()
            return 1
    try:
        ctx = Context(base_url=url, source_root=source or "")
        attack_enabled = args.launch is not None or args.source is None
        astras = load_astras()
        selected = []
        if attack_enabled:
            selected += [a for a in astras if getattr(a, "EYE", "attack") == "attack"]
        if source:
            selected += [a for a in astras if getattr(a, "EYE", "attack") == "code"]
        findings, score = run_scan(ctx, selected)
        label = url if attack_enabled else source
        terminal_report(findings, score, len(selected), label)
        if args.json:
            json_report(findings, score, args.json)
        if args.html:
            html_report(findings, score, label, len(selected), args.html)
    finally:
        if proc:
            proc.terminate()
    return 0


def _code_findings(repo, source):
    ctx = Context(source_root=source or repo)
    astras = [a for a in load_astras() if getattr(a, "EYE", "attack") == "code"]
    findings, _ = run_scan(ctx, astras)
    return astras, findings


def cmd_arm(args):
    from trinetra.core import fingerprint as fp
    repo = os.path.abspath(args.repo)
    source = os.path.abspath(args.source) if args.source else repo
    profile = fp.fingerprint(source)
    cfg = {"source_root": source, "stack": profile["stack"], "profile": profile}
    if args.url:
        cfg["base_url"] = args.url
    memory.save_config(repo, cfg)
    hp = memory.install_hook(repo, sys.executable, pythonpath=PKG_PARENT)
    print(f"\n  👁 Trinetra armed on {repo}")
    fw = ", ".join(profile["frameworks"]) or "none detected"
    print(f"     detected stack: {fw}   (web app: {'yes' if profile['web_app'] else 'no'})")
    print(f"     hook installed: {hp}")
    print("     every commit is now guarded — High/Critical issues block it.")
    if not profile["web_app"]:
        print("     note: no web framework detected — the attack eye needs a running web app;")
        print("           the code-reading eye still guards every commit.")
    print()
    return 0


def cmd_fingerprint(args):
    from trinetra.core import fingerprint as fp
    profile = fp.fingerprint(os.path.abspath(args.repo))
    print(f"\n  👁 Fingerprint of {args.repo}")
    print(f"     frameworks: {', '.join(profile['frameworks']) or 'none'}")
    print(f"     web app:    {'yes' if profile['web_app'] else 'no'}")
    print(f"     stack:      {', '.join(profile['stack'])}")
    print(f"     languages:  {', '.join(profile['languages']) or 'n/a'}")
    print(f"     deps:       {profile['dep_count']} declared\n")
    return 0


def cmd_guard(args):
    repo = os.path.abspath(args.repo)
    cfg = memory.load_config(repo)
    _, findings = _code_findings(repo, cfg.get("source_root"))
    blockers = [f for f in findings if f.severity in ("CRITICAL", "HIGH")]
    if blockers:
        print("\n  ✗ Trinetra blocked this commit — High/Critical issue(s) found:")
        for f in blockers:
            print(f"    [{f.severity}] {f.name} ({f.cwe})\n        {f.evidence}\n        fix: {f.fix}")
        print("    Fix the above, or override with:  git commit --no-verify\n")
        return 1
    print("  ✓ Trinetra: clean — commit allowed")
    return 0


def cmd_freeze(args):
    repo = os.path.abspath(args.repo)
    cfg = memory.load_config(repo)
    source = cfg.get("source_root") or repo
    astras, findings = _code_findings(repo, source)
    proven_ids = {f.astra_id for f in findings}
    frozen = [a.ID for a in astras if a.ID not in proven_ids]
    path = memory.write_regression_tests(repo, frozen, source)
    print(f"\n  🧊 Froze {len(frozen)} clean checks as regression tests: {', '.join(frozen)}")
    print(f"     test file: {path}")
    print("     if any of these vulns come back, the commit-time guard + pytest will catch it.\n")
    return 0


def _learned_ids(all_astras):
    learned = set()
    for a in all_astras:
        try:
            if "AUTO-DRAFTED" in open(a.__file__).read():
                learned.add(a.ID)
        except Exception:
            pass
    return learned


def _scan_for_dashboard(url, source, attack_enabled, serve=False):
    from trinetra.core import dashboard
    from trinetra.feed import watcher
    all_astras = load_astras()
    ctx = Context(base_url=url, source_root=source or "")
    selected = []
    if attack_enabled:
        selected += [a for a in all_astras if getattr(a, "EYE", "attack") == "attack"]
    if source:
        selected += [a for a in all_astras if getattr(a, "EYE", "attack") == "code"]
    findings, score = run_scan(ctx, selected)
    label = url if attack_enabled else source
    return dashboard.render(findings, score, label, all_astras,
                            _learned_ids(all_astras), watcher.list_pending(), serve=serve)


def cmd_validate(args):
    import importlib.util
    from trinetra.feed import watcher
    target_file = None
    for fn in watcher.list_pending():
        if fn.split("_")[0] == args.astra.lower():
            target_file = os.path.join(watcher.PENDING, fn)
            break
    if not target_file:
        print(f"\n  no pending astra with id {args.astra}\n")
        return 1
    try:
        spec = importlib.util.spec_from_file_location("pending_astra", target_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"\n  ✗ INVALID: the drafted astra does not import — {e}\n")
        return 1
    missing = [a for a in ("ID", "NAME", "SEVERITY", "CWE", "FIX", "run") if not hasattr(mod, a)]
    if missing:
        print(f"\n  ✗ INVALID: missing {', '.join(missing)}\n")
        return 1
    print(f"\n  ✓ syntax + interface OK  ({mod.ID} — {mod.NAME})")
    proc = None
    url = args.url
    if args.launch == "chaicart":
        proc = subprocess.Popen(
            [sys.executable, os.path.abspath(CHAICART)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        url = "http://127.0.0.1:5001"
        _wait_port("127.0.0.1", 5001)
    try:
        proven, evidence = mod.run(Context(base_url=url))
    except Exception as e:
        proven, evidence = False, f"raised: {e}"
    finally:
        if proc:
            proc.terminate()
    if proven:
        print("  ✓ SANDBOX: the astra fired against the demo target")
        print(f"      {evidence}")
        print(f"  Looks safe — approve with:  trinetra review --approve {mod.ID}\n")
    else:
        print(f"  · SANDBOX: astra ran cleanly but did not fire ({evidence})")
        print("      (fine if the demo target isn't vulnerable to this — review manually)\n")
    return 0


def cmd_dashboard(args):
    from trinetra.core import dashboard, server
    from trinetra.feed import watcher
    proc = None
    url = args.url
    source = args.source
    if args.launch == "chaicart":
        proc = subprocess.Popen(
            [sys.executable, os.path.abspath(CHAICART)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        url = "http://127.0.0.1:5001"
        if source is None:
            source = os.path.abspath(os.path.dirname(CHAICART))
        if not _wait_port("127.0.0.1", 5001):
            print("  target did not start")
            proc.terminate()
            return 1
    attack_enabled = args.launch is not None or args.source is None
    try:
        if args.serve:
            server.serve(lambda: _scan_for_dashboard(url, source, attack_enabled, serve=True), port=args.port)
        else:
            all_astras = load_astras()
            ctx = Context(base_url=url, source_root=source or "")
            selected = []
            if attack_enabled:
                selected += [a for a in all_astras if getattr(a, "EYE", "attack") == "attack"]
            if source:
                selected += [a for a in all_astras if getattr(a, "EYE", "attack") == "code"]
            findings, score = run_scan(ctx, selected)
            dashboard.build(findings, score, url if attack_enabled else source,
                            all_astras, _learned_ids(all_astras), watcher.list_pending(), args.out)
            print(f"\n  👁 Dashboard → {args.out}  (open it in a browser)\n")
    finally:
        if proc:
            proc.terminate()
    return 0


def cmd_feed(args):
    from trinetra.feed import watcher
    from trinetra.brain.registry import get_brain
    if getattr(args, "repo", None):
        cfg = memory.load_config(os.path.abspath(args.repo))
        stack = tuple(cfg.get("stack", ["flask", "jinja2"]))
    elif args.stack:
        stack = tuple(s.strip() for s in args.stack.split(","))
    else:
        stack = ("flask", "jinja2")
    brain = get_brain(args.brain)
    print(f"\n  👁 Third eye: scanning disclosures for stack={list(stack)} (brain={brain.name})")
    results = watcher.run_feed(stack=stack, brain=brain)
    for feed_id, aid, msg in results:
        mark = "✚" if msg.startswith("DRAFTED") else "·"
        print(f"    {mark} [{feed_id}] {aid}: {msg}")
    pend = watcher.list_pending()
    if pend:
        print(f"\n  {len(pend)} astra(s) awaiting review. Run: trinetra review\n")
    else:
        print("\n  nothing new to review.\n")
    return 0


def cmd_review(args):
    from trinetra.feed import watcher
    astras_dir = os.path.join(PKG_PARENT, "trinetra", "astras")
    if args.approve:
        dst = watcher.approve(args.approve, astras_dir)
        if dst:
            print(f"\n  ✓ Approved {args.approve} → {os.path.relpath(dst, PKG_PARENT)} (now live)\n")
        else:
            print(f"\n  no pending astra with id {args.approve}\n")
        return 0
    pend = watcher.list_pending()
    if not pend:
        print("\n  no astras pending review.\n")
        return 0
    print("\n  Astras pending review (sandboxed until approved):")
    for fn in pend:
        print(f"    - {fn}   (approve with: trinetra review --approve {fn.split('_')[0].upper()})")
    print()
    return 0


def main():
    p = argparse.ArgumentParser(prog="trinetra", description="A self-updating immune system for code.")
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("scan", help="attack a target and prove vulnerabilities")
    s.add_argument("--url", default="http://127.0.0.1:5001", help="target base URL")
    s.add_argument("--launch", choices=["chaicart"], default=None, help="auto-launch a bundled demo target")
    s.add_argument("--source", default=None, help="path to source for the code-reading eye")
    s.add_argument("--json", default=None, help="write a JSON report to this path")
    s.add_argument("--html", default=None, help="write an HTML report to this path")
    s.set_defaults(func=cmd_scan)

    a = sub.add_parser("arm", help="install the pre-commit wall into a repo")
    a.add_argument("--repo", required=True)
    a.add_argument("--source", default=None)
    a.add_argument("--url", default=None)
    a.set_defaults(func=cmd_arm)

    g = sub.add_parser("guard", help="(used by the hook) block a commit on High/Critical issues")
    g.add_argument("--repo", required=True)
    g.set_defaults(func=cmd_guard)

    fz = sub.add_parser("freeze", help="freeze the current clean checks as regression tests")
    fz.add_argument("--repo", required=True)
    fz.set_defaults(func=cmd_freeze)

    fd = sub.add_parser("feed", help="third eye: draft new astras from disclosures")
    fd.add_argument("--stack", default=None, help="comma-separated stack, e.g. flask,jinja2")
    fd.add_argument("--repo", default=None, help="use the armed repo's detected stack")
    from trinetra.brain.registry import available as _brains
    fd.add_argument("--brain", default=None, choices=_brains(), help="which brain drafts the astra")
    fd.set_defaults(func=cmd_feed)

    rv = sub.add_parser("review", help="list/approve astras the third eye drafted")
    rv.add_argument("--approve", default=None, help="astra id to approve (e.g. A09)")
    rv.set_defaults(func=cmd_review)

    fp_p = sub.add_parser("fingerprint", help="detect a repo's stack")
    fp_p.add_argument("--repo", required=True)
    fp_p.set_defaults(func=cmd_fingerprint)

    vl = sub.add_parser("validate", help="sandbox-test a drafted (pending) astra before approving")
    vl.add_argument("--astra", required=True, help="astra id to validate (e.g. A19)")
    vl.add_argument("--launch", choices=["chaicart"], default=None)
    vl.add_argument("--url", default="http://127.0.0.1:5001")
    vl.set_defaults(func=cmd_validate)

    db = sub.add_parser("dashboard", help="build the 'see everything' HTML dashboard")
    db.add_argument("--launch", choices=["chaicart"], default=None)
    db.add_argument("--url", default="http://127.0.0.1:5001")
    db.add_argument("--source", default=None)
    db.add_argument("--out", default="trinetra_dashboard.html")
    db.add_argument("--serve", action="store_true", help="run a live local web dashboard")
    db.add_argument("--port", type=int, default=7000)
    db.set_defaults(func=cmd_dashboard)

    args = p.parse_args()
    if not getattr(args, "cmd", None):
        p.print_help()
        return
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
