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
    repo = os.path.abspath(args.repo)
    cfg = {"source_root": os.path.abspath(args.source) if args.source else repo}
    if args.url:
        cfg["base_url"] = args.url
    memory.save_config(repo, cfg)
    hp = memory.install_hook(repo, sys.executable, pythonpath=PKG_PARENT)
    print(f"\n  👁 Trinetra armed on {repo}")
    print(f"     hook installed: {hp}")
    print("     every commit is now guarded — High/Critical issues block it.\n")
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


def cmd_dashboard(args):
    from trinetra.core import dashboard
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
    try:
        all_astras = load_astras()
        ctx = Context(base_url=url, source_root=source or "")
        attack_enabled = args.launch is not None or args.source is None
        selected = []
        if attack_enabled:
            selected += [a for a in all_astras if getattr(a, "EYE", "attack") == "attack"]
        if source:
            selected += [a for a in all_astras if getattr(a, "EYE", "attack") == "code"]
        findings, score = run_scan(ctx, selected)
        learned = set()
        for a in all_astras:
            try:
                if "AUTO-DRAFTED" in open(a.__file__).read():
                    learned.add(a.ID)
            except Exception:
                pass
        dashboard.build(findings, score, url if attack_enabled else source,
                        all_astras, learned, watcher.list_pending(), args.out)
        print(f"\n  👁 Dashboard → {args.out}  (open it in a browser)\n")
    finally:
        if proc:
            proc.terminate()
    return 0


def cmd_feed(args):
    from trinetra.feed import watcher
    stack = tuple(s.strip() for s in args.stack.split(",")) if args.stack else ("flask", "jinja2")
    print(f"\n  👁 Third eye: scanning disclosures for stack={list(stack)}")
    results = watcher.run_feed(stack=stack)
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
    fd.set_defaults(func=cmd_feed)

    rv = sub.add_parser("review", help="list/approve astras the third eye drafted")
    rv.add_argument("--approve", default=None, help="astra id to approve (e.g. A09)")
    rv.set_defaults(func=cmd_review)

    db = sub.add_parser("dashboard", help="build the 'see everything' HTML dashboard")
    db.add_argument("--launch", choices=["chaicart"], default=None)
    db.add_argument("--url", default="http://127.0.0.1:5001")
    db.add_argument("--source", default=None)
    db.add_argument("--out", default="trinetra_dashboard.html")
    db.set_defaults(func=cmd_dashboard)

    args = p.parse_args()
    if not getattr(args, "cmd", None):
        p.print_help()
        return
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
