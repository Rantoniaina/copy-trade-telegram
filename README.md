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

### 🔍 Message Filtering

The application includes an optimized message filtering system that:

- Filters incoming messages based on customizable buy/sell conditions
- Only displays and processes messages containing trading signals
- Uses case-insensitive matching to ensure all relevant signals are captured
- Supports mapping of symbols from message text to trading pairs

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
