import pyrogram
import dateutil
import asyncio
from datetime import datetime
from pyrogram import filters


async def execute(bot: 'pyrogram.client.Client', Env):
  """
  Function to enable global rule of the bot
  """
  @bot.on_chat_member_updated(pyrogram.filters.private)
  async def block_unblock(client: 'pyrogram.client.Client', chatmember: 'pyrogram.types.ChatMemberUpdated'):
    if chatmember.new_chat_member.status is pyrogram.enums.ChatMemberStatus.BANNED:
      # The bot is blocked by the user
      lastPing = dateutil.parser.parse(datetime.today().isoformat())
      await Env.MONGO.biltudas1bot.userList.update_one({'ID': chatmember.from_user.id}, {'$set': {'blocked': True, 'lastPing': lastPing}})
    else:
      # The bot is unblocked by the user
      await Env.MONGO.biltudas1bot.userList.update_one({'ID': chatmember.from_user.id}, {'$set': {'blocked': False}})


  # Load Modules
  modules = await Env.MONGO.biltudas1bot.settings.find_one({}, {'_id': False, 'loadModules': True})
  if modules:
    Env.MODULES = modules['loadModules']
  else:
    Env.MODULES = ['FORWARD', 'SRC', 'LEECH', 'FILE']
    await Env.MONGO.biltudas1bot.settings.insert_one({'loadModules': Env.MODULES})


