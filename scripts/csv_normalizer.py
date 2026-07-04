#!/usr/bin/env python3
"""Normalize a messy legacy inventory export before it goes anywhere near
the platform.

Everything migrated so far arrives as flat file CSV, and legacy exports
are exactly as bad as you would expect: mixed date formats, three
spellings of the same impact level, systems with no owner, duplicate
rows, whitespace everywhere. The rule here is simple: fix what is safely
mechanical, REJECT what needs a human, and never invent data. Every
rejected row is a conversation with the owning office, not a silent guess.

Usage:
  python scripts/csv_normalizer.py sample-data/legacy-inventory-export.csv
  (writes <name>.normalized.csv and <name>.exceptions.csv next to it)
"""

import csv
import re
import sys
from datetime import datetime

REQUIRED = ["system_name", "system_acronym", "owner_office", "impact_level",
            "ato_status", "ato_expiration"]

IMPACT_MAP = {
    "l": "Low", "low": "Low", "lo": "Low",
    "m": "Moderate", "mod": "Moderate", "moderate": "Moderate", "med": "Moderate",
    "h": "High", "hi": "High", "high": "High",
}

ATO_MAP = {
    "active": "Active", "current": "Active", "atoed": "Active", "ato": "Active",
    "expired": "Expired", "lapsed": "Expired",
    "in progress": "In Progress", "in-progress": "In Progress",
    "pending": "In Progress", "underway": "In Progress",
    "none": "No ATO", "n/a": "No ATO", "na": "No ATO",
}

DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d-%b-%Y", "%B %d, %Y",
                "%d %b %Y", "%Y/%m/%d", "%d-%b-%y"]


def clean(s):
    return re.sub(r"\s+", " ", (s or "")).strip()


def parse_date(raw):
    raw = clean(raw)
    if not raw:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def normalize_row(row, line_no):
    """Returns (normalized_row, fixed, fatal). Problems that are fixable get
    fixed and noted, problems that are not send the row to exceptions."""
    fixed, fatal = [], []

    # legacy exports love unquoted commas. DictReader shoves the overflow
    # into a None key as a list. Rejoin it onto the last real field and
    # flag it, because a comma that moved a column once will do it again.
    overflow = row.pop(None, None)
    out = {k: clean(v) for k, v in row.items() if k is not None}
    if overflow:
        last_field = list(out)[-1]
        out[last_field] = clean(", ".join([out[last_field]] + [clean(x) for x in overflow]))
        fixed.append(f"rejoined unquoted comma overflow into {last_field}")

    for field in REQUIRED:
        if not out.get(field):
            fatal.append(f"missing {field}")

    if out.get("impact_level"):
        key = out["impact_level"].lower()
        if key in IMPACT_MAP:
            if IMPACT_MAP[key] != out["impact_level"]:
                fixed.append(f"impact_level '{out['impact_level']}' -> '{IMPACT_MAP[key]}'")
            out["impact_level"] = IMPACT_MAP[key]
        else:
            fatal.append(f"unrecognizable impact_level '{out['impact_level']}'")

    if out.get("ato_status"):
        key = out["ato_status"].lower()
        if key in ATO_MAP:
            if ATO_MAP[key] != out["ato_status"]:
                fixed.append(f"ato_status '{out['ato_status']}' -> '{ATO_MAP[key]}'")
            out["ato_status"] = ATO_MAP[key]
        else:
            fatal.append(f"unrecognizable ato_status '{out['ato_status']}'")

    if out.get("ato_expiration"):
        parsed = parse_date(out["ato_expiration"])
        if parsed:
            if parsed != out["ato_expiration"]:
                fixed.append(f"ato_expiration '{out['ato_expiration']}' -> '{parsed}'")
            out["ato_expiration"] = parsed
        else:
            fatal.append(f"unparseable date '{out['ato_expiration']}'")

    if out.get("system_acronym"):
        upper = out["system_acronym"].upper()
        if upper != out["system_acronym"]:
            fixed.append(f"acronym '{out['system_acronym']}' -> '{upper}'")
        out["system_acronym"] = upper

    out["_source_line"] = line_no
    return out, fixed, fatal


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    src = sys.argv[1]
    base = re.sub(r"\.csv$", "", src)

    with open(src, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    seen, good, bad, fix_count = set(), [], [], 0
    for i, row in enumerate(rows, start=2):  # header is line 1
        out, fixed, fatal = normalize_row(row, i)

        key = (out.get("system_acronym"), out.get("owner_office"))
        if all(key) and key in seen:
            fatal.append("duplicate of an earlier row (same acronym + office)")
        elif all(key):
            seen.add(key)

        fix_count += len(fixed)
        if fatal:
            out["_problems"] = "; ".join(fatal)
            bad.append(out)
        else:
            out.pop("_source_line")
            good.append(out)

    if good:
        with open(base + ".normalized.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(good[0].keys()))
            w.writeheader()
            w.writerows(good)
    if bad:
        with open(base + ".exceptions.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(bad[0].keys()))
            w.writeheader()
            w.writerows(bad)

    print(f"read      : {len(rows)} rows from {src}")
    print(f"normalized: {len(good)} rows  ({fix_count} mechanical fixes applied)")
    print(f"exceptions: {len(bad)} rows -> {base + '.exceptions.csv' if bad else 'none'}")
    if bad:
        print("\nevery exception row needs a human answer from the owning office:")
        for r in bad[:8]:
            print(f"  line {r['_source_line']:>3}: {r.get('system_name') or '(no name)'} :: {r['_problems']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
