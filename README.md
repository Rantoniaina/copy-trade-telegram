# 🤖 copy-trade-telegram

## 📱 Telegram CLI

A command-line interface for connecting to Telegram API using your account.

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
   ```

   You can get your API ID and hash by creating an application at https://my.telegram.org

3. If you don't set credentials in the `.env` file, you'll be prompted for them when running the command.

### 🚀 Usage

Connect to Telegram:
```
python telegram_cli.py connect
```

With manual parameters:
```
python telegram_cli.py connect --api-id YOUR_API_ID --api-hash YOUR_API_HASH --phone YOUR_PHONE
```

### 💻 Technology Stack

- **Python**: Core programming language
- **Telethon**: Telegram client library for Python
- **Click**: Command-line interface creation kit
- **python-dotenv**: Environment variable management
- **asyncio**: Asynchronous I/O, event loop, and coroutines
