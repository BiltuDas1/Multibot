import asyncio
import pyrogram
import time
from pyrogram import filters
from modules import forward, default
from apis import Env, account, bot


async def main():
  print("Bot is starting...")

  # Loading modules
  await default.execute(bot, Env)

  if "FORWARD" in Env.MODULES:
    await forward.personal_message(bot, Env)
  if "SRC" in Env.MODULES:
    pass
  if "LEECH" in Env.MODULES:
    pass
  if "FILE" in Env.MODULES:
    pass
  if not Env.MODULES:
    print("No Module Loaded")

  loop = True
  while loop:
    try:
      async with bot:
        print("Bot started")
        await pyrogram.idle()
        loop = False

    except pyrogram.errors.exceptions.flood_420.FloodWait as e:
      try:
        print(f"FloodWait: Waiting for {e.value} seconds")
        await asyncio.sleep(e.value)
        print("Service resumed")
        continue

      except asyncio.exceptions.CancelledError:
        print("\nTerminating Process..")
        await bot.stop()
        await account.stop()
        loop = False
        print("\nProcess Terminated")


# Starts the bot
if __name__ == "__main__":
  bot.run(main())