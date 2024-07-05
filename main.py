import asyncio
from apis import Env, account, bot
import pyrogram
from pyrogram import filters


@bot.on_message(filters.command(["start"]) & filters.private)
async def start_handler(client: pyrogram.client.Client, message: pyrogram.types.Message):
  if str(message.from_user.id) in Env.ADMIN:
    await client.send_message(
      chat_id = message.from_user.id,
      text = f"Bot Online ✅"
    )
  else:
    await client.send_message(
      chat_id = message.from_user.id,
      text = f"Hello **{message.from_user.first_name}**!\nI'm an Assistant of **@{Env.OWNER_USERNAME}**, you can write me anything and I will forward it to the admins, Thanks."
    )


@bot.on_message(filters.group & pyrogram.filters.new_chat_members)
async def start_group_handler(client: pyrogram.client.Client, message: pyrogram.types.Message):
  """
  Handler to handle operation when the bot joined in a group
  """
  for mem in message.new_chat_members:
    if mem.is_self:
      user = await client.get_chat_member(
        chat_id = message.chat.id,
        user_id = "me"
      )
      invited_user = user.invited_by

      # Checks if the bot is admin
      if user.status is not pyrogram.enums.ChatMemberStatus.ADMINISTRATOR:
        # Send Warning message and leave the group
        try:
          await client.send_message(
            chat_id = message.chat.id,
            text = f"**Error:** __No Administrator Permission__"
          )
        except pyrogram.errors.exceptions.forbidden_403.ChatWriteForbidden:
          await client.send_message(
            chat_id = invited_user.id,
            text = f"**Error:** __No Administrator Permission__"
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
            chat_id = invited_user.id,
            text = error_text
          )
        else:
          await client.send_message(
            chat_id = message.chat.id,
            text = error_text
          )
        await client.leave_chat(message.chat.id)
        return

      # Send Instructions
      await client.send_message(
        chat_id = message.chat.id,
        text = f"Hello [{invited_user.first_name}](tg://user?id={invited_user.id})!\nNow follow the steps:\n1. Goto @BotFather and use /mybots command\n2. Choose **@{Env.BOT_USERNAME}** from the list\n3. Choose Bot Settings > Allow Groups?\n4. Turn the groups off"
      )


# Starts the bot
if __name__ == "__main__":
  bot.start()
  print("Bot Started...")

  Env.BOT_USERNAME = bot.get_me().username
  pyrogram.idle() # Holds the Console for Infinite Period

  bot.stop()
  account.stop()