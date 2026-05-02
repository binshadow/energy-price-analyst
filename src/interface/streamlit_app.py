# src/interface/streamlit_app.py
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from src.query.semantic_query_runner import run_semantic_query


st.set_page_config(
    page_title="Energy Price Analyst",
    layout="wide",
)

st.title("Energy Price Analyst")

st.write(
    "Ask a question about market prices. "
    "The app will generate SQL, run it against the gold layer, and return a table."
)

question = st.text_area(
    "Question",
    placeholder="Example: Show me the top 20 highest NYISO day-ahead LBMP prices.",
    height=120,
)

run_button = st.button("Run Analysis")

if run_button:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Generating SQL and running query..."):
                sql, df = run_semantic_query(question)

            st.subheader("Generated SQL")
            st.code(sql, language="sql")

            st.subheader("Results")
            st.dataframe(df, use_container_width=True)

        except Exception as exc:
            st.error(str(exc))