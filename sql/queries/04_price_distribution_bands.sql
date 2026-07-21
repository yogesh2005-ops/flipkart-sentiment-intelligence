SELECT
    CASE
        WHEN Price < 500 THEN '1-Budget (<500)'
        WHEN Price BETWEEN 500 AND 1999 THEN '2-Mid (500-2000)'
        WHEN Price BETWEEN 2000 AND 9999 THEN '3-Upper-Mid (2000-10000)'
        ELSE '4-Premium (10000+)'
    END AS price_band,
    COUNT(*) AS review_count,
    CAST(AVG(CAST(Rate AS FLOAT)) AS DECIMAL(4,2)) AS avg_rating,
    CAST(SUM(CASE WHEN sentiment_category='Negative' THEN 1 ELSE 0 END) * 100.0 
         / COUNT(*) AS DECIMAL(5,2)) AS negative_pct
FROM dbo.reviews
GROUP BY
    CASE
        WHEN Price < 500 THEN '1-Budget (<500)'
        WHEN Price BETWEEN 500 AND 1999 THEN '2-Mid (500-2000)'
        WHEN Price BETWEEN 2000 AND 9999 THEN '3-Upper-Mid (2000-10000)'
        ELSE '4-Premium (10000+)'
    END
ORDER BY price_band;