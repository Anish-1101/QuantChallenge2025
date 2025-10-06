/*
* Quant Challenge 2025
*
* Algorithmic strategy template
*/

#include <cstdint>
#include <optional>
#include <string>

enum class Side { buy = 0, sell = 1 };
enum class Ticker : std::uint8_t { TEAM_A = 0 }; // NOLINT

/**
 * Place a market order
 *
 * @param side Side of the order to place ("BUY" or Side::sell)
 * @param ticker Ticker of the order to place ("TEAM_A")
 * @param quantity Volume of the order to place
 *
 * @return (ignore return value)
 */
bool place_market_order(Side side, Ticker ticker, float quantity);

/**
 * Place a limit order
 *
 * @param side Side of the order to place ("BUY" or Side::sell)
 * @param ticker Ticker of the order to place (Ticker::TEAM_A)
 * @param quantity Volume of the order to place
 * @param price Price of the order to place - MUST be between 0.0 and 100.0 (percentage)
 * @param ioc Immediate or cancel
 *
 * @return order_id
 */
std::int64_t place_limit_order(Side side, Ticker ticker, float quantity,
                               float price, bool ioc = false);

/**
 * Cancel an order
 *
 * @param ticker Ticker the original order was placed on
 * @param order_id Order_id returned by place_limit_order
 *
 * @return (ignore return value)
 */

bool cancel_order(Ticker ticker, std::int64_t order_id);

// Prints log, viewable in the sandbox after 5mins. Might help for debugging
// DO NOT USE std::cout. Your code will not work
void println(const std::string &text);

class Strategy {
public:
  /**
   * Reset the state of the strategy to the start of game position.
   * 
   * Since the sandbox execution can start mid-game, we recommend creating a
   * function which can be called from constructor and on_game_event_update (END_GAME).
   *
   * Note: In production execution, the game will start from the beginning
   * and will not be replayed.
   */
  void reset_state() {
    // Add any state reset logic here
  }

  Strategy() {
    // Your initialization code goes here
    reset_state();
  }

  /**
   * Called whenever two orders match. Could be one of your orders, or two other
   * people's orders.
   *
   * @param ticker Ticker of the orders that were matched
   * @param side Side of the orders that were matched
   * @param quantity Volume traded
   * @param price Price that trade was executed at
   */
  void on_trade_update(Ticker ticker, Side side, float quantity, float price) {
    println("Python Trade update: " + std::to_string(static_cast<int>(ticker)) + " " + std::to_string(static_cast<int>(side)) + " " + std::to_string(quantity) + " shares @ " + std::to_string(price));
  }

  /**
   * Called whenever the orderbook changes. This could be because of a trade, or
   * because of a new order, or both.
   *
   * @param ticker Ticker that has an orderbook update
   * @param side Which orderbook was updated
   * @param quantity Volume placed into orderbook
   * @param price Price of orderbook that has an update
   */
  void on_orderbook_update(Ticker ticker, Side side, float quantity,
                           float price) {}

  /**
   * Called whenever one of your orders is filled.
   *
   * @param ticker Ticker of order that was fulfilled
   * @param side Side of order that was fulfilled
   * @param price Price that order was fulfilled at
   * @param quantity Volume of order that was fulfilled
   * @param capital_remaining Amount of capital after fulfilling order
   */
  void on_account_update(Ticker ticker, Side side, float price, float quantity,
                         float capital_remaining) {}

  /**
   * Called whenever a basketball game event occurs.
   *
   * @param event_type Type of event that occurred
   * @param home_away Team indicator ("home", "away", or "unknown")
   * @param home_score Home team score after event
   * @param away_score Away team score after event
   * @param player_name Player involved in event (optional)
   * @param substituted_player_name Player being substituted out (optional)
   * @param shot_type Type of shot (optional)
   * @param assist_player Player who made the assist (optional)
   * @param rebound_type Type of rebound (optional)
   * @param coordinate_x X coordinate of shot location in feet (optional)
   * @param coordinate_y Y coordinate of shot location in feet (optional)
   * @param time_seconds Game time remaining in seconds (optional)
   */
  virtual void on_game_event_update(
      const std::string& event_type,
      const std::string& home_away,
      int home_score,
      int away_score,
      const std::optional<std::string>& player_name,
      const std::optional<std::string>& substituted_player_name,
      const std::optional<std::string>& shot_type,
      const std::optional<std::string>& assist_player,
      const std::optional<std::string>& rebound_type,
      const std::optional<double>& coordinate_x,
      const std::optional<double>& coordinate_y,
      const std::optional<double>& time_seconds
  ) {
    println(event_type + " " + std::to_string(home_score) + " - " + std::to_string(away_score));

    if (event_type == "END_GAME") {
      // IMPORTANT: Highly recommended to call reset_state() when the
      // game ends. See reset_state() for more details.
      reset_state();
      return;
    }
  }
};
