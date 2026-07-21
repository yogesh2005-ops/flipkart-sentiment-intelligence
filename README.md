# flipkart-sentiment-intelligence
End-to-end BI project analyzing 162K+ Flipkart reviews using SQL, Python NLP (VADER, aspect-based sentiment, LDA), and Power BI to uncover product quality and customer satisfaction insights.
# Flipkart Customer Sentiment & Product Intelligence Platform

An end-to-end business intelligence project that turns 162,183 unstructured Flipkart product reviews into structured, actionable insight — built to answer questions real e-commerce teams (Customer Experience, Category Management, Product, Operations) actually ask, not just to report sentiment percentages.

[Dashboard Preview]<img width="1954" height="1027" alt="image" src="https://github.com/user-attachments/assets/7e66a155-d8b9-42ef-b2b9-d6a502a9dc85" />

---

## Business Problem

Star ratings alone don't explain *why* customers are satisfied or dissatisfied — a 3-star average could mean "great product, terrible delivery" or "cheap materials, fine service." Flipkart generates millions of reviews containing this exact signal, but it goes largely unused because it's unstructured text.

This project builds a pipeline that converts raw review text into structured sentiment, aspect-level complaint themes, and category/brand-level KPIs — the kind of intelligence that lets Category Management, Customer Experience, and Operations teams act on specific, evidence-backed problems instead of guessing from an average rating.

**Business questions this project answers:**
- Which product categories have the worst customer sentiment, and *why* specifically?
- What are customers actually complaining about — sizing, material, delivery, battery life?
- Do star ratings reliably reflect what customers write, or do they diverge?
- Does price correlate with satisfaction, and if so, how?

---

## Key Findings

**1. Fashion is the platform's weakest category — and the root cause is fabric quality, not sizing.**
Fashion shows 24.7% negative sentiment (vs. 12.8% platform average); Footwear alone is the single worst category at 25.2% negative. Aspect-based sentiment analysis shows Material & Fabric complaints run at **38.4% negative within Fashion** — nearly double the 24.7% platform-wide rate — while Size & Fit complaints are a comparatively minor 19.0%. The intuitive assumption (fashion complaints = sizing problems) is not supported by the data.

**2. Unsupervised topic modeling surfaced two complaint themes invisible to keyword-based analysis.**
LDA topic modeling on negative reviews independently discovered a "premature failure" theme (products failing within months of purchase — a durability/QA issue) and a "shipping damage" theme (items arriving already broken — a logistics issue), each distinct from general quality complaints and requiring different owners to fix.

**3. Star ratings and review sentiment disagree in 2.84% of reviews (4,677 reviews).**
Most commonly, a 4-5 star rating paired with negative-sentiment text — customers rating generously out of habit while describing real problems. Any team monitoring only average star rating is missing this signal.

**4. Material & Fabric and Battery are the two highest-friction aspects platform-wide** (24.7% and 38.4% negative mention rate respectively), identified via windowed aspect-based sentiment analysis across 8 tracked product aspects.

**5. Premium products outperform Budget products on sentiment, but it's a threshold effect, not a linear trend.** Budget (<₹500) shows 13.97% negative sentiment vs. 10.30% for Premium (₹10,000+), while the raw Price–Rating correlation is only 0.08 — the gain is concentrated in moving *out of* the Budget tier, not a smooth "more expensive = better" relationship.

Full writeup with supporting data: [`docs/business_recommendations.md`](docs/business_recommendations.md)

---

## Dashboard Preview

| Executive Overview |  

 <img width="1954" height="1027" alt="image" src="https://github.com/user-attachments/assets/e684ad93-171f-4f4b-9b33-799706052ed7" />
 | Category Brand | <img width="1309" height="765" alt="image" src="https://github.com/user-attachments/assets/d8521f6c-cca7-40fd-937f-58be3188db5d" />
 | NLP Insights | <img width="1333" height="761" alt="image" src="https://github.com/user-attachments/assets/a41db129-69e1-4a49-b5cf-2f9e108bbf69" />
 




| Price Intelligence | <img width="1317" height="751" alt="image" src="https://github.com/user-attachments/assets/09597898-d255-461c-94dc-db0929cdc40d" />



---

## Architecture

```
Raw CSV (Kaggle)
      │
      ▼
Python — Encoding Repair, Deduplication, Null Handling  (src/01_data_cleaning.py)
      │
      ▼
Python — Feature Engineering (Category, Category_Group, Brand extraction)
      │
      ▼
Python — NLP (VADER Sentiment, Aspect-Based Sentiment, LDA Topic Modeling)  (src/02_nlp_sentiment.py)
      │
      ▼
SQL Server — Structured Storage, Business Query Layer
      │
      ▼
Power BI — 4-Page Executive Dashboard
      │
      ▼
Business Recommendations
```

