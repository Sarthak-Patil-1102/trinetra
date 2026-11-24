# 🧠 Brains — the pluggable intelligence behind the third eye

This folder is the **reserved space for brains**. A "brain" is whatever model
turns a security disclosure into a new astra (attack plugin). Trinetra does not
care which one you use — swap it freely. Today we ship the offline
`TemplateBrain`; wiring a real model (Ollama/Claude/Fable) is a drop-in here,
intentionally left for later.

## What a brain is (the whole contract)
One class, one method:

```python
from trinetra.brain.base import Brain

class MyBrain(Brain):
    name = "mybrain"
    def draft_astra(self, entry) -> str:
        # `entry` is a disclosure (structured dict, or freeform text in entry["raw_text"])
        # return Python source for an astra: ID, NAME, SEVERITY, CWE, EYE, FIX, run(ctx)
        ...
```

That's it. The feed watcher calls `brain.draft_astra(entry)` and writes the
result into `astras_pending/` for human review.

## Brains shipped / reserved
| Brain | Status | Runs where | Notes |
|---|---|---|---|
| `TemplateBrain` | **active** | offline, no model | Deterministic; fills an astra template from a structured entry. The no-LLM fallback. |
| `OllamaBrain` | stub (not wired) | local model on your machine | Free + private; `draft_astra` HTTP-calls a local Ollama. **Reserved — wire later.** |
| `ClaudeBrain` | reserved | API | For high-value targets / harder disclosures. **Add later.** |
| `FableBrain` / other | reserved | API | Any HTTP LLM fits the same interface. |

## The tiering idea (why pluggable matters)
A small vibecoder faces *automated, known* attacks → the free starter astras +
a small local brain cover them. A big builder faces *targeted, novel* attacks →
they can afford a big brain (Claude/Fable) to power the third eye. The brain
scales with the threat; the person who needs the expensive brain is the one who
can pay for it.

## How to add a brain (later)
1. Create `trinetra/brain/<name>_brain.py` subclassing `Brain`, implement
   `draft_astra`.
2. Let the user select it (a `--brain` flag on `trinetra feed`, or a config key).
3. Done — the review/approve + sandbox flow is unchanged.

## Safety rule (never skip)
A brain is **never trusted blindly.** Every drafted astra lands in
`astras_pending/`, runs only against a sandbox/demo target, and a human must
approve it before it joins the live library. A wrong or malicious draft can't
go live on its own.
