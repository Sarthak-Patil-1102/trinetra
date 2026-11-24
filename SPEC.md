# Trinetra — Implementation Spec (v0.2)

> **Trinetra** (त्रिनेत्र, "the three-eyed one" — Shiva's third eye that sees
> and burns threats on sight). A self-updating **immune system for code**.
> Tagline: *"Two eyes find today's bugs. The third sees tomorrow's."*

Date: 2026-11-24 · Builder: solo · Budget: ~16 hours · Mode: assisted (you
approve each gate, I build + verify).

---

## 0. THE IDEA IN ONE BREATH
Every security scanner today has **two eyes**:
- **Eye 1 — reads the code** (static analysis / SAST).
- **Eye 2 — attacks the running app** (dynamic analysis / DAST), proving real
  exploits instead of just warning.

Trinetra opens a **third eye**:
- **Eye 3 — learns tomorrow's attacks.** It watches security disclosures and
  grows a new attack-plugin (an *"astra"*) for each new technique. Other
  scanners ship a frozen ruleset and wait for a vendor update; Trinetra
  updates itself from the open security firehose.

Honest limit, stated up front: Eye 3 adapts fast to *published, known*
attacks. It cannot invent defenses for attacks nobody has disclosed yet.
"Living" = stays current, not omniscient. Trinetra makes an app *expensive to
hack and always current*, not unhackable.

But when Trinetra *detects* a hole it has no confident fix for (a known attack
with no clean patch yet), it does not go silent — it runs the
**contain-and-escalate** path (section 5c): warn loudly, apply an interim
mitigation to hold the wall, and offer to draft a sanitized help-request the
user can post to a community to crowdsource a real fix.

