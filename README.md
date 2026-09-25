# Selby clearance stock — public list

Public, read-only list of clearance glass stock offered by My Glass Selby
to other fitment centres. Completely separate from the fitment scheduler:
no server, no database, no logins — one static page with the stock list
baked in.

Live at: https://stock.oneglass.co.za
(the old https://michealbotes.github.io/selby-legacy-stock/ still redirects here)

The custom domain is the `CNAME` file in this folder, backed by a CNAME
record `stock.oneglass.co.za` -> `michealbotes.github.io` in the
oneglass.co.za zone at domains.co.za. Never push a change to that file
before the matching DNS record resolves: Pages 301s the github.io URL to
whatever `CNAME` says, so a wrong or missing record takes the page dark
for the centres using it. Branding stays My Glass on purpose, despite the
oneglass.co.za domain.

## Refreshing

Three gitignored spreadsheets next to `build.py` are the sources (bin
locations, costs and prices never reach the page or this repo):

- `selby-inventory.xlsx` — the emailed Selby clearance list; defines which
  Selby items are offered. Nothing is ever added from the on-hand file.
- `selby-on-hand.xlsx` — live-Xero stock-on-hand export; offered items
  missing from it are removed, kept items take its current quantity.
- `x-stock.xlsx` — the second stock list; its rows are marked with an X
  on the page.

Copy the new export(s) over the file(s) above, then:

    python3 build.py
    git add index.html
    git commit -m "stock refresh" -- index.html

Do NOT push — hand the commit to the deploy session (pushes to this repo
deploy GitHub Pages).

`build.py` cross-references the scheduler's `master-stock.csv` only to add
SX codes, departments (for the glass-type filter) and discontinued tags.
Tools, consumables and wiper blades are kept off the page by the exclusion
rules at the top of `build.py`.
