use FlipkartDB
--Rating Distribution
SELECT Rate, COUNT(*) AS review_count,
       CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) AS pct
FROM dbo.reviews
GROUP BY Rate
ORDER BY Rate;