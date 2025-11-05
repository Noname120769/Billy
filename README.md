# Billy - Discord Bot

🐾 **Billy** is a feature-rich Discord bot built with Python and discord.py, offering moderation tools, interactive games, and an economy system to enhance your Discord server experience.

## 📋 Features

### 🛡️ Moderation & Management
- **Purge** - Delete multiple messages at once
- **Kick/Ban** - Manage members with reason tracking
- **Role Assignment** - Assign or remove roles from members
- **Direct Messaging** - Send DMs to server members
- **Polls** - Create quick thumbs up/down polls

### 🎮 Games & Entertainment
- **Hangman** - Classic word-guessing game with hints
- **Word Scramble** - Unscramble words within a time limit
- **Truth or Dare** - Interactive party game with prompts
- **8-Ball** - Ask the magic 8-ball your questions
- **Coin Flip** - Flip a coin for heads or tails
- **Dice Roll** - Roll a six-sided die

### 💰 Economy System
- **Billy Bucks** - Virtual currency system
- **Slot Machine** - Gamble your billy bucks with various multipliers
- **Send Currency** - Transfer billy bucks to other members
- **Balance Tracking** - Persistent balance storage in JSON

### 🤖 Utility Commands
- **Hello** - Friendly greeting command
- **Member Welcome** - Automatic DM greetings for new members

## 🚀 Setup

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Noname120769/Billy.git
   cd Billy
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

## 📁 Project Structure

```
Billy/
├── main.py              # Main bot code with all commands
├── webserver.py         # Flask webserver for keep-alive (hosting support)
├── requirements.txt     # Python dependencies
├── currency.json        # Stores user balance data
├── words.txt           # Word list for games (3-8 letter words)
├── common_words.txt    # Common words for Hangman
├── discord.log         # Bot activity logs
└── .env                # Environment variables (create this)
```

## 🎯 Slash Commands

All commands use Discord's slash command system. Simply type `/` in any channel to see available commands.

### Moderation Commands
- `/purge [amount]` - Delete messages (requires manage_messages permission)
- `/kick [member] [reason]` - Kick a member (requires kick_members permission)
- `/ban [member] [reason]` - Ban a member (requires ban_members permission)
- `/assign [member] [role_name]` - Assign a role (requires manage_roles permission)
- `/remove [member] [role_name]` - Remove a role (requires manage_roles permission)
- `/dm [member] [message]` - Send a DM to a member
- `/poll [question]` - Create a poll

### Game Commands
- `/hangman` - Start a Hangman game
- `/guess [letter]` - Guess a letter in your Hangman game
- `/hint` - Reveal a letter in Hangman
- `/restart` - Restart your Hangman game
- `/quit` - End your Hangman game
- `/scramble` - Start a word scramble game
- `/tod` - Start Truth or Dare
- `/truth` - Get a truth prompt
- `/dare` - Get a dare prompt
- `/eightball [question]` - Ask the magic 8-ball
- `/flip` - Flip a coin
- `/roll` - Roll a die

### Economy Commands
- `/balance` - Check your billy bucks balance
- `/slots [amount]` - Spin the slot machine
- `/send [amount] [member]` - Send billy bucks to another member

### Utility Commands
- `/hello` - Get a friendly greeting

## 🎰 Slot Machine Multipliers

- 🐾🐾🐾 - 10x your bet
- 🐀🐀🐀 - 5x your bet  
- 🧶🧶🧶 - 5x your bet
- 🐟🐟🐟 - 3x your bet
- 💰💰💰 - 2x your bet

## 🔧 Configuration

### Starting Balance
New users start with **1,000 billy bucks**. You can modify this in `main.py`:
```python
currency[user_id] = 1000  # Change starting balance here
```

### Hangman Attempts
Players get **4 attempts** by default. Modify in the `/hangman` command.

### Slot Cooldown
Slots command has a **5-second cooldown** to prevent spam.

## 🌐 Hosting

The bot includes `webserver.py` for hosting on platforms like Replit, Heroku, or similar services that require a keep-alive mechanism.

### For Replit:
1. Upload all files to your Replit project
2. The webserver will automatically start on port 8080
3. Set up UptimeRobot or similar to ping your bot and keep it alive

### For VPS/Dedicated Server:
1. Follow the standard installation steps
2. Consider using a process manager like `pm2` or `systemd` for automatic restarts

## 📦 Dependencies

- `discord.py` - Discord API wrapper
- `python-dotenv` - Environment variable management  
- `discord==2.3.2` - Discord library
- `Flask==3.0.2` - Web framework for keep-alive server

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📝 License

This project is open source and available for personal and educational use.

## ⚠️ Notes

- The bot requires appropriate Discord permissions for moderation commands
- Keep your bot token secure and never share it publicly
- The currency system data is stored locally in `currency.json`
- Make sure to enable necessary intents in the Discord Developer Portal (Server Members Intent is required)

## 🐛 Troubleshooting

**Bot not responding to commands?**
- Ensure the bot has proper permissions in your server
- Check that slash commands are synced (bot logs should show sync confirmation)
- Verify your bot token is correct in the `.env` file

**Hangman/Scramble not working?**
- Ensure `words.txt` and `common_words.txt` exist and contain words
- Check that the word files are properly formatted (one word per line)

**Currency not saving?**
- Verify the bot has write permissions in its directory
- Check that `currency.json` is not corrupted

---

**Enjoy using Billy! 🐾**
