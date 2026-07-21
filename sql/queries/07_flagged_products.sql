USE FlipkartDB;
GO

SELECT TOP 15
    ProductName,
    Category,
    COUNT(*) AS Review_Count,
    ROUND(AVG(CAST(Rate AS FLOAT)), 2) AS Avg_Rating,
    SUM(CASE WHEN sentiment_category = 'Negative' THEN 1 ELSE 0 END) AS Negative_Reviews,
    ROUND(
        100.0 * SUM(CASE WHEN sentiment_category = 'Negative' THEN 1 ELSE 0 END)
        / COUNT(*), 2
    ) AS Negative_Pct
FROM reviews
GROUP BY ProductName, Category
HAVING COUNT(*) >= 10
   AND (
        AVG(CAST(Rate AS FLOAT)) <= 3.5
        OR
        100.0 * SUM(CASE WHEN sentiment_category = 'Negative' THEN 1 ELSE 0 END)
        / COUNT(*) >= 30
   )
ORDER BY
    Negative_Pct DESC,
    Review_Count DESC;