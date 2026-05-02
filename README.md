# Energy Price Analyst

A local, end-to-end data platform for ingesting, modeling, and analyzing wholesale energy market prices, enhanced with an AI-powered natural language query interface.

This project demonstrates a modern data architecture using the medallion pattern combined with a local LLM, LLaMA via Ollama, to enable natural language to SQL analytics workflows.

---

## Overview

Energy Price Analyst is designed to:

- Ingest ISO market data, starting with NYISO LBMP
- Transform raw data into a structured analytics model
- Store data in a Parquet-based warehouse using Bronze, Silver, and Gold layers
- Enable users to query data using natural language
- Generate SQL dynamically using a local LLM
- Return results through an interactive Streamlit UI

---

## Architecture

```text
Raw Data
  ↓
Bronze Layer
  ↓
Silver Layer
  ↓
Gold Layer
  ↓
DuckDB
  ↓
LLaMA via Ollama
  ↓
Streamlit UI
```

---

## Tech Stack

- Python
- DuckDB
- Parquet
- Pandas
- Streamlit
- Ollama
- LLaMA 3.1
- YAML
- python-dotenv

---

## Project Structure

```text
src/
  ai/                  # LLM integration and SQL generation
  ingestion/           # Source ingestion logic
  transformation/      # Bronze to Silver to Gold transforms
  query/               # SQL execution and validation
  interface/           # Streamlit UI
  orchestration/       # ETL runner
  utils/               # Config and helpers

config/
  settings.yaml        # Path and model configuration

main.py                # Main command entry point
.env.example           # Environment template
```

---

## Data Model

The Gold layer uses a star schema optimized for analytics.

### Fact Table

**fact_market_price**

Grain: one row per market, product, zone or location, and timestamp.

Measures include:

- `lbmp`
- `marginal_cost_losses`
- `marginal_cost_congestion`

### Dimensions

- `dim_market`
- `dim_market_product`
- `dim_zone`

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/binshadow/energy-price-analyst.git
cd energy-price-analyst
```

### 2. Create virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

For Mac or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Create a `.env` file from `.env.example`.

```text
DATA_ROOT=G:\data\energy-price-analyst
AI_PROVIDER=ollama
```

### 5. Start Ollama

Make sure Ollama is running and the model is installed.

```bash
ollama run llama3.1
```

---

## Usage

### Run ETL pipeline

```bash
python main.py etl
```

This will ingest source data, build the Silver layer, and generate Gold-layer analytics tables.

### Launch AI interface

```bash
python main.py ui
```

Example questions:

- Show top 10 highest LBMP prices
- Average real-time price by zone last month
- Compare day-ahead vs real-time prices

---

## AI Query Layer

The system converts natural language questions into SQL using a local LLaMA model.

```text
User question
  ↓
Prompt and schema context
  ↓
LLaMA via Ollama
  ↓
Generated SQL
  ↓
SQL validation
  ↓
DuckDB execution
  ↓
Results returned to UI
```

### Safety Controls

- Only SELECT statements are allowed
- Destructive SQL keywords are blocked
- Queries are restricted to approved Gold-layer views
- Generated SQL does not use file paths

---

## Configuration

| Variable | Description |
|---|---|
| `DATA_ROOT` | Root directory for all local data layers |
| `AI_PROVIDER` | AI backend, currently `ollama` |

---

## Roadmap

- Dynamic schema injection
- Chart generation in the UI
- AI-generated result summaries
- Support for additional ISOs such as PJM and ERCOT
- CLI query mode using `python main.py ask`
- Data quality validation layer

---

## Why This Project Matters

This project demonstrates:

- End-to-end data engineering
- Medallion architecture using local Parquet storage
- Gold-layer star schema modeling
- Natural language to SQL querying
- Local-first AI integration
- Modular, configuration-driven Python design

---

## License

MIT License