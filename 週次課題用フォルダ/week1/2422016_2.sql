SELECT
    block,
    COUNT(*) AS non_restaurant_count
FROM 
    minato_restaurant
WHERE
    business_type <> '飲食店営業'
GROUP BY
    block;