# Publishing Trinetra — M2 package (drafts only)

You're at **M2 (usable v1)**. Below: a pre-publish checklist, then drafts for a
commit message, LinkedIn, X, a demo-video script, and where to post. Edit
freely — nothing is posted automatically.

## Pre-publish checklist
- [x] README (problem, demo, run steps, honest limits, responsible-use)
- [x] LICENSE (MIT)
- [x] .gitignore (excludes *.db, __pycache__, .env)
- [x] No real secrets (ChaiCart's are intentional fake demo values — noted in README)
- [ ] Add a screenshot: the dashboard + the HTML report (drop them in a `docs/` folder and link from the README)
- [ ] Record a 30–60s demo GIF/video (script below)
- [ ] Double-check `git status` for stray `chaicart.db` or `__pycache__` before first push

## Commit message
```
feat: Trinetra v0.1 — a self-updating security scanner (three eyes)

- attack eye (DAST): proves 9 web-app exploits with real request/response evidence
- code eye (SAST): flags hardcoded secrets, debug mode, string-built SQL, eval
- regression memory + git pre-commit hook: blocks reintroduced High/Critical vulns
- third eye: learns new astras from a disclosure feed via a pluggable brain
  (local Ollama / Claude), with a human-approve step
- bundled ChaiCart demo target, HTML report + dashboard

My F.Y. B.Tech Python mini project.
```

## LinkedIn post (edit the brackets)
```
I spent the last couple of days building Trinetra — a small security scanner,
for my first-year Python project.

Most scanners just warn you "this might be vulnerable." I wanted one that
actually proves it — so Trinetra attacks a running copy of an app and shows you
the exact request that broke it. It also does two things I hadn't seen combined:

• it freezes every bug it finds as a test and blocks your next commit if the
  bug comes back (AI coding tools re-introduce fixed bugs a lot — this stops that)
• it can learn new attacks on its own: it reads public security disclosures and
  writes itself a new check for each one

Biggest lesson: being honest about limits is the hard part. It makes an app
expensive to hack, not unhackable — and I had to resist every urge to overclaim.

Code + how it works: [GitHub link]
Feedback very welcome, still learning.

#cybersecurity #python #appsec #buildinpublic
```

## X / Twitter thread
```
1/ I built Trinetra: a security scanner that doesn't just warn you — it breaks
into a demo app and PROVES the hole, then remembers it so it can't come back.
My first-year Python project. 🧵

2/ Three "eyes":
• reads your code for weak spots
• attacks a running copy and proves the exploit
• learns NEW attacks from public disclosures and writes itself a new check

3/ The part I like most: it freezes every fixed bug as a test and blocks your
next commit if the bug returns. AI coding tools re-introduce fixed bugs a lot.
This is a wall against that.

4/ Honest limits (matters): it makes an app expensive to hack, not unhackable.
It learns disclosed attacks fast, not secret zero-days. Only run it on apps you
own.

5/ Code + demo: [GitHub link]. Still a student, feedback welcome.
```

## Demo video script (~45s)
1. (5s) Terminal: `trinetra scan --launch chaicart` — findings scroll, "PROVEN".
2. (8s) Open the HTML report — score 0/100, the proofs, the fixes.
3. (12s) The wall: `git commit` with a reintroduced bug → "✗ blocked".
4. (12s) The third eye: `trinetra feed` → it drafts an SSTI astra → approve →
   re-scan → it now catches a vuln it had never seen.
5. (8s) Open the dashboard — library of astras, one tagged "learned".

## Where to post (M2)
- **LinkedIn** — best fit for a student portfolio; the post above.
- **X/Twitter** — the thread; tag #buildinpublic.
- **r/Python** — allowed as an "I made this" project post. Keep it humble,
  lead with what you learned, include the repo. Read their showcase rules first.
- **r/cybersecurity** — fine for a learning-project share; not r/netsec yet.
- Save **Show HN** and **r/netsec** for M3, once you have a written technical
  write-up (they expect depth + no self-promo vibe).

Security-tool note for every post: include "only test apps you own or have
permission for," and mention ChaiCart is an intentionally vulnerable demo.
