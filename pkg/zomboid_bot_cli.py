r''' @file zomboid_bot_cli.py
@brief Adds CLI options to the bot.
'''
from argparse import ArgumentParser

class ZomboidBotCLI(Log.getLoggerClass()):
    def __init__(self):
        super().__init__(__name__)
        self.info("poop")


def main():
    r'''
    Description:
    This main function exists to inform any user to avoid running this python script directly.
    '''
    log = Log.getLogger(__name__)
    log.info("This file defines a class to add CLI arguments to the bot, don't run this python script.")

    bot = ZomboidBotCLI()

if __name__ == "__main__":
    main()