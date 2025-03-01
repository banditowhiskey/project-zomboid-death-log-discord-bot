import os
import time
import asyncio
import random
from discord.ext import commands
from discord import Intents
import re

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.insert(0, "./pkg")
sys.path.insert(0, "./inc")

from constant_configuration import FUNNY_LINES
from constant_configuration import CLI_ARG_DEFAULTS
from constant_configuration import INSULTS

from zomboid_bot_cli import ZomboidBotCLI
from Log import Log

# Bot token and channel IDs
DISCORD_TOKEN                             = os.getenv("DISCORD_BOT_TOKEN")
PRIMARY_CHANNEL_ID                        = int(os.getenv("PRIMARY_CHANNEL_ID"))  # For the death cause
SECONDARY_CHANNEL_ID                      = int(os.getenv("SECONDARY_CHANNEL_ID"))  # For detailed info


# Load real-life hours per in-game day from environment
REAL_LIFE_HOURS_PER_IN_GAME_DAY = float(os.getenv("REAL_LIFE_HOURS_PER_IN_GAME_DAY", 2.0))  # Real-life hours per in-game day, with a default of 2.0
# Calculate real-life hours per in-game hour based on real-life hours per in-game day
REAL_LIFE_HOURS_PER_IN_GAME_HOUR = REAL_LIFE_HOURS_PER_IN_GAME_DAY / 24


# For migrating to a configurable implementation
# The handle for this gets passed where feasible.
# TODO: Recall if threads can have a class handle passed to them; I haven't worked with python threads in ages.
bot_cli = ZomboidBotCLI()
log = Log("Main")

def check_for_environment_variables(bot_cli)->None:
    r'''
    Ensures the environment variables exist.
    '''
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


def initialize_bot():
    r'''
    Initialize the bot
    '''
    intents = Intents.all()
    intents.messages = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    return bot

# TODO: Figure out how to compartmentalize the global class handles
bot = initialize_bot()

# Function to parse and format the log entry
def parse_log_entry(log_entry):
    # Extract desired fields from the log entry
    highest_skill_levels = []
    data                 = {}

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
    skills_list          = data["skills"].replace("{", "").replace("}", "").split(",")
    skills_list          = sorted([skill.strip() for skill in skills_list])
    data["skills"]       = "{\n" + "\n".join(skills_list) + "\n}"
    highest_skill_levels = find_highest_level_skill(data["skills"])

    # Remove {} brackets, alphabetize traits
    traits_list          = data["traits"].replace("{", "").replace("}", "").split(",")
    traits_list          = sorted([trait.strip() for trait in traits_list if trait.strip()])
    data["traits"]       = ", ".join(traits_list)

    # Parse survival time into real-life hours
    data["real_life_hours"] = parse_survived_time(data["time_survived"])

    return data, highest_skill_levels

def find_highest_level_skill(skills_list:list)->dict:
    biggest        = []
    current_max    = 0
    next_skill_lvl = 0
    skill_name     = None
    strengh_level  = 0
    fitness_level  = 0

    # I realize there are likely better ways to do this and I am lazy and thus doing it the way I know how.
    # TODO: Come back and fix this laziness me.
    skills         = skills_list.split("\n")

    for skill in skills:
        # Strength and fitness are always pretty high so I'm excluding those.
        if "strength" not in skill.lower() and "fitness" not in skill.lower() and "{" not in skill.lower() and "}" not in skill.lower():
            skill_name     = re.findall(r'\S+', skill)[0]
            next_skill_lvl = int(re.findall(r'\d+', skill)[0])

            log.debug_message(f"Checking if {skill_name} is largest  -- RE found {next_skill_lvl}")

            # This statement should guarantee nothing at level 0 makes it in.
            if next_skill_lvl > current_max:
                if biggest != []:
                    # If the list is not empty and a bigger value is found, pop off the list.
                    # FIXME: I'm pretty sure there is a built in method that will acheive the same end goal
                    # of a list of the highest skill(s)... a proper dict implementation if you will.
                    while(len(biggest)):
                        biggest.pop(0)

                current_max = next_skill_lvl
                biggest.append({skill_name : current_max})

        elif "strength" in skill.lower():
            strengh_level = int(re.findall(r'\d+', skill)[0])
            log.info(f"Strength Level: {strengh_level}")

        elif "fitness" in skill.lower():
            fitness_level = int(re.findall(r'\d+', skill)[0])
            log.info(f"Fitness Level: {fitness_level}")

    biggest.append({"Strength" : strengh_level})
    biggest.append({"Fitness"  : fitness_level})

    return biggest


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

