import os

class Error(Exception):
    """
    Exception Class for any kind of Error encounter in the Telegram bot
    """
    
    __ERR_MSG_LIST = {
        0: "Something unexpected happened into the code, please contact the developer",
        1: "BOT_TOKEN Environment can't be empty",
        2: "BOT_TOKEN Environment have Invalid Bot Token, Please provide the correct token and try again",
        3: "OWNER_IDs Environment can't be empty",
        4: "OWNER_IDs Environment variable contains invalid ID, Please provide correct ID and try again",
        5: "API_ID Environment variable can't be empty",
        6: "API_ID Environment variable contains invalid ID, Please provide correct ID and try again",
        7: "API_HASH Environment variable can't be empty",
        8: "Invalid API_HASH, Please provide correct Hash and try again",
        9: "GROUP_ID Environment can't be empty",
        10: "GROUP_ID Environment variable contains invalid ID, Please provide correct ID and try again",
        11: "STRING_SESSION Environment variable can't be empty",
        12: "Invalid STRING_SESSION, Please provide correct Session and try again",
        13: "OWNER_USERNAME Environment can't be empty",
        14: "OWNER_USERNAME is invalid",
        15: "MONGO_URI Environment can't be empty",
        16: "MONGO_URI contains invalid URI, Please provide the correct URI"
    }

    __ERR_CODE_LIST = {
        "UNEXPECTED_EXCEPTION": 0,
        "NO_TG_BOT_TOKEN": 1,
        "INVALID_TG_BOT_TOKEN": 2,
        "NO_OWNER_ID": 3,
        "INVALID_OWNER_ID": 4,
        "NO_API_ID": 5,
        "INVALID_API_ID": 6,
        "NO_API_HASH": 7,
        "INVALID_API_HASH": 8,
        "NO_GROUP_ID": 9,
        "INVALID_GROUP_ID": 10,
        "NO_SESSION_TOKEN": 11,
        "INVALID_SESSION_TOKEN": 12,
        "NO_OWNER_USERNAME": 13,
        "INVALID_OWNER_USERNAME": 14,
        "NO_MONGO_URI": 15,
        "INVALID_MONGO_URI": 16
    }

    def __init__(self, ERR_CODE: 'str', MSG: 'str'=None):
        if type(ERR_CODE) == str:
            self.__ERR_CODE = int(self.__ERR_CODE_LIST[ERR_CODE])
        else:
            self.__ERR_CODE = int(0)

        if type(MSG) == str:
            self.__MSG = MSG
        else:
            self.__MSG = self.__ERR_MSG_LIST[self.__ERR_CODE]

        # Set terminate lock
        with open('terminate.lock', 'w') as lock:
            lock.write('')

        # Remove Local Lock
        try:
            os.remove('process.lock')
        except FileNotFoundError:
            pass

    def __str__(self):
        return self.__MSG
    
    def ErrorCode(self):
        """
        Returns the Error Code (in int)
        """
        return self.__ERR_CODE
    