**Why this shape:** cleaning and NLP feature extraction happen in Python (where sentiment models and text processing belong), the result is loaded into SQL Server as a queryable business layer, and Power BI consumes both the row-level table and pre-aggregated summary tables for fast, clean visuals — mirroring how a real analytics team would structure this pipeline rather than doing everything in one place.

---

## Tech Stack

`SQL Server (T-SQL)` · `Python` (Pandas, NumPy, VADER Sentiment, scikit-learn, WordCloud) · `Power BI` (DAX, Power Query) · `Matplotlib`

---

## Repository Structure

```
flipkart-sentiment-intelligence/
│
├── README.md
├── LICENSE
├── requirements.txt
│
├── data/
│   └── README.md                  # raw data not committed (size) — links to Kaggle source
│
├── sql/
│   ├── 01_schema.sql              # table creation, typed to match cleaned dataset
│   └── queries/
│       ├── 01_rating_distribution.sql
│       ├── 02_category_volume_rating.sql
│       ├── 03_negative_sentiment_by_category.sql
│       ├── 04_price_distribution_bands.sql
│       ├── 05_price_rating_correlation.sql
│       ├── 06_top10_most_reviewed.sql
│       ├── 07_flagged_products.sql
│       ├── 08_brand_ranking_electronics.sql
│       ├── 09_rating_sentiment_mismatch.sql
│       ├── 10_review_length_vs_sentiment.sql
│       ├── 11_csat_index.sql
│       ├── 12_word_frequency.sql
│       └── 13_aspect_keyword_search.sql
│
├── src/
│   ├── 01_data_cleaning.py        # single-pass pipeline: raw CSV → cleaned, categorized,
│   │                               # sentiment-scored dataset
│   └── 02_nlp_sentiment.py        # negation-aware n-grams, aspect-based sentiment,
│                                   # LDA topic modeling, word clouds
│
├── powerbi/
│   └── flipkart_dashboard.pbix    # 4-page executive dashboard
│
├── images/
│   ├── dashboard_executive_overview.png
│   ├── dashboard_category_brand.png
│   ├── dashboard_nlp_insights.png
│   ├── dashboard_price_intelligence.png
│   └── wordclouds.png
│
└── docs/
    ├── business_recommendations.md   # full findings: data → implication → recommendation
    └── nlp_analysis_summary.txt      # generated NLP run summary (bigrams, aspects, LDA topics)
```

---

## How to Run

```bash
git clone https://github.com/yogesh2005-ops/flipkart-sentiment-intelligence.git
cd flipkart-sentiment-intelligence
pip install -r requirements.txt
```

1. **Data cleaning:**
   ```bash
   python src/01_data_cleaning.py data/flipkart_product.csv data/flipkart_cleaned_final.csv
   ```
   (raw source CSV linked in `data/README.md`, since it isn't committed to the repo)

2. **NLP analysis:**
   ```bash
   python src/02_nlp_sentiment.py
   ```
   Produces aspect-sentiment tables, LDA topics, and word clouds in the output folder.

3. **SQL:** in SQL Server Management Studio, run `sql/01_schema.sql` to create the table, import `flipkart_cleaned_final.csv`, then run any file under `sql/queries/` to reproduce the business analysis.

4. **Dashboard:** open `powerbi/flipkart_dashboard.pbix` in Power BI Desktop.

---

## Known Limitations

- **Brand-level analysis is bit of a curveball.** Brand was derived from the first word of the product name, which is reliable for real brand-led naming (Apple, Bosch, Dettol) but breaks down for Fashion, where names typically start with a style descriptor rather than a brand.
- **~3.4% of reviews contain irrecoverable character loss** — emojis partially or fully replaced with literal `?` characters before this dataset was exported. Confirmed unfixable via encoding-repair tooling; does not affect sentiment scoring, since text cleaning strips non-alphabetic characters before analysis.
- **No native date field exists in the source data**, so time-trend analysis (e.g., month-over-month complaint volume) is out of scope for this version rather than simulated.

## Future Work

- Time-series complaint tracking, pending a data source that includes a review date field
- Fake/incentivized review detection
- Transformer-based sentiment scoring (e.g., DistilBERT) benchmarked against VADER, particularly for sarcasm-sensitive cases
- Brand extraction via a maintained brand-name reference list rather than first-word parsing

---

## Author

Yogesh — B.Tech Computer Science 
[LinkedIn : https://www.linkedin.com/in/k-yogesh-sathvik-0225ab371/]
[Gmail: yogeshsai2005@gmail.com]
