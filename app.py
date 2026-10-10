"""MarketLab: a historical trading game and strategy lab."""

import streamlit as st

from game import show_trading_game
from strategy_lab import show_strategy_lab


st.set_page_config(page_title="MarketLab | Learn the market", page_icon="📈", layout="wide")
st.markdown(
    """
    <style>
    :root {
        --ink: #0b100d;
        --panel: #111a15;
        --panel-raised: #18231c;
        --line: #2b3a30;
        --text: #eef1e5;
        --muted: #a0ada0;
        --lime: #c8ec68;
        --mint: #70d4a2;
        --amber: #e8b66e;
        --coral: #ed806e;
    }
    .stApp {
        background-color: var(--ink);
        background-image: linear-gradient(rgba(107, 139, 104, 0.035) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(107, 139, 104, 0.035) 1px, transparent 1px);
        background-size: 34px 34px;
        color: var(--text);
    }
    [data-testid="stSidebar"] {
        background: #0e1713;
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
    .block-container { max-width: 1510px; padding-top: 1.25rem; padding-bottom: 3rem; }
    h1, h2, h3 { color: var(--text); font-family: Georgia, "Palatino Linotype", serif; }
    h2 { font-size: 1.65rem; margin-top: 1.2rem; }
    p, label, [data-testid="stCaptionContainer"] { color: var(--muted); }
    [data-testid="stAlert"] {
        background: #18221b;
        border: 1px solid #39483a;
        border-left: 3px solid var(--lime);
        border-radius: 4px;
    }
    [data-testid="stAlertContainer"] {
        background: #18221b !important;
        color: var(--text);
    }
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p { color: var(--text); }
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, var(--panel-raised), var(--panel));
        border: 1px solid var(--line);
        border-top: 2px solid var(--mint);
        padding: 16px 18px;
        border-radius: 4px;
        min-height: 104px;
    }
    [data-testid="stMetricLabel"] { color: var(--muted); font-size: 0.78rem; }
    [data-testid="stMetricValue"] { color: var(--text); font-variant-numeric: tabular-nums; }
    [data-testid="stMetricDelta"] { font-variant-numeric: tabular-nums; }
    [data-testid="stPlotlyChart"] {
        background: rgba(17, 26, 21, 0.88);
        border: 1px solid var(--line);
        border-radius: 4px;
        padding: 0.55rem;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 4px;
        overflow: hidden;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        border-radius: 4px;
        padding: 0.2rem 0.3rem;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: #1c2a20;
        color: var(--lime);
        border-left: 2px solid var(--lime);
    }
    [data-testid="stSelectbox"], [data-testid="stNumberInput"] { color: var(--text); }
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background: var(--panel);
        border-color: var(--line);
    }
    div[data-testid="stButton"] button {
        border-radius: 4px;
        min-height: 2.7rem;
        font-weight: 600;
        transition: border-color 120ms ease, background-color 120ms ease, color 120ms ease;
    }
    div[data-testid="stButton"] button[kind="primary"] {
        background: var(--lime);
        border-color: var(--lime);
        color: #17200e;
        font-weight: 700;
    }
    div[data-testid="stButton"] button[kind="primary"] p { color: #17200e; }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background: #d9f58d;
        border-color: #d9f58d;
        color: #17200e;
    }
    div[data-testid="stButton"] button:hover { border-color: var(--mint); color: var(--mint); }
    .marketlab-masthead {
        align-items: center;
        background: linear-gradient(100deg, rgba(29, 44, 33, 0.92), rgba(17, 26, 21, 0.72));
        border: 1px solid var(--line);
        border-left: 3px solid var(--lime);
        display: flex;
        justify-content: space-between;
        margin-bottom: 1.45rem;
        padding: 1rem 1.2rem;
        gap: 1rem;
    }
    .marketlab-brand { align-items: center; display: flex; gap: 0.85rem; }
    .marketlab-mark {
        align-items: center;
        background: var(--lime);
        border-radius: 3px;
        color: #17200e;
        display: flex;
        font-family: Georgia, serif;
        font-size: 1rem;
        font-weight: 700;
        height: 2.75rem;
        justify-content: center;
        width: 2.75rem;
    }
    .marketlab-name {
        color: var(--text);
        font-family: Georgia, "Palatino Linotype", serif;
        font-size: 1.45rem;
        font-weight: 700;
        margin: 0;
    }
    .marketlab-tagline { color: var(--muted); font-size: 0.82rem; margin-top: 0.12rem; }
    .marketlab-status {
        align-items: center;
        border: 1px solid var(--line);
        border-radius: 3px;
        color: var(--mint);
        display: flex;
        font-size: 0.7rem;
        padding: 0.45rem 0.65rem;
        text-transform: uppercase;
    }
    .marketlab-status-dot {
        background: var(--mint);
        border-radius: 50%;
        display: inline-block;
        height: 0.42rem;
        margin-right: 0.45rem;
        width: 0.42rem;
    }
    @media (max-width: 640px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; }
        .marketlab-masthead { align-items: flex-start; padding: 0.85rem; }
        .marketlab-status { font-size: 0.62rem; padding: 0.4rem; }
        .marketlab-tagline { max-width: 15rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <header class="marketlab-masthead">
        <div class="marketlab-brand">
            <div class="marketlab-mark">ML</div>
            <div>
                <h1 class="marketlab-name">MarketLab</h1>
                <div class="marketlab-tagline">Read the chart. Understand the signal. Test the idea.</div>
            </div>
        </div>
        <div class="marketlab-status"><span class="marketlab-status-dot"></span>Historical data only</div>
    </header>
    """,
    unsafe_allow_html=True,
)

st.session_state.setdefault("page_mode", "Trading Game")
page_mode = st.sidebar.radio(
    "Explore",
    ["Trading Game", "Strategy Lab"],
    key="page_mode",
    format_func=lambda mode: f"{'01' if mode == 'Trading Game' else '02'}  /  {mode}",
)
st.sidebar.markdown("---")
st.sidebar.markdown("**MARKET DATA**")
st.sidebar.caption("Adjusted daily prices · Historical only · Not real-time")
st.sidebar.markdown("---")
st.sidebar.caption("Educational simulation. No real trades or brokerage connections.")

if page_mode == "Trading Game":
    show_trading_game()
else:
    show_strategy_lab()

