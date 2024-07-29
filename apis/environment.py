import os
import platform
import re
from .errors import Error

class Environment:
  def __init__(self):
    # Loading Data from Environments
    self.BOT_TOKEN = os.getenv("BOT_TOKEN")
    self.GROUP_ID = os.getenv("GROUP_ID")

    if (ids := os.getenv("OWNER_IDs")) is not None:
      self.ADMIN = tuple(ids.split(" "))
    else:
      self.ADMIN = None

    self.API_ID = os.getenv("API_ID")
    self.API_HASH = os.getenv("API_HASH")
    self.SESSION_TOKEN = os.getenv("STRING_SESSION")
    self.PREMIUM_ACCOUNT = False
    self.BOT_USERNAME: 'str' = None  # Automatically Get Replaced while the bot is running
    self.MONGO_URI: 'str' = os.getenv("MONGO_URI")
    self.MONGO = None  # Automatically MongoClient Object will be replaced
    self.PYTHON_VERSION = platform.python_version()
    self.DUMP_CHAT = os.getenv("DUMP_CHAT")

    # If Cache Enabled
    CACHE = os.getenv("CACHE")
    if CACHE is None:
      self.CACHE_ENABLED = False
    else:
      if CACHE in ("yes", "true"):
        self.CACHE_ENABLED = True
      elif CACHE in ("no", "false"):
        self.CACHE_ENABLED = False
      else:
        raise Error("INVALID_CACHE")

    # Get bot version
    with open('version', 'r') as v:
      self.BOT_VERSION = v.readline().replace('\n', '')

      if not self.BOT_VERSION:
        self.BOT_VERSION = '0.0.0'

    self.OWNER_USERNAME = os.getenv("OWNER_USERNAME")
    self.MODULES: 'dict[str, bool]' = {}  # Replaced automatically by reading mongodb config
    self.NON_ADMIN_COMMANDS = []  # Replaced automatically by modules
    self.HELP_ADMIN_MESSAGE = ""  # Replaced automatically by modules
    self.HELP_USER_MESSAGE = ""  # Replaced automatically by modules
    self.CACHED_MODULE_OPTIONS: 'list[list]' = None
    self.RESTARTED = False  # Flag tells if the bot is restarted or started directely
    self.RESTARTED_BY_USER: 'int' = None  # User who restarted the bot
    self.REFRESH_TIME = 2  # Seconds to wait to Refresh the download Progress
    self.UNITS = ("B", "KiB", "MiB", "GiB", "TiB", "EiB", "PiB")
    self.ACTIVE_USERS = set()  # Stores user ID of those whose tasks are running
    self.DOWNLOADED = 0  # Total Downloaded data
    self.UPLOADED = 0  # Total Uploaded data

    self.__test_data()  # For testing the Environments


  def __test_data(self):
    # Checking Admin IDs
    if self.ADMIN is None:
      raise Error('NO_OWNER_ID')

    for uid in self.ADMIN:
      try:
        int(uid)
      except ValueError:
        raise Error('INVALID_OWNER_ID', f"The Admin ID is invalid: {uid}")

    # Checking Bot Token
    if self.BOT_TOKEN is None:
      raise Error('NO_TG_BOT_TOKEN')

    if re.match("^[0-9]{8,10}:[a-zA-Z0-9_-]{35}$", self.BOT_TOKEN) is None:
      raise Error('INVALID_TG_BOT_TOKEN')
      
    # Checking the Group ID
    if self.GROUP_ID is None:
      raise Error('NO_GROUP_ID')

    if re.match("^-100\d+$", self.GROUP_ID) is None:
      raise Error('INVALID_GROUP_ID')

    # Checking API_ID
    if self.API_ID is None:
      raise Error('NO_API_ID')

    try:
      int(self.API_ID)
    except ValueError:
      raise Error('INVALID_API_ID')

    # Checking API_HASH
    if self.API_HASH is None:
      raise Error('NO_API_HASH')

    if re.match("^[\d(abcdef)]{32}$", self.API_HASH) is None:
      raise Error('INVALID_API_HASH')

    # Checking String Session
    if self.SESSION_TOKEN is None:
      raise Error('NO_SESSION_TOKEN')

    if re.match("^[a-zA-Z0-9_-]+$", self.SESSION_TOKEN) is None:
      raise Error('INVALID_SESSION_TOKEN')

    # Checking Owner Username
    if self.OWNER_USERNAME is None:
      raise Error('NO_OWNER_USERNAME')

    if re.match("^\D[\w]{4,31}$", self.OWNER_USERNAME) is None:
      raise Error('INVALID_OWNER_USERNAME')

    # Checks for the mongodb uri
    if self.MONGO_URI is None:
      raise Error('NO_MONGO_URI')

    if re.match("^mongodb\+srv:\/\/.+:.+@[\w\-\.]+\/?$", self.MONGO_URI) is None:
      raise Error('INVALID_MONGO_URI')

    # Checks for Dump Chat ID
    if self.CACHE_ENABLED:
      if self.DUMP_CHAT is None:
        raise Error('NO_DUMP_CHAT_ID')

    if self.DUMP_CHAT is not None:
      if re.match("^-100\d+$", self.DUMP_CHAT) is None:
        raise Error('INVALID_DUMP_CHAT_ID')