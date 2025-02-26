r''' @file zomboid_bot_cli.py
@author SV-Engineer

@brief Adds CLI options to the bot.

'''

from argparse import ArgumentParser
from Log import Log

# IMPORT Configuration Constants
# import sys
# sys.path.insert(0, "../inc")

# import constant_configuration
from constant_configuration import DEFAULT_NUMBER_OF_DISCORD_CHANNELS
from constant_configuration import DEFAULT_LUA_LOG_FILE_PATH

class ZomboidBotCLI(Log):
    def __init__(self,
        arg_defaults={
            "number_of_channels"   : DEFAULT_NUMBER_OF_DISCORD_CHANNELS,
            "path_to_lua_log_file" : DEFAULT_LUA_LOG_FILE_PATH
        },
        get_parser=False
    ):
        r''' @fn __init__
        @brief Class constructor that intakes a dictionary to set dafault values for the arguments if NOT passed via the CLI.

        '''
        super().__init__(__name__)

        self.arg_defaults = arg_defaults

        # Init to None for error handling
        self.args         = None
        self.parser       = None

        # In case class extension occurs and it is decided to add more arguments to the parser.
        if not get_parser:
            self.args = self.get_cli_args()
        
        else:
            self.parser = self.get_cli_args(get_parser)
    
    def get_cli_args(self, get_parser=False):
        r''' @fn def get_cli_args(self, get_parsed=True)
        @brief Gets the Command line interfaces args

        @param get_parser
        If True, it returns just the parser so that an extended class may add more arguments to the parser, if desired.
        Else False, it returns the namespace object with the arguments parsed.

        '''

        parser = ArgumentParser()
        # -<single character option> and --<multi-character option> are aliased, either works when passing to the script from CLI.
        # The multi-character option must be used to access the value
        parser.add_argument('-n', '--number_of_channels',   type=int, default=self.arg_defaults["number_of_channels"],   required=False, help="Number of Discord channels to use")
        parser.add_argument('-p', '--path_to_lua_log_file', type=str, default=self.arg_defaults["path_to_lua_log_file"], required=False, help="Path to the LUA log file. Absolute or relative; default is accesses it from the Zomboid directory that acts as your server info root")

        # Expected common case; common case first
        if not get_parser:
            return parser.parse_args()

        else:
            return parser

    def get_args(self):
        r''' @fn get_args
        @brief I exist for if the user wants to reduce verbosity of argument accesses after constructor has run.
        '''
        if self.args is None:
            warn("Returning None object for args namespace request")

        else:
            info("Args namespace exists and is NOT None")
        
        return self.args

    def get_parser(self):
        r''' @fn get_parser
        @brief I exist for if the user wants to reducd verbosity of parser access after constructor has run.
        '''
        if self.parser is None:
            warn("Returning None object for parser request")

        else:
            info("Parser exists and is NOT None")
        
        return self.parser


def main():
    r''' @fn def main()
    @brief This main function exists to inform any user to avoid running this python script directly.
    '''
    log = Log(__name__)
    log.warn("This file defines a class to add CLI arguments to the bot, don't run this python script directly.")
    log.info("Import and instantiate or extend it else-where.")

    log.dump_status()

if __name__ == "__main__":
    main()