# Get random funny line
def get_funny_line():
    return random.choice(FUNNY_LINES)

def setup_log_to_primary_cord(data:dict, notable_skills:str, bot_cli=bot_cli):
    if bot_cli.args.only_character_names:
        details = (
            # -o take priority over -c  --  It will be easier to just communicate this rather than try to support multiple permutations.
            f"**{data['character_name']}** was killed by {data['death_cause']}\n"
            f"Notable Skill Levels\n: {notable_skills}"
            f"Statistics:\n"
            f"> This {random.choice(INSULTS)} survived for {data['time_survived']} and killed {data['zombie_kills']} zombies. \n > That's {data['real_life_hours']} real life hours wasted. \n > {get_funny_line()}"
        )

    # !!! DEFAULT OPTION
    elif bot_cli.args.character_names:
        details = (
            f"**{data['steam_name']}** ({data['character_name']}) was killed by {data['death_cause']}\n"
            f"Notable Skill Levels {notable_skills}"
            f"Statistics:\n"
            f"> This {random.choice(INSULTS)} survived for {data['time_survived']} and killed {data['zombie_kills']} zombies. \n > That's {data['real_life_hours']} real life hours wasted. \n > {get_funny_line()}"
        )

    # No Character names included !!! This was legacy behavior and I think including both profile names and character names is better default behavior
    else:
        details = (
            f"**{data['steam_name']}** was killed by {data['death_cause']}\n"
            f"Notable Skill Levels {notable_skills}"
            f"Statistics:\n"
            f"> This {random.choice(INSULTS)} survived for {data['time_survived']} and killed {data['zombie_kills']} zombies. \n > That's {data['real_life_hours']} real life hours wasted. \n > {get_funny_line()}"
        )

    return details


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
                        data, highest_skill_levels = parse_log_entry(log_entry)
                        notable_skills = ""
                        tmp_skill      = ""

                        for skill in highest_skill_levels:
                            for key in skill:
                                tmp_key        = f"{key}".ljust(10)
                                notable_skills = f"{notable_skills}\n> {tmp_key}  --  {skill[key]}"

                        notable_skills = f"{notable_skills}\n"

                        log.debug_message(f"Notable Skills String: {notable_skills}")
                        # Send message to primary channel
                        log.info("try send message")
                        primary_channel = bot.get_channel(PRIMARY_CHANNEL_ID)
                        if primary_channel:
                            details=setup_log_to_primary_cord(data, notable_skills)

                            log.debug_message(f"Log Entry: {details}")

                            if not "test_mode" in bot_cli.args:
                                await primary_channel.send(details)

                        else:
                            log.info("Primary Channel DNE?")

                        # Do a check here to see if the user wants this information or not.
                        if bot_cli.args.number_of_channels == CLI_ARG_DEFAULTS["number_of_channels"]:
                            log.debug_message("Second Discord Channel in use")
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
                                log.debug_message(f"Log Entry: {details}")
                                
                                if not "test_mode" in bot_cli.args:
                                    await secondary_channel.send(details)

                            else:
                                log.warn("Secondary Channel DNE?")

                        else:
                            log.debug_message("Second discord Channel NOT in use")

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


def main()->None:
    # Run the bot
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    check_for_environment_variables(bot_cli)
    main()
