"""Core data types shared by every astra."""
from dataclasses import dataclass

import requests

# Penalty each proven finding subtracts from the 100-point safety score.
SEVERITY_WEIGHT = {"CRITICAL": 25, "HIGH": 18, "MEDIUM": 10, "LOW": 4}


@dataclass
class Finding:
    astra_id: str
    name: str
    severity: str  # CRITICAL | HIGH | MEDIUM | LOW
    cwe: str
    evidence: str  # proof the exploit actually worked
    fix: str
    eye: str = "attack"  # "attack" (DAST) | "code" (SAST)


class Context:
    """Everything an astra needs to run against a target."""

    def __init__(self, base_url: str = "", source_root: str = ""):
        self.base_url = base_url.rstrip("/")
        self.source_root = source_root

    def session(self) -> requests.Session:
        return requests.Session()
