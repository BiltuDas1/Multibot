if __name__ != '__main__':
  import dotenv
  dotenv.load_dotenv()

  import pyrogram
  from .environment import Environment

  # Setting up Client and Bot
  Env = Environment()
  bot: 'pyrogram.client.Client' = pyrogram.Client(
    "bot",
    api_id = Env.API_ID,
    api_hash = Env.API_HASH,
    bot_token = Env.BOT_TOKEN
  )

  account: 'pyrogram.client.Client' = pyrogram.Client(
    "telegram_account",
    api_id = Env.API_ID,
    api_hash = Env.API_HASH,
    session_string = Env.SESSION_TOKEN,
    device_model = f"BiltuDas1Bot {Env.BOT_VERSION}",
    app_version = f"Python {Env.PYTHON_VERSION}"
  )
  account.start()

  # Set Premium Account Flag
  try:
    Env.PREMIUM_ACCOUNT = account.get_me().is_premium
  except AttributeError:
    Env.PREMIUM_ACCOUNT = False