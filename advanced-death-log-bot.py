import os
import time
import asyncio
import random
from discord.ext import commands
from discord import Intents

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.insert(0, "./pkg")
sys.path.insert(0, "./inc")

from constant_configuration import DEFAULT_NUMBER_OF_DISCORD_CHANNELS
from constant_configuration import DEFAULT_LUA_LOG_FILE_PATH

from zomboid_bot_cli import ZomboidBotCLI
from Log import Log

# Bot token and channel IDs
DISCORD_TOKEN                             = os.getenv("DISCORD_BOT_TOKEN")
PRIMARY_CHANNEL_ID                        = int(os.getenv("PRIMARY_CHANNEL_ID"))  # For the death cause
SECONDARY_CHANNEL_ID                      = int(os.getenv("SECONDARY_CHANNEL_ID"))  # For detailed info

# For migrating to a configurable implementation
bot_cli = ZomboidBotCLI()

# Load real-life hours per in-game day from environment
REAL_LIFE_HOURS_PER_IN_GAME_DAY = float(os.getenv("REAL_LIFE_HOURS_PER_IN_GAME_DAY", 2.0))  # Real-life hours per in-game day, with a default of 2.0
# Calculate real-life hours per in-game hour based on real-life hours per in-game day
REAL_LIFE_HOURS_PER_IN_GAME_HOUR = REAL_LIFE_HOURS_PER_IN_GAME_DAY / 24


log = Log("Main")

# I reworked this a bit to help myself debug the changes to add the CLI arguments. The intent of the CLI arguments addition is to maintain 
# legacy functionality while also enabling easier configuration for the use case of the user. The goal is to make it so configurable that
# future users need not modify the code.
if not DISCORD_TOKEN: 
    log.e("DISCORD_BOT_TOKEN Environment variable not found")
    log.info("Put your discord bot token in a .env file in the root of this project")
    raise RuntimeError("Missing bot token in environment variables")

if not PRIMARY_CHANNEL_ID:
    log.e("PRIMARY_CHANNEL_ID Environment variable not found")
    log.info("Put your primary channel ID in a .env file in the root of this project; .env is in gitignore because it is private and unique per bot made")
    log.info('Enable Developer Mode in Discord if not done so already and then right click the channel to output to and select context menu option: "Copy Channel ID"')
    log.info('The Project Zomboid Server ".ini" file needs a channel ID as well')
    raise RuntimeError("Channel ID 1 in environment variables")

if bot_cli.args.number_of_channels == 2 and not SECONDARY_CHANNEL_ID:    
    log.e("SECONDARY_CHANNEL_ID Environment variable not found")
    log.info("Put your secondary channel ID in a .env file in the root of this project; .env is in gitignore because it is private and unique per bot made")
    log.info('Enable Developer Mode in Discord if not done so already and then right click the channel to output to and select context menu option: "Copy Channel ID"')
    raise RuntimeError("Channel ID 2 in environment variables")


# Initialize the bot
intents = Intents.all()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Function to parse and format the log entry
def parse_log_entry(log_entry):
    # Extract desired fields from the log entry
    data = {}
    data["timestamp"]           = log_entry.split("Timestamp:")[1].split("\n")[0].strip()
    data["death_cause"]         = log_entry.split("Death Cause:")[1].split("\n")[0].strip()
    data["steam_name"]          = log_entry.split("Steam Name:")[1].split("\n")[0].strip()
    data["character_name"]      = log_entry.split("Character Name:")[1].split("\n")[0].strip()
    data["position"]            = log_entry.split("Position:")[1].split("\n")[0].strip()
    data["traits"]              = log_entry.split("Traits:")[1].split("\n")[0].strip()
    data["skills"]              = log_entry.split("Skills:")[1].split("\n")[0].strip()
    data["inventory"]           = log_entry.split("Inventory:")[1].split("\n")[0].strip()
    data["zombie_kills"]        = log_entry.split("Zombie Kills:")[1].split("\n")[0].strip()
    data["time_survived"]       = log_entry.split("Survived Time:")[1].split("\n")[0].strip()

    # Alphabetize skills and format into a bullet list
    skills_list = data["skills"].replace("{", "").replace("}", "").split(",")
    skills_list = sorted([skill.strip() for skill in skills_list])
    data["skills"] = "{\n" + "\n".join(skills_list) + "\n}"

    # Remove {} brackets, alphabetize traits
    traits_list = data["traits"].replace("{", "").replace("}", "").split(",")
    traits_list = sorted([trait.strip() for trait in traits_list if trait.strip()])
    data["traits"] = ", ".join(traits_list)

    # Parse survival time into real-life hours
    data["real_life_hours"] = parse_survived_time(data["time_survived"])

    return data

# Function to parse and calculate real-life hours from survival time
def parse_survived_time(time_str):
    months = 0
    days = 0
    hours = 0
    minutes = 0

    # Split the string into different time components
    time_units = time_str.split(",")
    
    for unit in time_units:
        unit = unit.strip()
        if "month" in unit:
            months = int(unit.split("month")[0].strip())
        elif "day" in unit:
            days = int(unit.split("day")[0].strip())
        elif "hour" in unit:
            hours = int(unit.split("hour")[0].strip())
        elif "minute" in unit:
            minutes = int(unit.split("minute")[0].strip())
    
    # Convert everything to real-life hours
    total_real_life_hours = (
        (months * 30 * REAL_LIFE_HOURS_PER_IN_GAME_DAY) +
        (days * REAL_LIFE_HOURS_PER_IN_GAME_DAY) +
        (hours * REAL_LIFE_HOURS_PER_IN_GAME_HOUR) +
        (minutes * REAL_LIFE_HOURS_PER_IN_GAME_HOUR / 60)
    )
    return round(total_real_life_hours, 2)

