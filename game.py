import random

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from backtest import evaluate_direction
from indicators import add_indicators
from stock_data import SUPPORTED_TICKERS, get_stock_data


def round_chart_data(data: pd.DataFrame, decision_index: int, revealed: bool) -> pd.DataFrame:
    """Return only decision-day candles until the user has made a prediction."""
    first_index = max(0, decision_index - 59)
    if revealed:
        last_index = decision_index + 6
    else:
        last_index = decision_index + 1
    return data.iloc[first_index:last_index].copy()


def score_round_once(state: dict, correct: bool, result: dict) -> bool:
    """Update score and history once, even if Streamlit reruns  page."""
    if state["round_scored"]:
        return False

    state["round_scored"] = True
    if correct:
        state["score"] += 1
        state["streak"] += 1
        state["best_streak"] = max(state["best_streak"], state["streak"])
    else:
        state["streak"] = 0
    state["round_history"].append(result)
    return True


def _initialize_game_state() -> None:
    defaults = {
        "game_active": False,
        "game_over": False,
        "round_number": 0,
        "score": 0,
        "streak": 0,
        "best_streak": 0,
        "round_history": [],
        "seen_rounds": [],
        "prediction": None,
        "round_scored": False,
        "current_round": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _start_game() -> None:
    st.session_state.game_active = True
    st.session_state.game_over = False
    st.session_state.round_number = 1
    st.session_state.score = 0
    st.session_state.streak = 0
    st.session_state.best_streak = 0
    st.session_state.round_history = []
    st.session_state.seen_rounds = []
    st.session_state.prediction = None
    st.session_state.round_scored = False
    st.session_state.current_round = None


def _open_strategy_lab(ticker: str) -> None:
    """Switch modes before Streamlit recreates the keyed navigation widget."""
    st.session_state.lab_ticker = ticker
    st.session_state.page_mode = "Strategy Lab"


def _pick_round() -> tuple[str, pd.DataFrame, int]:
    """Choose an unseen ticker/date with enough warmup and future candles."""
    tickers = SUPPORTED_TICKERS.copy()
    random.shuffle(tickers)
    for ticker in tickers:
        try:
            data = add_indicators(get_stock_data(ticker))
        except ValueError:
            continue
        unseen = []
        for index in range(200, len(data) - 5):
            round_id = f"{ticker}:{data.index[index].date()}"
            if round_id not in st.session_state.seen_rounds:
                unseen.append(index)
        if unseen:
            decision_index = random.choice(unseen)
            st.session_state.seen_rounds.append(
                f"{ticker}:{data.index[decision_index].date()}"
            )
            return ticker, data, decision_index
    raise ValueError("No new historical rounds are available. Start a new game to try again.")


def _begin_round() -> None:
    ticker, data, decision_index = _pick_round()
    st.session_state.current_round = {
        "ticker": ticker,
        "data": data,
        "decision_index": decision_index,
    }
    st.session_state.prediction = None
    st.session_state.round_scored = False


def _indicator_summary(row: pd.Series) -> None:
    columns = st.columns(3)

    rsi = row.get("RSI_14")
    if pd.isna(rsi):
        rsi_display = "--"
    else:
        rsi_display = f"{rsi:.2f}"
    columns[0].metric("RSI (14)", rsi_display)
    columns[0].caption("Momentum on a 0-100 scale; high readings can indicate a stretched move.")

    macd = row.get("MACD")
    if pd.isna(macd):
        macd_display = "--"
    else:
        macd_display = f"{macd:.2f}"
    columns[1].metric("MACD", macd_display)
    columns[1].caption("Difference between fast and slow averages; its signal line helps show momentum shifts.")

    relative_volume = row.get("RVOL")
    if pd.isna(relative_volume):
        volume_display = "--"
    else:
        volume_display = f"{relative_volume:.2f}"
    columns[2].metric("Relative volume", volume_display)
    columns[2].caption("Today's volume divided by its recent 20-day average.")


def _draw_game_chart(data: pd.DataFrame, decision_index: int, revealed: bool) -> None:
    visible = round_chart_data(data, decision_index, revealed)
    figure = go.Figure()
    figure.add_trace(
        go.Candlestick(
            x=visible.index,
            open=visible["Open"],
            high=visible["High"],
            low=visible["Low"],
            close=visible["Close"],
            name="Price",
            increasing_line_color="#c8ec68",
            decreasing_line_color="#ed806e",
        )
    )
    figure.add_trace(go.Scatter(x=visible.index, y=visible["EMA_20"], name="EMA 20", line={"color": "#70d4a2", "width": 2}))
    figure.add_trace(go.Scatter(x=visible.index, y=visible["EMA_50"], name="EMA 50", line={"color": "#e8b66e", "width": 2}))
    figure.add_vline(x=data.index[decision_index], line_dash="dot", line_color="#c8ec68")
    figure.update_layout(
        height=430,
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        xaxis_rangeslider_visible=False,
        legend={"orientation": "h", "y": 1.08},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111a15",
        font={"color": "#d9e2d7", "family": "Avenir Next, sans-serif"},
        yaxis_title="Adjusted price ($)",
        xaxis={"gridcolor": "#29372e", "linecolor": "#39473c"},
        yaxis={"gridcolor": "#29372e", "linecolor": "#39473c"},
    )
    st.plotly_chart(figure, width="stretch")


def _show_game_results() -> None:
    history = st.session_state.round_history
    player_accuracy = st.session_state.score / 10 * 100
    algorithm_correct = sum(item["Algorithm correct"] for item in history)
    columns = st.columns(4)
    columns[0].metric("Player accuracy", f"{player_accuracy:.0f}%")
    columns[1].metric("Algorithm accuracy", f"{algorithm_correct / 10 * 100:.0f}%")
    columns[2].metric("Correct calls", f"{st.session_state.score} / 10")
    columns[3].metric("Best streak", st.session_state.best_streak)

    if history:
        results = pd.DataFrame(history)
        st.dataframe(results, width="stretch", hide_index=True)
        chart = go.Figure()
        chart.add_bar(name="Player", x=["Correct predictions"], y=[st.session_state.score], marker_color="#c8ec68")
        chart.add_bar(name="Rule-Based Algorithm", x=["Correct predictions"], y=[algorithm_correct], marker_color="#70d4a2")
        chart.update_layout(
            barmode="group",
            height=280,
            margin={"l": 10, "r": 10, "t": 30, "b": 10},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#111a15",
            font={"color": "#d9e2d7", "family": "Avenir Next, sans-serif"},
            yaxis={"gridcolor": "#29372e", "range": [0, 10], "dtick": 2},
        )
        st.plotly_chart(chart, width="stretch")
    st.button("Play Again", on_click=_start_game, type="primary")


def show_trading_game() -> None:
    """Render the ten-round game and preserve progress across reruns."""
    _initialize_game_state()
    st.subheader("Trading Game")
    st.caption("Read a historical chart, call the next five trading days, then compare your result with a transparent rule.")

    if not st.session_state.game_active and not st.session_state.game_over:
        st.info("Ten rounds. Predict whether the adjusted closing price five trading days later is UP or DOWN. Ties do not score.")
        st.button("Start Game", on_click=_start_game, type="primary")
        return
    if st.session_state.game_over:
        st.success("Game complete. These historical results are educational, not a forecast.")
        _show_game_results()
        return

    if st.session_state.current_round is None:
        try:
            _begin_round()
        except ValueError as error:
            st.error(str(error))
            return

    current = st.session_state.current_round
    data = current["data"]
    decision_index = current["decision_index"]
    decision_row = data.iloc[decision_index]
    st.markdown(f"**Round {st.session_state.round_number} of 10**  ·  `{current['ticker']}`  ·  {data.index[decision_index].date()}")
    _draw_game_chart(data, decision_index, st.session_state.prediction is not None)
    _indicator_summary(decision_row)
    st.caption("EMA 20/50 show shorter- and longer-term average price trends. The chart stops at the decision date until you submit a prediction.")

    if st.session_state.prediction is None:
        st.markdown("### Your call")
        up_column, down_column = st.columns(2)
        if up_column.button("Predict UP", width="stretch", type="primary"):
            st.session_state.prediction = "UP"
            st.rerun()
        if down_column.button("Predict DOWN", width="stretch", type="primary"):
            st.session_state.prediction = "DOWN"
            st.rerun()
    else:
        future_close = float(data["Close"].iloc[decision_index + 5])
        start_close = float(decision_row["Close"])
        actual = evaluate_direction(start_close, future_close)
        fast_average = decision_row["EMA_20"]
        slow_average = decision_row["EMA_50"]
        rsi = decision_row["RSI_14"]
        if fast_average > slow_average and rsi < 70:
            algorithm = "UP"
        else:
            algorithm = "DOWN"
        change = (future_close / start_close - 1) * 100
        player_correct = st.session_state.prediction == actual
        algorithm_correct = algorithm == actual
        if player_correct:
            player_result_text = "correct"
        else:
            player_result_text = "not correct"
        if algorithm_correct:
            algorithm_result_text = "correct"
        else:
            algorithm_result_text = "not correct"
        result = {
            "Round": st.session_state.round_number,
            "Ticker": current["ticker"],
            "Date": str(data.index[decision_index].date()),
            "Your call": st.session_state.prediction,
            "Your prediction correct": player_correct,
            "Actual": actual,
            "Change": f"{change:+.2f}%",
            "Rule-based call": algorithm,
            "Algorithm correct": algorithm_correct,
        }
        score_round_once(st.session_state, player_correct, result)
        if actual == "TIE":
            st.info(f"The five-day result was unchanged ({change:+.2f}%). A tie is neither UP nor DOWN.")
        else:
            st.success(f"Actual move: **{actual}** ({change:+.2f}%). Your prediction was {player_result_text}.")
        st.write(f"Rule-Based Algorithm: **{algorithm}**. It was {algorithm_result_text}.")
        st.caption("Rule: predict UP when EMA 20 is above EMA 50 and RSI is below 70; otherwise predict DOWN. It uses only indicators known on the decision date.")
        score_columns = st.columns(3)
        score_columns[0].metric("Score", f"{st.session_state.score} / 10")
        score_columns[1].metric("Current streak", st.session_state.streak)
        score_columns[2].metric("Best streak", st.session_state.best_streak)
        st.button(
            "Explore This Strategy",
            key="explore_game_strategy",
            on_click=_open_strategy_lab,
            args=(current["ticker"],),
        )
        if st.button("Next Round", type="primary"):
            st.session_state.round_number += 1
            st.session_state.current_round = None
            st.session_state.prediction = None
            st.session_state.round_scored = False
            if st.session_state.round_number > 10:
                st.session_state.game_active = False
                st.session_state.game_over = True
            st.rerun()