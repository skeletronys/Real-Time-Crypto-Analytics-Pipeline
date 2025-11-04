-- Marts model: daily metrics for analysis and API

{{ config(
    materialized='table',
    schema='marts'
) }}

WITH daily_stats AS (
    SELECT
        symbol,
        fetched_date,

        -- Daily aggregation
        SUM(num_records) AS total_records,
        AVG(avg_price_usd) AS daily_avg_price,
        MIN(min_price_usd) AS daily_min_price,
        MAX(max_price_usd) AS daily_max_price,
        AVG(price_volatility_pct) AS daily_avg_volatility,
        AVG(avg_volume_24h_usd) AS daily_avg_volume,
        AVG(avg_market_cap_usd) AS daily_avg_market_cap

    FROM {{ ref('int_hourly_prices') }}

    GROUP BY
        symbol,
        fetched_date
)

SELECT
    symbol,
    fetched_date,
    total_records,
    daily_avg_price,
    daily_min_price,
    daily_max_price,
    daily_avg_volatility,

    -- Calculation of the daily price range
    (daily_max_price - daily_min_price) AS daily_price_range,

    -- Price range in percent
    CASE
        WHEN daily_avg_price > 0
        THEN ((daily_max_price - daily_min_price) / daily_avg_price) * 100
        ELSE 0
    END AS daily_price_range_pct,

    daily_avg_volume,
    daily_avg_market_cap,

    -- Volume to Market Cap ratio
    CASE
        WHEN daily_avg_market_cap > 0
        THEN (daily_avg_volume / daily_avg_market_cap) * 100
        ELSE 0
    END AS volume_to_mcap_ratio,

    -- Timestamp as a string instead of timestamp with timezone
    CAST(NOW() AS VARCHAR) AS updated_at

FROM daily_stats

ORDER BY
    fetched_date DESC,
    symbol