# Add an array of funny lines to say when someone dies
funny_lines = [
    "They're dead, Jim.",
    "Looks like they won't be coming back from that one.",
    "F to pay respects.",
    "Survival is overrated anyway.",
    "Another one bites the dust."
    "They were too beautiful for this world.",
    "Goodnight, sweet prince.",
    "They did not go gentle into that good night.",
    "They are now one with the zombies.",
    "They have left the building.",
    "Looks like they weren't built different.",
    "Skill Issue.",
    "They fought bravely... kinda.",
    "R.I.P. buddy, you will be… forgotten soon.",
    "A zombie's favorite snack.",
    "Oops. Better luck next time.",
    "Remember, death is just a respawn point. Oh wait…",
    "L in chat.",
    "Their watch has ended.",
    "Game over, man! Game over!",
    "You were meant to be the chosen one!",  
    "Should've zigged when you zagged.",  
    "Not today, champ. Or, well... today, actually.",  
    "One step closer to the high score... for deaths.",  
    "An honorable death. Well, almost.",  
    "Turns out you can't outrun your mistakes.",  
    "Another name added to the wall of shame.",  
    "Oops... That wasn't in the survival guide.",  
    "May their loot live on in better hands.",  
    "Looks like they ran out of plot armor.",  
    "Pro tip: Don't die.",  
    "Death comes for us all... just sooner for some.",  
    "Should've stayed in the safe zone.",  
    "They looked death in the eye and blinked.",  
    "When in doubt, don't do whatever they did.",  
    "Nature is healing... this player is gone.",  
    "Should've brought a bigger stick.",  
    "What were they thinking?",  
    "Death speedrun.",  
    "A valiant effort… well, kind of.",  
    "The zombie buffet welcomes its newest entrée.",  
    "It's not a failure, it's a tactical respawn... right?",  
    "May their next life be less embarrassing.",  
    "They believed they could fly. They were wrong.",  
    "Don't feed the zombies' wasn't just a suggestion."  
]

# Get random funny line
def get_funny_line():
    return random.choice(funny_lines)

# Monitor the file and send messages
async def monitor_log_file(file_path):
    while True:
        try:
            log.banner("open file and monitor")
            # Open the file and start monitoring
            with open(file_path, "r") as file:
                file.seek(0, 2)  # Seek to the end of the file
                while True:
                    log.debug_message("I am awake...")

                    line = file.readline()

                    if not line:
                        log.debug_message("...going back to sleep")
                        await asyncio.sleep(2)  # Wait for new log entries, check every 2 seconds
                        continue

                    # When a new entry is added, parse it and send messages
                    if "Death," in line:
                        log.info("Found Death")
                        log_entry = line + "".join([file.readline() for _ in range(15)])  # Read full log block
                        data = parse_log_entry(log_entry)


                        # Send message to primary channel
                        log.info("try send message")
                        primary_channel = bot.get_channel(PRIMARY_CHANNEL_ID)
                        if primary_channel:
                            details = (
                                f"**{data['steam_name']}** ({data['character_name']}) was killed by {data['death_cause']}\n"
                                f"> They survived for {data['time_survived']} and killed {data['zombie_kills']} zombies. \n > That's {data['real_life_hours']} real life hours wasted. \n > {get_funny_line()}"
                            )
                            log.info(f"Log Entry: {details}")
                            await primary_channel.send(details)

                        else:
                            log.info("Primary Channel DNE?")

                        # Send detailed message to secondary channel
                        secondary_channel = bot.get_channel(SECONDARY_CHANNEL_ID)
                        if secondary_channel:
                            details = (
                                f"**Steam Name:** {data['steam_name']}\n"
                                f"**Time of Death:** {data['timestamp']}\n"
                                f"**Position:** {data['position']}\n"
                                f"**Traits:** {data['traits']}\n"
                                f"**Skills:** {data['skills']}\n"
                                # f"**Inventory:** {data['inventory']}"
                            )
                            await secondary_channel.send(details)

                        else:
                            log.info("Secondary Channel DNE?")

                    else:
                        log.info("Death not found")

        except FileNotFoundError:
            log.warn(f"Log file not found: {file_path}. Retrying...")
            await asyncio.sleep(5)  # Wait before retrying
        except Exception as e:
            log.err(f"Error while monitoring log file: {e}")
            await asyncio.sleep(5)  # Pause before retrying

@bot.event
async def on_ready():
    log.info(f"Logged in as {bot.user}")
    # Start monitoring the log file
    log_file_path = bot_cli.args.path_to_lua_log_file

    log.info(f"Log file for death path resolved to: {log_file_path}")
    bot.loop.create_task(monitor_log_file(log_file_path))


# Run the bot
bot.run(DISCORD_TOKEN)
