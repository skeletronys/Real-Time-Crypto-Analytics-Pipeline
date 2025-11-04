{{ config(
    materialized='view',
    schema='staging'
) }}

SELECT
    symbol,
    price_usd,
    market_cap_usd,
    volume_24h_usd,
    price_change_24h_pct,
    last_updated_at,
    source,
    fetched_at,

    -- A simple method - we only take the date without the time
    SUBSTR(fetched_at, 1, 10) AS fetched_date,  -- '2025-10-30'

    -- We take out an hour
    CAST(SUBSTR(fetched_at, 12, 2) AS INTEGER) AS hour_of_day

FROM {{ source('raw', 'crypto_prices') }}

WHERE
    price_usd > 0
    AND fetched_at IS NOT NULL