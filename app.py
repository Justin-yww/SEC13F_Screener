"""
The Streamlit dashboard entry point.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import plotly.express as px
from config import DEFAULT_CIK, TOP_N
from src.pipeline import run, load_entities

st.set_page_config(page_title="13F Terminal", layout="wide")
st.title("13F Institutional Holdings Monitor")

# Data retrieval function with caching for 1 hour
@st.cache_data(ttl=3600)
def get_data(cik: str, force: bool = False) -> dict:
    return run(cik, force_refresh=force)


# Sidebar controls
entities = load_entities()
name_to_cik = {e["name"]: e["cik"] for e in entities}
default_name = next(
    (e["name"] for e in entities if e["cik"] == DEFAULT_CIK),
    entities[0]["name"],
)
with st.sidebar:
    st.header("Settings")
    cik_input = st.text_input(
        "CIK number",
        value=DEFAULT_CIK,
        max_chars=10,
        placeholder="e.g. 0001067983",
        help="10-digit SEC Central Index Key. Find it at www.sec.gov/cgi-bin/browse-edgar"
    )
    force_refresh = st.button("Refresh from EDGAR")
    st.caption(f"Showing top {TOP_N} buys and sells by share count.")

# Pad to 10 digits and validate
cik = cik_input.strip().zfill(10)
if not cik.isdigit() or len(cik) != 10:
    st.error("Please enter a valid numeric CIK.")
    st.stop()

# Data fetch
with st.spinner("Loading filings..."):
    data = get_data(cik, force=force_refresh)

buys  = data["top_buys"]
sells = data["top_sells"]
meta  = data.get("meta", {})

if meta.get("fetched_at"):
    st.caption(f"Data fetched: {meta['fetched_at'][:19].replace('T', ' ')} UTC")

# Charts
col_b, col_s = st.columns(2)

_DISPLAY_COLS = {
    "name": "Issuer",
    "ticker": "Ticker",
    "shares": "Shares (current)",
    "share_delta": "Δ shares",
    "value_usd": "Value (USD)",
    "action": "Action",
}

with col_b:
    st.subheader(f"Top {TOP_N} buys")
    fig = px.bar(
        buys,
        x="ticker",
        y="share_delta",
        color_discrete_sequence=["#10b981"],
        labels={"share_delta": "Shares added", "ticker": ""},
    )
    fig.update_layout(showlegend=False, margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(
        buys[list(_DISPLAY_COLS.keys())].rename(columns=_DISPLAY_COLS),
        use_container_width=True,
        hide_index=True,
    )

with col_s:
    st.subheader(f"Top {TOP_N} sells")
    fig = px.bar(
        sells,
        x="ticker",
        y="share_delta",
        color_discrete_sequence=["#e11d48"],
        labels={"share_delta": "Shares removed", "ticker": ""},
    )
    fig.update_layout(showlegend=False, margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(
        sells[list(_DISPLAY_COLS.keys())].rename(columns=_DISPLAY_COLS),
        use_container_width=True,
        hide_index=True,
    )

# Full change table
st.divider()
st.subheader("All position changes")

all_df = data["all_changes"]
action_options = sorted(all_df["action"].unique().tolist())
selected_actions = st.multiselect("Filter by action", action_options,default=action_options)

st.dataframe(
    all_df[all_df["action"].isin(selected_actions)][list(_DISPLAY_COLS.keys())]
    .rename(columns=_DISPLAY_COLS)
    .reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)
