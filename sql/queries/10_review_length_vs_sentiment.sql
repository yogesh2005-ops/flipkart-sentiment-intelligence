use FlipkartDB
SELECT sentiment_category,
       AVG(CAST(LEN(Summary) AS FLOAT)) AS avg_length,
       CAST(AVG(CAST(confidence_score AS FLOAT)) AS DECIMAL(5,3)) AS avg_confidence
FROM dbo.reviews
GROUP BY sentiment_category
ORDER BY avg_length DESC;