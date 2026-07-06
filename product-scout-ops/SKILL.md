---
name: product-scout-ops
description: Score and rank affiliate product categories on commission economics (payout structure, cookie duration, repeat-purchase potential, program reliability, buyer research-intent fit) — separate from niche/topic scoring. Use whenever the user wants to find "the best products to sell," evaluate whether a product line is worth building affiliate content around, compare affiliate programs, or find the intersection between a good niche and good product economics (the "goldilocks zone"). Push toward using this any time affiliate product selection, commission structure, or "what should I promote" comes up, even without the user naming this skill directly. Pairs with niche-scout-ops — run both and cross-reference before committing to a new affiliate site.
---

# Product Scout Ops

Scores affiliate product categories on their economics, independent of whether the surrounding topic/niche is any good. A great niche with weak product economics still fails; this skill catches that, and the companion `niche-scout-ops` skill catches the reverse case (great product, oversaturated topic).

## Why this is a separate skill from niche scoring

Niche viability (search volume, competition, content depth) and product economics (commission, repeat purchase, cookie length) are independent variables. A niche can score 5/5 on niche-scout-ops and still be a bad business if the only products in it pay 3% once with a 24-hour cookie. Score both, then look at where they intersect.

## Scoring Rubric

Score each candidate product category 0-5 on each dimension:

| Dimension | Weight | 5 = Best | 0 = Worst |
|---|---|---|---|
| Commission structure | 25% | Recurring/subscription commission, or high-ticket ($150+) at 8%+ | Flat low-ticket item under $30 at under 5% |
| Cookie duration | 20% | 30-90 day dedicated-program cookie | 24-hour cookie (standard Amazon Associates) |
| Repeat purchase / consumable | 25% | Buyer reorders regularly (filters, refills, cartridges, subscriptions) | One-time durable purchase, no reorder |
| Program reliability | 15% | Established direct affiliate program or reputable network (ShareASale, CJ, Impact), consistent payout history | Obscure/unverified program, no track record |
| Research-intent fit | 15% | Buyers actively compare options before purchasing ("best X," "X vs Y" search behavior) | Impulse-buy category, spec-driven commodity purchase |

**Weighted score** = (Commission×0.25 + Cookie×0.20 + Repeat×0.25 + Reliability×0.15 + Research×0.15) — max 5.0

**Go threshold: 3.5+**, same convention as niche-scout-ops for comparability.

## The Goldilocks Zone (combine with niche-scout-ops)

Plot each candidate on both scores:

```
                    WEAK NICHE SCORE          STRONG NICHE SCORE
                    (saturated/thin)          (niche-scout-ops 3.5+)

STRONG PRODUCT      Skip — good product,      ★ BUILD THIS — rare,
SCORE (3.5+)        no room to compete          move fast when found

WEAK PRODUCT        Skip entirely —           Content is easy but
SCORE               worst of both worlds        revenue ceiling is low;
                                                  only pursue as a
                                                  volume/portfolio play
```

Only greenlight a new site when **both** scores clear 3.5. A niche-only or product-only high score is a yellow flag, not a green one.

## Output format

Always output a ranked table:

| Rank | Product Category | Commission | Cookie | Repeat | Reliability | Research Fit | Weighted Score | Verdict |
|---|---|---|---|---|---|---|---|---|

If the user has also run niche-scout-ops on related niches, produce the combined 2x2 placement for each niche+product pairing and call out anything landing in the top-left "build this" quadrant.

## Important caveats

- **Don't invent specific commission percentages or named program terms.** Affiliate program rates change and vary by approval tier. If you don't have verified current data (web search the program's actual affiliate page), give a reasoned estimate and flag it as unverified rather than stating a precise number as fact.
- Amazon Associates is usually a reasonable default inclusion for trust/conversion even when its commission/cookie scores are weak — the point isn't to exclude it, it's to pair it with at least one higher-margin dedicated program rather than relying on Amazon alone.
- This skill evaluates product economics in the abstract. It does not verify that a specific merchant's affiliate program is currently accepting applications, active, or paying out — confirm that separately before committing content to a program.
