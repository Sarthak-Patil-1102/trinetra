"""Flags regex PII redaction that misses common Indian identifiers.

Relevant to AI/data apps (and India's DPDP Act): a 'PII guardrail' that only
masks email + phone still leaks Aadhaar, PAN, card numbers, names, and
international formats to the model or the logs.
"""
from trinetra.core.sast import rel, walk_code

REDACTOR_HINTS = ("redact", "mask_pii", "anonymi", "sanitize_prompt", "scrub_pii", "pii")
MISS_TERMS = ("aadhaar", "aadhar", "pan card", "pancard", "pan number",
              "credit card", "card number", "passport", "ssn")


def _covers_email_phone(low):
    has_email = "email" in low
    has_phone = "phone" in low or "mobile" in low or r"\d{9}" in low or r"\d{10}" in low
    return has_email and has_phone


ID = "C09"
NAME = "Incomplete PII redaction"
SEVERITY = "MEDIUM"
CWE = "CWE-359"
EYE = "code"
FIX = "A regex filter that only masks email/phone misses Aadhaar, PAN, card numbers, names and international formats. Use a proper PII/NER redaction library and test it against those types."


def run(ctx):
    if not ctx.source_root:
        return False, "no source provided"
    for p, t in walk_code(ctx.source_root):
        low = t.lower()
        is_redactor = any(h in low for h in REDACTOR_HINTS) and ("re.sub" in low or "re.subn" in low)
        if not is_redactor or not _covers_email_phone(low):
            continue
        if any(term in low for term in MISS_TERMS):
            continue  # it already handles the bigger identifiers — looks complete
        for i, l in enumerate(t.splitlines(), 1):
            if "redact" in l.lower() or "pii" in l.lower():
                return True, (f"{rel(ctx.source_root, p)}:{i} regex PII redaction covers email/phone "
                              "but not Aadhaar/PAN/card/name — PII can still reach the model/logs")
        return True, f"{rel(ctx.source_root, p)} — regex PII redaction looks incomplete (email/phone only)"
    return False, "none found"
