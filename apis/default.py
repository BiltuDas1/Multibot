import pyrogram
import dateutil
import asyncio
import httpx
import json
import os
import signal
import psutil
import time
from datetime import datetime
from pyrogram import filters, types


async def execute(bot: 'pyrogram.client.Client', Env):
  """
  Function to enable global rule of the bot
  """

  async def collecting_machine_stats() -> str:
    def file_size_converter(size: 'int') -> str:
      """
      Converts Bytes to Human Readable Size
      """
      i = 0
      temp_size = size

      while temp_size > 1023:
        temp_size /= 1024
        i += 1

      temp_size = float(f"{temp_size:.2f}")
      return f"{temp_size} {Env.UNITS[i]}"

    def seconds_elapsed() -> int:
      return int(time.time() - psutil.boot_time())

    def convert_seconds(seconds: int) -> str:
      # Define the time units in seconds
      units = [
        ("year", 60 * 60 * 24 * 365),
        ("month", 60 * 60 * 24 * 30),
        ("day", 60 * 60 * 24),
        ("hour", 60 * 60),
        ("minute", 60),
        ("second", 1)
      ]

      # Dictionary to store the result
      result = {}

      # Loop through each time unit
      for name, count in units:
        if seconds >= count:
          value = seconds // count
          result[name] = value
          seconds %= count

      # Create the result string
      result_str = ' '.join(f"{value} {name}{'s' if value > 1 else ''}" for name, value in result.items())
      return result_str

    disk = psutil.disk_usage('/')
    ram = psutil.virtual_memory()

    final_msg = f"<u>Bot Stats:</u>\n**Uptime: **{convert_seconds(seconds_elapsed())}\n**Disk Total: **{disk.total / (2 ** 30):.2f} GiB\n**Disk Used: **{disk.used / (2 ** 30):.2f} GiB ({disk.percent:.2f}% used)\n**RAM Total: **{ram.total / (2 ** 30):.2f} GiB\n**RAM Used: **{ram.used / (2 ** 30):.2f} GiB ({ram.percent:.2f}% used)\n\n**Downloaded: **{file_size_converter(Env.DOWNLOADED)}\n**Uploaded: **{file_size_converter(Env.UPLOADED)}"

    return final_msg

  async def store_user_info(user: 'pyrogram.types.User', lastPing: 'int', banned=False):
    user_record = await Env.MONGO.biltudas1bot.userList.find_one({'ID': user.id})

    if user_record is None:
      # Create a new user
      if user.last_name is None:
        name = user.first_name
      else:
        name = user.first_name + " " + user.last_name

      await Env.MONGO.biltudas1bot.userList.insert_one(
        {
          'ID': user.id,
          'Name': name,
          'firstPing': lastPing,
          'lastPing': lastPing,
          'banned': banned,
          'blocked': False,
          'topicID': None,
          'userInfoID': None
        }
      )
    else:
      # Update the existing user last Interaction time
      await Env.MONGO.biltudas1bot.userList.update_one({'ID': user.id}, {'$set': {'lastPing': lastPing}})

  @bot.on_message(filters.command(["start"]) & filters.private & filters.regex("^\/start$"))
  async def start_handler(client: pyrogram.client.Client, message: pyrogram.types.Message):
    spammer = False

    if str(message.from_user.id) in Env.ADMIN:
      await client.send_message(
        chat_id=message.from_user.id,
        text=f"Bot Online ✅"
      )
    else:
      if Env.COMBOT_ENABLED:
        # Check if the user is banned in Combot Feed
        combot_resp = httpx.get("https://api.cas.chat/check", params={'user_id': message.from_user.id})
        if combot_resp.status_code == 200:
          if json.loads(combot_resp.text)['ok']:
            spammer = True

      if Env.SPAMWATCH_TOKEN is not None:
        # Check if user is banned in SpamWatch Feed
        swatch_resp = httpx.get(f"https://api.spamwat.ch/banlist/{message.from_user.id}",
                                headers={'Authorization': f"Bearer {Env.SPAMWATCH_TOKEN}"})
        if swatch_resp.status_code == 200:  # When User is not a spammer, then SpamWatch returns 404 status code
          spammer = True

      if not spammer:
        await client.send_message(
          chat_id=message.from_user.id,
          text=f"Hello **{message.from_user.first_name}**!\nI'm an Assistant of **@{Env.OWNER_USERNAME}**, you can write me anything and I will forward it to the admins, Thanks."
        )
      else:
        await client.send_message(
          chat_id=message.from_user.id,
          text=f"Hello **{message.from_user.first_name}**!\nSorry, you don't have permission to use the bot."
        )

    # Store the data in database
    lastPing = dateutil.parser.parse(message.date.isoformat())
    await store_user_info(message.from_user, lastPing, banned=spammer)

  @bot.on_message(filters.group & pyrogram.filters.new_chat_members)
  async def start_group_handler(client: pyrogram.client.Client, message: pyrogram.types.Message):
    """
    Handler to handle operation when the bot joined in a group
    """
    for mem in message.new_chat_members:
      if mem.is_self:
        user = await client.get_chat_member(
          chat_id=message.chat.id,
          user_id="me"
        )
        invited_user = user.invited_by

        # Checks if the bot is admin
        if user.status is not pyrogram.enums.ChatMemberStatus.ADMINISTRATOR:
          # Send Warning message and leave the group
          try:
            await client.send_message(
              chat_id=message.chat.id,
              text=f"**Error:** __No Administrator Permission__"
            )
          except pyrogram.errors.exceptions.forbidden_403.ChatWriteForbidden:
            await client.send_message(
              chat_id=invited_user.id,
              text=f"**Error:** __No Administrator Permission__"
            )
          finally:
            await client.leave_chat(message.chat.id)
          return

        # Checks the Administrator Permissions
        permissions = []
        if not user.privileges.can_manage_chat:
          permissions.append("can_manage_chat")
        if not user.privileges.can_delete_messages:
          permissions.append("can_delete_messages")
        if not user.privileges.can_pin_messages:
          permissions.append("can_pin_messages")
        if not user.privileges.can_manage_topics:
          permissions.append("can_manage_topics")
        if not user.privileges.can_change_info:
          permissions.append("can_change_info")

        # If any permission of the above is not granted, then send warning
        if permissions:
          error_text = "**Error: Please Provide the following Permissions to make the bot work:**\n"

          for p in permissions:
            error_text += f"  -  `{p}`\n"

          if 'can_send_messages' in permissions:
            # Send message to invited user (in personal) if group doesn't allow the bot to send message on the group
            await client.send_message(
              chat_id=invited_user.id,
              text=error_text
            )
          else:
            await client.send_message(
              chat_id=message.chat.id,
              text=error_text
            )
          await client.leave_chat(message.chat.id)
          return

        # Send Instructions
        await client.send_message(
          chat_id=message.chat.id,
          text=f"Hello [{invited_user.first_name}](tg://user?id={invited_user.id})!\nNow follow the steps:\n1. Goto @BotFather and use /mybots command\n2. Choose **@{Env.BOT_USERNAME}** from the list\n3. Choose Bot Settings > Allow Groups?\n4. Turn the groups off"
        )

  @bot.on_chat_member_updated(filters.private)
  async def block_unblock(client: 'pyrogram.client.Client', chatmember: 'pyrogram.types.ChatMemberUpdated'):
    if chatmember.new_chat_member.status is pyrogram.enums.ChatMemberStatus.BANNED:
      # The bot is blocked by the user
      lastPing = dateutil.parser.parse(datetime.today().isoformat())
      await Env.MONGO.biltudas1bot.userList.update_one({'ID': chatmember.from_user.id},
                                                       {'$set': {'blocked': True, 'lastPing': lastPing}})
    else:
      # The bot is unblocked by the user
      await Env.MONGO.biltudas1bot.userList.update_one({'ID': chatmember.from_user.id}, {'$set': {'blocked': False}})

  @bot.on_message(filters.private & filters.command("help"))
  async def help_method(client: 'pyrogram.client.Client', message: 'pyrogram.types.Message'):
    if str(message.from_user.id) in Env.ADMIN:
      await client.send_message(
        chat_id=message.chat.id,
        text=Env.HELP_ADMIN_MESSAGE
      )
    else:
      await client.send_message(
        chat_id=message.chat.id,
        text=Env.HELP_USER_MESSAGE
      )

    # Store user info in database
    lastPing = dateutil.parser.parse(message.date.isoformat())
    await store_user_info(message.from_user, lastPing)

  @bot.on_message(filters.private & filters.command("id"))
  async def get_user_id(client: 'pyrogram.client.Client', message: 'pyrogram.types.Message'):
    await client.send_message(
      chat_id=message.chat.id,
      text=f"Your ChatID is: `{message.from_user.id}`"
    )

    # Store user info in database
    lastPing = dateutil.parser.parse(message.date.isoformat())
    await store_user_info(message.from_user, lastPing)

  @bot.on_message(filters.private & filters.command("modules") & filters.user([int(uid) for uid in Env.ADMIN]))
  async def module_settings(client: 'pyrogram.client.Client', message: 'pyrogram.types.Message'):
    modules = []
    rows = []
    items = 2
    for name, enabled in Env.MODULES.items():
      mod_name = (name + " ✅") if enabled else (name + " ❌")

      if items:
        items -= 1
        rows.append(
          types.InlineKeyboardButton(
            text=mod_name,
            callback_data="toggle_" + name
          )
        )
      else:
        items = 2
        modules.append(rows)
        rows = [
          types.InlineKeyboardButton(
            text=mod_name,
            callback_data="toggle_" + name
          )
        ]
    else:
      modules.append(rows)
      modules.append(
        [
          types.InlineKeyboardButton(
            text="Close",
            callback_data="delete_message"
          )
        ]
      )

    Env.CACHED_MODULE_OPTIONS = modules
    # Show user the modules
    await client.send_message(
      chat_id=message.chat.id,
      text="Available Modules:",
      reply_markup=types.InlineKeyboardMarkup(Env.CACHED_MODULE_OPTIONS)
    )

    # Store user info in database
    lastPing = dateutil.parser.parse(message.date.isoformat())
    await store_user_info(message.from_user, lastPing)

  @bot.on_message(filters.private & filters.command("version") & filters.user([int(uid) for uid in Env.ADMIN]))
  async def print_version(client: 'pyrogram.client.Client', message: 'pyrogram.types.Message'):
    with open('version', 'r') as v:
      version = v.read().replace("\n", "")

      await client.send_message(
        chat_id=message.from_user.id,
        reply_to_message_id=message.id,
        text=f"Bot Version: `{version}`"
      )

    # Store user info in database
    lastPing = dateutil.parser.parse(message.date.isoformat())
    await store_user_info(message.from_user, lastPing)

  @bot.on_message(filters.private & filters.command("stats") & filters.user([int(uid) for uid in Env.ADMIN]))
  async def print_stats(client: 'pyrogram.client.Client', message: 'pyrogram.types.Message'):
    server_info = await client.send_message(
      chat_id=message.chat.id,
      reply_to_message_id=message.id,
      text="__Gathering Information...__"
    )

    await asyncio.sleep(Env.REFRESH_TIME)
    msg_body = await collecting_machine_stats()

    # Send the stats to User
    await server_info.edit_text(
      text=msg_body,
      reply_markup=types.InlineKeyboardMarkup(
        [
          [
            types.InlineKeyboardButton(
              text="Refresh 🔄",
              callback_data="refresh_stats"
            )
          ],
          [
            types.InlineKeyboardButton(
              text="Close",
              callback_data="delete_message"
            )
          ]
        ]
      )
    )

  @bot.on_message(filters.private & filters.command("power") & filters.user([int(uid) for uid in Env.ADMIN]))
  async def power_handler(client: pyrogram.client.Client, message: pyrogram.types.Message):
    await client.send_message(
      chat_id=message.chat.id,
      text="Choose the Operation",
      reply_markup=types.InlineKeyboardMarkup(
        [
          [
            types.InlineKeyboardButton(
              text="Power Off ⛔",
              callback_data="power_off"
            )
          ],
          [
            types.InlineKeyboardButton(
              text="Restart 🔄",
              callback_data="power_reset"
            )
          ],
          [
            types.InlineKeyboardButton(
              text="Close",
              callback_data="delete_message"
            )
          ]
        ]
      )
    )

  @bot.on_message(filters.private & filters.command("set") & filters.user([int(uid) for uid in Env.ADMIN]))
  async def set_msg(client: pyrogram.client.Client, message: pyrogram.types.Message):
    try:
      text = str(message.text).split(" ", 1)[1]
    except IndexError:
      await client.send_message(
        chat_id=message.chat.id,
        reply_to_message_id=message.id,
        text="**Error: Please Provide a message body to save**"
      )
      return

    await Env.MONGO.biltudas1bot.feeds.insert_one({'text': text, 'seen': False})

    await client.send_message(
      chat_id=message.chat.id,
      reply_to_message_id=message.id,
      text="**Success: Message saved**"
    )

  @bot.on_message(filters.private & filters.command("feed") & filters.user([int(uid) for uid in Env.ADMIN]))
  async def feed_msg(client: pyrogram.client.Client, message: pyrogram.types.Message):
    msg = Env.MONGO.biltudas1bot.feeds.aggregate([{'$match': {'seen': False}}, {'$sample': {'size': 1}}])

    async for feed in msg:
      await client.send_message(
        chat_id=message.chat.id,
        reply_to_message_id=message.id,
        text=f"{feed['text']}"
      )

      await Env.MONGO.biltudas1bot.feeds.update_one(
        {'_id': feed['_id']},
        {'$set': {'seen': True}}
      )
      break
    else:
      await client.send_message(
        chat_id=message.chat.id,
        reply_to_message_id=message.id,
        text="**Feed is Empty**"
      )

  @bot.on_callback_query(filters.regex("^refresh_stats$"))
  async def refresh_stats_machine(client: pyrogram.client.Client, callback_query: pyrogram.types.CallbackQuery):
    if str(callback_query.from_user.id) in Env.ADMIN:
      await callback_query.message.edit_text(
        text="__Gathering Information...__"
      )

      await asyncio.sleep(Env.REFRESH_TIME)
      msg_body = await collecting_machine_stats()

      await callback_query.message.edit_text(
        text=msg_body,
        reply_markup=types.InlineKeyboardMarkup(
          [
            [
              types.InlineKeyboardButton(
                text="Refresh 🔄",
                callback_data="refresh_stats"
              )
            ],
            [
              types.InlineKeyboardButton(
                text="Close",
                callback_data="delete_message"
              )
            ]
          ]
        )
      )

  @bot.on_callback_query(filters.regex("^(delete_message|toggle_[A-Z0-9_]+)$"))
  async def update_module_settings(client: 'pyrogram.client.Client', callback_query: 'pyrogram.types.CallbackQuery'):
    if str(callback_query.from_user.id) in Env.ADMIN:
      if callback_query.data[:7] == "toggle_":
        module_name = callback_query.data[7:]

        # Updating Module Option
        for col, lst in enumerate(Env.CACHED_MODULE_OPTIONS):
          for row, module in enumerate(lst):
            if module_name in module.text:
              Env.MODULES[module_name] = not Env.MODULES[module_name]
              await Env.MONGO.biltudas1bot.settings.update_one({}, {'$set': {'loadModules': Env.MODULES}})
              mod_new_name = (module_name + " ✅") if Env.MODULES[module_name] else (module_name + " ❌")

              Env.CACHED_MODULE_OPTIONS[col][row] = types.InlineKeyboardButton(
                text=mod_new_name,
                callback_data="toggle_" + module_name
              )
              break
          else:
            continue
          break

        # Adding Restart bot button and Remove the Cancel button
        Env.CACHED_MODULE_OPTIONS.pop()
        Env.CACHED_MODULE_OPTIONS.append(
          [
            types.InlineKeyboardButton(
              text="Restart bot 🔄",
              callback_data="power_reset"
            )
          ]
        )

        # Edit Reply Markup
        await client.edit_message_reply_markup(
          chat_id=callback_query.from_user.id,
          message_id=callback_query.message.id,
          reply_markup=types.InlineKeyboardMarkup(Env.CACHED_MODULE_OPTIONS)
        )

      elif callback_query.data == "delete_message":
        await client.delete_messages(
          chat_id=callback_query.from_user.id,
          message_ids=callback_query.message.id
        )

  @bot.on_callback_query(filters.regex("^power_off$"))
  async def shutdown_bot(client: pyrogram.client.Client, callback_query: pyrogram.types.CallbackQuery):
    if str(callback_query.from_user.id) in Env.ADMIN:
      await client.answer_callback_query(
        callback_query_id=callback_query.id,
        text="The bot is shutting down, Please check the server Console Panel for more information.",
        show_alert=True
      )
      await client.delete_messages(
        chat_id=callback_query.from_user.id,
        message_ids=callback_query.message.id
      )

      os.kill(os.getpid(), signal.SIGINT)

  @bot.on_callback_query(filters.regex("^power_reset$"))
  async def restart_bot(client: 'pyrogram.client.Client', callback_query: 'pyrogram.types.CallbackQuery'):
    if str(callback_query.from_user.id) in Env.ADMIN:
      await Env.MONGO.biltudas1bot.settings.update_one({}, {
        '$set': {'restarted': True, 'restarted_by': int(callback_query.from_user.id)}})
      await client.answer_callback_query(
        callback_query_id=callback_query.id,
        text="The bot is currently restarting. Please wait a moment. It will be back online shortly.",
        show_alert=True
      )
      await client.delete_messages(
        chat_id=callback_query.from_user.id,
        message_ids=callback_query.message.id
      )

      # Set the Process Terminate Flag
      with open('main.lock', 'w') as flag:
        flag.write("")

      os.kill(os.getpid(), signal.SIGINT)

  # Loading Modules
  settings = await Env.MONGO.biltudas1bot.settings.find_one({}, {'_id': False})
  if settings:
    Env.MODULES = settings['loadModules']
    with open('modules.json', 'r') as mod_list:
      load = set(json.load(mod_list)["modules"])

      # Removing any module from the list which is not into modules.json
      for mod in tuple(Env.MODULES.keys()):
        if mod.lower() not in load:
          del Env.MODULES[mod]

      # Adding new modules to the Environment
      for mod in load:
        if mod.upper() not in Env.MODULES:
          Env.MODULES[mod.upper()] = False  # By default new third party modules are not loaded

    await Env.MONGO.biltudas1bot.settings.update_one({}, {'$set': {'loadModules': Env.MODULES}})
  else:
    Env.MODULES = {}
    with open('modules.json', 'r') as mod_list:
      for mod in list(json.load(mod_list)["modules"]):
        Env.MODULES[mod.upper()] = True

    await Env.MONGO.biltudas1bot.settings.insert_one({'loadModules': Env.MODULES})

  # Enable Global Lock
  if settings is None or not 'global_lock' in settings or not settings['global_lock']:
    await Env.MONGO.biltudas1bot.settings.update_one({}, {'$set': {'global_lock': True}})
  else:
    if not os.path.exists('suspend.lock'):
      return "TERMINATE"
    else:
      os.remove('suspend.lock')

  # Set Restart flag accordingly
  if settings and 'restarted' in settings:
    if settings['restarted']:
      Env.RESTARTED = settings['restarted']
      Env.RESTARTED_BY_USER = int(settings['restarted_by'])
    else:
      Env.RESTARTED = False
      Env.RESTARTED_BY_USER = None

    if not settings['restarted'] == False or not settings['restarted_by'] is None:
      await Env.MONGO.biltudas1bot.settings.update_one({}, {
        '$set': {'restarted': False, 'restarted_by': None}})  # Reset Restart data in database
  else:
    Env.RESTARTED = False
    Env.RESTARTED_BY_USER = None
    await Env.MONGO.biltudas1bot.settings.update_one({}, {
      '$set': {'restarted': False, 'restarted_by': None}})  # Reset Restart data in database

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
          help_str_user += f"/{cmd} - {comment}\n"
        else:
          help_str_user += f"/{cmd} - {comment}"
          help_str_user += "\n\nIf you want to Contact the Admin then write 'Hi' or 'Hello' and then drop your question, your message will be forwarded to the Admins."

      # Not adding new line to the last command available into the JSON
      if (total_commands - 1) == pos:
        help_str += f"/{cmd} - {comment}"
      else:
        help_str += f"/{cmd} - {comment}\n"

    Env.HELP_ADMIN_MESSAGE += help_str
    Env.HELP_USER_MESSAGE += help_str_user

  # Loading Stats
  stats = await Env.MONGO.biltudas1bot.botstats.find_one({}, {'_id': False})
  if stats:
    if 'downloaded' in stats:
      Env.DOWNLOADED = stats['downloaded']

    if 'uploaded' in stats:
      Env.UPLOADED = stats['uploaded']
  else:
    await Env.MONGO.biltudas1bot.botstats.insert_one(
      {
        'downloaded': 0,
        'uploaded': 0
      }
    )
