"""
Real-Time Crypto Analytics Dashboard
Show DBT tables from Athena
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pyathena import connect
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Crypto Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("Real-Time Crypto Analytics Dashboard")
st.markdown("---")


# Athena connection
@st.cache_resource
def get_athena_connection():
    return connect(
        s3_staging_dir=os.getenv('AWS_ATHENA_OUTPUT_LOCATION', 's3://crypto-analytics-athena/query-results/'),
        region_name=os.getenv('AWS_REGION', 'eu-north-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )


# Query function
@st.cache_data(ttl=300)  # Cache for 5 minutes
def query_athena(sql):
    conn = get_athena_connection()
    return pd.read_sql(sql, conn)


# Sidebar filters
st.sidebar.header("🔧 Filters")

# Get available symbols
symbols_query = """
SELECT DISTINCT symbol 
FROM crypto_analytics_raw_marts.fct_crypto_metrics
ORDER BY symbol
"""
symbols_df = query_athena(symbols_query)
symbols = symbols_df['symbol'].tolist()

selected_symbols = st.sidebar.multiselect(
    "Select Cryptocurrencies",
    options=symbols,
    default=symbols
)

# Date range
st.sidebar.subheader("Date Range")
days_back = st.sidebar.slider("Days to show", 1, 30, 7)

# Refresh button
if st.sidebar.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Main query
if selected_symbols:
    symbols_str = "', '".join(selected_symbols)

    main_query = f"""
        SELECT 
            symbol,
            fetched_date,
            daily_avg_price,
            daily_min_price,
            daily_max_price,
            daily_avg_volatility,
            daily_price_range_pct,
            daily_avg_volume,
            total_records
        FROM crypto_analytics_raw_marts.fct_crypto_metrics
        WHERE symbol IN ('{symbols_str}')
            AND DATE(CAST(fetched_date AS VARCHAR)) >= CURRENT_DATE - INTERVAL '{days_back}' DAY
        ORDER BY fetched_date DESC, symbol
        """

    df = query_athena(main_query)

    if not df.empty:
        # KPIs Row
        st.header("Key Metrics (Latest)")

        latest_df = df[df['fetched_date'] == df['fetched_date'].max()]

        cols = st.columns(len(selected_symbols))
        for idx, symbol in enumerate(selected_symbols):
            symbol_data = latest_df[latest_df['symbol'] == symbol]
            if not symbol_data.empty:
                with cols[idx]:
                    st.metric(
                        label=symbol.upper(),
                        value=f"${symbol_data['daily_avg_price'].iloc[0]:,.2f}",
                        delta=f"{symbol_data['daily_avg_volatility'].iloc[0]:.2f}% volatility"
                    )

        st.markdown("---")

        # Price Chart
        st.header("Price Trends")

        fig_price = px.line(
            df,
            x='fetched_date',
            y='daily_avg_price',
            color='symbol',
            title='Average Daily Prices',
            labels={'daily_avg_price': 'Price (USD)', 'fetched_date': 'Date'}
        )
        fig_price.update_layout(height=500)
        st.plotly_chart(fig_price, use_container_width=True)

        # Volatility Chart
        st.header("Volatility Analysis")

        col1, col2 = st.columns(2)

        with col1:
            fig_volatility = px.bar(
                df,
                x='fetched_date',
                y='daily_avg_volatility',
                color='symbol',
                title='Daily Volatility %',
                barmode='group'
            )
            st.plotly_chart(fig_volatility, use_container_width=True)

        with col2:
            fig_range = px.bar(
                df,
                x='fetched_date',
                y='daily_price_range_pct',
                color='symbol',
                title='Daily Price Range %',
                barmode='group'
            )
            st.plotly_chart(fig_range, use_container_width=True)

        # Volume Chart
        st.header("Trading Volume")

        fig_volume = px.area(
            df,
            x='fetched_date',
            y='daily_avg_volume',
            color='symbol',
            title='Average Daily Volume (USD)'
        )
        st.plotly_chart(fig_volume, use_container_width=True)

        # Data Quality
        st.header("Data Quality")

        quality_df = df.groupby('symbol').agg({
            'total_records': 'sum',
            'fetched_date': 'count'
        }).reset_index()
        quality_df.columns = ['Symbol', 'Total Records', 'Days with Data']

        st.dataframe(quality_df, use_container_width=True)

        # Raw Data Table
        with st.expander("📋 View Raw Data"):
            st.dataframe(df, use_container_width=True)

        # Footer
        st.markdown("---")
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data refresh every 5 minutes")

    else:
        st.warning("No data available for selected filters")
else:
    st.info("Please select at least one cryptocurrency from the sidebar")