# Example Output — Tested End-to-End Run

This is real output from a full pipeline test run against sample data (a portable
SQLite database and generated Obsidian vault), run before this system was deployed
against the production site. Included here so the architecture claims below are
backed by something that actually executed, not just designed on paper.

## 1. Database + lifecycle test

```
$ python db.py --db /tmp/test.db init
Initialized database at /tmp/test.db

$ python db.py --db /tmp/test.db add-niche "Balcony Drip Irrigation" --weighted 4.1 \
    --difficulty 4 --affiliate 4 --volume 3.5 --depth 4.5 --seasonality 3
Added/updated niche: Balcony Drip Irrigation

$ python db.py --db /tmp/test.db add-product "Barbed Tee Fitting" --layer connective \
    --repeat 1 --weighted 3.8
Added/updated product: Barbed Tee Fitting

$ python db.py --db /tmp/test.db add-program "Drip Depot" --network direct \
    --commission-structure "8% one-time" --status approved_active
Added/updated program: Drip Depot

$ python db.py --db /tmp/test.db link-product-program "Barbed Tee Fitting" "Drip Depot" \
    --notes "confirmed active"
Linked product 'Barbed Tee Fitting' <-> program 'Drip Depot'
```

## 2. Generated Obsidian note (auto-produced from the database, not hand-written)

```markdown
---
layer: connective
repeat_purchase: true
weighted_score: 3.8
---

# Barbed Tee Fitting

**Layer:** connective
**Repeat purchase:** Yes
**Est. price range:** None–None

## Product Economics Scores
- Commission structure: None
- Cookie duration: None
- Repeat purchase potential: None
- Program reliability: None
- Research-intent fit: None
- **Weighted score: 3.8**

## Found in niches
- [[Balcony Drip Irrigation]]

## Available affiliate programs
- [[Drip Depot]] (direct, approved_active) — confirmed active
```

Every `[[bracketed]]` reference is a real Obsidian wikilink, so opening this vault
renders a navigable graph between niches, products, and programs — generated
automatically from relational data rather than maintained by hand.

## 3. Blog lifecycle / graduation trigger test

```
$ python blog_lifecycle.py --db /tmp/test.db register "balcony-drip-guide" \
    --niche "Balcony Drip Irrigation" --status active

$ python blog_lifecycle.py --db /tmp/test.db update-metrics "balcony-drip-guide" \
    --articles 40 --sales 0 --last-commit-at "2026-05-06T21:40:01Z"

$ python blog_lifecycle.py --db /tmp/test.db check-graduation "balcony-drip-guide"
'balcony-drip-guide' does not yet meet graduation criteria (articles: 40/50, sales: 0/1)

$ python blog_lifecycle.py --db /tmp/test.db update-metrics "balcony-drip-guide" \
    --articles 55 --sales 1
$ python blog_lifecycle.py --db /tmp/test.db check-graduation "balcony-drip-guide"
'balcony-drip-guide' MEETS graduation criteria: first_sale, article_count
Run `graduate` to fire the next-blog trigger, or do it manually if you want a final review first.
```

## 4. Portfolio health monitor test

```
$ python health_monitor.py --db /tmp/test.db run
Health check complete — 1 blogs checked, 1 flagged.

⚠️  ALERTS:
  balcony-drip-guide:
    - no commits in 60 days (threshold: 7)
```

This last one is worth calling out specifically: this test run against sample
timestamps independently reproduced a real, previously-undetected problem in the
production system this architecture was built for — a backup automation job that
had silently stopped running two months prior. See the main README's "Engineering
Hurdle" section for the full story.
