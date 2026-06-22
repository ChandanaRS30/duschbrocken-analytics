import streamlit as st
import pandas as pd
from google.cloud import bigquery
import plotly.express as px

st.set_page_config(
    page_title="Duschbrocken Analytics Dashboard",
    page_icon="🧼",
    layout="wide"
)

# Header with Duschbrocken branding
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("https://duschbrocken.de/cdn/shop/files/DuBro_Logo_02_A_1200x628_pad_f4f1ed.png?v=1613176205", width=150)
with col_title:
    st.title("Sales Analytics Dashboard")
    st.markdown("Datengetriebene Einblicke fuer nachhaltiges Wachstum")

st.divider()

@st.cache_resource
def get_client():
    return bigquery.Client(project="cobalt-mantis-291519")

client = get_client()

@st.cache_data
def load_category_data():
    query = """
        SELECT
            p.category AS category,
            COUNT(DISTINCT oi.order_id) AS total_orders,
            ROUND(SUM(oi.sale_price), 2) AS total_revenue,
            ROUND(AVG(oi.sale_price), 2) AS avg_price
        FROM `bigquery-public-data.thelook_ecommerce.order_items` oi
        LEFT JOIN `bigquery-public-data.thelook_ecommerce.products` p
        ON oi.product_id = p.id
        WHERE oi.status = 'Complete'
        GROUP BY category
        ORDER BY total_revenue DESC
        LIMIT 10
    """
    return client.query(query).to_dataframe()

@st.cache_data
def load_monthly_trend():
    query = """
        SELECT
            FORMAT_DATE('%Y-%m', DATE(created_at)) AS month,
            COUNT(DISTINCT order_id) AS total_orders,
            ROUND(SUM(sale_price), 2) AS total_revenue
        FROM `bigquery-public-data.thelook_ecommerce.order_items`
        WHERE status = 'Complete'
            AND DATE(created_at) >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
        GROUP BY month
        ORDER BY month
    """
    return client.query(query).to_dataframe()

@st.cache_data
def load_top_products():
    query = """
        SELECT
            p.name AS product_name,
            p.category AS category,
            COUNT(oi.order_id) AS units_sold,
            ROUND(SUM(oi.sale_price), 2) AS revenue
        FROM `bigquery-public-data.thelook_ecommerce.order_items` oi
        JOIN `bigquery-public-data.thelook_ecommerce.products` p
        ON oi.product_id = p.id
        WHERE oi.status = 'Complete'
        GROUP BY product_name, category
        ORDER BY revenue DESC
        LIMIT 10
    """
    return client.query(query).to_dataframe()

@st.cache_data
def load_customer_data():
    query = """
        SELECT
            gender,
            country,
            COUNT(id) AS total_customers
        FROM `bigquery-public-data.thelook_ecommerce.users`
        GROUP BY gender, country
        ORDER BY total_customers DESC
        LIMIT 20
    """
    return client.query(query).to_dataframe()

@st.cache_data
def load_return_rate():
    query = """
        SELECT
            p.category AS category,
            COUNTIF(oi.status = 'Returned') AS returned_orders,
            COUNT(oi.order_id) AS total_orders,
            ROUND(COUNTIF(oi.status = 'Returned') * 100.0 / COUNT(oi.order_id), 1) AS return_rate_pct
        FROM `bigquery-public-data.thelook_ecommerce.order_items` oi
        JOIN `bigquery-public-data.thelook_ecommerce.products` p
        ON oi.product_id = p.id
        GROUP BY category
        ORDER BY return_rate_pct DESC
        LIMIT 10
    """
    return client.query(query).to_dataframe()

with st.spinner("Daten werden aus BigQuery geladen..."):
    df_category = load_category_data()
    df_trend = load_monthly_trend()
    df_products = load_top_products()
    df_customers = load_customer_data()
    df_returns = load_return_rate()

# KPI metrics
st.subheader("Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue = df_trend['total_revenue'].sum()
    st.metric("Gesamtumsatz (12 Monate)", f"EUR {total_revenue:,.0f}")

with col2:
    total_orders = df_trend['total_orders'].sum()
    st.metric("Bestellungen (12 Monate)", f"{total_orders:,}")

with col3:
    avg_order = total_revenue / total_orders if total_orders > 0 else 0
    st.metric("Durchschn. Bestellwert", f"EUR {avg_order:.2f}")

with col4:
    top_category = df_category.iloc[0]['category'] if len(df_category) > 0 else "N/A"
    st.metric("Top Kategorie", top_category)

st.divider()

# Charts row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("Monatlicher Umsatztrend")
    fig1 = px.line(
        df_trend,
        x='month',
        y='total_revenue',
        title='Umsatz der letzten 12 Monate',
        labels={'total_revenue': 'Umsatz (EUR)', 'month': 'Monat'},
        color_discrete_sequence=['#4CAF50']
    )
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Umsatz nach Kategorie")
    fig2 = px.bar(
        df_category,
        x='total_revenue',
        y='category',
        orientation='h',
        title='Top 10 Kategorien nach Umsatz',
        labels={'total_revenue': 'Umsatz (EUR)', 'category': 'Kategorie'},
        color='total_revenue',
        color_continuous_scale='Greens'
    )
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# Charts row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Produkte nach Umsatz")
    fig3 = px.bar(
        df_products,
        x='revenue',
        y='product_name',
        orientation='h',
        title='Meistverkaufte Produkte',
        labels={'revenue': 'Umsatz (EUR)', 'product_name': 'Produkt'},
        color='revenue',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("Kundensegmentierung")
    fig4 = px.pie(
        df_customers.groupby('gender')['total_customers'].sum().reset_index(),
        values='total_customers',
        names='gender',
        title='Kunden nach Geschlecht',
        color_discrete_sequence=['#4CAF50', '#2196F3', '#9E9E9E']
    )
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# Charts row 3
col1, col2 = st.columns(2)

with col1:
    st.subheader("Retourenquote nach Kategorie")
    fig5 = px.bar(
        df_returns,
        x='return_rate_pct',
        y='category',
        orientation='h',
        title='Retourenquote % nach Kategorie',
        labels={'return_rate_pct': 'Retourenquote (%)', 'category': 'Kategorie'},
        color='return_rate_pct',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    st.subheader("Bestellungen pro Monat")
    fig6 = px.bar(
        df_trend,
        x='month',
        y='total_orders',
        title='Bestellvolumen pro Monat',
        labels={'total_orders': 'Bestellungen', 'month': 'Monat'},
        color_discrete_sequence=['#4CAF50']
    )
    st.plotly_chart(fig6, use_container_width=True)

st.divider()

# Data table
st.subheader("Kategorie-Performance Tabelle")
st.dataframe(
    df_category.rename(columns={
        'category': 'Kategorie',
        'total_orders': 'Bestellungen',
        'total_revenue': 'Umsatz (EUR)',
        'avg_price': 'Durchschn. Preis (EUR)'
    }),
    use_container_width=True,
    hide_index=True
)

st.caption("Datenquelle: Google BigQuery Public Dataset TheLook E-commerce | Erstellt mit Python, BigQuery, Plotly und Streamlit")