import os
import re
import asyncio
import random
from discord.ext import commands
from discord import Intents

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Bot token and channel IDs
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PRIMARY_CHANNEL_ID = int(os.getenv("PRIMARY_CHANNEL_ID"))    # Main death/kill announcements
SECONDARY_CHANNEL_ID = int(os.getenv("SECONDARY_CHANNEL_ID"))  # Positional details

# Directory where Build 42 writes its logs
LOG_DIR = os.getenv("LOG_DIR", "/home/pzuser/Zomboid/Logs")

if not DISCORD_TOKEN or not PRIMARY_CHANNEL_ID or not SECONDARY_CHANNEL_ID:
    raise RuntimeError("Missing bot token or channel IDs in environment variables")

# Initialize the bot
intents = Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Build 42 log patterns
# pvp file:  [01-03-26 18:15:24.389][IMPORTANT] Kill: "RyderZ" (8110,11522,0) killed "Rod" (8110,11523,0).
PVP_KILL_PATTERN = re.compile(
    r'\[.*?\]\[IMPORTANT\] Kill: "(.+?)" \((\d+,\d+,\d+)\) killed "(.+?)" \((\d+,\d+,\d+)\)'
)
# user file: [01-03-26 18:44:27.041] user Neil Fallon died at (1878,6469,0) (non pvp).
USER_DEATH_PATTERN = re.compile(
    r'\[.*?\] user (.+?) died at \((\d+,\d+,\d+)\) \(non pvp\)'
)

# Funny lines for death/kill announcements
funny_lines = [
    "They're dead, Jim.",
    "Looks like they won't be coming back from that one.",
    "F to pay respects.",
    "Survival is overrated anyway.",
    "Another one bites the dust.",
    "They were too beautiful for this world.",
    "Goodnight, sweet prince.",
    "They did not go gentle into that good night.",
    "They are now one with the zombies.",
    "They have left the building.",
    "Looks like they weren't built different.",
    "Skill Issue.",
    "They fought bravely...kinda.",
    "R.I.P. buddy, you will be… forgotten soon.",
    "A zombie's favorite snack.",
    "Oops. Better luck next time.",
    "Remember, death is just a respawn point. Oh wait…",
    "L in chat.",
    "Their watch has ended.",
    "Game over, man! Game over!",
    "You were meant to be the chosen one!",
    "Should've zigged when you zagged.",
    "Not today, champ. Or, well...today, actually.",
    "One step closer to the high score...for deaths.",
    "An honorable death. Well, almost.",
    "Turns out you can't outrun your mistakes.",
    "Another name added to the wall of shame.",
    "Oops... That wasn't in the survival guide.",
    "May their loot live on in better hands.",
    "Looks like they ran out of plot armor.",
    "Pro tip: Don't die.",
    "Death comes for us all...just sooner for some.",
    "Should've stayed in the safe zone.",
    "They looked death in the eye and blinked.",
    "When in doubt, don't do whatever they did.",
    "Nature is healing...this player is gone.",
    "Should've brought a bigger stick.",
    "What were they thinking?",
    "Death speedrun.",
    "A valiant effort… well, kind of.",
    "The zombie buffet welcomes its newest entrée.",
    "It's not a failure, it's a tactical respawn...right?",
    "May their next life be less embarrassing.",
    "They believed they could fly. They were wrong.",
    "Don't feed the zombies' wasn't just a suggestion.",
]

def get_funny_line():
    return random.choice(funny_lines)

def find_latest_log(log_dir, keyword):
    """Return the path of the most recently modified log file whose name contains keyword."""
    try:
        files = [
            os.path.join(log_dir, f)
            for f in os.listdir(log_dir)
            if keyword in f.lower() and os.path.isfile(os.path.join(log_dir, f))
        ]
        if not files:
            return None
        return max(files, key=os.path.getmtime)
    except OSError:
        return None

async def handle_pvp_line(line):
    match = PVP_KILL_PATTERN.search(line)
    if not match:
        return
    killer, killer_pos, victim, victim_pos = match.groups()

    primary_channel = bot.get_channel(PRIMARY_CHANNEL_ID)
    if primary_channel:
        await primary_channel.send(
            f"**{killer}** killed **{victim}**\n> {get_funny_line()}"
        )

    secondary_channel = bot.get_channel(SECONDARY_CHANNEL_ID)
    if secondary_channel:
        await secondary_channel.send(
            f"**Killer:** {killer} at ({killer_pos})\n**Victim:** {victim} at ({victim_pos})"
        )

async def handle_user_death_line(line):
    match = USER_DEATH_PATTERN.search(line)
    if not match:
        return
    player, position = match.groups()

    primary_channel = bot.get_channel(PRIMARY_CHANNEL_ID)
    if primary_channel:
        await primary_channel.send(
            f"**{player}** died (non-PVP)\n> {get_funny_line()}"
        )

    secondary_channel = bot.get_channel(SECONDARY_CHANNEL_ID)
    if secondary_channel:
        await secondary_channel.send(
            f"**Player:** {player}\n**Position:** ({position})"
        )

async def monitor_logs(log_dir):
    """Watch log_dir for the latest pvp and user log files.

    When the server restarts it generates new files, so we re-check for the
    newest matching file each poll cycle and switch to it automatically.
    """
    pvp_file = None
    user_file = None
    pvp_pos = 0
    user_pos = 0

    while True:
        # --- pvp file ---
        new_pvp = find_latest_log(log_dir, "pvp")
        if new_pvp != pvp_file:
            pvp_file = new_pvp
            # Start from the current end so we don't replay old entries
            pvp_pos = os.path.getsize(pvp_file) if pvp_file else 0
            if pvp_file:
                print(f"Monitoring PVP log: {pvp_file}")

        if pvp_file and os.path.exists(pvp_file):
            try:
                with open(pvp_file, "r", errors="replace") as f:
                    f.seek(pvp_pos)
                    lines = f.readlines()
                    pvp_pos = f.tell()
                for line in lines:
                    await handle_pvp_line(line)
            except OSError as e:
                print(f"Error reading PVP log: {e}")

        # --- user file ---
        new_user = find_latest_log(log_dir, "user")
        if new_user != user_file:
            user_file = new_user
            user_pos = os.path.getsize(user_file) if user_file else 0
            if user_file:
                print(f"Monitoring user log: {user_file}")

        if user_file and os.path.exists(user_file):
            try:
                with open(user_file, "r", errors="replace") as f:
                    f.seek(user_pos)
                    lines = f.readlines()
                    user_pos = f.tell()
                for line in lines:
                    await handle_user_death_line(line)
            except OSError as e:
                print(f"Error reading user log: {e}")

        await asyncio.sleep(2)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(monitor_logs(LOG_DIR))

# Run the bot
bot.run(DISCORD_TOKEN)
