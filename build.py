#!/usr/bin/env python3
"""Bake the public Selby stock-clearance page.

Source of truth is the emailed clearance list, `selby-inventory.xlsx` in this
folder (columns: Bin Location, Item Code, Item Description, System Qty).
EVERY item on it with qty > 0 goes on the page — no legacy/year filtering;
the list itself is the decision of what's offered. Bin locations stay
private (the xlsx is gitignored; only the baked index.html is published).

The scheduler's master catalogue is used only to enrich rows with SX codes,
departments (for the glass-type filter) and discontinued tags.

Refreshing after a new list:

    cp ~/Downloads/"Selby Inventory .xlsx" selby-inventory.xlsx
    python3 build.py
    git add -A && git commit -m "stock refresh" && git push
"""
import base64
import csv
import datetime
import json
import os

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "selby-inventory.xlsx")
MASTER = os.path.join(HERE, "..", "fitment-scheduler", "catalogue", "master-stock.csv")
LOGO = os.path.join(HERE, "..", "fitment-scheduler", "public", "myglass-logo.png")

# Not offered to other centres (Micheal, 2026-07-22) — survives list refreshes
EXCLUDE_CODES = {"104270", "19-0422", "WT01"}
EXCLUDE_DESC_PREFIXES = ("WB FLAT", "WB STD")


def main():
    master = {r["wd_code"].strip().lower(): r
              for r in csv.DictReader(open(MASTER, newline="", encoding="utf-8-sig"))}
    ws = openpyxl.load_workbook(SOURCE, data_only=True).worksheets[0]
    header = [str(c or "").strip().lower() for c in next(ws.iter_rows(min_row=1, max_row=1, values_only=True))]
    col = {name: header.index(name) for name in ("item code", "item description", "system qty")}

    items = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        code = row[col["item code"]]
        if code is None:
            continue
        # Numeric codes come back as ints/floats; 1028.0 must publish as "1028"
        code = str(int(code)) if isinstance(code, (int, float)) else str(code).strip()
        desc = str(row[col["item description"]] or "").strip()
        try:
            qty = int(float(row[col["system qty"]] or 0))
        except (TypeError, ValueError):
            qty = 0
        if not code or not desc or qty <= 0:
            continue
        if code in EXCLUDE_CODES or desc.upper().startswith(EXCLUDE_DESC_PREFIXES):
            continue
        m = master.get(code.lower(), {})
        items.append({
            "code": code,
            "sx": (m.get("sx_code") or "").strip(),
            "desc": desc,
            "qty": qty,
            "dept": (m.get("department") or "").strip(),
            "disc": (m.get("discontinued") or "").strip() in ("1", "yes", "true"),
        })
    items.sort(key=lambda i: i["desc"])

    logo = base64.b64encode(open(LOGO, "rb").read()).decode()
    updated = datetime.date.fromtimestamp(os.path.getmtime(SOURCE)).strftime("%-d %B %Y")

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
