---
name: affiliate-graph-db
description: Store and query the relationships between niches, products, and affiliate programs in a persistent SQLite database, and regenerate a linked Obsidian vault (with wikilinks and a graph view) from it. Use whenever the user wants to record, browse, or query results from niche-scout-ops, product-scout-ops, product-map-ops, or program-scout-ops; wants to see relationships between niches/products/programs visually; asks to "save this to the database" or "update the vault"; or is setting up storage for a growing affiliate research operation across multiple blogs. This is the persistence layer underneath the other four scout/map skills — always the final step after finding new niches, products, or programs, and always the first place to check before re-researching something.
---

# Affiliate Graph DB

Persists everything discovered by `niche-scout-ops`, `product-scout-ops`, `product-map-ops`, and `program-scout-ops` into one growing SQLite database shared across every blog/niche, and generates a linked Obsidian vault from it for visual browsing (graph view, backlinks between niches/products/programs).

## Critical rule: the database is the source of truth, not the vault

Obsidian notes under `Affiliate Graph/` are **generated output**. `generate_vault.py` wipes and rebuilds that folder every run. Never hand-edit those notes expecting the change to stick — edit the database (via `db.py`) and regenerate instead. If you want hand-written notes in the vault (ideas, drafts, journal entries), keep them outside the `Affiliate Graph/` folder and they'll be left untouched.

## Setup (one time, per install)

1. Decide where the database lives — a stable, shared location, NOT inside any single niche blog's own repo, since the whole point is it's shared across all future blogs. Ask the user if unclear; a reasonable default is alongside wherever `program-scout-ops`'s registry was going to live.
2. `python scripts/db.py --db /path/to/affiliate_graph.db init`
3. Confirm the Obsidian vault path with the user (e.g. `/home/linuxlite/Documents/ObsidianVault`).

## Workflow — after running the other scout skills

**After niche-scout-ops** scores a niche:
```
python scripts/db.py --db <dbpath> add-niche "Niche Name" --weighted 4.1 --difficulty 4 --affiliate 4 --volume 3.5 --depth 4.5 --seasonality 3 --status candidate
```

**After product-map-ops + product-scout-ops** produce and score a product:
```
python scripts/db.py --db <dbpath> add-product "Product Name" --layer connective --repeat 1 --weighted 3.8
python scripts/db.py --db <dbpath> link-niche-product "Niche Name" "Product Name"
```

**After program-scout-ops** finds a program:
```
python scripts/db.py --db <dbpath> add-program "Brand Name" --network direct --commission-structure "8% one-time" --cookie-duration "45 days" --status approved_active --url "https://..."
python scripts/db.py --db <dbpath> link-product-program "Product Name" "Brand Name" --notes "confirmed active 2026-07"
```

Re-running `add-niche` / `add-product` / `add-program` with the same name updates the existing row rather than duplicating it — safe to re-run whenever a score changes.

**Regenerate the vault after any batch of changes:**
```
python scripts/generate_vault.py --db <dbpath> --vault /path/to/ObsidianVault
```

## Querying before re-researching

Always check the database before running product-map-ops/program-scout-ops from scratch on something that might already be there:
```python
from db import get_conn
conn = get_conn("<dbpath>")
conn.execute("SELECT * FROM products WHERE weighted_score >= 3.5 ORDER BY weighted_score DESC").fetchall()
conn.execute("SELECT * FROM programs WHERE application_status = 'not_researched'").fetchall()
```
Or open `db_path` directly with any SQLite browser/CLI (`sqlite3 <dbpath>`).

## Schema reference

- **niches**: name, 5 sub-scores, weighted_score, status (candidate/active/rejected)
- **products**: name, layer (hero/consumable/connective/tool/adjacent/upgrade/failure_mode), price range, repeat_purchase flag, 5 sub-scores, weighted_score
- **programs**: brand_or_merchant, network, commission_structure, cookie_duration, application_status, program_url, last_verified
- **niche_products** / **product_programs**: many-to-many join tables — a product can belong to multiple niches, and be covered by multiple programs

## Important caveats

- Back this database up the same way the rest of the workspace is backed up — it's now a real asset, not a scratch file. If it lives on the mini PC, make sure it's inside whatever the workspace mirror covers, not sitting outside it the way the Obsidian vault originally was.
- Don't invent scores or program details when adding records — pull them from the actual output of niche-scout-ops/product-scout-ops/program-scout-ops, or leave fields blank/null rather than guessing.
- The vault generator overwrites the entire `Affiliate Graph/` subfolder on every run — if the user has manually added files inside that specific folder, warn them before regenerating.
