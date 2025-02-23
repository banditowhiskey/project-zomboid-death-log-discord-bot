r''' @file zomboid_bot_cli.py
@brief Adds CLI options to the bot.
'''
from argparse import ArgumentParser
from Log import Log

class ZomboidBotCLI(Log):
    def __init__(self):
        super().__init__(__name__)
        self.info("poop")


def main():
    r''' @fn def main()
    @brief This main function exists to inform any user to avoid running this python script directly.
    '''
    log = Log(__name__)
    log.warn("This file defines a class to add CLI arguments to the bot, don't run this python script directly.")
    log.info("Import and instantiate or extend it else-where.")

    bot = ZomboidBotCLI()

if __name__ == "__main__":
    main()