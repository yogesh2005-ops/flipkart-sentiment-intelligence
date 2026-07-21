"""
Flipkart Customer Sentiment & Product Intelligence Platform
Consolidated cleaning pipeline: RAW CSV -> fully cleaned, categorized,
sentiment-scored dataset — in one deterministic pass.

Why one script instead of chained manual patches:
Every earlier iteration (encoding fix -> category fix -> null fix) was applied
on top of the PREVIOUS pass's output, so mistakes compounded (e.g. an encoding
fix on already-mojibake'd text introduced a new '??' corruption). Running this
single script against the ORIGINAL raw file avoids that entirely and is also
what you want for your GitHub repo: one reproducible, defensible pipeline.

Usage:
    python clean_pipeline.py raw_flipkart.csv flipkart_cleaned_final.csv
"""

import sys
import re
import numpy as np
import pandas as pd
import ftfy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# ---------------------------------------------------------------------------
# STEP 1: LOAD
# ---------------------------------------------------------------------------
def load_raw(path):
    # CHANGED: Read using latin1 because the original Flipkart dataset is not UTF-8.
    df = pd.read_csv(path, encoding="latin1")

    # CHANGED: Repair common mojibake if present.
    for col in ["ProductName", "Review", "Summary"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.encode("latin1", errors="ignore")
                .str.decode("utf-8", errors="ignore")
            )

    return df

def fix_dtypes(df):

    # Remove everything except digits and decimal point
    df["Price"] = (
        df["Price"]
        .astype(str)
        .str.replace(r"[^\d.]", "", regex=True)
    )

    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df["Rate"] = pd.to_numeric(df["Rate"], errors="coerce")

    before = len(df)

    df = df.dropna(subset=["Price", "Rate"]).reset_index(drop=True)

    print(f"[fix_dtypes] removed {before-len(df)} rows")

    return df


# ---------------------------------------------------------------------------
# STEP 2: NORMALIZE MISSING VALUES
# ---------------------------------------------------------------------------
def normalize_missing(df):
    """
    Catches BOTH real NaNs and the 'fake missing' pattern we found last time
    (actual missing values that got stringified into literal 'Nan'/'None' text
    somewhere upstream). Doing this immediately after load — before any other
    step touches these columns — prevents that bug from ever reappearing.
    """
    fake_null_tokens = ['nan', 'none', 'null', 'n/a', 'na', '']
    text_cols = [
    "ProductName",
    "Review",
    "Summary",
    "Price",
    "Rate"
]
    for col in text_cols:
        if col in df.columns:
            mask = df[col].astype(str).str.strip().str.lower().isin(fake_null_tokens)
            n_fake = mask.sum()
            if n_fake:
                print(f"[normalize_missing] '{col}': converting {n_fake} "
                      f"fake-null strings to real NaN")
            df.loc[mask, col] = np.nan

    return df


# ---------------------------------------------------------------------------
# STEP 3: DROP DUPLICATES
# ---------------------------------------------------------------------------
def drop_duplicates(df):
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"[drop_duplicates] removed {before - len(df)} duplicate rows")
    return df


# ---------------------------------------------------------------------------
# STEP 4: HANDLE REMAINING NULLS
# ---------------------------------------------------------------------------
def handle_nulls(df):
    """
    Rule: Rate and Summary are essential for rating/sentiment analysis —
    drop rows missing either. Price nulls are dropped too (needed for the
    price-vs-sentiment KPI). This is a documented, defensible rule for your
    README, not silent data loss.
    """
    before = len(df)
    df = df.dropna(subset=['Rate', 'Summary', 'Price']).reset_index(drop=True)
    print(f"[handle_nulls] dropped {before - len(df)} rows missing "
          f"Rate/Summary/Price")
    return df


# ---------------------------------------------------------------------------
# STEP 5: DATA TYPES
# ---------------------------------------------------------------------------
# def fix_dtypes(df):
#     df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
#     df['Rate'] = pd.to_numeric(df['Rate'], errors='coerce')
#     # coercion can create new NaNs if a value was non-numeric junk -> drop those too
#     before = len(df)
#     df = df.dropna(subset=['Price', 'Rate']).reset_index(drop=True)
#     if before - len(df):
#         print(f"[fix_dtypes] dropped {before - len(df)} rows with "
#               f"non-numeric Price/Rate")
#     return df


# ---------------------------------------------------------------------------
# STEP 6: TEXT CLEANING FOR NLP
# ---------------------------------------------------------------------------
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def add_clean_review(df):
    df['clean_review'] = df['Summary'].apply(clean_text)
    df['has_summary_text'] = df['clean_review'].str.len() > 0
    return df


# ---------------------------------------------------------------------------
# STEP 7: BRAND EXTRACTION
# ---------------------------------------------------------------------------
def add_brand(df):
    df['Brand'] = df['ProductName'].apply(lambda x: str(x).split()[0])
    return df


