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
    elif result.get("Actual") != "TIE":
        state["streak"] = 0
    state["round_history"].append(result)
    return True


def calculate_game_accuracy(history: list[dict]) -> tuple[float | None, float | None, int]:
    """Calculate directional accuracy while leaving tied rounds neutral."""
    decisive_round_count = 0
    player_correct_count = 0
    algorithm_correct_count = 0
    tie_count = 0

    for result in history:
        if result["Actual"] == "TIE":
            tie_count += 1
        else:
            decisive_round_count += 1
            if result["Your prediction correct"]:
                player_correct_count += 1
            if result["Algorithm correct"]:
                algorithm_correct_count += 1

    if decisive_round_count == 0:
        return None, None, tie_count

    player_accuracy = player_correct_count / decisive_round_count * 100
    algorithm_accuracy = algorithm_correct_count / decisive_round_count * 100
    return player_accuracy, algorithm_accuracy, tie_count


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
    history_start = max(0, decision_index - 59)
    history = data.iloc[history_start:decision_index + 1]
    figure = go.Figure()
    figure.add_trace(
        go.Candlestick(
            x=history.index,
            open=history["Open"],
            high=history["High"],
            low=history["Low"],
            close=history["Close"],
            name="Price history",
            increasing_line_color="#c8ec68",
            decreasing_line_color="#ed806e",
        )
    )
    if revealed:
        future_data = data.iloc[decision_index + 1:decision_index + 6]
        figure.add_trace(
            go.Candlestick(
                x=future_data.index,
                open=future_data["Open"],
                high=future_data["High"],
                low=future_data["Low"],
                close=future_data["Close"],
                name="Five-day reveal",
                increasing_line_color="#70d4a2",
                decreasing_line_color="#e8b66e",
            )
        )
        figure.add_vrect(
            x0=future_data.index[0],
            x1=future_data.index[-1],
            fillcolor="rgba(200, 236, 104, 0.08)",
            line_width=0,
            layer="below",
        )

    visible = round_chart_data(data, decision_index, revealed)
    figure.add_trace(go.Scatter(x=visible.index, y=visible["EMA_20"], name="EMA 20", line={"color": "#70d4a2", "width": 2}))
    figure.add_trace(go.Scatter(x=visible.index, y=visible["EMA_50"], name="EMA 50", line={"color": "#e8b66e", "width": 2}))
    figure.add_vline(
        x=data.index[decision_index],
        line_dash="dot",
        line_color="#c8ec68",
        annotation_text="Decision",
        annotation_position="top",
        annotation_font_color="#c8ec68",
    )
    figure.update_layout(
        height=470,
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
    player_accuracy, algorithm_accuracy, tie_count = calculate_game_accuracy(history)
    algorithm_correct = 0
    for result in history:
        if result["Actual"] != "TIE" and result["Algorithm correct"]:
            algorithm_correct += 1

    if player_accuracy is None:
        player_accuracy_text = "N/A"
        algorithm_accuracy_text = "N/A"
    else:
        player_accuracy_text = f"{player_accuracy:.0f}%"
        algorithm_accuracy_text = f"{algorithm_accuracy:.0f}%"

    columns = st.columns(5)
    columns[0].metric("Player accuracy", player_accuracy_text)
    columns[1].metric("Algorithm accuracy", algorithm_accuracy_text)
    columns[2].metric("Correct calls", f"{st.session_state.score} / 10")
    columns[3].metric("Best streak", st.session_state.best_streak)
    columns[4].metric("Tie rounds", tie_count)

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

    if not st.session_state.game_active and not st.session_state.game_over:
        st.markdown(
            """
            <section class="game-launch">
                <div class="game-launch-label">Trading Game / 10 rounds</div>
                <h2>Read the chart. Make your call.</h2>
                <p class="game-launch-intro">Study a historical stock chart, predict whether its closing price will be higher or lower in five trading sessions, then compare your call with a simple rule-based opponent.</p>
                <div class="game-steps">
                    <div>
                        <div class="game-step-number">01 / STUDY</div>
                        <p class="game-step-title">Read the setup</p>
                        <p class="game-step-copy">Review about 60 sessions of price action and the indicators at the decision date.</p>
                    </div>
                    <div>
                        <div class="game-step-number">02 / PREDICT</div>
                        <p class="game-step-title">Choose a direction</p>
                        <p class="game-step-copy">Call UP or DOWN using only the information visible before the reveal.</p>
                    </div>
                    <div>
                        <div class="game-step-number">03 / REVIEW</div>
                        <p class="game-step-title">Compare the outcome</p>
                        <p class="game-step-copy">See the next five candles, your score, and the rule-based result. An unchanged close is a tie.</p>
                    </div>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        st.button("Start 10-round game", on_click=_start_game, type="primary", width="stretch")
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
    decision_date = data.index[decision_index].date()
    st.markdown(
        f"""
        <div class="game-roundbar">
            <div>
                <div class="game-round-label">Round {st.session_state.round_number:02d} / 10</div>
                <h2>{current['ticker']}</h2>
            </div>
            <div>
                <div class="game-round-detail">Decision date</div>
                <div class="game-round-value">{decision_date}</div>
            </div>
            <div>
                <div class="game-round-detail">Forecast horizon</div>
                <div class="game-round-value">5 trading sessions</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(st.session_state.round_number / 10, text=f"Round {st.session_state.round_number} of 10")
    _draw_game_chart(data, decision_index, st.session_state.prediction is not None)
    if st.session_state.prediction is not None:
        st.caption("Five-day reveal: the highlighted candles are the five sessions after your decision date.")
    _indicator_summary(decision_row)
    st.caption("EMA 20/50 show shorter- and longer-term average price trends. The chart stops at the decision date until you submit a prediction.")

    if st.session_state.prediction is None:
        st.markdown("### Make your call")
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
            "Your prediction correct": None if actual == "TIE" else player_correct,
            "Actual": actual,
            "Change": f"{change:+.2f}%",
            "Rule-based call": algorithm,
            "Algorithm correct": None if actual == "TIE" else algorithm_correct,
        }
        score_round_once(st.session_state, player_correct, result)
        if actual == "TIE":
            st.info(f"The five-day result was unchanged ({change:+.2f}%). This tie changes neither your score nor streak, and neither call is marked correct or incorrect.")
            st.write(f"Rule-Based Algorithm called **{algorithm}**. The tie is not counted as a correct or incorrect call.")
        else:
            if player_correct:
                player_result_text = "correct"
            else:
                player_result_text = "not correct"
            if algorithm_correct:
                algorithm_result_text = "correct"
            else:
                algorithm_result_text = "not correct"
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