# 👁 Trinetra

**A self-updating immune system for your code.**

> Two eyes find today's bugs. The third sees tomorrow's.

Most security scanners are a frozen checklist — they only catch yesterday's
attacks, and they just *warn* you. Trinetra is different. It has three eyes:

1. **Reads your code** (static analysis) for weak spots.
2. **Attacks a running copy** and *proves* the exploit with real evidence —
   not "this might be vulnerable," but "here's the request that broke it."
3. **Learns tomorrow's attacks** — it watches public security disclosures and
   grows a new attack-plugin (an *astra*) for each new technique, using a
   brain you choose (a local Ollama model, Claude, anything).

It also **remembers**: every proven exploit becomes a regression test wired
into a git pre-commit hook, so a fixed bug can never silently come back — even
if an AI coding tool rewrites the code later.

## Why I built this
I kept reading that ~45% of AI-generated code ships with a vulnerability, and
that AI coding agents re-introduce already-fixed bugs most of the time. The
tools that check for this are siloed per-platform, only warn, and never learn.
I wanted one tool, independent of whoever wrote the code, that proves the hole,
remembers it, and keeps itself current.

## What it protects against
16 attack types at launch across broken access control (IDOR, missing auth,
privilege escalation), business logic (price tampering, negative quantity,
coupon abuse), injection (SQLi, XSS, SSTI), auth weakness (no rate limit),
secrets & config (hardcoded keys, debug mode, keys in the bundle), and unsafe
input handling — and it grows more over time through the third eye.

## Quickstart
```bash
# scan a deliberately-vulnerable demo app (bundled)
python -m trinetra.cli scan --launch chaicart --html report.html

# make it a wall: block commits that (re)introduce High/Critical issues
python -m trinetra.cli arm --repo /path/to/your/repo
python -m trinetra.cli freeze --repo /path/to/your/repo

# the third eye: learn new attacks from disclosures
python -m trinetra.cli feed            # drafts new astras from the feed
python -m trinetra.cli review          # see what it drafted
python -m trinetra.cli review --approve A09   # approve one

# see everything
python -m trinetra.cli dashboard --launch chaicart --out dashboard.html
```

## How it's powered
Almost everything runs locally on your laptop in plain Python — no GPU, no
cloud. The only part that uses an AI model is the third eye (turning a
disclosure into a new astra), and the brain is pluggable: a free local Ollama
model, or Claude for heavier work. Your code never has to leave your machine.

## Honest limits (read these)
- Trinetra makes an app *expensive to hack and always current* — **not
  unhackable.** No tool stops a true zero-day nobody has disclosed yet.
- The third eye adapts fast to *published, known* attacks; it does not invent
  defenses for secret attacks.
- Astras are surface-specific. Trinetra is strongest on web apps with
  request/response endpoints (Flask/FastAPI/Express-style). A clean result on a
  different kind of app (e.g. a Streamlit data dashboard) means "clean on the
  checks Trinetra currently runs," not "fully audited."

## ⚠️ Responsible use
Trinetra runs real exploits. **Only run it against targets you own or have
written permission to test.** `targets/chaicart` is a deliberately vulnerable
demo app; its "secrets" are fake demo values, not a real leak. Attacking
systems you don't own is illegal.

## Status
Student project (MIT-WPU, F.Y. B.Tech). Built as a working prototype. See
`SPEC.md` for the design and build log.

## License
MIT — see `LICENSE`.
