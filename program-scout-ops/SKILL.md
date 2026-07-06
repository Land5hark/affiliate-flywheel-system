---
name: program-scout-ops
description: Find and record where to actually obtain affiliate commissions for specific products — searching major networks (Amazon Associates, ShareASale, CJ, Impact, Rakuten, Awin, ClickBank) down to individual manufacturer direct programs — and store results in a persistent, growing registry so the research compounds across niches instead of being redone every time. Use whenever the user asks where to find affiliate programs for a product, wants to identify which network carries a brand, needs to check commission rates/cookie durations before committing content to a product, or is building out monetization for a niche or product list. Always the fourth step after product-map-ops (list products) and product-scout-ops (score economics) — take the highest-scoring products and find where to actually sign up.
---

# Program Scout Ops

Finds the actual affiliate program(s) behind a specific product or product category, and records the finding in a persistent registry file so it's never re-researched from scratch. This is the step that turns a scored product list into money — a product with great theoretical economics is worthless until you know which program to join and get approved.

## Position in the pipeline

1. `product-map-ops` → exhaustive list of every product in the niche
2. `product-scout-ops` → scores each for commission economics (theoretical, based on typical program types)
3. **`program-scout-ops` (this skill)** → finds the *actual, real, current* program for each high-scoring product and records it
4. Content gets built and linked against verified, real programs — never invented ones

## Workflow

For each product/brand from the prioritized list (usually the ones that cleared 3.5+ in product-scout-ops):

1. **Check the major networks first** — see `references/network-directory.md` for the full list and search patterns. Search each candidate network's merchant directory or use the site-search pattern (`"[brand]" site:shareasale.com OR site:cj.com` etc.) via web search.
2. **Check for a direct manufacturer program** — visit the brand's own website, check the footer for "Affiliates" / "Partners" / "Affiliate Program." Direct programs often pay better than the same product via a generalist network.
3. **Check for a niche-specific specialty network or marketplace** — established hobby/trade niches often have one dedicated retailer network (worth asking the user if they already know of one, since they may have prior domain knowledge from running similar sites).
4. **Record every finding in the registry**, whether or not it panned out — a "checked, no program found" entry is still valuable so nobody re-checks it in six months.
5. **Flag anything requiring action** — most affiliate programs require an application and approval, not instant signup. Call out which ones need the user to actually go apply.

## The registry

A CSV file that persists across every niche and blog, not just the current project — this is the compounding asset. Template at `references/program-registry-template.csv` with these columns:

`product_or_category, niche, brand_or_merchant, network, commission_structure, cookie_duration, application_status, program_url, last_verified, notes`

**Where to keep it:** if working inside a project repo (like an OpenClaw workspace or a blog repo), store it at a stable path such as `data/affiliate-program-registry.csv` in the root workspace/repo — not inside any single niche blog's own repo, since the whole point is that it's shared across all future blogs. If no such shared location exists yet, ask the user where they want the master copy to live, then always append to that same file going forward rather than creating a new one per session.

**Always check the existing registry before researching from scratch.** If a brand or product category is already in there with a `last_verified` date less than ~6 months old, use the stored data instead of re-searching — only re-verify if it's old, contradicts something the user just told you, or the entry says "not found" and the user thinks that's changed.

**application_status values:** `not_researched`, `program_found_not_applied`, `applied_pending`, `approved_active`, `applied_rejected`, `no_program_exists`

## Output format

When reporting findings for a batch of products, output a table matching the registry columns, then explicitly separate:
- **Ready to link now** (already approved/active programs)
- **Needs application** (found the program, user needs to apply — give direct links)
- **No program found** (dead end for that specific product — go back to product-map-ops/product-scout-ops for an alternative in the same slot)

## Important caveats

- **Never invent a program, URL, commission rate, or cookie duration.** Web search to verify. If you can't verify, say "found evidence of a program but couldn't confirm current terms — verify directly before applying" rather than presenting a plausible-sounding number as fact.
- **Application approval is not guaranteed** — a "program found" entry means a path exists, not that the user will be accepted. Some programs (especially manufacturer-direct ones) require existing traffic or sales history.
- **Terms change** — a `last_verified` date matters. Don't treat a 2-year-old registry entry as current without flagging it for re-check.
- Legal/compliance note: remind the user (briefly, not repeatedly) that affiliate relationships require FTC disclosure on the site — this is a content/compliance detail, not something this skill enforces, but worth a one-line mention when programs go live.
