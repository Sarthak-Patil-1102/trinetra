"""Interactive dashboard — matte charcoal / dusty purple / gold theme.

render() returns a self-contained HTML app (data embedded as JSON, vanilla JS for
filtering/expanding). build() writes it; server.py calls render(serve=True) for a
live Re-scan button.

The template is a plain string with __TOKENS__ (not an f-string), so CSS/JS braces
stay literal and readable.
"""
import html
import json

# palette: Charcoal #2B2B2E · Dusty Purple #6B5B7B · Gold #F2C14E
SEV = {"CRITICAL": "#E5654F", "HIGH": "#F2C14E", "MEDIUM": "#A08DB8", "LOW": "#77737D"}
ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]

TEMPLATE = r"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trinetra · scan report</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Crect width='24' height='24' rx='6' fill='%232B2B2E'/%3E%3Cpath d='M12 4.5 19.5 12 12 19.5 4.5 12z' fill='%23F2C14E'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{
  --char:#2B2B2E; --deep:#232326; --panel:#303034; --line:#3B3B40;
  --purple:#6B5B7B; --purple-lt:#9C8BB0; --gold:#F2C14E;
  --ink:#EFE9DD; --mute:#9A96A0; --faint:#6E6A74;
  --display:'Anton',Impact,'Arial Narrow Bold','Helvetica Neue',sans-serif;
  --body:'Inter',-apple-system,'Segoe UI',Roboto,sans-serif;
  --mono:'JetBrains Mono',ui-monospace,Menlo,monospace;
  color-scheme:dark;
}
*{box-sizing:border-box}
body{margin:0;background:var(--char);color:var(--ink);font-family:var(--body);font-size:14px;-webkit-font-smoothing:antialiased}
/* matte grain */
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.07;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.page{position:relative;z-index:1;max-width:1180px;margin:0 auto;padding:0 40px 60px}

/* nav */
nav{display:flex;align-items:center;gap:28px;padding:26px 0 18px}
.brand{display:flex;align-items:center;gap:10px;font-family:var(--display);font-size:21px;letter-spacing:1.2px;text-transform:uppercase}
.brand i{width:11px;height:11px;background:var(--gold);transform:rotate(45deg);display:inline-block}
.tabs{display:flex;gap:26px;margin-left:auto;margin-right:auto}
.tab{color:var(--mute);font-size:13px;font-weight:500;cursor:pointer;padding:6px 0;position:relative;transition:color .15s}
.tab:hover{color:var(--ink)}
.tab.on{color:var(--ink)}
.tab.on::after{content:"";position:absolute;left:50%;bottom:-6px;width:5px;height:5px;border-radius:50%;background:var(--gold);transform:translateX(-50%)}
.pill{background:var(--gold);color:#1d1d1f;border:0;border-radius:999px;padding:9px 18px;font-weight:700;font-size:12.5px;
  font-family:var(--body);cursor:pointer;white-space:nowrap}
.pill:hover{filter:brightness(1.06)}

/* hero */
.hero{display:grid;grid-template-columns:1.15fr 1fr;gap:30px;align-items:center;padding:14px 0 34px;border-bottom:1px solid var(--line)}
.big{font-family:var(--display);text-transform:uppercase;line-height:.95;letter-spacing:-.5px;margin:0}
.big .l2{margin-top:6px}
.big .l1{display:block;color:var(--purple);font-size:clamp(70px,10vw,138px)}
.big .l2{display:block;color:var(--gold);font-size:clamp(70px,10vw,138px)}
.meta{display:grid;grid-template-columns:auto auto;gap:6px 34px;margin-top:26px;justify-content:start}
.meta div{font-size:10.5px;letter-spacing:1.6px;text-transform:uppercase;color:var(--mute);font-weight:600;line-height:1.7}
.meta b{color:var(--ink);font-weight:600}
.tgt{max-width:340px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:block}

