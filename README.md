# Selby legacy stock — public list

Public, read-only list of legacy / discontinued glass stock on the shelf at
My Glass Selby, for other fitment centres. Completely separate from the
fitment scheduler: no server, no database, no logins — one static page with
the stock list baked in.

Live at: https://michealbotes.github.io/selby-legacy-stock/

## Refreshing after a new stock export

Drop the new export at `../fitment-scheduler/catalogue/selby-inventory.csv`, then:

    python3 build.py
    git add -A && git commit -m "stock refresh" && git push

`build.py` keeps only legacy items: flagged discontinued in the master
catalogue, or fitting vehicles whose production ended 2010 or earlier
(`LEGACY_YEAR_CUTOFF`).
