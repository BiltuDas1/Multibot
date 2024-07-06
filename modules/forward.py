import asyncio
import pyrogram
import dateutil
from pyrogram import filters

async def personal_message(bot: pyrogram.client.Client, Env):
  """
  Function to enable functionality of user to user direct message bot
  """
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

    # Store the data in database
    lastPing = dateutil.parser.parse(message.date.isoformat())
    user = await Env.MONGO.biltudas1bot.userList.find_one({'ID': message.chat.id})

    if user is None:
      # Create a new user
      if message.chat.last_name is None:
        name = message.chat.first_name
      else:
        name = message.chat.first_name + " " + message.chat.last_name

      await Env.MONGO.biltudas1bot.userList.insert_one(
        {
          'ID': message.chat.id,
          'Name': name,
          'firstPing': lastPing,
          'lastPing': lastPing,
          'banned': False,
          'blocked': False,
          'topicID': None,
          'userInfoID': None
        }
      )
    else:
      # Update the existing user Interaction time
      await Env.MONGO.biltudas1bot.userList.update_one({'ID': message.chat.id}, {'$set': {'lastPing': lastPing}})


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


  @bot.on_message(filters.private)
  async def handle_private(client: pyrogram.client.Client, message: pyrogram.types.Message):
    if str(message.chat.id) not in Env.ADMIN:
      user_details = await Env.MONGO.biltudas1bot.userList.find_one({'ID': message.chat.id}, {'_id': False})
      topicID = user_details["topicID"]
      userInfoID = user_details["userInfoID"]

      if topicID is None:
        # Full Name
        if message.from_user.last_name is None:
          name = message.from_user.first_name
        else:
          name = message.from_user.first_name + " " + message.from_user.last_name

        # Create a new topic
        thread = await client.create_forum_topic(
          chat_id = int(Env.GROUP_ID),
          title = name
        )

        # Get DataCenter
        if message.from_user.dc_id is None:
          dc = "N/A"
        else:
          dc = f"DC{message.from_user.dc_id}"

        # If Premium User
        if message.from_user.is_premium:
          user_type = "Premium User"
        else:
          user_type = "Regular User"

        # Store user info in topic
        user_info = await client.send_message(
          chat_id = int(Env.GROUP_ID),
          message_thread_id = thread.id,
          text = f"Name: {name}\nUserID: `{message.from_user.id}`\nLanguage: {message.from_user.language_code}\nDataCenter: {dc}\nUser Type: {user_type}\nProfile Permalink: tg://user?id={message.from_user.id}"
        )

        topicID = thread.id
        userInfoID = user_info.message_thread_id

      # If topicID exist then send message to that topicID
      if message.forward_date is None:
        await client.copy_message(
          chat_id = int(Env.GROUP_ID),
          message_thread_id = int(topicID),
          from_chat_id = message.chat.id,
          message_id = message.id
        )
      else:
        await client.forward_messages(
          chat_id = int(Env.GROUP_ID),
          message_thread_id = int(topicID),
          from_chat_id = message.chat.id,
          message_ids = message.id
        )

      # Send Acknowledgement Message to user
      ack = await client.send_message(
        chat_id = message.chat.id,
        text = "Message Sended ✅"
      )

      # Delete Ackowledgement Message (After 5 seconds)
      await asyncio.sleep(5)
      await client.delete_messages(
        chat_id = message.chat.id,
        message_ids = ack.id
      )

      # Store data in Database
      lastPing = dateutil.parser.parse(message.date.isoformat())
      if user_details["topicID"] is None:
        await Env.MONGO.biltudas1bot.userList.update_one({'ID': message.chat.id}, {'$set': {'topicID': topicID, 'userInfoID': userInfoID, 'lastPing': lastPing}})
      else:
        await Env.MONGO.biltudas1bot.userList.update_one({'ID': message.chat.id}, {'$set': {'lastPing': lastPing}})

