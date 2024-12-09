import os
from discord.ext import commands
from discord import Intents

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Bot token and channel IDs
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PRIMARY_CHANNEL_ID = int(os.getenv("PRIMARY_CHANNEL_ID"))  # For the death cause
SECONDARY_CHANNEL_ID = int(os.getenv("SECONDARY_CHANNEL_ID"))  # For detailed info

if not DISCORD_TOKEN or not PRIMARY_CHANNEL_ID or not SECONDARY_CHANNEL_ID:
    raise RuntimeError("Missing bot token or channel IDs in environment variables")

# Initialize the bot
intents = Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Function to parse and format the log entry
def parse_log_entry(log_entry):
    # Extract desired fields from the log entry
    data = {}
    data["death_cause"] = log_entry.split("Death Cause:")[1].split("\n")[0].strip()
    data["steam_name"] = log_entry.split("Steam Name:")[1].split("\n")[0].strip()
    data["position"] = log_entry.split("Position:")[1].split("\n")[0].strip()
    data["traits"] = log_entry.split("Traits:")[1].split("\n")[0].strip()
    data["skills"] = log_entry.split("Skills:")[1].split("\n")[0].strip()
    data["inventory"] = log_entry.split("Inventory:")[1].split("\n")[0].strip()
    return data

# Monitor the file and send messages
async def monitor_log_file(file_path):
    with open(file_path, "r") as file:
        # Seek to the end of the file initially
        file.seek(0, 2)
        while True:
            line = file.readline()
            if not line:
                await asyncio.sleep(1)  # Wait for new log entries
                continue

            # When a new entry is added, parse it and send messages
            if "Death," in line:
                log_entry = line + "".join([file.readline() for _ in range(20)])  # Read full log block
                data = parse_log_entry(log_entry)

                # Send message to primary channel
                primary_channel = bot.get_channel(PRIMARY_CHANNEL_ID)
                if primary_channel:
                    await primary_channel.send(f"Player Death: {data['death_cause']}")

                # Send detailed message to secondary channel
                secondary_channel = bot.get_channel(SECONDARY_CHANNEL_ID)
                if secondary_channel:
                    details = (
                        f"**Steam Name:** {data['steam_name']}\n"
                        f"**Position:** {data['position']}\n"
                        f"**Traits:** {data['traits']}\n"
                        f"**Skills:** {data['skills']}\n"
                        f"**Inventory:** {data['inventory']}"
                    )
                    await secondary_channel.send(details)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    # Start monitoring the log file
    log_file_path = "../Lua/AdvancedDeathLog/Most-Recent-Deaths.txt"  # Replace with your actual file path
    bot.loop.create_task(monitor_log_file(log_file_path))

# Run the bot
bot.run(DISCORD_TOKEN)
