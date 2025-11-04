-- Intermediate model: hourly aggregations

{{ config(
    materialized='table',
    schema='intermediate'
) }}

WITH hourly_data AS (
    SELECT
        symbol,
        fetched_date,
        hour_of_day,

        -- Aggregations for each hour
        COUNT(*) AS num_records,
        AVG(price_usd) AS avg_price_usd,
        MIN(price_usd) AS min_price_usd,
        MAX(price_usd) AS max_price_usd,
        AVG(volume_24h_usd) AS avg_volume_24h_usd,
        AVG(market_cap_usd) AS avg_market_cap_usd

    FROM {{ ref('stg_crypto_prices') }}

    GROUP BY
        symbol,
        fetched_date,
        hour_of_day
)

SELECT
    symbol,
    fetched_date,
    hour_of_day,
    num_records,
    avg_price_usd,
    min_price_usd,
    max_price_usd,

    -- Calculation of volatility per hour
    CASE
        WHEN avg_price_usd > 0
        THEN ((max_price_usd - min_price_usd) / avg_price_usd) * 100
        ELSE 0
    END AS price_volatility_pct,

    avg_volume_24h_usd,
    avg_market_cap_usd,

    -- Calculation of price range
    (max_price_usd - min_price_usd) AS price_range_usd

FROM hourly_data