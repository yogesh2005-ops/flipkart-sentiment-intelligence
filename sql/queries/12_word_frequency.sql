use FlipkartDB
SELECT value AS word, COUNT(*) AS frequency
FROM dbo.reviews
CROSS APPLY STRING_SPLIT(clean_review, ' ')
WHERE sentiment_category = 'Negative'
  AND LEN(value) > 3   -- filter out short/noise tokens
GROUP BY value
ORDER BY frequency DESC
OFFSET 0 ROWS FETCH NEXT 30 ROWS ONLY;