---
name: portfolio-flywheel-ops
description: Orchestrate a self-replicating portfolio of hyper-niche affiliate blogs — track each blog's lifecycle from candidate to graduated, detect when a blog hits its graduation trigger (first sale or article count threshold) and should spawn the next niche/blog, run centralized health monitoring across the whole portfolio so silent failures get caught automatically, and enforce content-differentiation guardrails that reduce Google spam-policy risk at scale. Use whenever the user talks about "the flywheel," scaling to multiple blogs, spawning a new niche automatically, checking on the health of the whole portfolio, or setting up autopilot/hands-off affiliate blog operations. This is the top-level orchestration layer above niche-scout-ops, product-map-ops, product-scout-ops, program-scout-ops, and affiliate-graph-db — it decides *when* to run those skills again, not what they each individually do.
---

# Portfolio Flywheel Ops

The top of the stack. This skill doesn't research niches or write content — it watches the whole portfolio, decides when a blog has proven itself and should trigger the next one, and catches silent failures before they compound across dozens or hundreds of sites.

## The flywheel, end to end

1. **niche-scout-ops** finds and scores a candidate niche
2. **product-map-ops** + **product-scout-ops** map and score the niche's product ecosystem
3. **program-scout-ops** finds real affiliate programs for the top products
4. **affiliate-graph-db** stores all of it
5. A new blog repo is scaffolded (from a template — see Scaffolding below) and registered via `blog_lifecycle.py register`
6. A dedicated agent trio (Researcher/Writer/Editor — see `references/agent-trio-roles.md`) is spawned for that blog and runs indefinitely
7. As the blog publishes, the Editor reports metrics via `blog_lifecycle.py update-metrics`
8. When the blog hits its **graduation trigger** (first confirmed sale, or 50 articles — whichever comes first), `check-graduation` flags it
9. On graduation, go back to step 1 for the next niche — the flywheel turns

## Setup

This skill's database tables live in the **same SQLite file** as `affiliate-graph-db` — pass the same `--db` path to both, so blogs, niches, products, and programs are all one connected graph, not separate silos.

```
python scripts/blog_lifecycle.py --db <path> init
```

## Running the portfolio

**Register a new blog once it's built:**
```
python scripts/blog_lifecycle.py --db <path> register "blog-name" --niche "Niche Name" --repo-url "https://github.com/..." --status active
```

**After each publishing cycle, report metrics (the Editor's job — see agent-trio-roles.md):**
```
python scripts/blog_lifecycle.py --db <path> update-metrics "blog-name" --articles 42 --sales 1
```

**Check whether a specific blog should graduate:**
```
python scripts/blog_lifecycle.py --db <path> check-graduation "blog-name"
```

**Graduate it and kick off the next cycle:**
```
python scripts/blog_lifecycle.py --db <path> graduate "blog-name" --trigger first_sale
```
Follow this immediately by re-invoking `niche-scout-ops` on a fresh candidate batch — graduation isn't just a status flag, it's the signal to go build the next blog.

**Portfolio-wide health check — run this on a schedule (weekly minimum), not just when something feels wrong:**
```
python scripts/health_monitor.py --db <path> run --repos-root /path/to/all/blog/repos
```
This flags any blog with no recent commits or no recent metrics updates — the exact failure mode that let the backup system go silent for two months undetected. At portfolio scale, this check is what stands in for you manually noticing something's wrong.

## Scaffolding a new blog

When a new niche clears both niche-scout-ops and product-scout-ops thresholds:
1. Copy the proven repo template (e.g., the balcony-drip-guide structure: Hugo site, agent bootstrap files, memory folders) to a new repo named for the niche
2. **Vary the template meaningfully** per `references/content-differentiation-checklist.md` — don't ship byte-identical themes across every blog
3. Populate its content-planner/memory with the niche's data pulled from `affiliate-graph-db`
4. Spin up its dedicated Researcher/Writer/Editor trio per `references/agent-trio-roles.md`
5. Register it here with `blog_lifecycle.py register`

## Graduation thresholds

Defaults in `blog_lifecycle.py`: first confirmed sale OR 50 published articles, whichever comes first. These are starting points, not fixed law — revisit them once you have real data from the first few blogs on what article count or timeline actually correlates with a blog being a real earner versus a dud that happened to hit 50 articles without converting.

## Cost and revenue tracking

`update-metrics` accepts `--token-cost` and `--revenue` — use these. At small scale, "is this profitable" is a vibe. At portfolio scale, it's the only thing that tells you whether to keep spawning blogs at the same pace, slow down, or reconsider the whole model. Don't let this field sit empty once you have more than 2-3 active blogs.

## Important caveats

- **This skill decides *when* to act, not *whether the underlying research is any good*.** Garbage niche/product data in affiliate-graph-db produces garbage graduation decisions. Keep the upstream skills honest (verified data, no invented programs) — this layer trusts what they recorded.
- **Graduation triggers are proxies, not guarantees of quality.** A blog hitting 50 articles with zero sales is not actually a success — treat article-count graduation as "worth a manual look," not an automatic green light to spawn the next blog with full confidence. Sales-triggered graduation is the stronger signal.
- **Read `references/content-differentiation-checklist.md` before scaffolding blog #2 and revisit it periodically** — this is the mitigation for the biggest structural risk in the whole flywheel model (Google spam policy exposure at scale), and it degrades in value if treated as a one-time read rather than an ongoing constraint on how the trios operate.
- Affiliate program applications are not automatable (see program-scout-ops) — factor recurring human admin time into the flywheel's real velocity, don't assume it scales for free.
