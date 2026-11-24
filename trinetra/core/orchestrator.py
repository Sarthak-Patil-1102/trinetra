"""Run astras against a target, collect proven findings, compute a score."""
from .astra import Finding, SEVERITY_WEIGHT


def run_scan(ctx, astras):
    findings = []
    for a in astras:
        try:
            proven, evidence = a.run(ctx)
        except Exception as e:  # an astra must never crash the whole scan
            proven, evidence = False, f"astra error: {e}"
        if proven:
            findings.append(
                Finding(
                    astra_id=a.ID,
                    name=a.NAME,
                    severity=a.SEVERITY,
                    cwe=a.CWE,
                    evidence=evidence,
                    fix=a.FIX,
                    eye=getattr(a, "EYE", "attack"),
                )
            )
    return findings, compute_score(findings)


def compute_score(findings):
    penalty = sum(SEVERITY_WEIGHT.get(f.severity, 5) for f in findings)
    return max(0, 100 - penalty)
