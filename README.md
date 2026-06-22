# Duschbrocken Sales Analytics Dashboard

An interactive sales analytics dashboard built with Python, Google BigQuery, 
Pandas, Plotly, and Streamlit. Demonstrates end-to-end cloud data engineering 
from SQL queries on BigQuery to interactive business intelligence dashboards.

## Features

- Live connection to Google BigQuery public e-commerce dataset
- SQL queries for data aggregation, filtering, and KPI calculation
- Interactive Plotly charts with zoom, filter, and hover capabilities
- KPI metrics: total revenue, orders, average order value, top category
- Monthly revenue trend line chart (last 12 months)
- Revenue by category horizontal bar chart (top 10)
- Top 10 products by revenue
- Customer segmentation by gender (pie chart)
- Return rate by category (horizontal bar chart)
- Order volume per month bar chart
- Category performance data table with German labels
- Duschbrocken branding with official logo

## Tech Stack

- Python 3.x
- Google BigQuery (public dataset: thelook_ecommerce)
- Pandas (data processing)
- Plotly (interactive visualizations)
- Streamlit (web dashboard framework)
- Google Cloud SDK (authentication)

## Architecture

Google BigQuery (SQL queries)
        ↓
Python + Pandas (data processing)
        ↓
Plotly (chart generation)
        ↓
Streamlit (web dashboard)

## Getting Started

### Prerequisites

- Python 3.8+
- Google Cloud SDK installed and authenticated
- Google Cloud project with BigQuery API enabled

### Installation

git clone https://github.com/ChandanaRS30/duschbrocken-analytics.git
cd duschbrocken-analytics
pip install -r requirements.txt

### Authentication

gcloud auth application-default login

### Run

python -m streamlit run app.py

Open http://localhost:8501 in your browser.

## Dataset

Uses the Google BigQuery public dataset `bigquery-public-data.thelook_ecommerce` 
which simulates a real e-commerce company with orders, products, and customer data.
The same pipeline architecture works directly with real
