# Selby clearance stock — public list

Public, read-only list of clearance glass stock on the shelf at My Glass
Selby, for other fitment centres. Completely separate from the fitment
scheduler: no server, no database, no logins — one static page with the
stock list baked in.

Live at: https://michealbotes.github.io/selby-legacy-stock/

## Refreshing after a new stock list

The source of truth is `selby-inventory.xlsx` in this folder (the emailed
clearance list: Bin Location, Item Code, Item Description, System Qty).
Every item on it with qty > 0 is published — no filtering; the list itself
decides what's offered. Bin locations never reach the page, and the xlsx is
gitignored so it stays off the public repo.

    cp ~/Downloads/"Selby Inventory .xlsx" selby-inventory.xlsx
    python3 build.py
    git add -A && git commit -m "stock refresh" && git push

`build.py` cross-references the scheduler's `master-stock.csv` only to add
SX codes, departments (for the glass-type filter) and discontinued tags.
