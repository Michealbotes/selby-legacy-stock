#!/usr/bin/env python3
"""Bake the public Selby legacy-stock page.

Reads the scheduler's Selby inventory export + master catalogue, keeps only
legacy items (flagged discontinued in the master, OR newest model-year
coverage ended 2010 or earlier), and writes a fully self-contained
index.html — data embedded, no server, no login, nothing shared with the
scheduler. Refreshing the public list after a new inventory export is:

    python3 build.py && git add -A && git commit -m "stock refresh" && git push
"""
import base64
import csv
import datetime
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEDULER = os.path.join(HERE, "..", "fitment-scheduler")
INVENTORY = os.path.join(SCHEDULER, "catalogue", "selby-inventory.csv")
MASTER = os.path.join(SCHEDULER, "catalogue", "master-stock.csv")
LOGO = os.path.join(SCHEDULER, "public", "myglass-logo.png")

# An item is "legacy" when the supplier has dropped the code, or the newest
# vehicle it fits went out of production in 2010 or earlier.
LEGACY_YEAR_CUTOFF = 2010


def end_year(desc):
    ys = []
    for m in re.finditer(r"\b(\d{2})-(\d{2})?(?!\d)", desc):
        e = m.group(2)
        if e is None:
            return 9999  # open-ended range: still-current model
        e = int(e)
        e += 1900 if e >= 40 else 2000
        ys.append(e)
    return max(ys) if ys else None


def main():
    master = {r["wd_code"].strip().lower(): r
              for r in csv.DictReader(open(MASTER, newline="", encoding="utf-8-sig"))}
    items = []
    for r in csv.DictReader(open(INVENTORY, newline="", encoding="utf-8-sig")):
        code = (r.get("code") or "").strip()
        desc = (r.get("description") or "").strip()
        try:
            qty = int(float((r.get("qty") or "0").strip() or 0))
        except ValueError:
            qty = 0
        if not code or not desc or qty <= 0:
            continue
        m = master.get(code.lower(), {})
        disc = (m.get("discontinued") or "").strip() in ("1", "yes", "true")
        if not disc and (end_year(desc) or 9999) > LEGACY_YEAR_CUTOFF:
            continue  # still-current stock stays private
        items.append({
            "code": code,
            "sx": (m.get("sx_code") or "").strip(),
            "desc": desc,
            "qty": qty,
            "dept": (m.get("department") or "").strip(),
            "disc": disc,
        })
    items.sort(key=lambda i: i["desc"])

    logo = base64.b64encode(open(LOGO, "rb").read()).decode()
    updated = datetime.date.fromtimestamp(os.path.getmtime(INVENTORY)).strftime("%-d %B %Y")

    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    html = (tpl
            .replace("__ITEMS__", json.dumps(items, separators=(",", ":")))
            .replace("__LOGO__", logo)
            .replace("__UPDATED__", updated)
            .replace("__COUNT__", str(len(items))))
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"index.html written: {len(items)} items, list dated {updated}")


if __name__ == "__main__":
    main()
