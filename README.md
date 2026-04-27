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

### Gold Layer
- Builds analytics-ready, conformed datasets using a star schema design
- Combines multiple Silver datasets (e.g., NYISO Day-Ahead and Real-Time prices) into a unified model
- Designed to support future expansion to additional markets (e.g., PJM, ERCOT)

#### Fact Tables
- **fact_market_price**
  - Grain: one row per market, market product, zone, and timestamp
  - Contains price measures and supporting metadata for analysis
  - Partitioned by market and time (year/month) for efficient querying

#### Dimension Tables
- **dim_market**
  - Represents each market (e.g., NYISO)

- **dim_market_product**
  - Represents market run types (e.g., Day-Ahead, Real-Time)

- **dim_zone**
  - Represents pricing locations (zones/nodes) within each market

#### Key Design Principles
- Uses conformed dimensions to enable cross-market analytics
- Keeps source-specific logic in Silver; Gold is fully standardized
- Supports incremental loading by processing only new market-date combinations
- Optimized for downstream BI tools (e.g., Power BI, Fabric semantic models)

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
