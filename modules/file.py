import pyrogram
import secrets
import asyncio
from apis import environment
from pyrogram import filters


async def execute(bot: pyrogram.client.Client, account: pyrogram.client.Client, Env: environment.Environment):
  """
  Function to enable Send message functionality
  """
  @bot.on_message(filters.command("store") & filters.group & filters.chat(int(Env.GROUP_ID)) & filters.create(lambda a, b, msg: msg.message_thread_id == 1) & filters.create(lambda a, b, msg: str(msg.from_user.id) in Env.ADMIN))
  async def handle_bot_file_msg(client: pyrogram.client.Client, message: pyrogram.types.Message):
    if not Env.DUMP_CHAT:
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = "**Error: DUMP_CHAT is not set, Please set DUMP_CHAT Environment in your server and then restart the bot**"
      )
      return

    if not message.reply_to_message:
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = "**Please Reply a message to save**"
      )
      return

    # Copy the replied Message to DUMP_CHAT
    msg = await client.copy_message(
      chat_id = int(Env.DUMP_CHAT),
      from_chat_id = int(Env.GROUP_ID),
      message_id = message.reply_to_message.id
    )

    if msg:
      TOKEN = secrets.token_urlsafe()
      await Env.MONGO.biltudas1bot.savedMsgs.insert_one({'TOKEN': TOKEN, 'message_id': msg.id})

      # Show the final URL to the User
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = f"https://t.me/{Env.BOT_USERNAME}?start={TOKEN}"
      )
    else:
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = f"**Error: Unable to copy the message, Please forward the source message into this chat and try again**"
      )


  @bot.on_message(filters.command(["start"]) & filters.private & filters.regex("^\/start [\w-]+$"))
  async def handle_bot_url(client: pyrogram.client.Client, message: pyrogram.types.Message):
    TOKEN = message.text.split(" ", 1)[1]
    savedMsg = await Env.MONGO.biltudas1bot.savedMsgs.find_one({'TOKEN': TOKEN}, {'_id': False})

    if not savedMsg:
      await client.send_message(
        chat_id = message.chat.id,
        reply_to_message_id = message.id,
        text = "**Invalid URL, Please ask for the sender to send the valid URL**"
      )
      return

    # Send message to the user
    msg = await client.copy_message(
      chat_id = message.chat.id,
      from_chat_id = int(Env.DUMP_CHAT),
      message_id = savedMsg['message_id'],
      reply_to_message_id = message.id,
      protect_content = True
    )

    # Delete message after 60 seconds
    await asyncio.sleep(60)
    await msg.delete()
