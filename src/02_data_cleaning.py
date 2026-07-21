import pandas as pd
import re
from collections import Counter
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
import time

# If vaderSentiment/wordcloud aren't installed:
# pip install vaderSentiment wordcloud scikit-learn

# INSERT YOUR FILE PATH HERE
df = pd.read_csv(r'flipkart1_cleaned_v2.csv')
print(df.shape)   

# Naive stopword list — includes 'not', 'no', 'nor'
BAD_STOPWORDS = set("""a an the this that these those i you it we they and or but of at by for with
about not no nor""".split())

def get_tokens_naive(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    return [w for w in text.split() if w not in BAD_STOPWORDS and len(w) > 2]

def get_bigrams(tokens):
    return list(zip(tokens, tokens[1:]))

fashion_neg = df[(df['Category_Group']=='Fashion') & (df['sentiment_category']=='Negative')]

bigrams_naive = []
for t in fashion_neg['clean_review'].dropna():
    bigrams_naive.extend(get_bigrams(get_tokens_naive(t)))

print("Naive (broken) top bigrams:")
for bg, c in Counter(bigrams_naive).most_common(10):
    print(' '.join(bg), c)

# Fix it: keep negation words
GOOD_STOPWORDS = set("""a an the this that these those i you it we they and or but of at by for with
about""".split())   # 'not'/'no'/'nor' deliberately excluded

def get_tokens(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    return [w for w in text.split() if w not in GOOD_STOPWORDS and len(w) > 2]

bigrams_fixed = []
for t in fashion_neg['clean_review'].dropna():
    bigrams_fixed.extend(get_bigrams(get_tokens(t)))

print("Fixed (negation-aware) top bigrams:")
for bg, c in Counter(bigrams_fixed).most_common(15):
    print(' '.join(bg), c)

analyzer = SentimentIntensityAnalyzer()

# Aspect-Based Sentiment Analysis 
ASPECTS = {
    'Size & Fit': ['size', 'fit', 'fitting', 'tight', 'loose'],
    'Material & Fabric': ['material', 'fabric', 'cloth', 'quality'],
    'Comfort': ['comfortable', 'comfort', 'soft'],
    'Value for Money': ['money', 'worth', 'price', 'waste', 'expensive', 'cheap'],
    'Color/Appearance': ['color', 'colour', 'look', 'design'],
    'Delivery & Packaging': ['delivery', 'package', 'packing', 'damaged', 'late'],
    'Battery': ['battery', 'backup', 'charge', 'charging'],
    'Camera': ['camera', 'photo', 'picture'],
}

def extract_aspect_windows(text, keywords, window=5):
    """For each aspect keyword found in the review, grab the +/- 5 words
    around it. This is the key idea: instead of scoring the WHOLE review
    (which mixes multiple topics), we score just the local context around
    each aspect mention."""
    tokens = str(text).split()
    snippets = []
    for i, tok in enumerate(tokens):
        if tok in keywords:
            start = max(0, i - window)
            end = min(len(tokens), i + window + 1)
            snippets.append(' '.join(tokens[start:end]))
    return snippets

results = []
for aspect_name, keywords in ASPECTS.items():
    kw_set = set(keywords)
    pos = neg = neu = mentions = 0
    for text in df['clean_review'].dropna():
        for snip in extract_aspect_windows(text, kw_set):
            score = analyzer.polarity_scores(snip)['compound']
            mentions += 1
            if score >= 0.05: pos += 1
            elif score <= -0.05: neg += 1
            else: neu += 1
    if mentions > 0:
        results.append({
            'Aspect': aspect_name, 'Mentions': mentions,
            'Positive_%': round(pos/mentions*100, 1),
            'Negative_%': round(neg/mentions*100, 1),
        })

aspect_df = pd.DataFrame(results).sort_values('Negative_%', ascending=False)
print(aspect_df)

# Same analysis, scoped to Fashion only
fashion = df[df['Category_Group']=='Fashion']
fashion_results = []
for aspect_name, keywords in ASPECTS.items():
    kw_set = set(keywords)
    neg = mentions = 0
    for text in fashion['clean_review'].dropna():
        for snip in extract_aspect_windows(text, kw_set):
            score = analyzer.polarity_scores(snip)['compound']
            mentions += 1
            if score <= -0.05: neg += 1
    if mentions > 0:
        fashion_results.append({'Aspect': aspect_name, 'Mentions': mentions,
                                 'Negative_%': round(neg/mentions*100, 1)})

print(pd.DataFrame(fashion_results).sort_values('Negative_%', ascending=False))

# Topic Modeling (LDA) — unsupervised discovery
neg_reviews = df[df['sentiment_category']=='Negative']['clean_review'].dropna()
neg_reviews = neg_reviews[neg_reviews.str.len() > 10]   # drop tiny/uninformative ones

vectorizer = CountVectorizer(max_df=0.5, min_df=10, stop_words='english', max_features=1000)
X = vectorizer.fit_transform(neg_reviews)

lda = LatentDirichletAllocation(n_components=6, random_state=42, max_iter=15)
lda.fit(X)

feature_names = vectorizer.get_feature_names_out()
for idx, topic in enumerate(lda.components_):
    top_words = [feature_names[i] for i in topic.argsort()[-10:][::-1]]
    print(f"Topic {idx+1}: {', '.join(top_words)}")

# Word Clouds
custom_stop = STOPWORDS.union({
    'product','products','good','one','use','used','using','also','get','got',
    'flipkart','item','really','quality','buy','dont'
})

neg_text = ' '.join(df[df['sentiment_category']=='Negative']['clean_review'].dropna())
pos_text = ' '.join(df[df['sentiment_category']=='Positive']['clean_review'].dropna())

fig, axes = plt.subplots(1, 2, figsize=(14,6))
wc_neg = WordCloud(width=700, height=500, background_color='white', colormap='Reds',
                    stopwords=custom_stop, collocations=True).generate(neg_text)
axes[0].imshow(wc_neg); axes[0].axis('off'); axes[0].set_title('Negative Reviews')

wc_pos = WordCloud(width=700, height=500, background_color='white', colormap='Greens',
                    stopwords=custom_stop, collocations=True).generate(pos_text)
axes[1].imshow(wc_pos); axes[1].axis('off'); axes[1].set_title('Positive Reviews')
plt.tight_layout()
plt.savefig('wordclouds.png', dpi=120)
plt.show()

# ==========================================================
# Create Output Folder
# ==========================================================

# INSERT YOUR OUTPUT FOLDER'S PATH HERE
output_folder = r"NLP_Outputs"
os.makedirs(output_folder, exist_ok=True)

print("\nSaving outputs...\n")

# Total number of save operations
TOTAL_STEPS = 6

with tqdm(total=TOTAL_STEPS,
          desc="Saving Files",
          unit="file",
          colour="green") as pbar:

    # ------------------------------------------------------
    # 1. Naive Bigrams
    # ------------------------------------------------------
    naive_df = pd.DataFrame(
        [(' '.join(bg), c) for bg, c in Counter(bigrams_naive).most_common()],
        columns=["Bigram", "Count"]
    )
    naive_df.to_csv(
        os.path.join(output_folder, "naive_bigrams.csv"),
        index=False
    )
    pbar.set_postfix(File="naive_bigrams.csv")
    pbar.update(1)

    # ------------------------------------------------------
    # 2. Fixed Bigrams
    # ------------------------------------------------------
    fixed_df = pd.DataFrame(
        [(' '.join(bg), c) for bg, c in Counter(bigrams_fixed).most_common()],
        columns=["Bigram", "Count"]
    )
    fixed_df.to_csv(
        os.path.join(output_folder, "fixed_bigrams.csv"),
        index=False
    )
    pbar.set_postfix(File="fixed_bigrams.csv")
    pbar.update(1)

    # ------------------------------------------------------
    # 3. Aspect Sentiment
    # ------------------------------------------------------
    aspect_df.to_csv(
        os.path.join(output_folder, "aspect_sentiment.csv"),
        index=False
    )
    pbar.set_postfix(File="aspect_sentiment.csv")
    pbar.update(1)

    # ------------------------------------------------------
    # 4. Fashion Aspect Sentiment
    # ------------------------------------------------------
    fashion_aspect_df = pd.DataFrame(fashion_results).sort_values(
        "Negative_%",
        ascending=False
    )

    fashion_aspect_df.to_csv(
        os.path.join(output_folder, "fashion_aspect_sentiment.csv"),
        index=False
    )
    pbar.set_postfix(File="fashion_aspect_sentiment.csv")
    pbar.update(1)

    # ------------------------------------------------------
    # 5. LDA Topics
    # ------------------------------------------------------
    topics = []

    for idx, topic in enumerate(lda.components_):
        top_words = [feature_names[i] for i in topic.argsort()[-10:][::-1]]
        topics.append({
            "Topic": idx + 1,
            "Top Words": ", ".join(top_words)
        })

    lda_df = pd.DataFrame(topics)

    lda_df.to_csv(
        os.path.join(output_folder, "lda_topics.csv"),
        index=False
    )
    pbar.set_postfix(File="lda_topics.csv")
    pbar.update(1)

    # ------------------------------------------------------
    # 6. Text Summary
    # ------------------------------------------------------
    with open(
        os.path.join(output_folder, "analysis_summary.txt"),
        "w",
        encoding="utf-8"
    ) as f:

        f.write("FLIPKART NLP ANALYSIS SUMMARY\n")
        f.write("="*60 + "\n\n")

        f.write(f"Dataset Shape: {df.shape}\n\n")

        f.write("TOP 10 NAIVE BIGRAMS\n")
        f.write("-"*40 + "\n")
        for bg, c in Counter(bigrams_naive).most_common(10):
            f.write(f"{' '.join(bg)} : {c}\n")

        f.write("\nTOP 15 NEGATION-AWARE BIGRAMS\n")
        f.write("-"*40 + "\n")
        for bg, c in Counter(bigrams_fixed).most_common(15):
            f.write(f"{' '.join(bg)} : {c}\n")

        f.write("\n\nASPECT SENTIMENT\n")
        f.write(aspect_df.to_string(index=False))

        f.write("\n\nFASHION ASPECT SENTIMENT\n")
        f.write(fashion_aspect_df.to_string(index=False))

        f.write("\n\nLDA TOPICS\n")
        for row in topics:
            f.write(f"\nTopic {row['Topic']}: {row['Top Words']}")

    pbar.set_postfix(File="analysis_summary.txt")
    pbar.update(1)

print("\nDone!")
print(f"All files saved successfully to:\n{output_folder}")