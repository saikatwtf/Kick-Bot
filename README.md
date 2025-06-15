# Kick-Bot

A Telegram bot that automatically removes inactive users from groups based on their last message activity.

## Features

- Automatically remove inactive users from a Telegram group
- Track user activity based on messages
- Configurable time periods (seconds, minutes, hours, days)
- Admin-only commands with permission checks
- Confirmation before kicking users
- Ignores admins and other bots

## Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help information and available commands
- `/kickinactive [time]` - Remove inactive users based on specified time period
  - Examples: `/kickinactive 7d`, `/kickinactive 24h`, `/kickinactive 30m`

## Requirements

- Python 3.7+
- Pyrogram
- MongoDB (optional, can be configured to use SQLite)

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on `.env.example` with your credentials:
   ```
   API_ID=your_api_id
   API_HASH=your_api_hash
   BOT_TOKEN=your_bot_token
   MONGO_URI=mongodb://localhost:27017/
   DB_NAME=kickbot
   ```
4. Run the bot:
   ```
   python main.py
   ```

## Permissions

The bot requires the following permissions in Telegram groups:
- Ban Users (to remove inactive members)

## License

See the [LICENSE](LICENSE) file for details.