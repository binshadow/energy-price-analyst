# Energy Price Analyst

An AI-powered data platform for ingesting, transforming, and analyzing energy market pricing data using a medallion architecture.

This project builds an end-to-end pipeline that collects public market data (starting with NYISO), stores it in a Parquet-based warehouse (Bronze/Silver/Gold), and exposes curated datasets to an AI-driven analytics layer that supports natural language querying.

---

## Overview

The objective of this project is to simulate a production-style data platform that combines:

- Data ingestion from external market sources
- Structured storage using Parquet
- Layered transformations (Bronze, Silver, Gold)
- Dimensional data modeling
- SQL-based analytics via DuckDB
- Natural language query capabilities using AI

---

## Architecture

External Data Sources (NYISO CSV/API)  
→ Bronze Layer (raw, append-only data)  
→ Silver Layer (cleaned and standardized data)  
→ Gold Layer (fact and dimension tables)  
→ DuckDB Query Layer  
→ AI Analyst (natural language to SQL)

---

## Data Pipeline

### Bronze Layer
- Ingests raw NYISO price data (Day-Ahead and Real-Time LBMP)
- Stores data as partitioned Parquet files
- Adds ingestion metadata:
  - `source_system`
  - `source_product`
  - `ingested_at_utc`

### Silver Layer (Planned)
- Standardizes schema across datasets
- Cleans and normalizes raw fields
- Handles deduplication and type consistency

### Gold Layer (Planned)
- Builds analytics-ready datasets:
  - Fact tables (price intervals, daily summaries)
  - Dimension tables (market, location, product, date)

---

## AI Query Layer (Planned)

The AI layer will allow users to query energy market data using natural language.

Example queries:

- What was the average price in NYC last week?
- Which zone had the highest price volatility yesterday?
- Show the largest price spikes this month
- Compare day-ahead vs real-time prices for Zone J

The system will:
1. Convert natural language into SQL
2. Execute queries against DuckDB
3. Return structured results and summaries

---

## Technology Stack

- Python
- Pandas
- DuckDB
- Parquet (PyArrow)
- Streamlit (planned)
- Local or API-based language models

---
