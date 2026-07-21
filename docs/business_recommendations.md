# Business Insights & Recommendations
## Flipkart Customer Sentiment & Product Intelligence Platform

**Dataset:** 162,183 cleaned product reviews across 22 product categories
**Methods:** SQL aggregation, Python/Pandas EDA, VADER sentiment scoring, windowed aspect-based sentiment analysis, LDA topic modeling

---

## Executive Summary

Star ratings alone significantly understate the complexity of customer sentiment on the platform. Text-based analysis reveals that dissatisfaction is concentrated in **specific, addressable root causes** — primarily fabric/material quality, product durability, and shipping damage — rather than being evenly spread across products. The three highest-priority findings below represent an estimated combined exposure across **40,000+ reviews** and point to concrete, ownable actions for Category Management, Product QA, and Operations respectively.

---

## Finding 1 — Fashion is the platform's weakest category, and the root cause is fabric quality, not sizing

**Data:** Fashion shows 24.7% negative sentiment (vs. 12.8% platform average) and the lowest average rating (3.70) of any category group. Footwear specifically is the single worst category (25.2% negative, 3.50 avg rating). Aspect-based sentiment analysis shows Material & Fabric complaints run at 38.4% negative within Fashion — nearly double the 24.7% platform-wide rate — while Size & Fit complaints (19.0%) and Comfort complaints (13.0%) are comparatively minor.

**Business Implication:** The intuitive assumption — that fashion complaints are mostly about sizing — is not supported by the data. Effort spent improving size charts or fit guides would address a secondary problem while leaving the primary one (perceived fabric/material quality) untouched.

**Recommendation:** Category Management should prioritize a fabric-quality and supplier audit for Fashion sellers, particularly Footwear, ahead of any sizing-related initiatives. *(n = 12,935 Fashion reviews; caveat: some sub-categories like Fashion-Women have low volume (n=471) and should be treated as directional, not conclusive.)*

---

Finding 2 — Unsupervised topic modeling surfaces complaint themes beyond generic "bad quality," including a distinct return/service-process issue

Data: LDA topic modeling (6 topics, negative reviews only) surfaced several distinct, independent themes not captured by keyword-based aspect analysis alone:

Return & service dissatisfaction (Topic 1: "worst," "days," "buy," "return," "service," "got," "time") — language centered on the return/support process itself, not just the product.
Installation & connectivity issues (Topic 2: "installation," "tv," "wifi," "sound," "working," "problem") — specific to smart appliances, distinct from general product-quality complaints.
Physical damage & functional defects (Topic 3: "water," "broken," "damage," "motor," "noise," "using") — appliances (e.g. motors, water-based products) arriving damaged or malfunctioning during use, not just cosmetic issues.
Material/build quality (Topic 6: "plastic," "cheap," "broken," "material," "used") — consistent with, and independently validating, the Material & Fabric finding from the aspect-based sentiment analysis (Finding 4).

One topic (Topic 5) showed weak separation, mixing positive and negative language ("good," "bad," "ok," "quality" together) — a known limitation of LDA when topic count isn't fully tuned to the data, noted here rather than forcing a clean label onto it.

Business Implication: These are largely different owners' problems. Return/service dissatisfaction points to the post-purchase support process, not the product itself; installation/connectivity issues point to smart-appliance onboarding UX; physical damage/functional defects point to manufacturing QA or logistics handling. Treating all of these as generic "bad quality" complaints would misdirect the fix to the wrong team.

Recommendation: Route return/service-themed complaints to Customer Support process owners for a return-experience audit. Route installation/connectivity language to the Product team responsible for smart-appliance setup and documentation. Route physical damage/motor-defect language to Product QA and Operations for a joint review of whether the issue originates in manufacturing or in-transit handling. Recommend re-running topic modeling with a smaller number of topics (e.g. 4-5) to check whether the weak Topic 5 separation resolves, before finalizing this as a recurring monitoring category.
---

