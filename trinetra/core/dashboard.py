"""Build the 'see everything' dashboard: score, findings, astra library, third eye.

render() returns the HTML string; build() writes it to a file; the server in
server.py calls render(serve=True) to add a live Re-scan button.
"""
import html

HEX = {"CRITICAL": "#e5484d", "HIGH": "#f5a623", "MEDIUM": "#4c82f7", "LOW": "#8a8f98"}


def _finding_cards(findings):
    out = []
    for f in findings:
        c = HEX.get(f.severity, "#8a8f98")
        eye = "code-reading eye" if f.eye == "code" else "attack eye"
        out.append(f"""<div class="card">
      <div class="row"><span class="sev" style="background:{c}">{html.escape(f.severity)}</span>
      <span class="nm">{html.escape(f.name)}</span>
      <span class="meta">{html.escape(f.cwe)} · {html.escape(f.astra_id)} · {eye}</span></div>
      <div class="proof">{html.escape(f.evidence)}</div>
      <div class="fix">fix: {html.escape(f.fix)}</div></div>""")
    return "\n".join(out) or '<div class="clean">No vulnerabilities proven. 🎉</div>'


def _astra_chips(astras, learned_ids):
    out = []
    for a in astras:
        c = HEX.get(a.SEVERITY, "#8a8f98")
        eye = "code" if getattr(a, "EYE", "attack") == "code" else "attack"
        tag = '<span class="learned">learned</span>' if a.ID in learned_ids else ""
        out.append(
            f'<div class="chip"><span class="dot" style="background:{c}"></span>'
            f'<b>{html.escape(a.ID)}</b> {html.escape(a.NAME)} '
            f'<span class="eye">{eye}</span>{tag}</div>'
        )
    return "\n".join(out)


def render(findings, score, target, astras, learned_ids, pending, serve=False):
    band = HEX["CRITICAL"] if score < 40 else ("#f5a623" if score < 70 else "#30a46c")
    n_attack = sum(1 for a in astras if getattr(a, "EYE", "attack") == "attack")
    n_code = sum(1 for a in astras if getattr(a, "EYE", "attack") == "code")
    pend_html = (
        "".join(f'<li>{html.escape(p)} <span class="pend">pending review</span></li>' for p in pending)
        if pending else '<li class="muted">nothing pending — the library is up to date</li>'
    )
    rescan = (
        '<form method="post" action="/rescan" style="margin-left:14px">'
        '<button class="rescan">↻ Re-scan</button></form>' if serve else ""
    )
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trinetra dashboard</title><style>
 body{{margin:0;font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:#0d0f13;color:#e6e8eb}}
 .wrap{{max-width:980px;margin:0 auto;padding:30px 20px}}
 header{{display:flex;align-items:center;gap:16px;border-bottom:1px solid #22262e;padding-bottom:18px}}
 .eye{{font-size:38px}} h1{{margin:0;font-size:20px}} .sub{{color:#9aa0a6;font-size:13px}}
 .score{{margin-left:auto;text-align:center}} .ring{{font-size:36px;font-weight:800;color:{band}}}
 .lbl{{font-size:10px;color:#9aa0a6;letter-spacing:.1em}}
 .rescan{{background:#2b6cb0;color:#fff;border:0;border-radius:8px;padding:9px 14px;font-size:13px;cursor:pointer}}
 .kpis{{display:flex;gap:12px;margin:18px 0}}
 .kpi{{flex:1;background:#141820;border:1px solid #22262e;border-radius:10px;padding:12px 14px}}
 .kpi b{{font-size:22px}} .kpi div{{color:#9aa0a6;font-size:12px}}
 h2{{font-size:14px;color:#cdd1d6;margin:24px 0 10px;text-transform:uppercase;letter-spacing:.08em}}
 .card{{background:#141820;border:1px solid #22262e;border-radius:10px;padding:12px 14px;margin:10px 0}}
 .row{{display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
 .sev{{color:#fff;font-size:11px;font-weight:700;padding:2px 8px;border-radius:5px}}
 .nm{{font-weight:600}} .meta{{color:#8a8f98;font-size:12px;margin-left:auto}}
 .proof{{margin-top:8px;font-size:12.5px;color:#cdd1d6;font-family:ui-monospace,Menlo,monospace;background:#0d0f13;border-radius:6px;padding:7px 9px}}
 .fix{{margin-top:6px;font-size:12.5px;color:#9fe0b0}}
 .lib{{display:flex;flex-wrap:wrap;gap:8px}}
 .chip{{background:#141820;border:1px solid #22262e;border-radius:20px;padding:5px 12px;font-size:12.5px;display:flex;align-items:center;gap:7px}}
 .dot{{width:8px;height:8px;border-radius:50%;display:inline-block}} .eye{{color:#8a8f98;font-size:11px}}
 .learned{{background:#2b6cb0;color:#fff;font-size:10px;padding:1px 6px;border-radius:10px;margin-left:4px}}
 ul{{list-style:none;padding:0}} li{{background:#141820;border:1px solid #22262e;border-radius:8px;padding:9px 12px;margin:6px 0;font-size:13px}}
 .pend{{color:#f5a623;font-size:11px;margin-left:6px}} .muted{{color:#6b7280}}
 .clean{{text-align:center;color:#30a46c;padding:30px}}
 footer{{margin-top:26px;color:#6b7280;font-size:12px;border-top:1px solid #22262e;padding-top:14px}}
</style></head><body><div class="wrap">
 <header><div class="eye">👁</div><div><h1>Trinetra — control plane</h1>
   <div class="sub">target: {html.escape(target)}</div></div>{rescan}
   <div class="score"><div class="ring">{score}</div><div class="lbl">SAFETY / 100</div></div></header>
 <div class="kpis">
   <div class="kpi"><b>{len(findings)}</b><div>vulnerabilities proven</div></div>
   <div class="kpi"><b>{len(astras)}</b><div>astras in library</div></div>
   <div class="kpi"><b>{n_attack}/{n_code}</b><div>attack / code astras</div></div>
   <div class="kpi"><b>{len(learned_ids)}</b><div>learned by third eye</div></div></div>
 <h2>Proven vulnerabilities</h2>{_finding_cards(findings)}
 <h2>Astra library (the two eyes + what the third eye grew)</h2><div class="lib">{_astra_chips(astras, learned_ids)}</div>
 <h2>Third eye — pending review</h2><ul>{pend_html}</ul>
 <footer>Trinetra — a self-updating immune system for code. Findings are proven, not guessed.
 Responsible use: run only against targets you own or have permission to test.</footer>
</div></body></html>"""


def build(findings, score, target, astras, learned_ids, pending, path):
    with open(path, "w") as fh:
        fh.write(render(findings, score, target, astras, learned_ids, pending))
    return path
