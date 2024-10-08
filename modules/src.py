import re
import pyrogram
import secrets
import asyncio
import os
import queue
import time
from pyrogram import filters


async def execute(bot: pyrogram.client.Client, account: pyrogram.client.Client, Env):

  async def get_file_size(message: pyrogram.types.Message) -> int:
    """
    Getting attached file size from a message
    Returns size in bytes
    """
    msg_type = await get_message_type(message)
    size = 0

    match msg_type:
      case "Document":
        size = message.document.file_size
      case "Video":
        size = message.video.file_size
      case "Animation":
        size = message.animation.file_size
      case "Sticker":
        size = message.sticker.file_size
      case "Voice":
        size = message.voice.file_size
      case "Audio":
        size = message.audio.file_size
      case "Photo":
        size = message.photo.file_size

    return size


  async def downloading_file(downloadable_msg: pyrogram.types.Message, message: pyrogram.types.Message, by_user: int) -> tuple[str, str]:
    """
    Function to Handle downloading file
    When a file is downloaded Successfully, then this function returns a tuple of (current_download_path, actual_download_path)
    If any exception occurs(including download failed) then this function returns None
    """
    stat = {
      "old_file_size": 0,
      "last_chunk_download_time": 0,
      "total_time": 0,
      "start_time_download": 0
    }

    async def progress(current_file_size: int, total_file_size: int, stat: dict):
      """
      Function to show Download Progress Bar to the User
      """
      active_block = "█"
      inactive_block = "▒"
      progress_bar_width = 15
      percentage = current_file_size * 100 / total_file_size

      try:
        # If the userID is not into the Active user list then stop the downloading
        if by_user not in Env.ACTIVE_USERS:
          await message.delete()
          await bot.stop_transmission()
          return

        # Calculate ETA and processing Speed
        stat['total_time'] = int(int(time.time()) - stat['start_time_download'])
        eta, process_speed = eta_calculate(
          current_file_size, 
          total_file_size, 
          stat["old_file_size"], 
          stat['total_time'] - stat["last_chunk_download_time"]
        )

        if eta != -1:
          if eta >= 60:
            eta_time = f"{eta//60} minutes {eta%60} seconds"
          else:
            eta_time = f"{eta} seconds"
        else:
          eta_time = "∞"

        # Calculate Elapse Time
        stat["old_file_size"] = current_file_size
        stat["last_chunk_download_time"] = stat['total_time']

        if stat['total_time'] >= 60:
          elapse_time = f"{stat['total_time']//60} minutes {stat['total_time']%60} seconds"
        else:
          elapse_time = f"{stat['total_time']} seconds"

        # File Size
        current_fs = file_size_converter(current_file_size)
        total_fs = file_size_converter(total_file_size)
        size_msg = f"{current_fs} out of {total_fs}"

        # Progress bar
        processed = int((progress_bar_width / 100) * percentage)
        remaining = progress_bar_width - processed
        progress_bar = (active_block * processed) + (inactive_block * remaining)

        # Update message
        msg_txt = f"**Downloading**: {percentage:.2f}% of 100%\n\n {progress_bar} \n\n**Size**: {size_msg}\n\n**Speed**: {process_speed}\n\n**ETA**: {eta_time}\n\n**Elapse Time**: {elapse_time}"
        await message.edit_text(
          text = msg_txt,
          reply_markup = pyrogram.types.InlineKeyboardMarkup(
            [[
                pyrogram.types.InlineKeyboardButton(
                  text = "Cancel",
                  callback_data = f"cancel_task_{by_user}"
                )
            ]]
          )
        )
        await asyncio.sleep(Env.REFRESH_TIME)
      except Exception:
        await asyncio.sleep(Env.REFRESH_TIME)



    # Downloading Task
    while True:
      try:
        stat["start_time_download"] = int(time.time())
        # Downloading file
        downloaded_path: str = await downloadable_msg.download(
          progress = progress,
          progress_args = [stat]
        )

      except pyrogram.errors.FloodWait as fw:
        print(f"[FLOOD_WAIT_X] Wait for {fw.value} Seconds")
        await asyncio.sleep(fw.value)

      except Exception as e:
        await message.edit_text(
          text = f"**Error:** __{e}__"
        )
        return None

      else:
        # Rename the file to something other than the original file to prevent ambiguity
        if not os.path.exists(downloaded_path):
          return ()

        rand_id = secrets.token_hex(32)
        new_location = f"{os.path.dirname(downloaded_path)}/{rand_id}"
        os.rename(downloaded_path, new_location)
        return (new_location, downloaded_path)


  async def uploading_file(msg_type: str, msg: pyrogram.types.Message, message: pyrogram.types.Message, file_path: str, encoded_file_path: str, smsg: pyrogram.types.Message, by_user: int):
    """
    Function to Handle uploading files
    """
    stat = {
      "old_file_size": 0,
      "last_chunk_download_time": 0,
      "total_time": 0,
      "start_time_download": 0
    }

    async def progress(current_file_size: int, total_file_size: int, stat: dict):
      """
      Function to show Upload Progress Bar to the User
      """
      active_block = "█"
      inactive_block = "▒"
      progress_bar_width = 15
      percentage = current_file_size * 100 / total_file_size

      try:
        # If the userID is not into the Active user list then stop the uploading
        if by_user not in Env.ACTIVE_USERS:
          await smsg.delete()
          await bot.stop_transmission()
          return

        # Calculate ETA and processing Speed
        stat['total_time'] = int(int(time.time()) - stat['start_time_download'])
        eta, process_speed = eta_calculate(
          current_file_size, 
          total_file_size, 
          stat["old_file_size"],
          stat['total_time'] - stat["last_chunk_download_time"]
        )

        if eta != -1:
          if eta >= 60:
            eta_time = f"{eta//60} minutes {eta%60} seconds"
          else:
            eta_time = f"{eta} seconds"
        else:
          eta_time = "∞"

        # Calculate Elapse Time 
        stat["old_file_size"] = current_file_size
        stat["last_chunk_download_time"] = stat['total_time']

        if stat['total_time'] >= 60:
          elapse_time = f"{stat['total_time']//60} minutes {stat['total_time']%60} seconds"
        else:
          elapse_time = f"{stat['total_time']} seconds"

        # File Size
        current_fs = file_size_converter(current_file_size)
        total_fs = file_size_converter(total_file_size)
        size_msg = f"{current_fs} out of {total_fs}"

        # Progress bar
        processed = int((progress_bar_width / 100) * percentage)
        remaining = progress_bar_width - processed
        progress_bar = (active_block * processed) + (inactive_block * remaining)

        # Update message
        msg_txt = f"**Uploading**: {percentage:.2f}% of 100%\n\n {progress_bar} \n\n**Size**: {size_msg}\n\n**Speed**: {process_speed}\n\n**ETA**: {eta_time}\n\n**Elapse Time**: {elapse_time}"
        await smsg.edit_text(
          text = msg_txt
        )
        await asyncio.sleep(Env.REFRESH_TIME)
      except Exception:
        await asyncio.sleep(Env.REFRESH_TIME)
    

    # Rename the file
    os.rename(encoded_file_path, file_path)

    while True:
      try:
        stat["start_time_download"] = int(time.time())
        if "Document" == msg_type:
          try:
            thumb = await account.download_media(msg.document.thumbs[0].file_id)
          except:
            thumb = None

          if Env.DUMP_CHAT:
            output_msg = await bot.send_document(
              chat_id = int(Env.DUMP_CHAT),
              document = file_path,
              thumb = thumb,
              caption = msg.caption,
              caption_entities = msg.caption_entities,
              progress = progress,
              progress_args = [stat]
            )
          else:
            output_msg = await bot.send_document(
              chat_id = int(Env.GROUP_ID),
              message_thread_id = message.message_thread_id,
              reply_to_message_id = message.id,
              document = file_path,
              thumb = thumb,
              caption = msg.caption,
              caption_entities = msg.caption_entities,
              progress = progress,
              progress_args = [stat]
            )

          if thumb is not None:
            os.remove(thumb)

        elif "Video" == msg_type:
          try:
            thumb = await account.download_media(msg.video.thumbs[0].file_id)
          except:
            thumb = None

          if Env.DUMP_CHAT:
            output_msg = await bot.send_video(
              chat_id = int(Env.DUMP_CHAT),
              video = file_path,
              duration = msg.video.duration,
              width = msg.video.width,
              height = msg.video.height,
              thumb = thumb,
              caption = msg.caption,
              caption_entities = msg.caption_entities,
              progress = progress,
              progress_args = [stat]
            )
          else:
            output_msg = await bot.send_video(
              chat_id = int(Env.GROUP_ID),
              message_thread_id = message.message_thread_id,
              reply_to_message_id = message.id,
              video = file_path,
              duration = msg.video.duration,
              width = msg.video.width,
              height = msg.video.height,
              thumb = thumb,
              caption = msg.caption,
              caption_entities = msg.caption_entities,
              progress = progress,
              progress_args = [stat]
            )
            
          if thumb is not None: 
            os.remove(thumb)

        elif "Animation" == msg_type:
          if Env.DUMP_CHAT:
            output_msg = await bot.send_animation(int(Env.DUMP_CHAT), file_path)
          else:
            output_msg = await bot.send_animation(
              chat_id = int(Env.GROUP_ID),
              message_thread_id = message.message_thread_id,
              reply_to_message_id = message.id,
              animation = file_path
            )

        elif "Sticker" == msg_type:
          if Env.DUMP_CHAT:
            output_msg = await bot.send_sticker(int(Env.DUMP_CHAT), file_path)
          else:
            output_msg = await bot.send_sticker(
              chat_id = int(Env.GROUP_ID),
              message_thread_id = message.message_thread_id,
              reply_to_message_id = message.id,
              sticker = file_path
            )

        elif "Voice" == msg_type:
          if Env.DUMP_CHAT:
            output_msg = await bot.send_voice(
              chat_id = int(Env.DUMP_CHAT),
              voice = file_path,
              caption = msg.caption,
              thumb = thumb,
              caption_entities = msg.caption_entities,
              progress = progress,
              progress_args = [stat]
            )
          else:
            output_msg = await bot.send_voice(
              chat_id = int(Env.GROUP_ID),
              message_thread_id = message.message_thread_id,
              reply_to_message_id = message.id,
              voice = file_path,
              caption = msg.caption,
              thumb = thumb,
              caption_entities = msg.caption_entities,
              progress = progress,
              progress_args = [stat]
            )

        elif "Audio" == msg_type:
          try:
            thumb = await account.download_media(msg.audio.thumbs[0].file_id)
          except:
            thumb = None

          if Env.DUMP_CHAT:
            output_msg = await bot.send_audio(
              chat_id = int(Env.DUMP_CHAT),
              audio = file_path,
              caption = msg.caption,
              caption_entities = msg.caption_entities,
              progress = progress,
              progress_args = [stat]
            )
          else:
            output_msg = await bot.send_audio(
              chat_id = int(Env.GROUP_ID),
              message_thread_id = message.message_thread_id,
              reply_to_message_id = message.id,
              audio = file_path,
              caption = msg.caption,
              caption_entities = msg.caption_entities,
              progress = progress,
              progress_args = [stat]
            )

          if thumb is not None: 
            os.remove(thumb)

        elif "Photo" == msg_type:
          if Env.DUMP_CHAT:
            output_msg = await bot.send_photo(
              chat_id = int(Env.DUMP_CHAT),
              photo = file_path,
              caption = msg.caption, 
              caption_entities = msg.caption_entities
            )
          else:
            output_msg = await bot.send_photo(
              chat_id = int(Env.GROUP_ID),
              message_thread_id = message.message_thread_id,
              reply_to_message_id = message.id,
              photo = file_path,
              caption = msg.caption,
              caption_entities = msg.caption_entities
            )

      except pyrogram.errors.FloodWait as fw:
        print(f"[FLOOD_WAIT_X] Waiting for {fw.value} Seconds")
        await asyncio.sleep(fw.value)

      except Exception as e:
        await smsg.edit_text(
          text = f"**Error:** __{e}__"
        )
        return False
      
      else:
        # Delete Status Message
        await smsg.delete()

        # Delete the file (If Exist)
        if file_path:
          os.remove(file_path)

        # If DUMP_CHAT is Set
        if Env.DUMP_CHAT:
          await output_msg.copy(
            chat_id = int(Env.GROUP_ID),
            message_thread_id = message.message_thread_id,
            reply_to_message_id = message.id
          )

        # If CACHE is Enabled then store the message info into Database
        if Env.CACHE_ENABLED:
          await Env.MONGO.biltudas1bot.cachedFiles.insert_one(
            {
              "chat_id": msg.chat.id,
              "message_id": msg.id,
              "cached_data": {
                "message_id": output_msg.id
              }
            }
          )

        return True


  def eta_calculate(new_file_size: 'int', total_file_size: 'int', old_file_size: 'int', download_time: 'int') -> tuple['int', 'str']:
    """
    Estimated Download/Upload time calculator
    """
    if new_file_size != old_file_size:
      d_speed = int(new_file_size - old_file_size)
      if download_time:
        eta = int(download_time / d_speed * (total_file_size - new_file_size))
      else:
        eta = -1

      # Getting download speed
      d_speed = d_speed // download_time
    else:
      d_speed = 0
      eta = -1
    return (eta, file_size_converter(d_speed))


  def file_size_converter(size: 'int') -> 'str':
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


  async def if_uploadable(message: pyrogram.types.Message, msg_type: str) -> 'tuple[bool, str]':
    """
    Tells if current account can upload the message or can send the message
    """
    async def check_text(text: 'str'):
      if Env.PREMIUM_ACCOUNT:
        if len(text) > 4096:
          return (False, "Text message length can't be more than 4096 characters")
        else:
          return (True, "")
      else:
        if len(text) > 2048:
          return (False, "Text message length can't be more than 2048 characters")
        else:
          return (True, "")


    async def check_size(size: 'int', caption: 'str'):
      if Env.PREMIUM_ACCOUNT:
        # 4GiB
        if size > 4294967296:
          return (False, "File size can't be more than 4GB")
        else:
          if caption:
            if len(caption) <= 2048:
              return (True, "")
            else:
              return (False, "Message caption can't be more than 2048 chracters")
          else:
            return (True, "")
      else:
        # 2GiB
        if size > 2147483648:
          return (False, "File size can't be more than 2GB")
        else:
          if caption:
            if len(caption) <= 1024:
              return (True, "")
            else:
              return (False, "Message caption can't be more than 1024 chracters")
          else:
            return (True, "")


    match msg_type:
      case "Text":
        return (await check_text(message.text))

      case "Document":
        return (await check_size(message.document.file_size, message.caption))

      case "Video":
        return (await check_size(message.video.file_size, message.caption))

      case "Animation":
        return (await check_size(message.animation.file_size, message.caption))

      case "Sticker":
        return (await check_size(message.sticker.file_size, message.caption))

      case "Voice":
        return (await check_size(message.voice.file_size, message.caption))

      case "Audio":
        return (await check_size(message.audio.file_size, message.caption))

      case "Photo":
        return (await check_size(message.photo.file_size, message.caption))


  async def get_message_type(msg: pyrogram.types.Message) -> 'str | None':
    """
    Tells the Message type (Text, Document, Audio, Video etc.)
    """
    try:
      msg.document.file_id
      return "Document"
    except: 
      pass

    try:
      msg.video.file_id
      return "Video"
    except: 
      pass

    try:
      msg.animation.file_id
      return "Animation"
    except: 
      pass

    try:
      msg.sticker.file_id
      return "Sticker"
    except: 
      pass

    try:
      msg.voice.file_id
      return "Voice"
    except: 
      pass

    try:
      msg.audio.file_id
      return "Audio"
    except: 
      pass

    try:
      msg.photo.file_id
      return "Photo"
    except: 
      pass

    try:
      msg.text

      # To make empty message type as None
      if msg.text is None:
        return None
      else:
        return "Text"
    except:
      pass

    return None


  async def handle_private_chat(message: pyrogram.types.Message, chatid: int | str, msgid: int, private = True, batch_job = False):
    if private:
      chatid = int(f"-100{chatid}")

    msg: 'pyrogram.types.Message' = await account.get_messages(chatid, msgid)
    msg_type = await get_message_type(msg)

    # If the type is invalid
    if msg_type is None:
      if not batch_job:
        await bot.send_message(
          chat_id = int(Env.GROUP_ID),
          reply_to_message_id = message.id,
          text = "**Error: Invalid Message, Only Text, Document, Audio, Video, Animation, Sticker, Voice, Photo are supported**"
        )
      return

    # Check if the message is uploadable
    if not (err := await if_uploadable(msg, msg_type))[0]:
      await bot.send_message(
        chat_id = int(Env.GROUP_ID),
        reply_to_message_id = message.id,
        text = f"**Error: {err[1]}**"
      )
      return

    # Send text message (Copy)
    if msg_type == "Text":
      await asyncio.sleep(Env.REFRESH_TIME)  # Waiting for specific time to prevent batch tasks to make FloodWait

      if Env.DUMP_CHAT:
        # If DUMP_CHAT is set then Copy to DUMP_CHAT
        dump = await bot.send_message(
          chat_id = int(Env.DUMP_CHAT),
          text = msg.text,
          entities = msg.entities
        )

        # Copy from DUMP_CHAT to GROUP_ID
        await bot.copy_message(
          chat_id = int(Env.GROUP_ID),
          message_thread_id = message.message_thread_id,
          reply_to_message_id = message.id,
          from_chat_id = int(Env.DUMP_CHAT),
          message_id = dump.id
        )
      else:
        # Copy to GROUP_ID
        await bot.send_message(
          chat_id = int(Env.GROUP_ID),
          reply_to_message_id = message.id,
          message_thread_id = message.message_thread_id,
          text = msg.text,
          entities = msg.entities
        )
      return


    # Starting download bot message
    smsg = await bot.send_message(
      chat_id = int(Env.GROUP_ID),
      reply_to_message_id = message.id,
      message_thread_id = message.message_thread_id,
      text = '__Starting download...__',
      reply_markup = pyrogram.types.InlineKeyboardMarkup(
        [[
            pyrogram.types.InlineKeyboardButton(
              text = "Cancel",
              callback_data = f"cancel_task_{message.from_user.id}"
            )
        ]]
      )
    )

    # Checking if Message exist into cache
    cache = await Env.MONGO.biltudas1bot.cachedFiles.find_one(
      {
        "chat_id": msg.chat.id,
        "message_id": msg.id
      },
      {'_id': False}
    )

    # If message exist in cache then copy the message to the user
    if cache:
      await asyncio.sleep(Env.REFRESH_TIME)  # Waiting for specific time to prevent batch tasks to make FloodWait
      await bot.copy_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        from_chat_id = int(Env.DUMP_CHAT),
        message_id = cache["cached_data"]["message_id"]
      )

      await smsg.delete()
      return

    # Starting Download
    size_of_file = await get_file_size(msg)
    Env.DOWNLOADED += size_of_file
    downloaded_file: tuple[str, str] = await downloading_file(
      downloadable_msg = msg,
      message = smsg,
      by_user = message.from_user.id
    )

    # Check if Download is stopped by the user
    if message.from_user.id not in Env.ACTIVE_USERS:
      return

    # Storing Download Details on Database
    await Env.MONGO.biltudas1bot.botstats.update_one({}, {
      '$set': {'downloaded': Env.DOWNLOADED}
    })

    if downloaded_file is None:
      await smsg.edit_text(
        text = "**Error: Unable to download the message at this moment, Please try again later.**"
      )
      return
    elif os.path.exists(downloaded_file[1]):
      await smsg.edit_text(
        text = "**Error: The filename already exist into the system.**"
      )
      return

    # Starting Upload
    Env.UPLOADED += size_of_file
    uploaded: bool = await uploading_file(
      msg_type = msg_type,
      msg = msg,
      message = message,
      smsg = smsg,
      file_path = downloaded_file[1],
      encoded_file_path = downloaded_file[0],
      by_user = message.from_user.id
    )

    # Check if Upload is stopped by the user
    if message.from_user.id not in Env.ACTIVE_USERS:
      return

    if not uploaded:
      print("Task Failed")
      return

    # Storing Upload Details on Database
    await Env.MONGO.biltudas1bot.botstats.update_one({}, {
      '$set': {'uploaded': Env.UPLOADED}
    })


  async def process(url: str, message: pyrogram.types.Message, batch_job = False):
    """
    Function to handle saving message based on the url
    Can handle Public Chats or Private One
    Parameters:
      url: Message URL (e.g. https://t.me/c/2058213468/40)
      message: The Message which contains the url (Will be used for replying)
    """
    if pattern_url := re.search("^(https|http):\/\/(t.me|telegram.me)\/c\/(\d+)\/(\d+)\/?(\?single)?$", url):
      # Match Private Chats
      chat_name = int(pattern_url.group(3))
      chat_message_id = int(pattern_url.group(4))

      try:
        await handle_private_chat(
          message = message,
          chatid = chat_name,
          msgid = chat_message_id,
          batch_job = batch_job
        )
      except pyrogram.errors.UsernameNotOccupied:
        await bot.send_message(
          chat_id = int(Env.GROUP_ID),
          message_thread_id = message.id,
          reply_to_message_id = message.id,
          text = "**Error: The chat doesn't seem to be exist**"
        )
      except pyrogram.errors.ChannelInvalid:
        await bot.send_message(
          chat_id = int(Env.GROUP_ID),
          message_thread_id = message.id,
          reply_to_message_id = message.id,
          text = "**Error: The chat is not accessible, please send the invitation link of the chat and then try again.**"
        )
      except Exception as e:
        await bot.send_message(
          chat_id = int(Env.GROUP_ID),
          message_thread_id = message.id,
          reply_to_message_id = message.id,
          text = f"**Error:** __{e}__"
        )

    elif pattern_url := re.search("^(https|http):\/\/(t.me|telegram.me)\/(\D[\w]{4,31})\/(\d+)\/?(\?single)?$", url):
      # Match Public Chats
      chat_name = str(pattern_url.group(3))
      chat_message_id = int(pattern_url.group(4))

      try:
        if Env.DUMP_CHAT:
          if Env.CACHE_ENABLED:
            cached_data = await Env.MONGO.biltudas1bot.cachedFiles.find_one(
              {'chat_id': f"https://t.me/{chat_name}", 'message_id': int(chat_message_id)}, 
              {'_id': False}
            )
          else:
            cached_data = None

          if cached_data is not None:
            # When Cache hit occurs
            # Copy from DUMP_CHAT to GROUP_ID
            await bot.copy_message(
              chat_id = int(Env.GROUP_ID),
              message_thread_id = message.message_thread_id,
              reply_to_message_id = message.id,
              from_chat_id = int(Env.DUMP_CHAT),
              message_id = int(cached_data['cached_data']['message_id'])
            )
          else:
              # When Cache Miss occurs
              # Copy to DUMP_CHAT
              cached = await bot.copy_message(
                chat_id = int(Env.DUMP_CHAT),
                from_chat_id = f"https://t.me/{chat_name}",
                message_id = int(chat_message_id)
              )
              
              # Copy from DUMP_CHAT to GROUP_ID
              await cached.copy(
                chat_id = int(Env.GROUP_ID),
                message_thread_id = message.message_thread_id,
                reply_to_message_id = message.id,
              )

              # Store Cache Information in Database
              if Env.CACHE_ENABLED:
                await Env.MONGO.biltudas1bot.cachedFiles.insert_one(
                  {
                    "chat_id": f"https://t.me/{chat_name}",
                    "message_id": chat_message_id,
                    "cached_data": {
                      "message_id": cached.id
                    }
                  }
                )
        else:
          # Copy to GROUP_ID
          await bot.copy_message(
            chat_id = int(Env.GROUP_ID),
            message_thread_id = message.message_thread_id,
            reply_to_message_id = message.id,
            from_chat_id = f"https://t.me/{chat_name}",
            message_id = chat_message_id
          )

      except pyrogram.errors.UsernameNotOccupied:
        await bot.send_message(
          chat_id = int(Env.GROUP_ID),
          message_thread_id = message.message_thread_id,
          reply_to_message_id = message.id,
          text = "**Error: The chat doesn't exist**"
        )
      except Exception as e:
        # Handle Public Chats which don't allow copying Content
        try:
          await handle_private_chat(
            message = message, 
            chatid = chat_name, 
            msgid = chat_message_id,
            private = False,
            batch_job = batch_job
          )
        except Exception as e1:
          await bot.send_message(
            chat_id = int(Env.GROUP_ID),
            message_thread_id = message.id,
            reply_to_message_id = message.id,
            text = f"**Error:** __{e1}__"
          )
    
    elif pattern_url := re.search("^(https|http):\/\/(t.me|telegram.me)\/b\/(\D[\w]{4,31})\/(\d+)\/?(\?single)?$", url):
      # Match Bot message
      chat_name = str(pattern_url.group(3))
      chat_message_id = int(pattern_url.group(4))

      try:
        await handle_private_chat(
          message = message,
          chatid = chat_name,
          msgid = chat_message_id,
          private = False,
          batch_job = batch_job
        )
      except pyrogram.errors.UsernameNotOccupied:
        await bot.send_message(
          chat_id = int(Env.GROUP_ID),
          message_thread_id = message.id,
          reply_to_message_id = message.id,
          text = "**Error: The chat doesn't seem to be exist**"
        )
      except Exception as e:
        await bot.send_message(
          chat_id = int(Env.GROUP_ID),
          message_thread_id = message.id,
          reply_to_message_id = message.id,
          text = f"**Error:** __{e}__"
        )

    else:
      # Invalid URL
      await bot.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = "**Invalid Message URL**"
      )



  @bot.on_message(filters.command("join") & filters.group & filters.chat(int(Env.GROUP_ID)) & filters.create(lambda a, b, msg: msg.message_thread_id == 1) & filters.create(lambda a, b, msg: str(msg.from_user.id) in Env.ADMIN))
  async def join_chat(client: pyrogram.client.Client, message: pyrogram.types.Message):
    try:
      url = str(message.text).split(" ", 1)[1]
    except IndexError:
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = "**Error: Please Provide a Chat Invite Link**"
      )
      return

    # If valid URL
    if re.match("^(https|http):\/\/(t.me|telegram.me)\/.+$", url):
      # Check If Private Link
      if re.match("^(https|http):\/\/(t.me|telegram.me)\/\+.+$", url):
        try: 
          await account.join_chat(url)
          await client.send_message(
            chat_id = int(Env.GROUP_ID), 
            text = "**Success: Chat Joined**", 
            message_thread_id = message.message_thread_id, 
            reply_to_message_id = message.id
          )
        except pyrogram.errors.UserAlreadyParticipant:
          await client.send_message(
            chat_id = int(Env.GROUP_ID), 
            text = "**Error: Account is already member of the Chat**", 
            message_thread_id = message.message_thread_id, 
            reply_to_message_id=message.id
          )
        except pyrogram.errors.InviteHashExpired:
          await client.send_message(
            chat_id = int(Env.GROUP_ID), 
            text = "**Error: Invalid invitation Link**",
            message_thread_id = message.message_thread_id,
            reply_to_message_id=message.id
          )
        except Exception as e:
          await client.send_message(
            chat_id = int(Env.GROUP_ID),
            text = f"**Error: **__{e}__",
            message_thread_id = message.message_thread_id,
            reply_to_message_id=message.id
          )
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
    # Checks if the current user is already saving some content
    if message.from_user.id in Env.ACTIVE_USERS:
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = "**Task Error: You can't add a task when another task is running**"
      )
      return
    
    try:
      url = str(message.text).split(" ", 1)[1]
    except IndexError:
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = "**Error: Please Provide a Message Link**"
      )
      return
    
    # Starts The Saving Process
    Env.ACTIVE_USERS.add(message.from_user.id)
    await process(
      url = url,
      message = message
    )
    Env.ACTIVE_USERS.discard(message.from_user.id)


  @bot.on_message(filters.command("batch") & filters.group & filters.chat(int(Env.GROUP_ID)) & filters.create(lambda a, b, msg: msg.message_thread_id == 1) & filters.create(lambda a, b, msg: str(msg.from_user.id) in Env.ADMIN))
  async def src_batch_handler(client: pyrogram.client.Client, message: pyrogram.types.Message):
    # Checks if the current user is already saving some content
    if message.from_user.id in Env.ACTIVE_USERS:
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = "**Task Error: You can't add a task when another task is running**"
      )
      return

    try:
      urls = str(message.text).split(" ", 2)[1:]
      start_msg = re.search("^(https|http):\/\/(t.me|telegram.me)\/(c\/\d+|\D[\w]{4,31})\/(\d+)\/?(\?single)?$", urls[0])
      end_msg = re.search("^(https|http):\/\/(t.me|telegram.me)\/(c\/\d+|\D[\w]{4,31})\/(\d+)\/?(\?single)?$", urls[1])

      if start_msg is None or end_msg is None:
        await client.send_message(
          chat_id = int(Env.GROUP_ID),
          message_thread_id = message.message_thread_id,
          reply_to_message_id = message.id,
          text = "**Error: Invalid URL, Please provide a valid message url**"
        )
        return
    except IndexError:
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = "**Error: Please Provide starting and ending Message Link**"
      )
      return

    start_chat_name = start_msg.group(3)
    start_msg_id = int(start_msg.group(4))
    end_chat_name = end_msg.group(3)
    end_msg_id = int(end_msg.group(4))

    # If Two links have different chat ID
    if start_chat_name != end_chat_name:
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = "**Error: Two Links have different chatID**"
      )
      return

    # If end message id is less than start message id
    if end_msg_id < start_msg_id:
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = "**Error: End messageID can't be before than start messageID**"
      )
      return

    # Batch Saving
    Env.ACTIVE_USERS.add(message.from_user.id)
    for msg_id in range(start_msg_id, end_msg_id + 1):
      # Breaks the Loop when User Press Cancel button
      if message.from_user.id not in Env.ACTIVE_USERS:
        break

      await process(
        url = f"https://t.me/{start_chat_name}/{msg_id}",
        message = message,
        batch_job = True
      )
      await asyncio.sleep(Env.REFRESH_TIME)
    Env.ACTIVE_USERS.discard(message.from_user.id)


  @bot.on_callback_query(filters.regex("^cancel_task_\d+$"))
  async def cancel_task_user(client: pyrogram.client.Client, callback_query: pyrogram.types.CallbackQuery):
    user_id = callback_query.data[12:]
    if int(user_id) == callback_query.from_user.id:
      Env.ACTIVE_USERS.discard(int(user_id))

      await client.answer_callback_query(
        callback_query_id = callback_query.id,
        text = "Success: Task stopped",
        show_alert = True
      )
    else:
      await client.answer_callback_query(
        callback_query_id = callback_query.id,
        text = "Error: You can't stop tasks of Other users",
        show_alert = True
      )