"""
Quant Challenge 2025

Algorithmic strategy template
"""

from enum import Enum
from typing import Optional
from math import exp

class Side(Enum):
    BUY = 0
    SELL = 1

class Ticker(Enum):
    # TEAM_A (home team)
    TEAM_A = 0

def place_market_order(side: Side, ticker: Ticker, quantity: float) -> None:
    """Place a market order.
    
    Parameters
    ----------
    side
        Side of order to place
    ticker
        Ticker of order to place
    quantity
        Quantity of order to place
    """
    return

def place_limit_order(side: Side, ticker: Ticker, quantity: float, price: float, ioc: bool = False) -> int:
    """Place a limit order.
    
    Parameters
    ----------
    side
        Side of order to place
    ticker
        Ticker of order to place
    quantity
        Quantity of order to place
    price
        Price of order to place
    ioc
        Immediate or cancel flag (FOK)

    Returns
    -------
    order_id
        Order ID of order placed
    """
    return 0

def cancel_order(ticker: Ticker, order_id: int) -> bool:
    """Cancel an order.
    
    Parameters
    ----------
    ticker
        Ticker of order to cancel
    order_id
        Order ID of order to cancel

    Returns
    -------
    success
        True if order was cancelled, False otherwise
    """
    return 0

class Strategy:
    """Template for a strategy."""

    def reset_state(self) -> None:
        self.home_score = 0
        self.away_score = 0
        self.time_seconds = 2400.0
        self.format_total = 2400.0
        self.possession = None

        self.best_bid = None
        self.best_ask = None

        self.equity = 100000.0
        self.position_qty = 0.0
        self.position_avg = 0.0
        self.max_notional = 0.20

        #Params
        self.edge_cushion = 0.1
        self.post_inside = 0.5
        self.flat_time = 0.0
        self.kelly_frac = 0.125
        self.size_floor = 50
        self.size_ceiling = 5000
        self.oreb_bonus = 0.5
        self.steal_to_bonus = 1.0
        self.clutch_time = 120.0

        self.event_weights = {
            ("REBOUND", "OFFENSIVE"):  self.oreb_bonus,
            ("REBOUND", "DEFENSIVE"):  0.25,
            ("STEAL",   None):         self.steal_to_bonus,
            ("TURNOVER", None):        self.steal_to_bonus * 0.8,
            ("SCORE",   "TWO_POINT"):  0.35,
            ("SCORE",   "THREE_POINT"):0.60,
            ("FOUL",    "SHOOTING"):   0.35,
            ("BLOCK",   None):         0.20,
        }

        self.phase_cfg = {
            "early": {"r_min": 2/3, "w":1.00},
            "mid": {"r_min": 1/3, "w":1.25},
            "late": {"r_min": 0.00, "w":1.60},
            "clutch_boost": 2.00,
        }

        self.event_half_life: float = 90.0
        self.event_impact: float = 0.0
        self._last_impact_time: float = self.time_seconds

        self.point_diff: int = 0
        self.point_diff_hist: list[tuple[float, int]] = []

    def __init__(self) -> None:
        """Your initialization code goes here."""
        self.reset_state()

    def on_trade_update(
        self, ticker: Ticker, side: Side, quantity: float, price: float
    ) -> None:
        print(f"Python Trade update: {ticker} {side} {quantity} shares @ {price}")

    def on_orderbook_update(
        self, ticker: Ticker, side: Side, quantity: float, price: float
    ) -> None:
        if ticker != Ticker.TEAM_A:
            return
        if side == Side.BUY:
            if price is not None:
                self.best_bid = max(self.best_bid, price) if self.best_bid is not None else price
        elif side == Side.SELL:
            if price is not None:
                self.best_ask = min(self.best_ask, price) if self.best_ask is not None else price

    def on_account_update(
        self,
        ticker: Ticker,
        side: Side,
        price: float,
        quantity: float,
        capital_remaining: float,
    ) -> None:
        if ticker != Ticker.TEAM_A:
            return
        
        self.equity = float(capital_remaining)

        q = float(quantity)
        p = float(price)
        if side == Side.BUY:
            new_q = self.position_qty + q
            if new_q != 0:
                self.position_avg = (self.position_avg * self.position_qty + p * q) / new_q
            else:
                self.position_avg = 0.0
            self.position_qty = new_q
        elif side == Side.SELL:
            new_q = self.position_qty - q
            if new_q == 0:
                self.position_avg = 0.0
            self.position_qty = new_q

    def on_game_event_update(self,
                           event_type: str,
                           home_away: str,
                           home_score: int,
                           away_score: int,
                           player_name: Optional[str],
                           substituted_player_name: Optional[str],
                           shot_type: Optional[str],
                           assist_player: Optional[str],
                           rebound_type: Optional[str],
                           coordinate_x: Optional[float],
                           coordinate_y: Optional[float],
                           time_seconds: Optional[float]
        ) -> None:
        """Called whenever a basketball game event occurs.
        Parameters
        ----------
        event_type
            Type of event that occurred
        home_score
            Home team score after event
        away_score
            Away team score after event
        player_name (Optional)
            Player involved in event
        substituted_player_name (Optional)
            Player being substituted out
        shot_type (Optional)
            Type of shot
        assist_player (Optional)
            Player who made the assist
        rebound_type (Optional)
            Type of rebound
        coordinate_x (Optional)
            X coordinate of shot location in feet
        coordinate_y (Optional)
            Y coordinate of shot location in feet
        time_seconds (Optional)
            Game time remaining in seconds
        """

        if event_type == "END_GAME":
            self._flatten_and_reset()
            return
        
        self._ingest_event(
            event_type = event_type,
            home_away = home_away,
            home_score = home_score,
            away_score = away_score,
            shot_type = shot_type,
            rebound_type = rebound_type,
            time_seconds = time_seconds,
        )

        if self.best_bid is None or self.best_ask is None:
            return
        
        if self.time_seconds <= self.flat_time:
            self._try_exit_late()
            return
        
        fair = self._fair_value_price()
        if self.best_bid is not None and self.best_ask is not None and self.best_bid > self.best_ask:
            m = 0.5 * (self.best_bid + self.best_ask)
            self.best_bid = min(self.best_bid, m)
            self.best_ask = max(self.best_ask, m)

        mid = 0.5 * (self.best_bid + self.best_ask)
        spread = max(0.0, self.best_ask - self.best_bid)
        half_spread = 0.5 * spread
        edge = fair - mid
        
        est_px = max(mid, 1e-6)
        exposure_dollars = abs(self.position_qty) * est_px
        cap_dollars = self.max_notional * self.equity
        remaining_cap_units = max(0.0, (cap_dollars - exposure_dollars) / est_px)
        if remaining_cap_units < self.size_floor:
            return
        
        prob_edge = edge / 100.0
        base_size = self.kelly_frac * 2.0 * abs(prob_edge) * self.equity
        size_units = base_size / est_px
        size = min(
            max(size_units, self.size_floor), 
            min(self.size_ceiling, remaining_cap_units)
        )

        if edge > (half_spread + self.edge_cushion):
            qty = size
            place_market_order(Side.BUY, Ticker.TEAM_A, qty)
        elif edge < -(half_spread + self.edge_cushion):
            qty = size
            place_market_order(Side.SELL, Ticker.TEAM_A, qty)
        else:
            skew = -0.50 if self.position_qty > 0 else 0.50 if self.position_qty < 0 else 0.0
            buy_price = min(fair - 0.25 + skew, self.best_ask + self.post_inside)
            sell_price = max(fair + 0.25 + skew, self.best_bid + self.post_inside)

            if self.best_bid < buy_price < self.best_ask:
                qty = 0.5 * size
                place_limit_order(Side.BUY, Ticker.TEAM_A, qty, round(buy_price, 2), ioc = False)
            
            if self.best_bid < sell_price < self.best_ask:
                qty = 0.5 * size
                place_limit_order(Side.SELL, Ticker.TEAM_A, qty, round(sell_price, 2), ioc = False)
        print(f"{event_type} {home_score} - {away_score}")

    def _flatten_and_reset(self) -> None:
        if self.position_qty != 0:
            side = Side.SELL if self.position_qty > 0 else Side.BUY
            place_market_order(side, Ticker.TEAM_A, abs(self.position_qty))
        self.reset_state()

    def _phase_weight(self, t_rem: float) -> float:
        T = max(self.format_total, 1.0)
        r = max(0.0, min(1.0, t_rem / T))
        if r >= self.phase_cfg["early"]["r_min"]:
            w = self.phase_cfg["early"]["w"]
        elif r >= self.phase_cfg["mid"]["r_min"]:
            w = self.phase_cfg["mid"]["w"]
        else:
            w = self.phase_cfg["late"]["w"]
        if t_rem <= self.clutch_time:
            w *= self.phase_cfg["clutch_boost"]
        return w

    def _decay_event_impact(self, new_time: float) -> None:
        dt = abs(self._last_impact_time - new_time)
        if dt > 0:
            hl = max(1e-6, self.event_half_life)
            gamma = 0.5 ** (dt / hl)
            self.event_impact *= gamma
            self._last_impact_time = new_time

    def _ingest_event(
        self,
        event_type: str,
        home_away: Optional[str],
        home_score: Optional[int],
        away_score: Optional[int],
        shot_type: Optional[str],
        rebound_type: Optional[str],
        time_seconds: Optional[float],
    ) -> None:
        if time_seconds is not None:
            new_time = float(time_seconds)
            self._decay_event_impact(new_time)
            self.time_seconds = new_time
            if self.time_seconds > self.format_total:
                self.format_total = self.time_seconds
        if home_score is not None:
            self.home_score = int(home_score)
        if away_score is not None:
            self.away_score = int(away_score)
        self.point_diff = self.home_score - self.away_score
        if not self.point_diff_hist or self.point_diff_hist[-1][1] != self.point_diff:
            self.point_diff_hist.append((self.time_seconds, self.point_diff))
            if len(self.point_diff_hist) > 100:
                self.point_diff_hist.pop(0)
        et = event_type
        team = home_away
        if et == "SCORE":
            if team == "home":
                self.possession = "away"
            elif team == "away":
                self.possession = "home"
        elif et == "REBOUND":
            if rebound_type in ("DEFENSIVE", "OFFENSIVE"):
                self.possession = team
        elif et in ("STEAL", "TURNOVER"):
            if team in ("home", "away"):
                self.possession = team
            else:
                self.possession = (
                    "away" if self.possession == "home"
                    else "home" if self.possession == "away"
                    else None
                )
        t_rem = max(self.time_seconds, 1.0)
        phase_w = self._phase_weight(t_rem)
        if et == "REBOUND":
            key = (et, rebound_type)
        elif et == "SCORE":
            key = (et, shot_type)
        else:
            key = (et, None)
        base = self.event_weights.get(key, 0.0)
        signed = base if team == "home" else -base if team == "away" else 0.0
        self.event_impact += signed * phase_w

    def _fair_value_price(self) -> float:
        sd = self.home_score - self.away_score
        t_rem = max(self.time_seconds, 1.0)
        T = max(self.format_total, 1.0)
        phase = 1.5 * (1.0 - (t_rem / T))
        k = 0.12 + 0.30 * phase
        x = k * sd
        poss_pts = (0.35 + 0.65 * phase)
        if self.possession == "home":
            x += k * poss_pts
        elif self.possession == "away":
            x -= k * poss_pts
        p = 1.0 / (1.0 + exp(-x))
        fair = 100.0 * p
        impact_scale = 1.5
        fair += max(-3.0, min(3.0, impact_scale * self.event_impact))
        return max(0.5, min(99.5, fair))

    def _try_exit_late(self) -> None:
        if self.position_qty == 0 or self.best_bid is None or self.best_ask is None:
            return
        fair = self._fair_value_price()
        side = Side.SELL if self.position_qty > 0 else Side.BUY
        price = self.best_bid if side == Side.SELL else self.best_ask
        if (self.position_qty > 0 and price >= self.position_avg) or \
        (self.position_qty < 0 and price <= self.position_avg) or \
        abs(fair - price) < 0.8:
            qty = abs(self.position_qty)
            if qty > 0:
                place_market_order(side, Ticker.TEAM_A, qty)

