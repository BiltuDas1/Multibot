# Checks for local lock
import os
if os.path.exists('process.lock'):
  print("Bot Process Terminated by Local Lock")
  with open('terminate.lock', 'w') as lock:
    lock.write("")

  exit(0)
else:
  with open('process.lock', 'w') as lock:
    lock.write("")


import asyncio
import pyrogram
import time
import signal
from pyrogram import filters
from modules import forward, default, src
from apis import Env, account, bot, errors


def terminate_handler(sig, frame):
  print("[PROCESS] Bot Termination request received")
  try:
    asyncio.run(bot.stop())
  except ConnectionError:
    pass

  try:
    asyncio.run(account.stop())
  except ConnectionError:
    pass

  disable_local_lock()
  disable_global_lock()
  terminate_lock()
  print("[PROCESS] Bot Terminated")
  exit()


def disable_local_lock():
  try:
    os.remove('process.lock')
  except FileNotFoundError:
    pass


def disable_global_lock():
  Env.MONGO.biltudas1bot.settings.update_one({}, {'$set': {'global_lock': False}})


def terminate_lock():
  with open('terminate.lock', 'w') as lock:
    lock.write("")


async def main():
  # Loading modules
  if (await default.execute(bot, Env)) == "TERMINATE":
    print("Bot Process Terminated by Global Lock")
    disable_local_lock()
    terminate_lock()
    return

  if Env.MODULES["FORWARD"]:
    await forward.personal_message(bot, Env)
  if Env.MODULES["SRC"]:
    await src.save_restricted_content(bot, account, Env)
  if Env.MODULES["LEECH"]:
    pass
  if Env.MODULES["FILE"]:
    pass

  print("Bot started")

  loop = True
  # Loop to handle FloodWait, so that bot don't get stop after a FloodWait
  while loop:
    try:
      async with bot:
        if Env.RESTARTED:
          await bot.send_message(
            chat_id = int(Env.RESTARTED_BY_USER),
            text = "Bot is ready to use ✅"
          )

        await pyrogram.idle()  # Loop for Infinite Period

        loop = False
        await account.stop()

        disable_local_lock()
        disable_global_lock()
        terminate_lock()

    except pyrogram.errors.exceptions.flood_420.FloodWait as e:
      try:
        print(f"FloodWait: Waiting for {e.value} seconds")
        await asyncio.sleep(e.value)
        print("Service resumed")
        continue

      except asyncio.exceptions.CancelledError:
        print("\nTerminating Process..")
        loop = False
        await bot.stop()
        await account.stop()

        disable_local_lock()
        disable_global_lock()
        terminate_lock()
        print("\nProcess Terminated")


# Starts the bot
if __name__ == "__main__":
  signal.signal(signal.SIGTERM, terminate_handler)
  signal.signal(signal.SIGINT, terminate_handler)
  bot.run(main())