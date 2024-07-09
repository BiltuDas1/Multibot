import asyncio
import pyrogram
import dateutil
from bidict import bidict
from pyrogram import filters

async def personal_message(bot: pyrogram.client.Client, Env):
  """
  Function to enable functionality of user to user direct message bot
  """
  @bot.on_message(filters.private)
  async def user_message_handler(client: pyrogram.client.Client, message: pyrogram.types.Message):
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
        reply_message = None

      else:
        if message.reply_to_message_id:
          try:
            reply_message = user_details["messageIDList"][str(message.reply_to_message_id)]
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
                message.id: forward_msg.id
              }
            }
          }
        )
      else:
        await Env.MONGO.biltudas1bot.userList.update_one(
          {'ID': message.chat.id}, 
          {'$set': {
            'lastPing': lastPing,
            f'messageIDList.{message.id}': forward_msg.id
            }
          }
        )

      # Delete Ackowledgement Message (After 5 seconds)
      await asyncio.sleep(5)
      await client.delete_messages(
        chat_id = message.chat.id,
        message_ids = ack.id
      )


  @bot.on_message(filters.group & filters.chat(int(Env.GROUP_ID)))
  async def admin_message_handler(client: pyrogram.client.Client, message: pyrogram.types.Message):
    if str(message.from_user.id) in Env.ADMIN:
      user_details = await Env.MONGO.biltudas1bot.userList.find_one({'topicID': message.message_thread_id}, {'_id': False})

      # If not General Topic
      if message.message_thread_id != 1:
        if user_details is None:
          client.send_message(
            chat_id = message.chat.id,
            message_thread_id = int(topicID),
            reply_to_message_id = message.id,
            text = f"**Error: User record not found, Please make sure that the user started the bot before.**"
          )
          return
          
        topicID = message.message_thread_id
        uid = user_details["ID"]

        if message.reply_to_message_id:
          try:
            reply_message = int(bidict(user_details["messageIDList"]).inverse[message.reply_to_message_id])
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
              f'messageIDList.{forward_msg_user.id}': message.id
            }
          }
        )

      else:
        # If General Topic
        pass