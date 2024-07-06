import dotenv
dotenv.load_dotenv()

import pyrogram
from motor import motor_asyncio
from .environment import Environment

# Setting Up
# Setting Up Database
Env = Environment()
Env.MONGO: 'motor_asyncio.AsyncIOMotorClient' = motor_asyncio.AsyncIOMotorClient(Env.MONGO_URI)

# Setting up Client and Bot
bot: 'pyrogram.client.Client' = pyrogram.Client(
  "bot",
  api_id = Env.API_ID,
  api_hash = Env.API_HASH,
  bot_token = Env.BOT_TOKEN,
  in_memory = True
)

account: 'pyrogram.client.Client' = pyrogram.Client(
  "telegram_account",
  api_id = Env.API_ID,
  api_hash = Env.API_HASH,
  session_string = Env.SESSION_TOKEN,
  device_model = f"BiltuDas1Bot {Env.BOT_VERSION}",
  app_version = f"Python {Env.PYTHON_VERSION}",
  in_memory = True
)
account.start()

# Set Premium Account Flag
try:
  Env.PREMIUM_ACCOUNT = account.get_me().is_premium
except AttributeError:
  Env.PREMIUM_ACCOUNT = False