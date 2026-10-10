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


def get_trade_marker_dates(equity: pd.DataFrame) -> tuple[list, list]:
    """Find the dates when the portfolio enters and exits stock positions."""
    buy_dates = []
    sell_dates = []
    previous_shares = 0

    for date in equity.index:
        current_shares = int(equity.loc[date, "Shares"])
        if previous_shares == 0 and current_shares > 0:
            buy_dates.append(date)
        elif previous_shares > 0 and current_shares == 0:
            sell_dates.append(date)
        previous_shares = current_shares

    return buy_dates, sell_dates


def show_strategy_lab() -> None:
    """Render the EMA crossover backtest and explain its results."""
    st.subheader("Strategy Lab")
    st.caption("Test a transparent historical rule against buy-and-hold. No trades are placed and historical results do not predict future returns.")
    st.markdown("**Set up a historical test**")
    st.caption("Choose a stock, period, and starting balance. Signals use completed daily candles and execute at the following session's open.")

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
    buy_dates, sell_dates = get_trade_marker_dates(equity)
    figures = go.Figure()
    figures.add_trace(go.Scatter(x=equity.index, y=equity["Strategy"], name="EMA 20/50 strategy", line={"color": "#c8ec68", "width": 2.8}))
    figures.add_trace(go.Scatter(x=equity.index, y=equity["Buy and hold"], name="Buy and hold", line={"color": "#70d4a2", "width": 2.2}))
    figures.add_trace(
        go.Scatter(
            x=buy_dates,
            y=[equity.loc[date, "Strategy"] for date in buy_dates],
            name="Entry executed",
            mode="markers",
            marker={"symbol": "triangle-up", "size": 12, "color": "#c8ec68", "line": {"color": "#111a15", "width": 1}},
            hovertemplate="Entry executed<br>%{x|%b %d, %Y}<br>Portfolio value: $%{y:,.2f}<extra></extra>",
        )
    )
    figures.add_trace(
        go.Scatter(
            x=sell_dates,
            y=[equity.loc[date, "Strategy"] for date in sell_dates],
            name="Exit executed",
            mode="markers",
            marker={"symbol": "triangle-down", "size": 12, "color": "#ed806e", "line": {"color": "#111a15", "width": 1}},
            hovertemplate="Exit executed<br>%{x|%b %d, %Y}<br>Portfolio value: $%{y:,.2f}<extra></extra>",
        )
    )
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
    st.markdown("**Backtest results**")
    st.caption(f"{st.session_state.backtest_ticker} · {st.session_state.backtest_period}-year historical test · {strategy}")
    st.plotly_chart(figures, width="stretch")
    st.caption("Triangles mark orders filled at the next trading day's open; their chart height shows that day's closing portfolio value.")

    metric_columns = st.columns(3)
    metric_columns[0].metric("Initial capital", f"${result['initial_capital']:,.2f}")
    metric_columns[1].metric("Final strategy value", f"${result['final_value']:,.2f}", f"{result['total_return']:+.2%}")
    metric_columns[2].metric("Buy-and-hold value", f"${result['buy_hold_final']:,.2f}", f"{result['buy_hold_return']:+.2%}")

    st.markdown("**Trade statistics**")
    trade_columns = st.columns(3)
    if result["win_rate"] is None:
        win_rate_text = "N/A"
    else:
        win_rate_text = f"{result['win_rate']:.1%}"
    if result["average_trade_profit"] is None:
        average_profit_text = "N/A"
    else:
        average_profit_text = f"${result['average_trade_profit']:+,.2f}"
    trade_columns[0].metric(
        "Trade win rate",
        win_rate_text,
        help="Winning completed trades divided by all completed trades. Open positions are not included.",
    )
    trade_columns[1].metric("Completed trades", result["completed_trade_count"])
    trade_columns[2].metric(
        "Average profit per trade",
        average_profit_text,
        help="Average net profit or loss across completed entry-and-exit pairs.",
    )

    st.markdown("**Performance comparison**")
    comparison_columns = st.columns(2)
    comparison_columns[0].metric(
        "Return vs. buy-and-hold",
        f"{result['excess_return'] * 100:+.2f} pp",
        help="Strategy total return minus buy-and-hold total return, in percentage points over this same test period.",
    )
    comparison_columns[1].metric("Maximum drawdown", f"{result['max_drawdown']:.2%}")
    st.markdown("**Reading the report**")
    st.write("Total return compares the ending portfolio value with the starting balance. Win rate counts completed trades with positive profit; a still-open position is not counted as a win or loss. Average profit includes both profitable and losing completed trades. Return versus buy-and-hold is the difference in total returns, measured in percentage points. Maximum drawdown is the largest peak-to-trough decline. An open position at the end is marked at the final close. Both approaches use the same dates and starting capital.")
    if result["trades"]:
        st.markdown("**Completed trades**")
        st.dataframe(pd.DataFrame(result["trades"]), width="stretch", hide_index=True)
    else:
        st.info("No crossover entry and exit pair completed during this period.")
