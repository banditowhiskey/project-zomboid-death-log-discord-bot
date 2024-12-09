import os
import asyncio
import random
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
    data["timestamp"] = log_entry.split("Timestamp:")[1].split("\n")[0].strip()
    data["death_cause"] = log_entry.split("Death Cause:")[1].split("\n")[0].strip()
    data["steam_name"] = log_entry.split("Steam Name:")[1].split("\n")[0].strip()
    data["position"] = log_entry.split("Position:")[1].split("\n")[0].strip()
    data["traits"] = log_entry.split("Traits:")[1].split("\n")[0].strip()
    data["skills"] = log_entry.split("Skills:")[1].split("\n")[0].strip()
    data["inventory"] = log_entry.split("Inventory:")[1].split("\n")[0].strip()
    data["zombie_kills"] = log_entry.split("Zombie Kills:")[1].split("\n")[0].strip()
    data["time_survived"] = log_entry.split("Survived Time:")[1].split("\n")[0].strip()

    #format skills into a bullet list and make a newline at the beginning after the { and before the }
    data["skills"] = data["skills"].replace("{", "{\n").replace(",", "\n").replace("}", "\n}")

    return data

# Add an array of funny lines to say when someone dies
funny_lines = [
    "They're dead, Jim.",
    "Looks like they won't be coming back from that one.",
    "F to pay respects.",
    "Survival is overrated anyway.",
    "Another one bites the dust."
    "They were too beautiful for this world.",
    "Goodniught sweet prince.",
    "They did not go gentle into that good night.",
    "They are now one with the zombies.",
    "They have left the building.",
    "Looks like they weren’t built different.",
    "Skill Issue.",
    "They fought bravely... kinda.",
    "R.I.P. buddy, you will be… forgotten soon.",
    "A zombie's favorite snack.",
    "Oops. Better luck next time.",
    "Remember, death is just a respawn point. Oh wait…",
    "L in chat.",
    "Their watch has ended.",
    "Game over, man! Game over!",
]

# Get random funny line
def get_funny_line():
    return random.choice(funny_lines)

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
                log_entry = line + "".join([file.readline() for _ in range(15)])  # Read full log block
                data = parse_log_entry(log_entry)

                # Send message to primary channel
                primary_channel = bot.get_channel(PRIMARY_CHANNEL_ID)
                if primary_channel:
                    details = (
                        f"**{data['steam_name']}** was killed by {data['death_cause']}\n"
                        f"> They survived for {data['time_survived']} and killed {data['zombie_kills']} zombies. \n > {get_funny_line()}"
                    )
                    await primary_channel.send(details)

                # Send detailed message to secondary channel
                secondary_channel = bot.get_channel(SECONDARY_CHANNEL_ID)
                if secondary_channel:
                    details = (
                        f"**Steam Name:** {data['steam_name']}\n"
                        f"**Time of Death:** {data['timestamp']}\n"
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
