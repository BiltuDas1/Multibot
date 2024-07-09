import re
import pyrogram
from pyrogram import filters


async def save_restricted_content(bot: pyrogram.client.Client, account: pyrogram.client.Client, Env):
  @bot.on_message(filters.command("join") & filters.group & filters.chat(int(Env.GROUP_ID)) & filters.create(lambda a, b, msg: msg.message_thread_id == 1) & filters.create(lambda a, b, msg: str(msg.from_user.id) in Env.ADMIN))
  async def join_chat(client: pyrogram.client.Client, message: pyrogram.types.Message):
    url = str(message.text).split(" ", 1)[1]
    # If valid URL
    if re.match("^(https|http):\/\/(t.me|telegram.me)\/.+$", url):
      # Check If Private Link
      if re.match("^(https|http):\/\/(t.me|telegram.me)\/\+.+$", url):
        try: 
          await account.join_chat(url)
          await client.send_message(int(Env.GROUP_ID), "**Chat Joined**", message_thread_id = message.message_thread_id, reply_to_message_id=message.id)
        except UserAlreadyParticipant:
          await client.send_message(int(Env.GROUP_ID), "**Chat already Joined**", message_thread_id = message.message_thread_id, reply_to_message_id=message.id)
        except InviteHashExpired:
          await client.send_message(int(Env.GROUP_ID), "**Invalid invitation Link**", message_thread_id = message.message_thread_id, reply_to_message_id=message.id)
        except Exception as e:
          await client.send_message(int(Env.GROUP_ID), f"**Error** : __{e}__", reply_to_message_id=message.id)
      else:
        await client.send_message(
          chat_id = int(Env.GROUP_ID),
          message_thread_id = message.message_thread_id,
          reply_to_message_id = message.id,
          text = "**Error: Joining into Public Chats are not required**"
        )
    else:
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = "**Error: Invalid Chat Joining Link**"
      )


  @bot.on_message(filters.command("save") & filters.group & filters.chat(int(Env.GROUP_ID)) & filters.create(lambda a, b, msg: msg.message_thread_id == 1) & filters.create(lambda a, b, msg: str(msg.from_user.id) in Env.ADMIN))
  async def save_content(client: pyrogram.client.Client, message: pyrogram.types.Message):
    pass