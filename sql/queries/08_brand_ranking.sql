use FlipkartDB
SELECT Brand,
       COUNT(*) AS review_count,
       CAST(AVG(CAST(Rate AS FLOAT)) AS DECIMAL(4,2)) AS avg_rating,
       RANK() OVER (ORDER BY AVG(CAST(Rate AS FLOAT)) DESC) AS brand_rank
FROM dbo.reviews
GROUP BY Brand
HAVING COUNT(*) >= 100
ORDER BY avg_rating DESC;