"""Strategy Lab controls and historical performance report."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from backtest import run_backtest
from indicators import add_indicators
from stock_data import SUPPORTED_TICKERS, get_stock_data


def _period_data(data: pd.DataFrame, years: int) -> pd.DataFrame:
    """Select the most recent requested number of calendar years."""
    last_date = data.index[-1]
    start_date = last_date - pd.DateOffset(years=years)
    return data.loc[data.index >= start_date].copy()


def _format_years(years: int) -> str:
    """Give the year selector a readable label."""
    if years == 1:
        return "1 year"
    return f"{years} years"


def show_strategy_lab() -> None:
    """Render the EMA crossover backtest and explain its results."""
    st.subheader("Strategy Lab")
    st.caption("Test a transparent historical rule against buy-and-hold. No trades are placed and historical results do not predict future returns.")

    default_ticker = st.session_state.get("lab_ticker", "AAPL")
    default_index = 0
    if default_ticker in SUPPORTED_TICKERS:
        default_index = SUPPORTED_TICKERS.index(default_ticker)

    ticker = st.selectbox("Stock", SUPPORTED_TICKERS, index=default_index)
    control_columns = st.columns(3)
    years = control_columns[0].selectbox(
        "Testing period",
        [1, 2, 3, 5],
        index=1,
        format_func=_format_years,
    )
    strategy = control_columns[1].selectbox("Strategy", ["EMA 20/50 Crossover"])
    capital = control_columns[2].number_input("Starting virtual balance ($)", min_value=100.0, max_value=1_000_000.0, value=10_000.0, step=1_000.0)

    if st.button("Run Backtest", type="primary"):
        try:
            historical = add_indicators(get_stock_data(ticker))
            testing_data = _period_data(historical, years)
            if len(testing_data) < 60:
                st.error("There are not enough daily prices in this period to calculate both moving averages.")
            else:
                st.session_state.backtest_result = run_backtest(testing_data, capital)
                st.session_state.backtest_ticker = ticker
                st.session_state.backtest_period = years
        except ValueError as error:
            st.error(str(error))

    result = st.session_state.get("backtest_result")
    if result is None:
        st.markdown("**EMA 20/50 Crossover**")
        st.write("Enter a long position when EMA 20 crosses above EMA 50. Exit when it crosses below. Each signal is calculated after a daily close and filled at the next trading day's open.")
        return

    equity = result["equity"]
    figures = go.Figure()
    figures.add_trace(go.Scatter(x=equity.index, y=equity["Strategy"], name="EMA 20/50 strategy", line={"color": "#c8ec68", "width": 2.8}))
    figures.add_trace(go.Scatter(x=equity.index, y=equity["Buy and hold"], name="Buy and hold", line={"color": "#70d4a2", "width": 2.2}))
    figures.update_layout(
        height=450,
        margin={"l": 12, "r": 12, "t": 28, "b": 12},
        yaxis_title="Portfolio value ($)",
        xaxis_title="Historical date",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111a15",
        font={"color": "#d9e2d7", "family": "Avenir Next, sans-serif"},
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.08, "x": 0},
        xaxis={"gridcolor": "#29372e", "linecolor": "#39473c"},
        yaxis={"gridcolor": "#29372e", "linecolor": "#39473c", "tickprefix": "$"},
    )
    st.markdown(f"**{st.session_state.backtest_ticker} · {st.session_state.backtest_period}-year historical test · {strategy}**")
    st.plotly_chart(figures, width="stretch")

    metric_columns = st.columns(3)
    metric_columns[0].metric("Initial capital", f"${result['initial_capital']:,.2f}")
    metric_columns[1].metric("Final strategy value", f"${result['final_value']:,.2f}", f"{result['total_return']:+.2%}")
    metric_columns[2].metric("Buy-and-hold value", f"${result['buy_hold_final']:,.2f}", f"{result['buy_hold_return']:+.2%}")
    metric_columns = st.columns(2)
    metric_columns[0].metric("Maximum drawdown", f"{result['max_drawdown']:.2%}")
    metric_columns[1].metric("Completed trades", len(result["trades"]))
    st.markdown("**Reading the report**")
    st.write("Total return compares the ending portfolio value with the starting balance. Maximum drawdown is the largest peak-to-trough decline. Completed trades count round trips from entry to exit; an open position at the end is marked at the final close. Buy-and-hold uses the same dates and starting capital.")
    if result["trades"]:
        st.markdown("**Completed trades**")
        st.dataframe(pd.DataFrame(result["trades"]), width="stretch", hide_index=True)
        st.info("No crossover entry and exit pair completed during this period.")
