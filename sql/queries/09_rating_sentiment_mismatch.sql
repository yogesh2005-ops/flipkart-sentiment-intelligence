use FlipkartDB
SELECT
    COUNT(*) AS Total_Reviews,
    SUM(
        CASE
            WHEN (Rate >= 4 AND sentiment_category = 'Negative')
              OR (Rate <= 2 AND sentiment_category = 'Positive')
            THEN 1
            ELSE 0
        END
    ) AS Mismatched_Reviews,
    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN (Rate >= 4 AND sentiment_category = 'Negative')
                  OR (Rate <= 2 AND sentiment_category = 'Positive')
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS Mismatch_Percentage
FROM reviews;