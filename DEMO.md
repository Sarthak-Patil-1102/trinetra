# Trinetra — Live Demo Cheat-Sheet (fresh laptop, NO brain)

Everything here runs on the **starter library alone** — no Ollama, no API key,
no running app. Pure Python + the built-in astras.

## 0. One-time setup on the fresh laptop
```bash
git clone <your-trinetra-repo-url> trinetra
cd trinetra
python3 -m pip install -r requirements.txt   # requests, flask, pytest, bs4
```

## 1. The money shot — scan a repo neither of us wrote
```bash
git clone https://github.com/adeyosemanputra/pygoat ../pygoat
python3 -m trinetra.cli scan --source ../pygoat
```
Expect: **17 proven findings, Safety score 0/100.** All real. All with file:line proof.

## 2. Open the interactive dashboard
```bash
python3 -m trinetra.cli dashboard --source ../pygoat --out dash.html
open dash.html          # macOS
```
Walk through on screen:
- **Taskbar**: proven count, astras count, score donut
- **Filter chips**: click "High" → table narrows live
- **Click any threat row** → it expands to show the exploit proof + the green "How to fix"
- **Astra library tab**: all 56 detectors (A01–A21 attack, C01–C35 code)
- **Third eye tab**: explains how the library grows itself once a brain is connected

## 3. Backup repos (if pygoat is slow to clone)
| repo | command | findings |
|------|---------|----------|
| DSVW | `scan --source ../dsvw` | 7 |
| Tiredful-API | `scan --source ../tiredful` | 3 |
| ChaiCart (ours) | `scan --launch chaicart` | 30 |

## 4. If someone asks "does it ever lie / make up findings?"
> No. Every finding is proven — a code astra points at a real file:line,
> an attack astra actually ran the exploit. If it can't prove it, it doesn't
> report it. That's the whole point: it makes an app **expensive to hack**,
> it does not claim it's **unhackable**.

## 5. If someone asks "what's the brain / Ollama for?"
> The third eye. With a local model (free) or Claude, Trinetra reads a new
> security disclosure and drafts a brand-new astra for it — so the library
> keeps growing after install. The demo you just saw used **none of that**.
