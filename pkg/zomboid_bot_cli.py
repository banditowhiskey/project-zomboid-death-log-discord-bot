r''' @file zomboid_bot_cli.py
@brief Adds CLI options to the bot.
'''
from argparse import ArgumentParser
from Log import Log

class ZomboidBotCLI(Log):
    def __init__(self, arg_defaults={"number_of_channels" : 2}):
        r''' @fn __init__
        @brief Class constructor that intakes a dictionary to set dafault values for the arguments if NOT passed via the CLI.

        '''
        super().__init__(__name__)

        self.arg_defaults = arg_defaults
    
    def get_cli_args(self, get_parser=False):
        r''' @fn def get_cli_args(self, get_parsed=True)
        @brief Gets the Command line interfaces args

        @param get_parser
        If True, it returns just the parser so that an extended class may add more arguments to the parser, if desired.
        Else False, it returns the namespace object with the arguments parsed.

        '''

        parser = ArgumentParser()
        # -n and --number_of_channels are aliased, either works
        parser.add_argument('-n', '--number_of_channels', type=int, default=self.arg_defaults["number_of_channels"], required=False, help="Number of Discord channels to use")

        # Expected common case; common case first
        if not get_parser:
            return parser.parse_args()

        else:
            return parser


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