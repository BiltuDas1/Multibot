import pyrogram
import dateutil
import asyncio
import json
from datetime import datetime
from pyrogram import filters


async def execute(bot: 'pyrogram.client.Client', Env):
  """
  Function to enable global rule of the bot
  """
  @bot.on_chat_member_updated(filters.private)
  async def block_unblock(client: 'pyrogram.client.Client', chatmember: 'pyrogram.types.ChatMemberUpdated'):
    if chatmember.new_chat_member.status is pyrogram.enums.ChatMemberStatus.BANNED:
      # The bot is blocked by the user
      lastPing = dateutil.parser.parse(datetime.today().isoformat())
      await Env.MONGO.biltudas1bot.userList.update_one({'ID': chatmember.from_user.id}, {'$set': {'blocked': True, 'lastPing': lastPing}})
    else:
      # The bot is unblocked by the user
      await Env.MONGO.biltudas1bot.userList.update_one({'ID': chatmember.from_user.id}, {'$set': {'blocked': False}})


  @bot.on_message(filters.private & filters.command("help"))
  async def help_method(client: 'pyrogram.client.Client', message: 'pyrogram.types.Message'):
    if str(message.from_user.id) in Env.ADMIN:
      await client.send_message(
        chat_id = message.chat.id,
        text = Env.HELP_ADMIN_MESSAGE
      )
    else:
      await client.send_message(
        chat_id = message.chat.id,
        text = Env.HELP_USER_MESSAGE
      )


  @bot.on_message(filters.private & filters.command("id"))
  async def get_user_id(client: 'pyrogram.client.Client', message: 'pyrogram.types.Message'):
    await client.send_message(
      chat_id = message.chat.id,
      text = f"Your ChatID is: `{message.from_user.id}`"
    )


  # Loading Modules
  modules = await Env.MONGO.biltudas1bot.settings.find_one({}, {'_id': False, 'loadModules': True})
  if modules:
    Env.MODULES = modules['loadModules']
  else:
    Env.MODULES = ['FORWARD', 'SRC', 'LEECH', 'FILE']
    await Env.MONGO.biltudas1bot.settings.insert_one({'loadModules': Env.MODULES})


  # Loading Help Message/Commands List
  with open('help.json', 'r') as h:
    man: 'dict[str, str]' = json.load(h)

    Env.NON_ADMIN_COMMANDS.extend(man["userCommands"])  # Loading User Command List

    help_str = ""
    help_str_user = ""
    count_cmd = len(Env.NON_ADMIN_COMMANDS)
    total_commands = len(man["commands"])
    for pos, (cmd, comment) in enumerate(man["commands"].items()):
      if cmd in Env.NON_ADMIN_COMMANDS:
        count_cmd -= 1

        # Not adding new line to the last command available into the JSON
        if count_cmd:
          help_str_user += f"/{cmd} {comment}\n"
        else:
          help_str_user += f"/{cmd} {comment}"
          help_str_user += "\n\nIf you want to Contact the Admin then write 'Hi' or 'Hello' and then drop your question, your message will be forwarded to the Admins."

      # Not adding new line to the last command available into the JSON
      if (total_commands - 1) == pos:
        help_str += f"/{cmd} {comment}"
      else:
        help_str += f"/{cmd} {comment}\n"

    Env.HELP_ADMIN_MESSAGE += help_str
    Env.HELP_USER_MESSAGE += help_str_user
