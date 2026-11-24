"""Discover astra plugins by scanning the astras/ package."""
import importlib
import pkgutil

import trinetra.astras as astras_pkg

REQUIRED = ("ID", "NAME", "SEVERITY", "CWE", "FIX", "run")


def load_astras():
    mods = []
    for m in pkgutil.iter_modules(astras_pkg.__path__):
        if m.name.startswith("_"):
            continue
        mod = importlib.import_module(f"trinetra.astras.{m.name}")
        if all(hasattr(mod, a) for a in REQUIRED):
            mods.append(mod)
    mods.sort(key=lambda x: x.ID)
    return mods
