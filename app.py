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
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { line-height: 1.5; }
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
    .game-launch {
        background: linear-gradient(115deg, rgba(30, 45, 32, 0.96), rgba(16, 25, 20, 0.92));
        border: 1px solid var(--line);
        border-left: 4px solid var(--lime);
        margin: 1.2rem 0 1rem;
        padding: 1.6rem 1.7rem 1.25rem;
    }
    .game-launch-label, .game-round-label {
        color: var(--lime);
        font-size: 0.72rem;
        font-weight: 700;
        margin-bottom: 0.55rem;
        text-transform: uppercase;
    }
    .game-launch h2 {
        color: var(--text);
        font-size: 2.15rem;
        margin: 0 0 0.55rem;
    }
    .game-launch-intro {
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.6;
        margin: 0;
        max-width: 54rem;
    }
    .game-steps {
        border-top: 1px solid var(--line);
        display: grid;
        gap: 1.2rem;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        margin-top: 1.4rem;
        padding-top: 1.05rem;
    }
    .game-step-number { color: var(--lime); font-size: 0.72rem; font-weight: 700; }
    .game-step-title { color: var(--text); font-size: 0.88rem; font-weight: 700; margin: 0.25rem 0; }
    .game-step-copy { color: var(--muted); font-size: 0.78rem; line-height: 1.45; margin: 0; }
    .game-roundbar {
        align-items: center;
        border-bottom: 1px solid var(--line);
        display: flex;
        gap: 1.5rem;
        justify-content: space-between;
        margin: 1rem 0 0.5rem;
        padding: 0 0 0.9rem;
    }
    .game-roundbar h2 { font-size: 1.55rem; margin: 0; }
    .game-round-detail { color: var(--muted); font-size: 0.72rem; text-transform: uppercase; }
    .game-round-value { color: var(--text); font-size: 0.9rem; font-weight: 600; margin-top: 0.22rem; }
    @media (max-width: 720px) {
        .game-launch { padding: 1.2rem 1rem 1rem; }
        .game-launch h2 { font-size: 1.7rem; }
        .game-steps { gap: 0.8rem; grid-template-columns: 1fr; }
        .game-roundbar { align-items: flex-start; flex-direction: column; gap: 0.7rem; }
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
    "Choose a workspace",
    ["Trading Game", "Strategy Lab"],
    key="page_mode",
    format_func=lambda mode: f"{'01  PLAY' if mode == 'Trading Game' else '02  ANALYZE'}  /  {mode}",
)
st.sidebar.caption("Start with a game round, then investigate a historical strategy.")
st.sidebar.markdown("---")
st.sidebar.markdown("**MARKET DATA**")
st.sidebar.caption("Adjusted daily prices · Historical only · Not real-time")
st.sidebar.markdown("---")
st.sidebar.caption("Educational simulation. No real trades or brokerage connections.")

if page_mode == "Trading Game":
    show_trading_game()
else:
    show_strategy_lab()

