---
name: niche-scout-ops
description: Score and rank candidate micro-niches for affiliate content sites using a weighted rubric (search volume, keyword difficulty, competition, affiliate program availability, content depth, seasonality). Use this whenever the user wants to evaluate, compare, or choose between potential niches for a new affiliate blog, asks "is this a good niche," wants a ranked shortlist of niche ideas, or references niche scoring/validation for an affiliate site. Push toward using this any time niche selection for content/affiliate sites comes up, even if the user just says "help me find a niche" without naming the rubric.
---

# Niche Scout Ops

Evaluates whether a candidate topic is a viable foundation for a hyper-specific affiliate content site, using a weighted scoring rubric. Ported from an OpenClaw agent skill of the same name; produces the same scores so results are comparable across tooling.

## When to use this

- User has a list of candidate niches and wants them ranked
- User has one niche idea and wants a go/no-go call
- User says "find me some niche ideas" — in this case, generate 15-20 candidates first (see Sourcing Candidates below), then score all of them
- User references "the rubric," "niche-scout," or wants something "repeatable" for niche selection

## Scoring Rubric

Score each candidate 0-5 on each dimension, then apply weights:

| Dimension | Weight | 5 = Best | 0 = Worst |
|---|---|---|---|
| Difficulty (inverse of keyword difficulty) | 25% | KD < 15, wide open | KD > 60, dominated by authority sites |
| Affiliate availability | 25% | 3+ programs, mix of direct + Amazon, decent commission | 0-1 weak/no programs |
| Search volume | 20% | 1,000–10,000/mo core keyword cluster | Under 100/mo or over 50,000/mo (too saturated) |
| Content depth | 20% | 10+ distinct article angles without repeating | Fewer than 5 angles, topic exhausts fast |
| Seasonality (inverse) | 10% | Flat, evergreen demand year-round | Sharp single-season spike |

**Volume sweet spot note:** 100–10,000/mo is the original OpenClaw rubric's range; treat 1,000–10,000 as the strong core and 100–1,000 as acceptable-but-thin. Above ~50,000/mo, competition from established sites usually makes the difficulty score collapse anyway — don't double-penalize, just let the difficulty dimension catch it.

**Weighted score** = (Difficulty×0.25 + Affiliate×0.25 + Volume×0.20 + Depth×0.20 + Seasonality×0.10) — max 5.0

**Go threshold: 3.5+.** Below 3.0, reject. Between 3.0-3.5, flag as marginal — only pursue if it fills a specific portfolio gap (e.g., a second niche in a season the first one is weak in).

## Sourcing candidates

If the user doesn't already have candidates, generate them by combining:
- A high-consumable/repeat-purchase product category (see product-scout-ops skill for what makes a product line strong) with a specific, narrow use case or audience (e.g., not "gardening" but "container gardening for apartment balconies")
- Adjacent niches to a proven winner — same buyer, different room/season/problem
- Forum/subreddit/Reddit search for recurring "what's the best X for Y" questions with no single dominant answer

Aim for 15-20 candidates before scoring — scoring one at a time in isolation produces noisy go/no-go calls with nothing to compare against.

## Output format

Always output a ranked table:

| Rank | Niche | Difficulty | Affiliate | Volume | Depth | Seasonality | Weighted Score | Verdict |
|---|---|---|---|---|---|---|---|---|

Below the table, for the top 2-3 candidates, give a one-paragraph rationale and name 2-3 real affiliate programs if you can identify or plausibly infer them (flag if unverified — see note below).

## Important caveats

- **Search volume and keyword difficulty numbers are estimates unless the user has connected a real keyword tool** (Ahrefs, SEMrush, Google Keyword Planner). If you don't have live data, say so explicitly and give a reasoned estimate rather than presenting a fabricated-looking precise number — round to the nearest order of magnitude and flag it as an estimate.
- **Don't invent named affiliate programs with specific commission rates** unless you've verified them (web search) — misquoting a real program's terms is worse than saying "verify commission structure before committing."
- This skill scores niches. It does not score whether specific products within that niche have good affiliate economics — pair with `product-scout-ops` for that, and treat a niche as a genuine "build this" candidate only when both scores land in the strong range. See that skill's Goldilocks Zone framework.
