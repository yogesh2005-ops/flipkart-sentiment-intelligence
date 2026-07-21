use FlipkartDB
SELECT TOP 10 ProductName, COUNT(*) AS review_count,
       CAST(AVG(CAST(Rate AS FLOAT)) AS DECIMAL(4,2)) AS avg_rating
FROM dbo.reviews
GROUP BY ProductName
ORDER BY review_count DESC;