import asyncio
import pyrogram
import dateutil
from bidict import bidict
from pyrogram import filters

async def personal_message(bot: pyrogram.client.Client, Env):
  """
  Function to enable functionality of user to user direct message bot
  """
  @bot.on_message(filters.private & filters.create(lambda a, b, msg: str(msg.from_user.id) not in Env.ADMIN))
  async def user_message_handler(client: pyrogram.client.Client, message: pyrogram.types.Message):
    user_details = await Env.MONGO.biltudas1bot.userList.find_one({'ID': message.chat.id}, {'_id': False})
    # If user data is not available
    if user_details is None:
      await client.send_message(
        chat_id = message.chat.id,
        text = "Something Went Wrong, Please use /start again"
      )
      return

    if user_details["banned"]:
      return

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
      reply_message = None

    else:
      if message.reply_to_message_id:
        try:
          reply_message = int(user_details["messageIDList"][str(message.reply_to_message_id)])
        except KeyError:
          reply_message = None
      else:
        reply_message = None

    # If topicID exist then send message to that topicID
    if message.forward_date is None:
      forward_msg = await client.copy_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = int(topicID),
        from_chat_id = message.chat.id,
        reply_to_message_id = reply_message,
        message_id = message.id
      )
    else:
      forward_msg = await client.forward_messages(
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

    # Store data in Database
    lastPing = dateutil.parser.parse(message.date.isoformat())
    if user_details["topicID"] is None:
      await Env.MONGO.biltudas1bot.userList.update_one(
        {'ID': message.chat.id}, 
        {'$set': {
          'topicID': topicID, 
          'userInfoID': userInfoID, 
          'lastPing': lastPing,
          'messageIDList': {
              str(message.id): str(forward_msg.id)
            }
          }
        }
      )
    else:
      await Env.MONGO.biltudas1bot.userList.update_one(
        {'ID': message.chat.id}, 
        {'$set': {
          'lastPing': lastPing,
          f'messageIDList.{message.id}': str(forward_msg.id)
          }
        }
      )

    # Delete Ackowledgement Message (After 5 seconds)
    await asyncio.sleep(5)
    await client.delete_messages(
      chat_id = message.chat.id,
      message_ids = ack.id
    )


  @bot.on_message(filters.group & filters.chat(int(Env.GROUP_ID)) & filters.create(lambda a, b, msg: str(msg.from_user.id) in Env.ADMIN))
  async def admin_message_handler(client: pyrogram.client.Client, message: pyrogram.types.Message):
    user_details = await Env.MONGO.biltudas1bot.userList.find_one({'topicID': message.message_thread_id}, {'_id': False})

    if user_details is None:
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = "**Error: User record not found, Please make sure that the user started the bot before.**"
      )
      return

    # If not General Topic
    if message.message_thread_id != 1:
      if user_details["blocked"]:
        await client.send_message(
          chat_id = int(Env.GROUP_ID),
          message_thread_id = message.message_thread_id,
          reply_to_message_id = message.id,
          text = f"**Error: User blocked the bot, so Sending Message is not Possible.**"
        )
        return
        
      topicID = message.message_thread_id
      uid = user_details["ID"]

      if message.reply_to_message_id:
        try:
          reply_message = int(bidict(user_details["messageIDList"]).inverse[str(message.reply_to_message_id)])
        except KeyError:
          reply_message = None
      else:
        reply_message = None

      # Copy/Forward the message to the user
      if message.forward_date is None:
        forward_msg_user = await client.copy_message(
          chat_id = int(uid),
          message_thread_id = int(topicID),
          from_chat_id = message.chat.id,
          reply_to_message_id = reply_message,
          message_id = message.id
        )
      else:
        forward_msg_user = await client.forward_messages(
          chat_id = int(uid),
          message_thread_id = int(topicID),
          from_chat_id = message.chat.id,
          message_ids = message.id
        )

      # Store lastPing time to database
      lastPing = dateutil.parser.parse(message.date.isoformat())
      await Env.MONGO.biltudas1bot.userList.update_one({'ID': message.from_user.id}, {'$set': {'lastPing': lastPing}})
      await Env.MONGO.biltudas1bot.userList.update_one(
        {'topicID': message.message_thread_id}, 
        {
          '$set': {
            f'messageIDList.{forward_msg_user.id}': str(message.id)
          }
        }
      )


  @bot.on_edited_message(filters.private & filters.create(lambda a, b, msg: str(msg.from_user.id) not in Env.ADMIN))
  async def user_edited_message_handler(client: pyrogram.client.Client, message: pyrogram.types.Message):
    user_details = await Env.MONGO.biltudas1bot.userList.find_one({'ID': message.chat.id}, {'_id': False})
    # If user data is not available
    if user_details is None:
      await client.send_message(
        chat_id = message.chat.id,
        text = "Something Went Wrong, Please use /start again"
      )
      return

    if user_details["banned"]:
      return

    if user_details["topicID"] is None:
      return

    # Edit message on the Admin Side
    forward_msg_id = int(user_details["messageIDList"][str(message.id)])
    await client.edit_message_text(
      chat_id = int(Env.GROUP_ID),
      message_id = forward_msg_id,
      text = message.text
    )

    # Store data in database
    lastPing = dateutil.parser.parse(message.date.isoformat())
    await Env.MONGO.biltudas1bot.userList.update_one({'ID': message.chat.id}, {'$set': {'lastPing': lastPing}})


  @bot.on_edited_message(filters.group & filters.chat(int(Env.GROUP_ID)) & filters.create(lambda a, b, msg: str(msg.from_user.id) in Env.ADMIN))
  async def admin_edited_message_hander(client: pyrogram.client.Client, message: pyrogram.types.Message):
    user_details = await Env.MONGO.biltudas1bot.userList.find_one({'topicID': message.message_thread_id}, {'_id': False})

    if user_details is None:
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = "**Error: User record not found, Please make sure that the user started the bot before.**"
      )
      return

        # If not General Topic
    if message.message_thread_id != 1:
      if user_details["blocked"]:
        await client.send_message(
          chat_id = int(Env.GROUP_ID),
          message_thread_id = message.message_thread_id,
          reply_to_message_id = message.id,
          text = f"**Error: User blocked the bot, so Sending Message is not Possible.**"
        )
        return
        
      topicID = message.message_thread_id
      uid = user_details["ID"]

      # Edit message on the User Side
      forward_msg_id = int(bidict(user_details["messageIDList"]).inverse[str(message.id)])
      await client.edit_message_text(
        chat_id = int(uid),
        message_id = forward_msg_id,
        text = message.text
      )

      # Store lastPing time to database
      lastPing = dateutil.parser.parse(message.date.isoformat())
      await Env.MONGO.biltudas1bot.userList.update_one({'ID': message.from_user.id}, {'$set': {'lastPing': lastPing}})