## Finding 3 — Star ratings and review sentiment disagree in ~2.84% of reviews — ratings alone are an incomplete signal

**Data:** 4,677 reviews (2.84%) show a mismatch between star rating and text sentiment — most commonly a 4-5 star rating paired with negative-sentiment text.

**Business Implication:** Any team relying solely on average star rating to monitor product health is missing a meaningful subset of dissatisfied customers who rate generously out of habit but describe real problems in text. This affects roughly 1 in every 35 reviews platform-wide.

**Recommendation:** Product/CX teams should treat `rating_sentiment_mismatch = True` reviews as a distinct, prioritized queue for manual reading — these are disproportionately likely to contain specific, actionable complaint detail despite a misleadingly positive rating.

---

## Finding 4 — Material/Fabric and Battery are the two highest-friction aspects platform-wide

**Data:** Aspect-based sentiment analysis across all categories ranks aspects by negative-mention rate: Material & Fabric (24.7%), Battery (20.4%), Value for Money (20.3%), Delivery & Packaging (15.6%), Size & Fit (15.6%), Camera (11.9%), Color/Appearance (10.2%), Comfort (7.5%).

**Business Implication:** Battery performance is a meaningful pain point for Electronics despite Electronics having a relatively healthy overall negative rate (12.1%) — aggregate category metrics can mask a specific high-friction aspect within an otherwise healthy category.

**Recommendation:** Electronics category owners should review battery-related complaints as a distinct workstream even though the category's overall sentiment looks acceptable; aggregate health scores can hide aspect-level problems.

---

## Finding 5 — Premium products consistently outperform Budget products on sentiment, but the relationship is a threshold effect, not a linear trend

**Data:** Budget products (<₹500) show 13.96% negative sentiment vs. 10.30% for Premium (₹10,000+), with average rating rising from 3.96 to 4.34 across price bands. However, the direct Price–Rating correlation is only 0.08 — near zero.

**Business Implication:** The gain is concentrated in moving *out of* the Budget tier rather than a continuous "more expensive = better" trend across Mid/Upper-Mid/Premium. This distinction matters for how the finding should be used — it supports quality-floor initiatives for budget-tier sellers more than it supports pure premium-tier expansion.

**Recommendation:** Prioritize quality-floor enforcement (minimum QC standards) for Budget-tier listings, where the sentiment gap is largest, rather than assuming premium expansion alone will lift average sentiment.

---

## Finding 6 — Negative reviews are substantially longer than positive ones, confirming text mining adds information stars/length alone can't

**Data:** Negative reviews average 63.7 characters (median 34) vs. 47.0 for positive (median 19) and 29.4 for neutral.

**Business Implication:** Dissatisfied customers self-report more detail voluntarily. This is supporting evidence (not a standalone action item) for why continued investment in text-based analysis — rather than star ratings or review counts alone — is justified.

**Recommendation:** Use review length as a low-cost proxy signal for complaint richness when prioritizing which reviews to route for manual CX follow-up.

---

## Known Limitations (documented, not hidden)

- **Brand-level analysis is bit of a curveball. Brand was derived from the first word of the product name, which is reliable for real brand-led naming (Apple, Bosch, Dettol) but breaks down for Fashion, where names typically start with a style descriptor rather than a brand.
- **~3.4% of reviews contain irrecoverable character loss** (emojis partially or fully replaced with literal `?` characters before this dataset was exported). Confirmed unfixable via encoding repair tools; does not affect sentiment scoring since text cleaning strips non-alphabetic characters.
- **No native date field exists in the source data**, so time-trend analysis (e.g. "are complaints increasing month over month") is out of scope for this version and noted as future work rather than simulated.

---

## Suggested Future Work
- Time-series complaint tracking (pending a reliable date field or a fresh data pull that includes one)
- Fake/incentivized review detection
- Transformer-based (e.g. DistilBERT) sentiment scoring as a comparison point against VADER, particularly for sarcasm-sensitive cases
- Proper brand-matching against a maintained brand list rather than first-word extraction