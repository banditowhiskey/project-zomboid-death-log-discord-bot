r''' @file Log.py
@author SV-Engineer

@brief Adds built in logging mechanisms to classes.

@par Description
The built in logging class in python is meh at best.

'''

# TODO: Implement log file functionality

class Log:
    # Statics to count all warning across all instances
    error_count           = 0
    warning_count         = 0

    # Enables a log file, if desired
    enable_log_file       = False
    # Enables an error log file, if desired
    enable_error_log_file = True

    ENABLE_DEBUG_MESSAGES = False

    def __init__(self, name=__name__):
        r''' @fn def __init__(self, name=__name__)
        @brief Class constructor
        '''
        self.name = name

    def __msg(self, msg_dict:dict)->None:
        r''' @fn def __msg(self, msg_dict:dict)->None
        @brief Prints to console based upon a dictionary passed to it.

        @param msg_dict
        Expects a dictionary with string entry "msg_type" of string type.
        Expects a dictionary with string entry "message" of string type.
        TBH I was trying something new here.

        '''
        print("{}  --  {}".format(msg_dict["msg_type"], msg_dict["message"]))

    def info(self, message:str)->None:
        r''' @fn def info(self, message:str)
        @brief Prints out information to the console window and log file (if enabled).

        '''
        message_dict = {
            "msg_type" : "*INFO      ",
            "message"  : message
        }
        self.__msg(message_dict)
    
    def warn(self, message:str)->None:
        r''' @fn def warn(self, message:str)
        @brief Prints out warnings to the console window and error log file (if enabled).

        '''
        message_dict = {
            "msg_type" : "*WARNING!!!",
            "message"  : message
        }
        self.__msg(message_dict)

        # Add to warning count
        Log.warning_count += 1

    def err(self, message:str)->None:
        r''' @fn def err(self, message:str)
        @brief Prints out errors to the console window and error log file (if enabled).

        '''
        message_dict = {
            "msg_type" : "*ERROR!!!  ",
            "message"  : message
        }
        self.__msg(message_dict)

        # Add to error count
        Log.error_count += 1

    def debug_message(self, message:str)->None:
        r''' @fn def debug_message(self: message:str)->None:
        @brief Prints out debug messages to the console window that may be toggled with static member ENABLE_DEBUG_MESSAGES.

        '''
        if Log.ENABLE_DEBUG_MESSAGES:
            message_dict = {
            "msg_type" : "*DEBUG!!!  ",
            "message"  : message
            }

            self.__msg(message_dict)

        else:
            return

    def banner(self, message:str)->None:
        r''' @fn def banner(self, message:str)->None:
        @brief Prints out banner messages to console.

        '''
        print("\n+ =====================================================================")
        print("| BANNER:")
        print(f"| {message}") 
        print("+ =====================================================================\n")

    def dump_status(self):
        r''' @fn def dump_status(self)
        @brief Dumps a status to the console on call; call at end of script.

        '''
        print("Script complete")
        print("    Error Count: {}".format(Log.error_count))
        print("  Warning Count: {}".format(Log.warning_count))

def main():
    r''' @fn def main()
    @brief This main function exists to inform any user to avoid running this python script directly.

    '''
    log = Log()

    log.warn("This class is meant to be extended off of to add logging to any child class.")
    log.info("Don't call it directly. Instead import and extend off of it.")
    log.dump_status()



if __name__ == "__main__":
    main()