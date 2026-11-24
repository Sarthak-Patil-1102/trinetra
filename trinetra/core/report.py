"""Render scan results to the terminal, to JSON, and to a standalone HTML page."""
import html
import json

CLR = {
    "CRITICAL": "\033[91m", "HIGH": "\033[93m", "MEDIUM": "\033[94m",
    "LOW": "\033[90m", "R": "\033[0m", "B": "\033[1m", "G": "\033[92m",
}
HEX = {"CRITICAL": "#e5484d", "HIGH": "#f5a623", "MEDIUM": "#4c82f7", "LOW": "#8a8f98"}


def terminal_report(findings, score, n_astras, target):
    print(f"\n  {CLR['B']}👁  Trinetra scan{CLR['R']}   target={target}   astras run={n_astras}")
    print("  " + "─" * 60)
    if not findings:
        print(f"  {CLR['G']}No vulnerabilities proven.{CLR['R']}")
    for f in findings:
        col = CLR.get(f.severity, "")
        eye = "code" if f.eye == "code" else "attack"
        print(f"  {col}[{f.severity}]{CLR['R']} {f.name}  ({f.cwe})  ·{f.astra_id}·{eye}")
        print(f"      proof: {f.evidence}")
        print(f"      fix:   {f.fix}")
    print("  " + "─" * 60)
    band = CLR["G"] if score >= 70 else (CLR["HIGH"] if score >= 40 else CLR["CRITICAL"])
    print(f"  Safety score: {band}{score}/100{CLR['R']}   ({len(findings)} proven)\n")


def json_report(findings, score, path):
    data = {
        "tool": "trinetra",
        "score": score,
        "count": len(findings),
        "findings": [f.__dict__ for f in findings],
    }
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)
    print(f"  JSON report → {path}")


def html_report(findings, score, target, n_astras, path):
    band = HEX["CRITICAL"] if score < 40 else ("#f5a623" if score < 70 else "#30a46c")
    cards = []
    for f in findings:
        c = HEX.get(f.severity, "#8a8f98")
        eye = "code-reading eye" if f.eye == "code" else "attack eye"
        cards.append(f"""
      <div class="card">
        <div class="row">
          <span class="sev" style="background:{c}">{html.escape(f.severity)}</span>
          <span class="name">{html.escape(f.name)}</span>
          <span class="meta">{html.escape(f.cwe)} · {html.escape(f.astra_id)} · {eye}</span>
        </div>
        <div class="proof"><b>Proof:</b> {html.escape(f.evidence)}</div>
        <div class="fix"><b>Fix:</b> {html.escape(f.fix)}</div>
      </div>""")
    body = "\n".join(cards) if cards else '<div class="clean">No vulnerabilities proven. 🎉</div>'
    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trinetra report — {html.escape(target)}</title>
<style>
 body{{margin:0;font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#0f1115;color:#e6e8eb}}
 .wrap{{max-width:860px;margin:0 auto;padding:32px 20px}}
 header{{display:flex;align-items:center;gap:18px;border-bottom:1px solid #22262e;padding-bottom:20px}}
 .eye{{font-size:40px}}
 h1{{margin:0;font-size:22px}} .sub{{color:#9aa0a6;font-size:13px;margin-top:4px}}
 .score{{margin-left:auto;text-align:center}}
 .ring{{font-size:34px;font-weight:700;color:{band}}}
 .scorelbl{{font-size:11px;color:#9aa0a6;letter-spacing:.08em}}
 .card{{background:#161a21;border:1px solid #22262e;border-radius:10px;padding:14px 16px;margin:14px 0}}
 .row{{display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
 .sev{{color:#fff;font-size:11px;font-weight:700;padding:2px 8px;border-radius:5px;letter-spacing:.04em}}
 .name{{font-weight:600}} .meta{{color:#8a8f98;font-size:12px;margin-left:auto}}
 .proof{{margin-top:10px;font-size:13px;color:#cdd1d6;font-family:ui-monospace,Menlo,monospace;background:#0f1115;border-radius:6px;padding:8px 10px}}
 .fix{{margin-top:8px;font-size:13px;color:#9fe0b0}}
 .clean{{text-align:center;color:#30a46c;padding:40px;font-size:18px}}
 footer{{margin-top:28px;color:#6b7280;font-size:12px;border-top:1px solid #22262e;padding-top:14px}}
</style></head><body><div class="wrap">
 <header>
   <div class="eye">👁</div>
   <div><h1>Trinetra security report</h1>
     <div class="sub">target: {html.escape(target)} &nbsp;·&nbsp; {n_astras} astras run &nbsp;·&nbsp; {len(findings)} proven</div></div>
   <div class="score"><div class="ring">{score}</div><div class="scorelbl">SAFETY / 100</div></div>
 </header>
 {body}
 <footer>Trinetra — a self-updating immune system for code. Findings are proven, not guessed.
 Responsible use: only run Trinetra against targets you own or have permission to test.</footer>
</div></body></html>"""
    with open(path, "w") as fh:
        fh.write(doc)
    print(f"  HTML report → {path}")
