#!/usr/bin/env python3
"""Email Doctor checker: scores a cold email the same way velocitylab.ai/emaildoctor does.

Usage:
  python email_doctor.py --subject "Quick question" --body "Hi Sam, ..."
  python email_doctor.py --file email.txt            # first line "Subject: ..." is optional
  python email_doctor.py --file email.txt --json     # machine-readable output

The catalog (catalog.json) holds 405 weighted phrases in 10 categories. Every entry
carries the reason it is flagged and a source (SpamAssassin rule, provider guideline,
or published study). Python 3.8+, standard library only.
"""
import argparse
import json
import math
import os
import re
import sys

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
SEVERITY_WEIGHT = {"critical": 15, "high": 6, "medium": 3, "low": 1}
BANDS = [(85, "Strong"), (70, "Good"), (50, "Needs work"), (0, "Poor")]

FLAGS = re.IGNORECASE | re.ASCII  # ASCII word boundaries, matching the browser's JavaScript regexes
SHORTENERS = re.compile(r"\b(bit\.ly|tinyurl\.com|t\.co|goo\.gl|ow\.ly|is\.gd|buff\.ly|rebrand\.ly|cutt\.ly|shorturl\.at|rb\.gy|tiny\.cc|lnkd\.in|s\.id|v\.gd)\b", FLAGS)
URL_RE = re.compile(r"\b((?:https?://|www\.)[^\s<>\"')\]]+)", FLAGS)
RAW_IP_URL = re.compile(r"https?://(?:\d{1,3}\.){3}\d{1,3}", FLAGS)
MERGE_TAG = re.compile(r"\{\{\s*[\w.]+\s*\}\}|\{[\w.]+\}|\[\[\s*[\w.]+\s*\]\]|%[A-Z_]+%", re.ASCII)
ZERO_WIDTH = re.compile("[​-‍﻿⁠]+")
SPACED_WORD = re.compile(r"\b(?:[a-z]\s){3,}[a-z]\b", FLAGS)
LEET = re.compile(r"\b(?:v[1!|]agra|c[1!|]al[1!|]s|fr3e|fre3|m0ney|0ffer|pr[1!]ce|[a-z]*\$[a-z]+|[a-z]+\$[a-z]*|[a-z]+[1!|][a-z]{2,}|[a-z]{2,}0[a-z]+)\b", FLAGS)
EXCLAIM_CLUSTER = re.compile(r"!{2,}|(?:!\s*){3,}")
DOLLAR_CLUSTER = re.compile(r"\${2,}")
PERCENT_CLUSTER = re.compile(r"%{2,}|(?:\d+%\s*){3,}")
PLACEHOLDER = re.compile(r"\[[^\]\n]{1,80}\]")
ATTACHMENT = re.compile(r"\b(?:see|find|please\s+find)\s+(?:the\s+)?attached\b|\battachments?\b", FLAGS)


def js_round(x):
    return math.floor(x + 0.5)


def score_from_risk(risk):
    # 3 pts -> 91, 6 -> 84, 15 -> 68, 30 -> 53, 60 -> 34, 100 -> 18
    return max(0, js_round(100 - 34 * math.log(1 + risk / 10)))


def band_for(score):
    return next(label for low, label in BANDS if score >= low)


def classify_fix(text):
    if re.match(r"^\[delete[^\]]*\]$", text, re.I):
        return {"kind": "delete", "text": "Delete"}
    if re.match(r"^\[[^\]]+\]$", text):
        return {"kind": "hint", "text": text[1:-1]}
    return {"kind": "swap", "text": text}


