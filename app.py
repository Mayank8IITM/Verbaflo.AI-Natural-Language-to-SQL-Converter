import os
import traceback
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

from nlsql import nl_to_sql
from db import run_query

load_dotenv()

st.set_page_config(page_title="Verbaflo.ai -> AI Query Assistant", page_icon="🏠", layout="wide")

st.title("Verbaflo.ai – AI Query Assistant")
st.caption("Type a plain-English question about your rental business. The system generates SQL, runs it, and shows results.")

with st.expander("Examples you can click", expanded=True):
    examples = [
        "Give me the name of all User's ?", 
        "Who are the top 10 tenants by total rent paid?", 
        "What's the average rating of apartments?", 
    
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state['user_query'] = ex

query = st.text_area("Your question", value=st.session_state.get('user_query', ''), height=100, placeholder="e.g., Which landlords generated the most revenue this year?")

colA, colB = st.columns([1,1])
with colA:
    run_btn = st.button("Generate SQL & Run", type="primary")
with colB:
    show_sql_box = st.checkbox("Show generated SQL", value=True)

if run_btn and query.strip():
    with st.spinner("Thinking (Gemini → SQL) and querying DB..."):
        try:
            result = nl_to_sql(query.strip())
            if not result or not result.get('sql'):
                st.error("Sorry, unable to answer at this point in time.")
            else:
                sql = result['sql']
                notes = result.get('notes', '')
                conf = result.get('confidence', 0.0)
                if show_sql_box:
                    st.code(sql, language='sql')
                    st.caption(f"Model confidence: {conf:.2f} — {notes}")

                try:
                    df = run_query(sql)
                    if df.empty:
                        st.warning("No rows found.")
                    else:
                        st.success(f"Returned {len(df)} row(s).")
                        st.dataframe(df, use_container_width=True)
                except Exception as db_ex:
                    st.error("Sorry, unable to answer at this point in time.")
                    st.stop()
        except Exception as e:
            st.error("Sorry, unable to answer at this point in time.")
            st.caption(str(e))
            st.caption(traceback.format_exc())
elif run_btn:
    st.warning("Please enter a question.")

st.divider()
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f5f5f5;
        color: #333;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        border-top: 1px solid #eaeaea;
    }
    </style>
    <div class="footer">
        Created by <b>Mayank</b> from IIT Madras 🚀
    </div>
    """,
    unsafe_allow_html=True
)
