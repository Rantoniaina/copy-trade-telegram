# 🤖 copy-trade-telegram

## 📱 Telegram CLI

A command-line interface for connecting to Telegram API using your account and monitoring messages from channels.

### 🛠️ Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the root directory with your Telegram credentials:
   ```
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   TELEGRAM_PHONE=your_phone_number
   TELEGRAM_CHANNEL_TO_LISTEN=@channelname
   CONFIGURATION={"buy_conditions": ["buy", "long", "bullish"], "sell_conditions": ["sell", "short", "bearish"], "pair_mappings": [{"from_message": ["BTC", "Bitcoin"], "mapping": "BTCUSDT"}], "sl_mappings": [], "tp_mappings": [], "position_type": "once", "interval_minutes": 0, "position_sl": "no_sl", "position_tp": "no_tp"}
   ```

   You can get your API ID and hash by creating an application at https://my.telegram.org

3. If you don't set credentials in the `.env` file, you'll be prompted for them when running the command.

### 🚀 Usage

Connect to Telegram and listen to a channel:
```
python telegram_cli.py connect
```

With manual parameters:
```
python telegram_cli.py connect --api-id YOUR_API_ID --api-hash YOUR_API_HASH --phone YOUR_PHONE --channel @channelname
```

Configure trading conditions and symbol mappings:
```
python telegram_cli.py setup
```

### ✨ Features

- 🔐 Easy authentication with API ID/hash
- 📢 Monitor messages from specified Telegram channels
- 📩 Real-time display of new messages with sender information
- 🎨 Beautiful, emoji-rich console output
- 📊 Intelligent message filtering based on buy/sell conditions
- ⚡ High-performance signal processing optimized for trading
- ⏱️ Configurable position timing (once or at intervals)
- 🛑 Customizable stop loss strategies

### 🔍 Message Filtering

The application includes an optimized message filtering system that:

- Filters incoming messages based on customizable buy/sell conditions
- Only displays and processes messages containing trading signals
- Uses case-insensitive matching to ensure all relevant signals are captured
- Supports mapping of symbols from message text to trading pairs
- Provides separate mappings for trading pairs, stop loss, and take profit identifiers

### ⏱️ Position Timing

Three position triggering modes are available:

- **ONCE**: Trigger a position only once per detected signal (default)
- **EACH**: Trigger a position at regular intervals (e.g., every 5 minutes)
- **TP_LENGTH**: Create as many positions as there are take profit levels in the signal (TP1, TP2, etc.)

This allows flexible trading strategies based on signal persistence, timing requirements, or take profit levels.

### 🛑 Stop Loss Modes

Three stop loss modes are available:

- **NO_SL**: No stop loss will be set (default)
- **SIGNAL_SL**: Stop loss will be set based on information in the signal
- **USER_SL**: Stop loss will be set based on user-defined parameters

When using **USER_SL** mode, you can specify a stop loss percentage (e.g., 5%) that will be applied to all trades. This value is set during configuration or can be specified in the `CONFIGURATION` environment variable with the `stop_loss` parameter.

When using **SIGNAL_SL** mode, you can specify the position of the stop loss value in relation to the stop loss keyword:
- **BEFORE**: The stop loss value appears before the keyword (e.g., "1.2345 sl")
- **AFTER**: The stop loss value appears after the keyword (e.g., "sl 1.2345")

Example configuration with signal-based stop loss:
```
CONFIGURATION={"pair_mappings": [{"from_message": ["BTC", "Bitcoin"], "mapping": "BTCUSDT"}], "sl_mappings": [{"from_message": ["sl", "stop"], "mapping": "sl", "sl_position": "after"}], "position_type": "once", "position_sl": "signal_sl"}
```

Example configuration with user-defined stop loss:
```
CONFIGURATION={"pair_mappings": [{"from_message": ["BTC", "Bitcoin"], "mapping": "BTCUSDT"}], "sl_mappings": [{"from_message": ["stop"], "mapping": "sl", "sl_position": "before"}], "position_type": "once", "position_sl": "user_sl", "stop_loss": 5.0}
```

### 📈 Take Profit Modes

Three take profit modes are available:

- **NO_TP**: No take profit will be set (default)
- **SIGNAL_TP**: Take profit will be set based on information in the signal
- **USER_TP**: Take profit will be set based on user-defined parameters
- **ALTERNATE**: When used with position_type EACH, the system will alternate between available take profit levels for each position created

When using **USER_TP** mode, you can specify a take profit percentage (e.g., 10%) that will be applied to all trades. This value is set during configuration or can be specified in the `CONFIGURATION` environment variable with the `take_profit` parameter.

When using **SIGNAL_TP** mode, you can specify the position of the take profit value in relation to the take profit keyword:
- **BEFORE**: The take profit value appears before the keyword (e.g., "1.2345 tp")
- **AFTER**: The take profit value appears after the keyword (e.g., "tp 1.2345")

Example configuration with signal-based take profit:
```
CONFIGURATION={"pair_mappings": [{"from_message": ["BTC", "Bitcoin"], "mapping": "BTCUSDT"}], "tp_mappings": [{"from_message": ["tp", "target"], "mapping": "tp", "tp_position": "after"}], "position_type": "once", "position_tp": "signal_tp"}
```

Example configuration with both signal-based stop loss and take profit:
```
CONFIGURATION={"pair_mappings": [{"from_message": ["BTC", "Bitcoin"], "mapping": "BTCUSDT"}], "sl_mappings": [{"from_message": ["sl", "stop"], "mapping": "sl", "sl_position": "after"}], "tp_mappings": [{"from_message": ["tp", "target"], "mapping": "tp", "tp_position": "after"}], "position_type": "once", "position_sl": "signal_sl", "position_tp": "signal_tp"}
```

Example configuration with multiple take profit levels:
```
CONFIGURATION={"pair_mappings": [{"from_message": ["BTC", "Bitcoin"], "mapping": "BTCUSDT"}], "sl_mappings": [{"from_message": ["sl"], "mapping": "sl", "sl_position": "after"}], "tp_mappings": [{"from_message": ["tp"], "mapping": "tp", "tp_position": "after"}], "position_type": "tp_length", "position_sl": "signal_sl", "position_tp": "signal_tp"}
```

Example configuration with alternating take profit levels for recurring positions:
```
CONFIGURATION={"pair_mappings": [{"from_message": ["BTC", "Bitcoin"], "mapping": "BTCUSDT"}], "sl_mappings": [{"from_message": ["sl"], "mapping": "sl", "sl_position": "after"}], "tp_mappings": [{"from_message": ["tp"], "mapping": "tp", "tp_position": "after"}], "position_type": "each", "interval_minutes": 30, "position_sl": "signal_sl", "position_tp": "alternate"}
```

These options provide flexibility in both risk management and profit-taking strategies.

### ⚡ Performance Optimizations

For high-frequency trading environments, the application includes several performance enhancements:

- Pre-computation of conditions during initialization
- Efficient set-based lookups for signal detection
- Single-pass filtering algorithms to minimize processing time
- Early termination when matches are found to reduce CPU usage
- Optimized string operations for minimal latency
- Smart data structures to maximize throughput of messages

### 💻 Technology Stack

- **Python**: Core programming language
- **Telethon**: Telegram client library for Python
- **Click**: Command-line interface creation kit
- **python-dotenv**: Environment variable management
- **asyncio**: Asynchronous I/O, event loop, and coroutines