# ---------------------------------------------------------------------------
# STEP 8: CATEGORY EXTRACTION (from category_mapping.py, validated earlier
# to bring 'Other' down from 60.7% to 8.0%)
# ---------------------------------------------------------------------------
def extract_category(name):
    if not isinstance(name, str) or not name.strip():
        return 'Other'
    n = name.lower()

    def has(*keywords):
        return any(k in n for k in keywords)

    if has('mobile', 'smartphone', ' phone', 'iphone', 'poco', 'redmi', 'realme',
           ' oppo', ' vivo', 'oneplus', 'iqoo', 'samsung galaxy', ' gb ram', ' gb rom'):
        return 'Electronics - Mobile'
    if has('laptop', 'notebook computer', 'macbook'):
        return 'Electronics - Laptop'
    if has('ipad', 'tablet'):
        return 'Electronics - Tablet'
    if has('dslr', 'camera', 'lens ', 'mirrorless'):
        return 'Electronics - Camera'
    if has('smart watch', 'smartwatch', 'analog watch', ' watch', 'wristwatch'):
        return 'Watches & Wearables'
    if has('headphone', 'earphone', 'earbud', 'speaker', 'bluetooth', 'charger',
           'cable', 'mouse', 'keyboard', 'router', 'printer', 'power bank',
           'memory card', 'hard disk', 'streaming device', 'pen drive'):
        return 'Electronics - Accessories'
    if has('air cooler', 'air conditioner', ' ac ', 'refrigerator', 'fridge',
           'washing machine', 'television', ' tv ', 'geyser', 'water heater',
           'chimney', 'dishwasher'):
        return 'Electronics - Appliance'
    if has('juicer', 'grinder', 'mixer', 'food processor', 'immersion',
           'induction', 'toaster', 'oven', 'kettle', 'water purifier',
           'rice cooker', 'sewing machine', 'dry iron', ' iron'):
        return 'Electronics - Kitchen Appliance'
    if has('ink cartridge', 'toner', ' cartridge'):
        return 'Electronics - Accessories'
    if has('wardrobe', 'study table', 'desk', 'bookshelf', 'shelf', 'chair',
           ' table ', 'sofa', 'bed frame'):
        return 'Home - Furniture'
    if has('lamp', 'ceiling light', 'ceiling fan', 'led light', 'led bulb',
           'bulb', 'pendant light', 'night lamp', 'wall light', 'led', 'wall clock'):
        return 'Home - Lighting & Decor'
    if has('flask', 'thermosteel', 'water bottle', 'thermos', 'tumbler'):
        return 'Home - Cookware & Dining'
    if has('mop', 'bucket', 'duster', 'cleaning', 'vacuum cleaner', 'broom'):
        return 'Home - Cleaning & Household'
    if has('kadhai', 'cookware', 'tawa', 'frying pan', 'dinner set', 'jar',
           'container', 'casserole', 'pressure cooker'):
        return 'Home - Cookware & Dining'
    if has('blanket', 'mink', 'carpet', 'cushion', 'bedsheet', 'mattress',
           'pillow', 'curtain', 'rug '):
        return 'Home - Textiles'
    if has('sandal', 'shoe', 'slipper', 'footwear', 'sneaker'):
        return 'Fashion - Footwear'
    if has('bicycle', 'mountain cycle', ' mtb '):
        return 'Sports & Fitness'
    if has('blazer', 'men shirt', 'men jeans', 'trouser', 'formal shirt',
           'casual shirt', 'men solid', 'men trouser', 'men cargo', 'men short',
           'three fourth'):
        return 'Fashion - Men'
    if has('dupatta', 'saree', 'kurti', 'women dress', 'salwar', 'blouse'):
        return 'Fashion - Women'
    if has('cricket', ' bat ', 'cricket bat', ' ball', 'yoga', 'fitness',
           'dumbbell', 'gym', 'football'):
        return 'Sports & Fitness'
    if has('balloon', 'birthday', 'party', 'decoration', 'toy '):
        return 'Toys & Party Supplies'
    if has('backpack', ' bag', 'wallet', 'belt', 'sunglasses', 'trimmer', 'shaver'):
        return 'Personal Accessories'
    if has('shirt', 'jeans', 'dress', 'kurta', 'top ', 'tshirt', 't-shirt'):
        return 'Fashion'
    if has('cream', 'lotion', 'moisturizer', 'shampoo', 'soap', 'makeup', 'lipstick',
           'hair oil', 'serum', 'antiseptic', 'face wash', 'conditioner'):
        return 'Beauty'
    if has('book', 'novel', 'guide '):
        return 'Books'
    if has('kitchen', 'home', 'curtain', 'mattress', 'pillow', 'bedsheet'):
        return 'Home & Kitchen'
    return 'Other'


