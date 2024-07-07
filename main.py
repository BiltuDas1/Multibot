# Checks if any other process is running
import os
if os.path.exists('process.lock'):
  exit(0)
else:
  with open('process.lock', 'w') as lock:
    lock.write("")


import asyncio
import pyrogram
import time
from pyrogram import filters
from modules import forward, default
from apis import Env, account, bot, errors

async def main():
  # Loading modules
  await default.execute(bot, Env)

  if Env.MODULES["FORWARD"]:
    await forward.personal_message(bot, Env)
  if Env.MODULES["SRC"]:
    pass
  if Env.MODULES["LEECH"]:
    pass
  if Env.MODULES["FILE"]:
    pass

  loop = True
  # Loop to handle FloodWait, so that bot don't get stuck after a FloodWait
  while loop:
    try:
      async with bot:
        print("Bot started")

        if Env.RESTARTED:
          await bot.send_message(
            chat_id = int(Env.RESTARTED_BY_USER),
            text = "Bot is ready to use ✅"
          )

        await pyrogram.idle()

        # Set the Process Restart Flag
        with open('terminate.lock', 'w') as flag:
          flag.write("")

        loop = False
        await account.stop()

        # Disable lock
        try:
          os.remove('process.lock')
        except FileNotFoundError:
          pass

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