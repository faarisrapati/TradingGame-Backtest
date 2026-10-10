"""Simple, chronological backtesting calculations."""

import math

import pandas as pd


def evaluate_direction(start_close: float, future_close: float) -> str:
    """Compare two closes and keep unchanged prices as a tie."""
    if future_close > start_close:
        return "UP"
    if future_close < start_close:
        return "DOWN"
    return "TIE"


def generate_ema_crossover_signals(data: pd.DataFrame) -> pd.Series:
    """Create close-of-day entry (1) and exit (-1) signals."""
    signals = pd.Series(0, index=data.index, dtype=int, name="Signal")
    holding_target = False

    for row_number in range(1, len(data)):
        previous_fast = data["EMA_20"].iloc[row_number - 1]
        previous_slow = data["EMA_50"].iloc[row_number - 1]
        current_fast = data["EMA_20"].iloc[row_number]
        current_slow = data["EMA_50"].iloc[row_number]
        if pd.isna(previous_fast):
            continue
        if pd.isna(previous_slow):
            continue
        if pd.isna(current_fast):
            continue
        if pd.isna(current_slow):
            continue

        crossed_up = previous_fast <= previous_slow and current_fast > current_slow
        crossed_down = previous_fast >= previous_slow and current_fast < current_slow
        if crossed_up and not holding_target:
            signals.iloc[row_number] = 1
            holding_target = True
        elif crossed_down and holding_target:
            signals.iloc[row_number] = -1
            holding_target = False

    return signals


def calculate_max_drawdown(values: pd.Series) -> float:
    """Return the largest peak-to-trough decline as a negative fraction."""
    if values.empty:
        return 0.0

    highest_value = float(values.iloc[0])
    largest_drawdown = 0.0

    for value in values:
        current_value = float(value)
        if current_value > highest_value:
            highest_value = current_value

        if highest_value != 0:
            drawdown = current_value / highest_value - 1
            if drawdown < largest_drawdown:
                largest_drawdown = drawdown

    return largest_drawdown


def run_backtest(
    data: pd.DataFrame,
    initial_capital: float = 10_000.0,
) -> dict:
    """Backtest EMA crossovers with free orders at the next day's open."""
    if data.empty:
        raise ValueError("There is not enough historical data to run this backtest.")
    if initial_capital <= 0:
        raise ValueError("Starting capital must be positive.")

    signals = generate_ema_crossover_signals(data)
    cash = float(initial_capital)
    shares = 0
    entry_date = None
    entry_price = 0.0
    entry_value = 0.0
    completed_trades = []
    equity_rows = []

    for row_number in range(len(data)):
        date = data.index[row_number]
        open_price = float(data["Open"].iloc[row_number])

        # A signal from the previous completed candle is filled at this day's open.
        if row_number > 0:
            order_signal = int(signals.iloc[row_number - 1])
            if order_signal == 1 and shares == 0:
                shares_to_buy = math.floor(cash / open_price)
                if shares_to_buy > 0:
                    entry_price = open_price
                    entry_date = date
                    entry_value = shares_to_buy * open_price
                    cash -= entry_value
                    shares = shares_to_buy
            elif order_signal == -1 and shares > 0:
                proceeds = shares * open_price
                completed_trades.append(
                    {
                        "Entry date": entry_date,
                        "Exit date": date,
                        "Shares": shares,
                        "Entry price": entry_price,
                        "Exit price": open_price,
                        "Net profit": proceeds - entry_value,
                    }
                )
                cash += proceeds
                shares = 0
                entry_date = None
                entry_price = 0.0
                entry_value = 0.0

        close_price = float(data["Close"].iloc[row_number])
        equity_rows.append(
            {"Date": date, "Strategy": cash + shares * close_price, "Cash": cash, "Shares": shares}
        )

    first_open = float(data["Open"].iloc[0])
    buy_hold_shares = math.floor(initial_capital / first_open)
    buy_hold_cash = initial_capital - buy_hold_shares * first_open
    equity = pd.DataFrame(equity_rows).set_index("Date")
    equity["Buy and hold"] = buy_hold_cash + buy_hold_shares * data["Close"].astype(float)

    final_value = float(equity["Strategy"].iloc[-1])
    buy_hold_final = float(equity["Buy and hold"].iloc[-1])
    total_return = final_value / initial_capital - 1
    buy_hold_return = buy_hold_final / initial_capital - 1

    completed_trade_count = len(completed_trades)
    winning_trade_count = 0
    total_trade_profit = 0.0
    for trade in completed_trades:
        trade_profit = float(trade["Net profit"])
        total_trade_profit += trade_profit
        if trade_profit > 0:
            winning_trade_count += 1

    if completed_trade_count > 0:
        win_rate = winning_trade_count / completed_trade_count
        average_trade_profit = total_trade_profit / completed_trade_count
    else:
        win_rate = None
        average_trade_profit = None

    return {
        "equity": equity,
        "signals": signals,
        "trades": completed_trades,
        "initial_capital": float(initial_capital),
        "final_value": final_value,
        "total_return": total_return,
        "buy_hold_final": buy_hold_final,
        "buy_hold_return": buy_hold_return,
        "excess_return": total_return - buy_hold_return,
        "completed_trade_count": completed_trade_count,
        "win_rate": win_rate,
        "average_trade_profit": average_trade_profit,
        "max_drawdown": calculate_max_drawdown(equity["Strategy"]),
        "open_position": shares > 0,
    }