def find_catalog(explicit=None):
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [explicit] if explicit else []
    candidates += [
        os.path.join(here, "catalog.json"),
        os.path.join(here, "..", "references", "catalog.json"),
        os.path.join(os.getcwd(), "catalog.json"),
        "/mnt/data/catalog.json",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    sys.exit("catalog.json not found. Pass --catalog PATH.")


def load_catalog(path):
    with open(path, encoding="utf-8") as f:
        cat = json.load(f)
    for t in cat["terms"]:
        t["re"] = re.compile(t["pattern"], FLAGS)
        t["fixes"] = [classify_fix(r) for r in t.get("replacements", [])]
    return cat


def match_field(text, field, terms):
    raw = []
    for t in terms:
        if t.get("subject_only") and field != "subject":
            continue
        matches = [t["re"].search(text)] if t.get("subject_only") else t["re"].finditer(text)
        for m in matches:
            if m and m.group(0):
                raw.append((t, m.start(), m.end(), m.group(0)))
    raw.sort(key=lambda r: (r[1], -(r[2] - r[1])))  # longest match wins, no overlaps
    kept, last_end = [], -1
    for r in raw:
        if r[1] >= last_end:
            kept.append(r)
            last_end = r[2]
    hits = []
    for t, start, end, txt in kept:
        sev = t.get("severity", "medium")
        mult = (t.get("subject_multiplier") or 2) if field == "subject" else 1
        caps = len(txt) >= 4 and txt == txt.upper() and re.search(r"[A-Z]", txt) is not None
        hits.append({"t": t, "field": field, "start": start, "end": end, "text": txt, "severity": sev,
                     "points": SEVERITY_WEIGHT[sev] * mult * (1.5 if caps else 1)})
    return hits


def find_all(regex, text, field, keep=None):
    return [{"field": field, "start": m.start(), "end": m.end(), "text": m.group(0)}
            for m in regex.finditer(text) if m.group(0) and (keep is None or keep(m.group(0)))]


def structural_checks(subject, body):
    out = []

    def add(key, label, severity, points, fixes, why, occ=None, **extra):
        if isinstance(fixes, str):
            fixes = [{"kind": "note", "text": fixes}]
        item = {"key": key, "label": label, "severity": severity, "points": points, "fixes": fixes, "why": why, "occ": occ or []}
        item.update(extra)
        out.append(item)

    letters = lambda s: re.sub(r"[^A-Za-z]", "", s)

    def caps_ratio(s):
        l = letters(s)
        return 0 if len(l) < 12 else len(re.sub(r"[^A-Z]", "", l)) / len(l)

    def both(regex, keep=None):
        return find_all(regex, subject, "subject", keep) + find_all(regex, body, "body", keep)

    if len(letters(subject)) >= 6 and subject == subject.upper():
        add("subject-caps", "ALL CAPS subject", "medium", 4, "Use sentence case", "SpamAssassin SUBJ_ALL_CAPS; Belkins' 5.5M subject lines show no open-rate gain from caps.")
    if caps_ratio(body) > 0.3:
        add("body-caps", "Too many capitals", "medium", 4, "Use sentence case", "SpamAssassin UPPERCASE_75_100 scores 1.48.")

    o = both(EXCLAIM_CLUSTER)
    if o: add("exclaim", "Stacked !!", "low", 2 * len(o), [{"kind": "swap", "text": "!"}, {"kind": "swap", "text": "."}], "Stacked exclamation marks are a bulk-mail pattern (MapsLeads 2026; SpamAssassin PLING rules).", o)
    o = both(DOLLAR_CLUSTER)
    if o: add("dollars", "Stacked $$", "medium", 3 * len(o), [{"kind": "delete", "text": "Delete"}], "'$$$' is a Tier-1 trigger on 12+ lists and a SpamAssassin money rule.", o)
    o = both(PERCENT_CLUSTER)
    if o: add("percent", "Stacked percentages", "low", 2, "Keep one figure", "Several percentage claims in a row read as a discount blast.", o)
    o = both(ZERO_WIDTH)
    if o: add("zero-width", "Hidden characters", "critical", 8, [{"kind": "delete", "text": "Delete"}], "Gmail's RETVec classifier was built to catch invisible-character obfuscation.", o)
    o = both(SPACED_WORD)
    if o: add("spaced", "S p a c e d letters", "high", 6, "Write the word normally", "Disguising a word scores worse than using it (SpamAssassin TVD_SPACED_*, Gmail RETVec).", o)
    o = both(LEET)
    if o: add("leet", "Symbol swaps like v1agra", "high", 6, "Spell it normally", "Gmail's RETVec detects homoglyph and LEET substitution.", o)
    o = both(MERGE_TAG)
    if o: add("merge-tag", "Merge tag " + o[0]["text"], "low", 1, "Check your tool fills it", "Fine in a sequencer template. Sent unfilled, it is the most visible bulk-mail tell.", o)
    o = both(PLACEHOLDER, keep=lambda t: not t.startswith("[["))
    if o: add("placeholder", "Fill in " + o[0]["text"], "low", 1, [{"kind": "hint", "text": "the real detail"}], "A placeholder is still in the email.", o,
              group="replies", category="To do", reason="Replace the placeholder before sending.")

    urls = find_all(URL_RE, body, "body")
    if len(urls) >= 3: add("links-many", f"{len(urls)} links", "medium", 4, "Keep one link", "SmartReach 2.3M emails: 1-2 links help, 5+ get flagged. Mailchimp: 6+ links 73% more likely marked spam.", urls)
    o = [u for u in urls if SHORTENERS.search(u["text"])]
    if o: add("links-short", "Shortened link", "high", 5, "Use the full URL", "Shorteners hide the destination; Gmail asks links to be clear about where they lead.", o)
    o = [u for u in urls if RAW_IP_URL.search(u["text"])]
    if o: add("links-ip", "Link to an IP address", "critical", 8, "Link to your domain", "SpamAssassin NUMERIC_HTTP_ADDR. Legitimate email almost never links to an IP.", o)
    o = find_all(ATTACHMENT, body, "body")
    if o: add("attachment", "Attachment", "low", 2, "Link it, or send it later", "Snov.io 44M emails: attachments bounce 2.98% vs 1.86%.", o)
    return out


def lint(catalog, subject, body):
    subject, body = subject or "", body or ""
    cats = catalog["categories"]
    hits = match_field(subject, "subject", catalog["terms"]) + match_field(body, "body", catalog["terms"])
    structural = structural_checks(subject, body)

    serious = [h for h in hits if SEVERITY_ORDER[h["severity"]] <= 1]
    stack = 1.5 if len(serious) >= 2 else 1  # 2+ high/critical terms together count 1.5x
    risk = sum(h["points"] * (stack if SEVERITY_ORDER[h["severity"]] <= 1 else 1) for h in hits)
    risk += sum(s["points"] for s in structural)
    score = score_from_risk(risk)

    by_id = {}
    for h in hits:
        t, c = h["t"], cats.get(h["t"]["category"], {})
        it = by_id.get(t["id"])
        if not it:
            it = by_id[t["id"]] = {
                "key": t["id"], "group": c.get("group", "filters"), "severity": h["severity"], "label": t["term"],
                "category": c.get("short", t["category"]), "reason": c.get("reason", ""), "why": t.get("why", ""),
                "anchor": t.get("anchor", ""), "source_url": t.get("source_url", ""), "fixes": t["fixes"],
                "points": 0, "count": 0, "occurrences": []}
        it["count"] += 1
        it["points"] += h["points"]
        it["occurrences"].append({"field": h["field"], "start": h["start"], "end": h["end"], "text": h["text"]})

    issues = list(by_id.values()) + [{
        "key": s["key"], "group": s.get("group", "filters"), "severity": s["severity"], "label": s["label"],
        "category": s.get("category", "Format"), "reason": s.get("reason", "Formatting filters notice."),
        "why": s["why"], "anchor": "", "source_url": "", "fixes": s["fixes"], "points": s["points"],
        "count": max(1, len(s["occ"])), "occurrences": s["occ"]} for s in structural]
    issues.sort(key=lambda i: (SEVERITY_ORDER[i["severity"]], -i["points"]))

    words = len(body.split()) if body.strip() else 0
    return {
        "score": score, "band": band_for(score), "risk": round(risk, 2), "stacking": stack, "words": words,
        "counts": {"spam_filter_issues": sum(1 for i in issues if i["group"] == "filters"),
                   "reply_rate_issues": sum(1 for i in issues if i["group"] == "replies")},
        "issues": issues,
    }


def fix_text(issue):
    parts = []
    for f in issue["fixes"][:3]:
        if f["kind"] == "swap": parts.append(f"→ \"{f['text']}\"")
        elif f["kind"] == "delete": parts.append("delete it")
        elif f["kind"] == "hint": parts.append(f"rewrite: {f['text']}")
        else: parts.append(f["text"])
    return "; ".join(parts) or "rephrase with a specific detail"


def report(result):
    lines = [f"Score: {result['score']}/100 ({result['band']}) · {result['words']} words",
             f"SPAM filter issues: {result['counts']['spam_filter_issues']} · Reply rate issues: {result['counts']['reply_rate_issues']}", ""]
    for group, title in (("filters", "SPAM filter issues"), ("replies", "Reply rate issues")):
        items = [i for i in result["issues"] if i["group"] == group]
        if not items:
            continue
        lines.append(f"## {title}")
        for i in items:
            where = sorted({o["field"] for o in i["occurrences"]}) or ["email"]
            count = f" ×{i['count']}" if i["count"] > 1 else ""
            lines.append(f"- [{i['severity']}] \"{i['label']}\"{count} ({i['category']}, {'+'.join(where)}) — {i['reason']} Fix: {fix_text(i)}")
            lines.append(f"    Why: {i['why']}" + (f" Source: {i['source_url']}" if i["source_url"] else ""))
        lines.append("")
    if not result["issues"]:
        lines.append("Nothing flagged.")
    return "\n".join(lines).rstrip()


def parse_file(path):
    with open(path, encoding="utf-8") as f:
        text = f.read().replace("\r\n", "\n")
    m = re.match(r"^\s*subject:\s*(.*)\n", text, re.I)
    if m:
        return m.group(1).strip(), text[m.end():].lstrip("\n")
    return "", text


def main():
    p = argparse.ArgumentParser(description="Check a cold email against the Email Doctor catalog.")
    p.add_argument("--subject", default="")
    p.add_argument("--body", default=None)
    p.add_argument("--file", help="text file; an optional first line 'Subject: ...' sets the subject")
    p.add_argument("--catalog", help="path to catalog.json")
    p.add_argument("--json", action="store_true", help="print the full result as JSON")
    a = p.parse_args()
    if a.file:
        subject, body = parse_file(a.file)
        subject = a.subject or subject
    else:
        subject, body = a.subject, a.body if a.body is not None else sys.stdin.read()
    result = lint(load_catalog(find_catalog(a.catalog)), subject, body)
    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    else:
        print(report(result))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