CATEGORY_GROUP_MAP = {
    'Electronics - Mobile': 'Electronics', 'Electronics - Laptop': 'Electronics',
    'Electronics - Tablet': 'Electronics', 'Electronics - Camera': 'Electronics',
    'Electronics - Accessories': 'Electronics', 'Electronics - Appliance': 'Electronics',
    'Electronics - Kitchen Appliance': 'Electronics', 'Watches & Wearables': 'Electronics',
    'Home - Furniture': 'Home', 'Home - Lighting & Decor': 'Home',
    'Home - Cookware & Dining': 'Home', 'Home - Cleaning & Household': 'Home',
    'Home - Textiles': 'Home', 'Home & Kitchen': 'Home',
    'Fashion - Footwear': 'Fashion', 'Fashion - Men': 'Fashion',
    'Fashion - Women': 'Fashion', 'Fashion': 'Fashion',
    'Personal Accessories': 'Fashion',
    'Sports & Fitness': 'Sports & Leisure', 'Toys & Party Supplies': 'Sports & Leisure',
    'Beauty': 'Beauty', 'Books': 'Books', 'Other': 'Other',
}


def add_category(df):
    df['Category'] = df['ProductName'].apply(extract_category)
    df['Category_Group'] = df['Category'].map(CATEGORY_GROUP_MAP).fillna('Other')
    return df


# ---------------------------------------------------------------------------
# STEP 9: SENTIMENT ANALYSIS (VADER)
# ---------------------------------------------------------------------------
def add_sentiment(df):
    analyzer = SentimentIntensityAnalyzer()

    def score(text):
        s = analyzer.polarity_scores(str(text))
        compound = s["compound"]

        if compound >= 0.05:
            label = "Positive"
        elif compound <= -0.05:
            label = "Negative"
        else:
            label = "Neutral"

        return label, abs(compound)

    # CHANGED: apply returns tuples, convert them into a DataFrame
    sentiment_results = df["Summary"].apply(score)

    sentiment_df = pd.DataFrame(
        sentiment_results.tolist(),
        columns=["sentiment_category", "confidence_score"],
        index=df.index
    )

    df = pd.concat([df, sentiment_df], axis=1)

    return df


# ---------------------------------------------------------------------------
# STEP 10: RATING-SENTIMENT MISMATCH FLAG (feeds Phase 9 business insight)
# ---------------------------------------------------------------------------
def add_mismatch_flag(df):
    df['rating_sentiment_mismatch'] = (
        ((df['Rate'] >= 4) & (df['sentiment_category'] == 'Negative')) |
        ((df['Rate'] <= 2) & (df['sentiment_category'] == 'Positive'))
    )
    return df


# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------
def run_pipeline(input_path, output_path):
    # df = load_raw(input_path)
    # df = fix_encoding(df)
    # df = normalize_missing(df)
    # df = drop_duplicates(df)
    # df = handle_nulls(df)
    # df = fix_dtypes(df)
    # df = add_clean_review(df)
    # df = add_brand(df)
    # df = add_category(df)
    # df = add_sentiment(df)
    # df = add_mismatch_flag(df)
    df = load_raw(input_path)
    print("Load:", df.shape)

    # optional
    # df = fix_encoding(df)
    # print("Encoding:", df.shape)

    df = normalize_missing(df)
    print("Normalize:", df.shape)

    df = drop_duplicates(df)
    print("Duplicates:", df.shape)

    df = handle_nulls(df)
    print("Nulls:", df.shape)

    df = fix_dtypes(df)
    print("Dtypes:", df.shape)

    df = add_clean_review(df)
    print("Clean Review:", df.shape)

    df = add_brand(df)
    print("Brand:", df.shape)

    df = add_category(df)
    print("Category:", df.shape)

    df = add_sentiment(df)
    print("Sentiment:", df.shape)

    df = add_mismatch_flag(df)
    print("Mismatch:", df.shape)

    df.to_csv(output_path, index=False, encoding='utf-8-sig')

    # print("\n=== FINAL SUMMARY ===")
    # print(f"Final shape: {df.shape}")
    # print(f"\nCategory distribution:\n{df['Category'].value_counts()}")
    # print(f"\n'Other' pct: {(df['Category']=='Other').mean()*100:.2f}%")
    # print(f"\nCategory Group distribution:\n{df['Category_Group'].value_counts()}")
    # print(f"\nSentiment distribution:\n{df['sentiment_category'].value_counts(normalize=True)*100}")
    # print(f"\nRating-sentiment mismatches: {df['rating_sentiment_mismatch'].sum()} "
    #       f"({df['rating_sentiment_mismatch'].mean()*100:.2f}%)")
    print(f"\nSaved to: {output_path}")

    return df


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clean_pipeline.py <raw_input.csv> <cleaned_output.csv>")
        sys.exit(1)
    run_pipeline(sys.argv[1], sys.argv[2])