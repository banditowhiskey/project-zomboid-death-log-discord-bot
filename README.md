
# Project Zomboid Discord Bot

  

This bot monitors a log file from a Project Zomboid server and posts relevant information to two Discord channels. The bot is designed to notify about player deaths, with one channel receiving the death cause and another receiving detailed player information.

  

---

  

## Features

- Posts the cause of death to a primary Discord channel.

- Posts detailed player information (Steam name, position, traits, skills, inventory) to a secondary Discord channel.

- Continuously monitors the server's log file for new entries.

  

---

  

## Requirements

- Python 3.8+

-  `discord.py` library

-  `python-dotenv` library

  

---

  

## Installation

  

1.  **Clone the Repository**:
```bash
git clone https://github.com/banditowhiskey/project-zomboid-death-log-discord-bot.git
cd project-zomboid-discord-bot
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set Up Environment Variables**:
The bot requires the following environment variables:
- `DISCORD_BOT_TOKEN`: Your bot's token from the Discord Developer Portal.
- `PRIMARY_CHANNEL_ID`: The ID of the channel for posting death causes.
- `SECONDARY_CHANNEL_ID`: The ID of the channel for posting detailed player information.

Create a `.env` file in the project directory:
``nano .env``

Add the following content (replace the placeholders with your values):
```bash
DISCORD_BOT_TOKEN=your_discord_bot_token
PRIMARY_CHANNEL_ID=your_primary_channel_id
SECONDARY_CHANNEL_ID=your_secondary_channel_id
```
Alternatively, export the variables to your Linux environment:
```bash
export DISCORD_BOT_TOKEN="your_discord_bot_token"
export PRIMARY_CHANNEL_ID="your_primary_channel_id"
export SECONDARY_CHANNEL_ID="your_secondary_channel_id"
```

To make these exports persistent across reboots, add them to your shell configuration file (e.g., `~/.bashrc` or `~/.zshrc`):
```bash
echo 'export DISCORD_BOT_TOKEN="your_discord_bot_token"' >> ~/.bashrc
echo 'export PRIMARY_CHANNEL_ID="your_primary_channel_id"' >> ~/.bashrc
echo 'export SECONDARY_CHANNEL_ID="your_secondary_channel_id"' >> ~/.bashrc
source ~/.bashrc
```

4. **Run the Bot:**
``python bot.py``


---

  

## Running the Bot as a Service
To ensure the bot runs continuously in the background, you can set it up as a `systemd` service.
1. **Create a Service File:**
```bash
sudo nano /etc/systemd/system/project-zomboid-bot.service
```
Add the following content:
```ini
[Unit]
Description=Project Zomboid Discord Bot
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/your/project-zomboid-discord-bot/bot.py
WorkingDirectory=/path/to/your/project-zomboid-discord-bot
Environment="DISCORD_BOT_TOKEN=your_discord_bot_token"
Environment="PRIMARY_CHANNEL_ID=your_primary_channel_id"
Environment="SECONDARY_CHANNEL_ID=your_secondary_channel_id"
Restart=always

[Install]
WantedBy=multi-user.target
```
2. **Start and Enable the Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl start project-zomboid-bot
sudo systemctl enable project-zomboid-bot
```
3. **Check the Service Status**
```bash
sudo systemctl status project-zomboid-bot
```


---

  

## Contributing

Feel free to submit issues or pull requests for enhancements and bug fixes.



---

## License

This project is licensed under the MIT License.
```javascript
Copy and paste this into your `README.md` file, and update the placeholders (e.g., `your-username`, `your_discord_bot_token`) with your actual values.
```