/* record sleeve */
.stage{position:relative;height:330px;max-width:430px;justify-self:end;width:100%}
.vinyl{position:absolute;right:0;top:28px;width:270px;height:270px;border-radius:50%;
  background:repeating-radial-gradient(circle at center,#151517 0 2px,#1b1b1e 2px 4px);box-shadow:0 18px 40px rgba(0,0,0,.45)}
.vinyl::after{content:"";position:absolute;inset:0;margin:auto;width:84px;height:84px;border-radius:50%;background:var(--gold)}
.sleeve{position:absolute;left:0;top:0;width:300px;height:300px;border-radius:4px;overflow:hidden;
  background:linear-gradient(160deg,#5E5070 0%,#6B5B7B 45%,#8A7A9A 100%);box-shadow:0 22px 50px rgba(0,0,0,.5)}
.sleeve::before{content:"";position:absolute;inset:0;opacity:.14;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='1.1' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.sun{position:absolute;left:58px;top:38px;width:150px;height:150px;border-radius:50%;background:var(--gold);
  box-shadow:0 0 60px 18px rgba(242,193,78,.45);display:flex;flex-direction:column;align-items:center;justify-content:center;color:#2B2B2E}
.sun .s{font-family:var(--display);font-size:62px;line-height:1}
.sun .u{font-size:10px;font-weight:700;letter-spacing:1.6px;margin-top:2px}
.vol{position:absolute;right:16px;top:14px;font-size:9.5px;letter-spacing:2.4px;color:rgba(239,233,221,.75);font-weight:600}
.title{position:absolute;left:18px;bottom:16px;font-family:var(--display);font-size:38px;line-height:.9;color:var(--ink);text-transform:uppercase}
.sticker{position:absolute;right:6px;bottom:0;width:96px;height:96px;border-radius:50%;background:var(--gold);color:#2B2B2E;
  display:flex;align-items:center;justify-content:center;text-align:center;font-family:var(--display);font-size:19px;line-height:.95;
  transform:rotate(-12deg);box-shadow:0 10px 24px rgba(0,0,0,.4)}

/* filters */
.bar{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:28px 0 16px}
.chip{padding:8px 15px;border-radius:999px;border:1px solid var(--line);background:transparent;color:var(--mute);
  cursor:pointer;font-size:12.5px;font-weight:600;user-select:none;display:flex;align-items:center;gap:8px;transition:all .15s}
.chip:hover{border-color:var(--purple-lt);color:var(--ink)}
.chip.on{background:var(--ink);border-color:var(--ink);color:#222}
.chip .c{font-family:var(--mono);font-size:11.5px}
.chip .d{width:7px;height:7px;border-radius:50%}
.search{margin-left:auto;background:var(--deep);border:1px solid var(--line);border-radius:999px;color:var(--ink);
  padding:9px 16px;font-size:13px;min-width:230px;outline:none;font-family:var(--body)}
.search:focus{border-color:var(--purple-lt)}
.search::placeholder{color:var(--faint)}

/* table */
.card{background:var(--deep);border:1px solid var(--line);border-radius:14px;overflow:hidden}
table{width:100%;border-collapse:collapse}
th{text-align:left;color:var(--faint);font-size:10px;text-transform:uppercase;letter-spacing:1.8px;font-weight:600;padding:14px 18px;border-bottom:1px solid var(--line)}
td{padding:0}
.frow{cursor:pointer;border-bottom:1px solid #2E2E32;transition:background .12s}
.frow:hover{background:#29292d}
.frow td{padding:14px 18px;vertical-align:middle}
.sev{display:inline-flex;align-items:center;gap:7px;font-size:10.5px;font-weight:700;letter-spacing:1.4px}
.sev i{width:8px;height:8px;border-radius:2px;display:inline-block;transform:rotate(45deg)}
.fname{font-weight:600;font-size:14px}
.id{font-family:var(--mono);font-size:11.5px;color:var(--faint);margin-left:8px}
.dim{color:var(--mute);font-size:12.5px}
.cwe{font-family:var(--mono);font-size:12px;color:var(--mute)}
.eye{font-size:10px;letter-spacing:1.4px;text-transform:uppercase;font-weight:600;color:var(--purple-lt)}
.chev{color:var(--faint);transition:transform .18s;font-size:16px;text-align:right}
.frow.open{background:#29292d}
.frow.open .chev{transform:rotate(90deg);color:var(--gold)}
.detail{display:none;background:#29292d}
.detail.show{display:table-row}
.detail td{padding:0 18px 20px 18px}
.proof{font-family:var(--mono);font-size:12.5px;color:#d8d2c6;background:var(--char);border-left:3px solid var(--purple);
  border-radius:4px;padding:12px 14px;white-space:pre-wrap;word-break:break-word;margin-bottom:14px}
.fixlbl{color:var(--gold);font-size:10px;text-transform:uppercase;letter-spacing:1.8px;font-weight:700;margin-bottom:5px}
.fix{color:var(--ink);font-size:13.5px;line-height:1.55;display:flex;gap:10px}
.fix i{width:7px;height:7px;background:var(--gold);transform:rotate(45deg);flex:none;margin-top:7px}
.lbl{font-size:10px;text-transform:uppercase;letter-spacing:1.8px;font-weight:600;color:var(--faint);margin-bottom:5px}

/* library */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px}
.acard{background:var(--deep);border:1px solid var(--line);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;gap:6px;transition:border-color .15s}
.acard:hover{border-color:var(--purple-lt)}
.acard .top{display:flex;align-items:center;gap:8px}
.acard .aid{font-family:var(--display);font-size:20px;letter-spacing:.5px;color:var(--ink)}
.acard .nm{font-size:13px;color:#d9d3c8;line-height:1.4}
.learned{margin-left:auto;background:var(--purple);color:var(--ink);font-size:9.5px;letter-spacing:1.2px;font-weight:700;padding:3px 8px;border-radius:999px;text-transform:uppercase}

/* third eye */
.eyebox{background:var(--deep);border:1px solid var(--line);border-radius:14px;padding:30px 32px}
.eyebox h3{font-family:var(--display);font-size:40px;text-transform:uppercase;margin:0 0 8px;line-height:1;color:var(--ink)}
.eyebox h3 span{color:var(--gold)}
.eyebox p{color:var(--mute);line-height:1.65;max-width:720px;margin:0 0 22px}
.eyebox p b{color:var(--ink);font-weight:600}
.nums{display:flex;gap:48px;flex-wrap:wrap;margin-bottom:22px}
.nums .n{font-family:var(--display);font-size:54px;line-height:1}
.nums .t{font-size:10px;letter-spacing:1.8px;text-transform:uppercase;color:var(--mute);font-weight:600;margin-top:6px}
code{font-family:var(--mono);color:var(--gold);background:var(--char);padding:2px 7px;border-radius:5px;font-size:12.5px}
.pending{background:var(--deep);border:1px solid var(--line);border-left:3px solid var(--gold);border-radius:10px;padding:12px 16px;margin-bottom:10px;font-size:13px}
.empty,.clean{text-align:center;color:var(--mute);padding:50px}
.clean{font-family:var(--display);font-size:40px;color:var(--gold);text-transform:uppercase}

footer{display:flex;gap:56px;flex-wrap:wrap;margin-top:40px;padding-top:20px;border-top:1px solid var(--line)}
footer div{font-size:10px;letter-spacing:1.8px;text-transform:uppercase;color:var(--faint);font-weight:600;line-height:1.8}

@media (max-width:900px){
  .page{padding:0 20px 50px}
  .hero{grid-template-columns:1fr}
  .stage{justify-self:start}
  .tabs{gap:16px}
}
</style></head><body><div class="page">

<nav>
  <div class="brand"><i></i>Trinetra</div>
  <div class="tabs">
    <div class="tab on" data-tab="find">Vulnerabilities</div>
    <div class="tab" data-tab="lib">Astra library</div>
    <div class="tab" data-tab="eye">Third eye</div>
  </div>
  __RIGHT__
</nav>

<section class="hero">
  <div>
    <h1 class="big"><span class="l1">__L1__</span><span class="l2">__L2__</span></h1>
    <div class="meta">
      <div>Target<br><b class="tgt" title="__TARGET__">__TARGET__</b></div>
      <div>Engine<br><b>__NASTRA__ astras · code + attack eye</b></div>
      <div>Critical · high<br><b>__NCRIT__ · __NHIGH__</b></div>
      <div>Brain<br><b>Offline · starter library</b></div>
    </div>
  </div>
  <div class="stage">
    <div class="vinyl"></div>
    <div class="sleeve">
      <div class="vol">VOL. __NASTRA__</div>
      <div class="sun"><div class="s">__SCORE__</div><div class="u">SAFETY / 100</div></div>
      <div class="title">Scan<br>Report</div>
    </div>
    <div class="sticker">__STICKER__</div>
  </div>
</section>

<div id="find">
  <div class="bar" id="sevFilters"></div>
  <div id="tableWrap"></div>
</div>
<div id="lib" style="display:none">
  <div class="bar"><input class="search" id="libSearch" placeholder="Search astras…" style="margin-left:0"></div>
  <div class="grid" id="libGrid"></div>
</div>
<div id="eye" style="display:none;margin-top:28px"><div id="eyeBox"></div></div>

<footer>
  <div>Proves findings<br>Never guesses</div>
  <div>Expensive to hack<br>Not unhackable</div>
  <div>Responsible use<br>Targets you own or may test</div>
</footer>
</div>
<script>
const DATA = __PAYLOAD__;
const SEV = {CRITICAL:"#E5654F",HIGH:"#F2C14E",MEDIUM:"#A08DB8",LOW:"#77737D"};
const ORDER = ["CRITICAL","HIGH","MEDIUM","LOW"];
let state = {sev:"ALL", q:""};

function esc(s){return (s||"").replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function title(s){return s[0]+s.slice(1).toLowerCase();}

function sevFilters(){
  const box = document.getElementById("sevFilters");
  let h = `<span class="chip ${state.sev==='ALL'?'on':''}" data-s="ALL">All <span class="c">${DATA.findings.length}</span></span>`;
  ORDER.forEach(s=>{
    const n = DATA.counts[s]||0;
    h += `<span class="chip ${state.sev===s?'on':''}" data-s="${s}"><span class="d" style="background:${SEV[s]}"></span>${title(s)} <span class="c">${n}</span></span>`;
  });
  h += `<input class="search" id="findSearch" placeholder="Search findings…" value="${esc(state.q)}">`;
  box.innerHTML = h;
  box.querySelectorAll(".chip").forEach(c=>c.onclick=()=>{state.sev=c.dataset.s;sevFilters();renderTable();});
  const si = document.getElementById("findSearch");
  si.oninput = ()=>{state.q=si.value.toLowerCase();renderTable();};
}

function renderTable(){
  const wrap = document.getElementById("tableWrap");
  if(!DATA.findings.length){wrap.innerHTML=`<div class="card"><div class="clean">Nothing proven</div></div>`;return;}
  let rows = DATA.findings.filter(f=>(state.sev==="ALL"||f.sev===state.sev) &&
    (!state.q || (f.name+f.cwe+f.id).toLowerCase().includes(state.q)));
  rows.sort((a,b)=>ORDER.indexOf(a.sev)-ORDER.indexOf(b.sev));
  if(!rows.length){wrap.innerHTML=`<div class="card"><div class="empty">No findings match this filter.</div></div>`;return;}
  let h = `<div class="card"><table><thead><tr><th style="width:130px">Severity</th><th>Finding</th><th style="width:120px">CWE</th><th style="width:90px">Eye</th><th style="width:36px"></th></tr></thead><tbody>`;
  rows.forEach((f,i)=>{
    h += `<tr class="frow" data-i="${i}">
      <td><span class="sev" style="color:${SEV[f.sev]}"><i style="background:${SEV[f.sev]}"></i>${f.sev}</span></td>
      <td><span class="fname">${esc(f.name)}</span><span class="id">${f.id}</span></td>
      <td class="cwe">${f.cwe}</td>
      <td class="eye">${f.eye==='code'?'code':'attack'}</td>
      <td class="chev">›</td></tr>
      <tr class="detail" data-d="${i}"><td colspan="5">
        <div class="lbl">Proof</div>
        <div class="proof">${esc(f.proof)}</div>
        <div class="fixlbl">How to fix</div>
        <div class="fix"><i></i><span>${esc(f.fix)}</span></div></td></tr>`;
  });
  h += `</tbody></table></div>`;
  wrap.innerHTML = h;
  wrap.querySelectorAll(".frow").forEach(r=>r.onclick=()=>{
    wrap.querySelector(`.detail[data-d="${r.dataset.i}"]`).classList.toggle("show");
    r.classList.toggle("open");
  });
}

function renderLib(q=""){
  document.getElementById("libGrid").innerHTML = DATA.astras
    .filter(a=>!q||(a.id+a.name).toLowerCase().includes(q))
    .map(a=>`<div class="acard">
      <div class="top"><span class="aid">${a.id}</span>
        <span class="sev" style="color:${SEV[a.sev]}"><i style="background:${SEV[a.sev]}"></i>${a.sev}</span>
        ${a.learned?'<span class="learned">Learned</span>':''}</div>
      <div class="nm">${esc(a.name)}</div>
      <div class="eye">${a.eye} eye · ${a.cwe}</div></div>`).join("");
}

function renderEye(){
  const learned = DATA.astras.filter(a=>a.learned).length;
  const pend = DATA.pending.map(p=>`<div class="pending">${esc(p)} <span style="color:var(--gold);margin-left:8px;font-weight:600">pending review</span></div>`).join("");
  document.getElementById("eyeBox").innerHTML = pend + `<div class="eyebox">
    <h3>The third <span>eye</span></h3>
    <p>Eye 1 reads your code. Eye 2 attacks a running app. <b>Eye 3 learns new attacks</b> from security disclosures and drafts fresh astras, so the library keeps growing after install — not just at build time.</p>
    <div class="nums">
      <div><div class="n" style="color:var(--ink)">${DATA.astras.length}</div><div class="t">Astras in library</div></div>
      <div><div class="n" style="color:var(--gold)">${learned}</div><div class="t">Learned by eye 3</div></div>
      <div><div class="n" style="color:var(--purple-lt)">Offline</div><div class="t">Brain · none connected</div></div>
    </div>
    <p style="margin:0">Connect a brain (local Ollama, free — or Claude) with <code>trinetra feed</code> to draft astras from a disclosure. Everything on this page already runs with <b>no brain</b>, on the starter library alone.</p>
  </div>`;
}

document.querySelectorAll(".tab").forEach(t=>t.onclick=()=>{
  document.querySelectorAll(".tab").forEach(x=>x.classList.remove("on")); t.classList.add("on");
  ["find","lib","eye"].forEach(id=>document.getElementById(id).style.display="none");
  document.getElementById(t.dataset.tab).style.display="block";
});
document.getElementById("libSearch").oninput = e=>renderLib(e.target.value.toLowerCase());
sevFilters(); renderTable(); renderLib(); renderEye();
</script></body></html>"""


def render(findings, score, target, astras, learned_ids, pending, serve=False):
    counts = {s: sum(1 for f in findings if f.severity == s) for s in ORDER}
    data = {
        "score": score,
        "target": target,
        "findings": [
            {"id": f.astra_id, "sev": f.severity, "name": f.name, "cwe": f.cwe,
             "eye": f.eye, "proof": f.evidence, "fix": f.fix}
            for f in findings
        ],
        "astras": [
            {"id": a.ID, "name": a.NAME, "sev": a.SEVERITY, "eye": getattr(a, "EYE", "attack"),
             "cwe": a.CWE, "learned": a.ID in learned_ids}
            for a in astras
        ],
        "pending": list(pending),
        "counts": counts,
    }
    # escape </ so an evidence string containing </script> can't break out of the <script> tag
    payload = json.dumps(data).replace("</", "<\\/")

    n = len(findings)
    if n:
        l1, l2 = f"{n} proven", "threats" if n != 1 else "threat"
        sticker = "Fix<br>Now" if counts["CRITICAL"] or counts["HIGH"] else "Review"
    else:
        l1, l2 = "Zero", "proven"
        sticker = "All<br>Clear"

    if serve:
        right = ('<form method="post" action="/rescan" style="margin:0">'
                 '<button class="pill">Re-scan</button></form>')
    else:
        right = f'<span class="pill">{n} proven</span>'

    out = TEMPLATE
    for k, v in {
        "__RIGHT__": right,
        "__L1__": html.escape(l1),
        "__L2__": html.escape(l2),
        "__TARGET__": html.escape(target),
        "__NASTRA__": str(len(astras)),
        "__NCRIT__": str(counts["CRITICAL"]),
        "__NHIGH__": str(counts["HIGH"]),
        "__SCORE__": str(score),
        "__STICKER__": sticker,
    }.items():
        out = out.replace(k, v)
    return out.replace("__PAYLOAD__", payload)  # last, so data can't collide with tokens


def build(findings, score, target, astras, learned_ids, pending, path):
    with open(path, "w") as fh:
        fh.write(render(findings, score, target, astras, learned_ids, pending))
    return path
