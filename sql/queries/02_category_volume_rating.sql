use FlipkartDB
SELECT Category_Group, Category,
       COUNT(*) AS review_count,
       CAST(AVG(CAST(Rate AS FLOAT)) AS DECIMAL(4,2)) AS avg_rating
FROM dbo.reviews
GROUP BY Category_Group, Category
ORDER BY review_count DESC;