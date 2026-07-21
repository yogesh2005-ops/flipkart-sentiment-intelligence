use FlipkartDB
WITH category_sentiment AS (
    SELECT Category_Group,
           SUM(CASE WHEN sentiment_category = 'Positive' THEN 1 ELSE 0 END) AS positive_count,
           COUNT(*) AS total_count
    FROM dbo.reviews
    GROUP BY Category_Group
)
SELECT Category_Group,
       CAST(positive_count * 100.0 / total_count AS DECIMAL(5,2)) AS csat_index,
       RANK() OVER (ORDER BY positive_count * 100.0 / total_count DESC) AS csat_rank
FROM category_sentiment;