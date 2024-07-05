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
    self.BOT_USERNAME = None
    self.PYTHON_VERSION = platform.python_version()

    # Get bot version
    with open('version', 'r') as v:
      self.BOT_VERSION = v.readline().replace('\n', '')

      if not self.BOT_VERSION:
        self.BOT_VERSION = '0.0.0'


    self.OWNER_USERNAME = os.getenv("OWNER_USERNAME")


    self.__test_data() # For testing the Environments


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

    if re.search("^[0-9]{8,10}:[a-zA-Z0-9_-]{35}$", self.BOT_TOKEN) is None:
      raise Error('INVALID_TG_BOT_TOKEN')
      
    # Checking the Group ID
    if self.GROUP_ID is None:
      raise Error('NO_GROUP_ID')

    if re.search("^-100\d+$", self.GROUP_ID) is None:
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

    if re.search("^[\d(abcdef)]{32}$", self.API_HASH) is None:
      raise Error('INVALID_API_HASH')

    # Checking String Session
    if self.SESSION_TOKEN is None:
      raise Error('NO_SESSION_TOKEN')

    if re.search("^[a-zA-Z0-9_-]+$", self.SESSION_TOKEN) is None:
      raise Error('INVALID_SESSION_TOKEN')

    # Checking Owner Username
    if self.OWNER_USERNAME is None:
      raise Error('NO_OWNER_USERNAME')