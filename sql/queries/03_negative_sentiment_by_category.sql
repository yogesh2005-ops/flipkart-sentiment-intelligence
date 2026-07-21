SELECT Category_Group,
       COUNT(*) AS total_reviews,
       SUM(CASE WHEN sentiment_category = 'Negative' THEN 1 ELSE 0 END) AS negative_count,
       CAST(SUM(CASE WHEN sentiment_category = 'Negative' THEN 1 ELSE 0 END) * 100.0 
            / COUNT(*) AS DECIMAL(5,2)) AS negative_pct
FROM dbo.reviews
GROUP BY Category_Group
ORDER BY negative_pct DESC;