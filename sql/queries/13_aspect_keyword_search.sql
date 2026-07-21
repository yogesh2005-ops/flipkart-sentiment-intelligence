use FlipkartDB
SELECT
    CASE WHEN clean_review LIKE '%material%' OR clean_review LIKE '%fabric%' THEN 'Material & Fabric'
         WHEN clean_review LIKE '%battery%' THEN 'Battery'
         WHEN clean_review LIKE '%size%' OR clean_review LIKE '%fit%' THEN 'Size & Fit'
         WHEN clean_review LIKE '%delivery%' OR clean_review LIKE '%damaged%' THEN 'Delivery & Packaging'
         ELSE 'Other/Unmentioned'
    END AS aspect_mentioned,
    COUNT(*) AS mentions,
    CAST(SUM(CASE WHEN sentiment_category='Negative' THEN 1 ELSE 0 END) * 100.0 
         / COUNT(*) AS DECIMAL(5,2)) AS negative_pct
FROM dbo.reviews
GROUP BY
    CASE WHEN clean_review LIKE '%material%' OR clean_review LIKE '%fabric%' THEN 'Material & Fabric'
         WHEN clean_review LIKE '%battery%' THEN 'Battery'
         WHEN clean_review LIKE '%size%' OR clean_review LIKE '%fit%' THEN 'Size & Fit'
         WHEN clean_review LIKE '%delivery%' OR clean_review LIKE '%damaged%' THEN 'Delivery & Packaging'
         ELSE 'Other/Unmentioned'
    END;