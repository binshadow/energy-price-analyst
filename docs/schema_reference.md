# Energy Price Analyst Schema Reference

This document describes the local Parquet warehouse schema used by the Energy Price Analyst project.

## Bronze Layer

Base path: `G:\data\energy-price-analyst\bronze`

### `market=nyiso/product=day_ahead_lbmp/year=2026/month=04`

| Column | Type |
|---|---|
| `Time Stamp` | `VARCHAR` |
| `Name` | `VARCHAR` |
| `PTID` | `BIGINT` |
| `LBMP ($/MWHr)` | `DOUBLE` |
| `Marginal Cost Losses ($/MWHr)` | `DOUBLE` |
| `Marginal Cost Congestion ($/MWHr)` | `DOUBLE` |
| `source_system` | `VARCHAR` |
| `source_product` | `VARCHAR` |
| `source_url` | `VARCHAR` |
| `market_date` | `VARCHAR` |
| `ingested_at_utc` | `VARCHAR` |
| `market` | `VARCHAR` |
| `month` | `VARCHAR` |
| `product` | `VARCHAR` |
| `year` | `BIGINT` |

### `market=nyiso/product=real_time_lbmp/year=2026/month=04`

| Column | Type |
|---|---|
| `Time Stamp` | `VARCHAR` |
| `Name` | `VARCHAR` |
| `PTID` | `BIGINT` |
| `LBMP ($/MWHr)` | `DOUBLE` |
| `Marginal Cost Losses ($/MWHr)` | `DOUBLE` |
| `Marginal Cost Congestion ($/MWHr)` | `DOUBLE` |
| `source_system` | `VARCHAR` |
| `source_product` | `VARCHAR` |
| `source_url` | `VARCHAR` |
| `market_date` | `VARCHAR` |
| `ingested_at_utc` | `VARCHAR` |
| `market` | `VARCHAR` |
| `month` | `VARCHAR` |
| `product` | `VARCHAR` |
| `year` | `BIGINT` |

## Silver Layer

Base path: `G:\data\energy-price-analyst\silver`

### `market=nyiso/product=day_ahead_lbmp/year=2026/month=04`

| Column | Type |
|---|---|
| `timestamp` | `TIMESTAMP` |
| `zone_name` | `VARCHAR` |
| `ptid` | `BIGINT` |
| `lbmp` | `DOUBLE` |
| `marginal_cost_losses` | `DOUBLE` |
| `marginal_cost_congestion` | `DOUBLE` |
| `source_system` | `VARCHAR` |
| `source_product` | `VARCHAR` |
| `source_url` | `VARCHAR` |
| `market_date` | `DATE` |
| `bronze_ingested_at_utc` | `TIMESTAMP WITH TIME ZONE` |
| `silver_ingested_at_utc` | `TIMESTAMP WITH TIME ZONE` |
| `market` | `VARCHAR` |
| `month` | `VARCHAR` |
| `product` | `VARCHAR` |
| `year` | `BIGINT` |

### `market=nyiso/product=real_time_lbmp/year=2026/month=04`

| Column | Type |
|---|---|
| `timestamp` | `TIMESTAMP` |
| `zone_name` | `VARCHAR` |
| `ptid` | `BIGINT` |
| `lbmp` | `DOUBLE` |
| `marginal_cost_losses` | `DOUBLE` |
| `marginal_cost_congestion` | `DOUBLE` |
| `source_system` | `VARCHAR` |
| `source_product` | `VARCHAR` |
| `source_url` | `VARCHAR` |
| `market_date` | `DATE` |
| `bronze_ingested_at_utc` | `TIMESTAMP WITH TIME ZONE` |
| `silver_ingested_at_utc` | `TIMESTAMP WITH TIME ZONE` |
| `market` | `VARCHAR` |
| `month` | `VARCHAR` |
| `product` | `VARCHAR` |
| `year` | `BIGINT` |

## Gold Layer

Base path: `G:\data\energy-price-analyst\gold`

### `dimensions/dim_market`


| Column | Type |
|---|---|
| `market_key` | `VARCHAR` |
| `market_code` | `VARCHAR` |
| `market_name` | `VARCHAR` |

### `dimensions/dim_market_product`

| Column | Type |
|---|---|
| `market_product_key` | `VARCHAR` |
| `market_key` | `VARCHAR` |
| `product_code` | `VARCHAR` |
| `product_name` | `VARCHAR` |

---

### `dimensions/dim_zone`

| Column | Type |
|---|---|
| `zone_key` | `VARCHAR` |
| `market_key` | `VARCHAR` |
| `zone_name` | `VARCHAR` |
| `ptid` | `BIGINT` |

### `facts/fact_market_price/market=nyiso/year=2026/month=04`

| Column | Type |
|---|---|
| `market_key` | `VARCHAR` |
| `market_product_key` | `VARCHAR` |
| `zone_key` | `VARCHAR` |
| `timestamp` | `TIMESTAMP` |
| `market_date` | `DATE` |
| `lbmp` | `DOUBLE` |
| `marginal_cost_losses` | `DOUBLE` |
| `marginal_cost_congestion` | `DOUBLE` |
| `source_url` | `VARCHAR` |
| `bronze_ingested_at_utc` | `TIMESTAMP WITH TIME ZONE` |
| `silver_ingested_at_utc` | `TIMESTAMP WITH TIME ZONE` |
| `gold_ingested_at_utc` | `TIMESTAMP WITH TIME ZONE` |
| `market` | `VARCHAR` |
| `month` | `VARCHAR` |
| `year` | `BIGINT` |

## Gold Layer Relationships

### Fact Table

`facts/fact_market_price`

Grain: one row per market, product, zone/location, and timestamp.

### Dimension Relationships

| Fact Table | Fact Column | Dimension Table | Dimension Column | Relationship |
|---|---|---|---|---|
| `facts/fact_market_price` | `market_key` | `dimensions/dim_market` | `market_key` | many-to-one |
| `facts/fact_market_price` | `market_product_key` | `dimensions/dim_market_product` | `market_product_key` | many-to-one |
| `facts/fact_market_price` | `zone_key` | `dimensions/dim_zone` | `zone_key` | many-to-one |

## Business Meaning

The gold layer uses a star-schema-style model.

`fact_market_price` contains interval-level price observations.

Dimensions provide descriptive context:

- `dim_market` describes the market, such as NYISO.
- `dim_market_product` describes the price product, such as day-ahead LBMP or real-time LBMP.
- `dim_zone` describes the pricing zone or location.

For analytics, queries should generally start from `fact_market_price` and join to dimensions using the key columns.