## 1. GOAL
A tool that:
1. Reads a target app's source for weak spots (Eye 1).
2. Attacks a running copy to *prove* working exploits with evidence (Eye 2).
3. Remembers — every proven exploit becomes a regression test wired into a
   commit hook, so a reintroduced bug blocks the commit (defeats the "AI
   agent silently brings a fixed bug back" problem).
4. Stays alive — pulls new disclosures and grows a new astra for each;
   demoed live by turning one real new writeup into a working astra.

Legal boundary baked in: Trinetra only attacks a target the user owns or
provides (localhost demo app, or a repo they point it at). Never third-party
systems. Opt-in by design.

## 2. WHO IT'S FOR (so the pitch lands)
The "vibe coder": a solo founder, student, or hobbyist who built an app with
AI tools (Lovable, Cursor, Bolt, v0) and has no idea it's leaking data.
Context: ~45% of AI-generated code ships with a vulnerability, and most of
these builders are not developers. Trinetra is their security-team-in-a-box —
no security knowledge required.

## 3. HOW A NORMAL PERSON USES IT (the product, not the internals)
1. **Point it:** `trinetra scan <folder-or-localhost-url>`. No config.
2. **Watch:** it reads the code, then attacks the running app live. On screen,
   plain English: *"Anyone can read other people's orders," "A customer can
   set their own price."*
3. **Read the report:** an HTML page with a safety **score** (a credit-score
   for the app), each problem in human words, and a **copy-paste fix** for
   each — including a prompt they can paste into their AI coding tool.
4. **Stay safe automatically:** `trinetra arm` once installs the hook; from
   then on every change is checked and anything that reintroduces an old hole
   is blocked. They never have to remember to run it again.

## 4. CURRENT STATE
Nothing built yet. Environment confirmed: Python 3.13, Flask 3.1, requests,
pytest, bs4 installed. Bash network is OFF (no pip installs / no arbitrary
curl) — so the live feed uses a bundled sample offline, and real CVEs are
pulled via the assistant's web tools during the demo.

## 5. WHAT SHOULD HAPPEN (architecture)
Demo target: **ChaiCart** — a deliberately vulnerable Flask shop we build,
seeded with: IDOR, price tampering, negative quantity, missing auth on
/admin, no rate limit, SQL injection, reflected XSS, hardcoded secret, debug
mode on.

Components:
- **Astra system** (`astras/`): each attack = one small Python file with a
  fixed interface — metadata (id, name, severity, CWE, eye: code|attack) and
  `run(target) -> Finding | None` returning proof. New attacks = new files.
- **Eye 1 — code reader (SAST)**: scans source for risky patterns (hardcoded
  secrets, `eval`, string-built SQL, `debug=True`, routes with no auth).
  Produces *leads* that aim Eye 2.
- **Eye 2 — attacker (DAST)**: hits the running app and returns *proven*
  exploits with evidence (request + response).
- **Orchestrator**: Eye 1 -> map leads to astras -> Eye 2 -> collect/de-dupe
  -> score.
- **Memory** (`regression/`): each proven exploit -> a pytest test; a
  generated pre-commit hook runs them so the bug can't return.
- **Eye 3 — living feed** (`feed/`): reads disclosures (bundled sample
  offline; real CVE via web tools in demo) -> drafts a new astra into
  `astras_pending/` -> human approves (moves to `astras/`) -> re-run. The
  "LLM" in the demo is the assistant generating the astra live.
- **Report** (`report/`): findings -> terminal + HTML + JSON, each with a
  copy-paste fix. Opt-in reporting: generate a GitHub-issue markdown + email
  *draft* (never sends).
- **Dashboard**: before/after score + one chart.

## 5b. WHAT TRINETRA PROTECTS FROM (attack coverage)
Each item is a proven exploit (astra), not just a warning.
**Starter set shipped at launch: 16 attack types.** (8 are built + proven in
P1 — the attack/DAST ones; the code/SAST ones and remaining DAST land in P2+.)
**The 16:**
- *Broken access control:* IDOR, /admin with no auth, admin-at-signup.
- *Business logic (scanners miss these):* price tampering, negative/zero
  quantity, coupon reuse / redeem-100 races.
- *Injection:* SQL injection, reflected XSS.
- *Auth weakness:* no rate limit (brute-force / guess login code), predictable
  tokens.
- *Secrets & config:* hardcoded keys, .env in git history, debug=True on, key
  in frontend bundle.
- *Unsafe input/file:* unrestricted upload (non-photo), mass assignment
  (role=admin in signup body).
**Stretch astras:** SSTI, SSRF, command injection, open redirect, missing
security headers.

### How the set improves on its own (the third eye loop)
1. **Watch** — poll disclosure sources (CVE/NVD, GitHub advisories, writeups).
   Offline: bundled sample feed. Live demo: a real CVE via web tools.
2. **Filter** — keep only relevant disclosures; de-dupe against known astras.
3. **Draft** — an LLM turns the writeup into a new astra (attack steps +
   success check) in the standard format.
4. **Sandbox + approve** — draft -> `astras_pending/`, runs only vs the demo
   app, human approves before it joins the live set (the safety valve).
5. **Run everywhere + remember** — next scan tests every target against it; a
   hit becomes a regression test, watched forever.
Net effect: coverage compounds over time without a human hand-writing each
rule. Limit (honest): learns *disclosed* attacks fast, not unpublished
zero-days.

## 5c. CONTAIN-AND-ESCALATE (when there's no clean fix yet)
A detected vulnerability doesn't always have a known fix. Instead of shrugging,
Trinetra:
1. **Warn** — flag it loud, mark severity, never let it pass silently.
2. **Contain (hold the wall)** — propose an interim mitigation that neutralises
   it until a real fix exists: e.g. disable/guard the affected route, turn the
   feature off behind a flag, add a blocking rule, or force auth on it. The
   point is to buy time safely, not to "fix" it.
3. **Escalate (find a fix)** — generate a **sanitized** help-request (the
   vulnerability class and symptoms only — no secrets, no proprietary code, no
   working exploit) that the user can choose to post to a community/portal
   (Stack Overflow, a relevant subreddit, a GitHub issue) to crowdsource a
   solution. Any good answer can later become a fix suggestion or a new astra.

Safety rule (hard): escalation is **opt-in and sanitized, never automatic**.
Publicly posting a live, unfixed exploit for your own app would help attackers,
so Trinetra posts a *description of the problem*, never a runnable exploit, and
only after you review and click send. (Stretch feature for the build; the warn
+ contain-suggestion parts are MVP-cheap and included.)

## 6. FILES / REPO LAYOUT
```
trinetra/
  SPEC.md  CLAUDE.md  README.md
  trinetra/
    cli.py                # trinetra scan | feed | arm
    engine/{sast,dast,orchestrator}.py
    astras/               # live attack plugins (one file each)
    astras_pending/       # LLM-drafted, awaiting human approval
    feed/{watcher.py, sample_feed.json}
    regression/           # auto-generated pytest files
    report/{html,json,issue}.py  report/templates/
  targets/chaicart/       # the deliberately vulnerable demo app
  hooks/pre-commit
```

## 7. RISKS & TRICKY PARTS
- **Scope vs 16h (biggest).** Mitigation: strict MVP/stretch split + phase
  order; each phase independently demoable.
- **Bash network off.** Mitigation: bundled sample feed; real CVE via web
  tools in demo.
- **Flaky exploits** (rate-limit timing). Mitigation: deterministic checks,
  generous thresholds, each astra self-verifies its proof.
- **LLM-drafted astra could be wrong/unsafe.** Mitigation: lands in
  `astras_pending/`, runs only against ChaiCart, human approves before it
  joins `astras/`. Never auto-promoted.
- **Over-claiming.** Report always states limits (known attacks only, opt-in,
  not a guarantee).

## 8. HOW WE VERIFY (run before calling anything done)
1. ChaiCart is actually exploitable — hit each flaw by hand with `requests`.
2. Eye 1 flags every planted source smell (file + line).
3. Eye 2 proves >=6 exploits end-to-end with real request/response evidence
   (no success claimed without proof).
4. Memory: re-introduce a fixed bug -> pre-commit hook blocks the commit.
5. Eye 3: feed one disclosure -> runnable astra in `astras_pending/` ->
   approve -> it runs and correctly finds/doesn't-find the flaw.
6. Report + dashboard render with findings, scores, chart, fixes.
Nothing is "done" until its check passes with evidence shown.

## 9. WHAT "DONE" MEANS
**MVP (win condition):**
- ChaiCart running with >=6 real vulns.
- Astra engine; Eye 1 leads + Eye 2 proving >=6 exploits with evidence.
- Memory: >=1 re-introduced bug blocked by the hook.
- Eye 3: >=1 new astra grown from a disclosure and run live.
- `trinetra scan <target>` -> HTML + JSON report with fixes.

**Stretch (only if MVP solid):**
- Dashboard before/after chart · `trinetra arm` into any repo ·
  auto GitHub-issue + email-draft · more astras (SSTI, SSRF, injection
  variants).

## 10. FINISHED-PRODUCT WALKTHROUGH (the demo you'd pitch)
1. `trinetra scan chaicart` — live feed scrolls: *"IDOR on /order… PROVEN —
   order #1002 belongs to another user. Negative quantity… PROVEN — total
   came back -₹2,500…"* 6+ real exploits, each with the exact request.
2. HTML **report** opens: findings + severity + proof + copy-paste fix.
   Score: **28/100**.
3. Fix two, re-scan: score jumps to **70/100**; before/after chart updates.
4. **Memory:** re-introduce a "fixed" bug, try to commit -> hook **blocks**
   it: *"Blocked: IDOR regression test failed."*
5. **Third eye (finale):** a brand-new vuln writeup arrives -> Trinetra reads
   it, drafts a new astra, you approve, re-scan -> it catches a flaw it had
   never seen before. The "it's alive" moment.

## 11. PHASED BUILD PLAN (16h, solo) — each phase demoable
- **P0 (0–1h) make-or-break:** scaffold; build ChaiCart with 3 flaws; prove
  them exploitable by hand.
- **P1 (1–4h):** astra interface + Eye 2 (DAST) + 6 astras; `trinetra scan`
  prints proven findings.
- **P2 (4–7h):** Eye 1 (SAST) + lead->astra mapping; JSON + HTML report + fixes.
- **P3 (7–10h):** memory + pre-commit hook; demo a blocked reintro.
- **P4 (10–13h):** Eye 3 feed + sample feed + live LLM-drafted astra.
- **P5 (13–16h):** dashboard/chart, `arm`, polish, README, full verify pass.

---
## 12. BUILD-IN-PUBLIC TRACKER (coach mode)
Goal: portfolio for internships + cybersecurity community rep. Drafts only — I
never post anything; Sarthak approves and posts.
Ladder:
- **M0** idea/spec → nothing public (optional 2-line "building X" post).
- **M1** first thing that works → public GitHub repo (README w/ problem +
  demo + run steps, .gitignore, LICENSE, no real secrets). ← **REACHED (P1)**
- **M2** usable v1 → tagged release + LinkedIn + X thread + demo video.
- **M3** polished → dev.to/blog write-up + Show HN / r/netsec-style forum.
- **M4** others use it → issues/feedback loop + "what I learned" post + resume.
Responsible-use (mandatory in README): Trinetra attacks only targets you own
or have written permission to test; ChaiCart is a deliberately vulnerable demo
and its "secrets" are fake demo values, not a real leak.

Status: at **M1**. To publish M1 cleanly we still need: README, .gitignore,
LICENSE, a screenshot of a scan. Recommend publishing after P2 (HTML report
gives a better screenshot).

---
## Build log
- **P0 ✅** ChaiCart built; 8/8 planted flaws proven exploitable by hand.
- **P1 ✅** Astra engine + 8 attack astras + `trinetra scan --launch chaicart`;
  proves all 8, scores 0/100, writes JSON. First working tool (M1).
- **P2 ✅** Code-reading eye (4 code astras) + HTML report. ChaiCart now shows
  11 proven (8 attack + 3 code). Real-world test: scanned Sarthak's repo
  (salonishriv0512-coder/final-python-project) — clean on current checks, but
  it's a Streamlit data app so the attack eye doesn't apply. Lesson: astras are
  surface-specific; honest scope limit recorded.
- **P3 ✅** Regression memory + `arm`/`guard`/`freeze`. Pre-commit hook blocks
  a reintroduced vuln (debug=True demo); generated pytest regression also fails.
- **P4 ✅** Third eye: pluggable brain (TemplateBrain offline + OllamaBrain),
  feed watcher with stack-filter + dedup, `feed`/`review` approve flow. Learned
  an SSTI astra from a disclosure and caught it on ChaiCart (12→13 astras).
- **P5 ✅** HTML dashboard (`dashboard`), README, LICENSE, requirements.txt,
  full end-to-end verification pass (all commands green; 13 astras load).
  BUILD COMPLETE — usable v1 (M2).
