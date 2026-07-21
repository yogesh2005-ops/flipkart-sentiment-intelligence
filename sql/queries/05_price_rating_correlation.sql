WITH stats AS (
    SELECT
        Price, Rate,
        AVG(Price) OVER() AS avg_price,
        AVG(CAST(Rate AS FLOAT)) OVER() AS avg_rate
    FROM dbo.reviews
)
SELECT
    SUM((Price - avg_price) * (Rate - avg_rate)) /
    (SQRT(SUM(SQUARE(Price - avg_price))) * SQRT(SUM(SQUARE(Rate - avg_rate)))) AS price_rate_correlation
FROM stats;