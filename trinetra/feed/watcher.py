"""Read disclosures, filter by stack, de-dupe, and draft new astras to pending."""
import json
import os

from trinetra.brain.template_brain import TemplateBrain
from trinetra.core.loader import load_astras

HERE = os.path.dirname(__file__)
FEED = os.path.join(HERE, "sample_feed.json")
PENDING = os.path.join(os.path.dirname(HERE), "astras_pending")


def _known_ids():
    ids = {a.ID for a in load_astras()}
    if os.path.isdir(PENDING):
        for fn in os.listdir(PENDING):
            if fn.endswith(".py") and not fn.startswith("_"):
                ids.add(fn.split("_")[0].upper())
    return ids


def run_feed(stack=("flask", "jinja2"), brain=None, feed_path=FEED):
    brain = brain or TemplateBrain()
    with open(feed_path) as f:
        entries = json.load(f)
    os.makedirs(PENDING, exist_ok=True)
    known = _known_ids()
    stack = {s.lower() for s in stack}
    results = []
    for e in entries:
        aid = e["astra"]["id"]
        relevant = bool({x.lower() for x in e.get("stack", [])} & stack)
        if not relevant:
            results.append((e["id"], aid, "skipped — not relevant to this stack"))
            continue
        if aid in known:
            results.append((e["id"], aid, f"skipped — {aid} already covered"))
            continue
        src = brain.draft_astra(e)
        slug = e["astra"]["name"].split("(")[0].strip().lower().split()[0]
        fn = f"{aid.lower()}_{slug}.py"
        with open(os.path.join(PENDING, fn), "w") as fh:
            fh.write(src)
        known.add(aid)
        results.append((e["id"], aid, f"DRAFTED → astras_pending/{fn} (brain={brain.name})"))
    return results


def list_pending():
    if not os.path.isdir(PENDING):
        return []
    return sorted(fn for fn in os.listdir(PENDING) if fn.endswith(".py") and not fn.startswith("_"))


def approve(astra_id, dest_dir):
    aid = astra_id.lower()
    for fn in list_pending():
        if fn.split("_")[0] == aid:
            src = os.path.join(PENDING, fn)
            dst = os.path.join(dest_dir, fn)
            os.rename(src, dst)
            return dst
    return None
