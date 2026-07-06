# Per-Blog Agent Trio — Role Specifications

Every blog that graduates from candidate to active status gets its own instance of these three roles. They are scoped to one blog only — their memory, schedule, and workspace should not bleed into other blogs' trios. This is what makes the flywheel "hands-off": once spun up, a trio runs indefinitely without you touching it.

## Researcher

**Job:** Keep the content pipeline fed with new, differentiated article angles for this specific niche.

**Inputs it should draw on:**
- The niche's entry in `affiliate-graph-db` (product list from product-map-ops, scored products, linked programs)
- Actual search/forum activity in the niche (real questions people are asking, not recycled "best X" templates)
- Competitor content gaps — what isn't being covered well by existing sites in this niche

**Output:** A prioritized queue of article topics, each tagged with which product(s)/program(s) it should link to, handed to the Writer.

**Guardrail:** Should refuse to queue a topic that's a near-duplicate of an already-published article on this blog (check existing article list first) or a generic template swap of an article structure used on a *different* blog in the portfolio (see Content Differentiation Checklist — cross-blog structural similarity is a real deindexing risk at scale).

## Writer

**Job:** Draft the article from the Researcher's queue.

**Guardrails (non-negotiable, tied to Google policy risk — see references/content-differentiation-checklist.md):**
- No boilerplate structure copy-pasted from another blog in the portfolio, even a different niche. Each blog's voice, structure, and formatting choices should read as genuinely distinct.
- Every article must contain at least one piece of specific, verifiable, non-generic content — a real comparison, a real number, a real edge case — not purely templated "in conclusion, X is great for Y" filler.
- Affiliate links only to products/programs verified in `affiliate-graph-db` — never link to an unverified or invented program.
- FTC affiliate disclosure included per the site's standard disclosure block.

## Editor

**Job:** Final review gate before publish — the last line of defense against the flywheel scaling a mistake across hundreds of sites before anyone notices.

**Checklist before approving publish:**
1. Does this read as genuinely differentiated from other portfolio blogs' content, not just find-and-replaced niche terms in the same template?
2. Are all affiliate links pointing to programs marked `approved_active` in the database (not `not_researched` or `applied_pending`)?
3. Does the article contain real specificity (see Writer guardrails) rather than generic filler?
4. Is the disclosure present?

**Also owns:** reporting article count and any confirmed sale events back to `blog_lifecycle.py update-metrics`, since that's what feeds the graduation trigger. If the Editor doesn't report, the flywheel doesn't turn.

## Scheduling note

A reasonable per-blog cadence to start with: Researcher runs weekly, Writer/Editor run against whatever's queued, metrics update after each publish. Tune based on actual output quality and cost-per-article once you have data from 2-3 active blogs — don't guess at scale before you've watched one or two trios run for a month.
