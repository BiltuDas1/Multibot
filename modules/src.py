import re
import pyrogram
import secrets
import asyncio
import os
import queue
from pyrogram import filters


async def save_restricted_content(bot: pyrogram.client.Client, account: pyrogram.client.Client, Env):
  # async def downloading_file(smsg, msg, rand_id: 'str', que: 'queue.Queue'):
  #   while True:
  #     try:
  #       # Downloading file
  #       file = await account.download_media(
  #         message = msg, 
  #         progress = progress, 
  #         progress_args = [rand_id, "down", smsg.chat.id, smsg]
  #       )
        
  #     except FloodWait as fw:
  #       print(f"[FLOOD_WAIT_X] Wait for {fw.value} Seconds")
  #       await asyncio.sleep(fw.value)

  #     else:
  #       if os.path.exists(f'{rand_id}.down.status.txt'):
  #         os.remove(f'{rand_id}.down.status.txt')
  #       que.put(file)
  #       break


  # def uploading_file(msg_type: 'str', msg, message: 'pyrogram.types.Message', qu: 'queue.Queue', smsg: 'pyrogram.types.Message', rand_id: 'str'):
  #   while True:
  #     if file_path := qu.get():
  #       try:
  #         if "Document" == msg_type:
  #           try:
  #             thumb = account.download_media(msg.document.thumbs[0].file_id)
  #           except:
  #             thumb = None

  #           output_msg = bot.send_document(
  #             chat_id = int(Env.GROUP_ID),
  #             message_thread_id = smsg.message_thread_id,
  #             document = file_path,
  #             thumb = thumb,
  #             caption = msg.caption,
  #             caption_entities = msg.caption_entities,
  #             progress = progress, 
  #             progress_args = [rand_id, "up", message.chat.id]
  #           )
  #           if thumb != None:
  #             os.remove(thumb)

  #         elif "Video" == msg_type:
  #           try:
  #             thumb = account.download_media(msg.video.thumbs[0].file_id)
  #           except:
  #             thumb = None

  #           output_msg = bot.send_video(
  #             Env.BUFFER_CHAT_ID,
  #             file_path,
  #             duration=msg.video.duration,
  #             width=msg.video.width,
  #             height=msg.video.height,
  #             thumb=thumb,
  #             caption=msg.caption,
  #             caption_entities=msg.caption_entities,
  #             progress=progress,
  #             progress_args=[rand_id, "up", message.chat.id]
  #           )
  #           if thumb != None: 
  #             os.remove(thumb)

  #         elif "Animation" == msg_type:
  #           output_msg = bot.send_animation(Env.BUFFER_CHAT_ID, file_path)

  #         elif "Sticker" == msg_type:
  #           output_msg = bot.send_sticker(Env.BUFFER_CHAT_ID, file_path)

  #         elif "Voice" == msg_type:
  #           output_msg = bot.send_voice(
  #             Env.BUFFER_CHAT_ID, 
  #             file_path, 
  #             caption=msg.caption, 
  #             thumb=thumb, 
  #             caption_entities=msg.caption_entities,
  #             progress=progress, 
  #             progress_args=[rand_id, "up", message.chat.id]
  #           )

  #         elif "Audio" == msg_type:
  #           try:
  #             thumb = account.download_media(msg.audio.thumbs[0].file_id)
  #           except:
  #             thumb = None

  #           output_msg = bot.send_audio(
  #             Env.BUFFER_CHAT_ID, 
  #             file_path, 
  #             caption=msg.caption, 
  #             caption_entities=msg.caption_entities,
  #             progress=progress, 
  #             progress_args=[rand_id, "up", message.chat.id]
  #           )
  #           if thumb != None: 
  #             os.remove(thumb)

  #         elif "Photo" == msg_type:
  #           output_msg = bot.send_photo(
  #             Env.BUFFER_CHAT_ID, 
  #             file_path, 
  #             caption=msg.caption, 
  #             caption_entities=msg.caption_entities
  #           )

  #       except FloodWait as fw:
  #         print(f"[FLOOD_WAIT_X] Wait for {fw.value} Seconds")
  #         Env.FLOOD_WAIT = fw.value

  #         while Env.FLOOD_WAIT:
  #           time.sleep(1)
  #           Env.FLOOD_WAIT -= 1
        
  #       else:
  #         if file_path:
  #           os.remove(file_path)

  #         if os.path.exists(f'{rand_id}.up.status.txt'):
  #           os.remove(f'{rand_id}.up.status.txt')

  #         bot.delete_messages(
  #           message.chat.id,
  #           [smsg.id]
  #         )

  #         if not Env.TERMINATE_CLONING[str(message.chat.id)]:
  #           # copy from BUFFER_CHAT_ID to user_id
  #           bot.copy_message(
  #             message.chat.id,
  #             Env.BUFFER_CHAT_ID,
  #             output_msg.id, 
  #             reply_to_message_id=message.id
  #           )

  #           # If DELETE_BUFFER is set, then delete BUFFER_MESSAGE
  #           if Env.DELETE_BUFFER:
  #             bot.delete_messages(
  #               Env.BUFFER_CHAT_ID,
  #               [output_msg.id]
  #             )

  #         # If single job into the cloning queue
  #         if isinstance(Env.CLONING_QUEUE[str(message.chat.id)][0], tuple):
  #           Env.TERMINATE_CLONING[str(message.chat.id)] = False
  #           Env.CLONING_QUEUE.pop(str(message.chat.id))
  #         break
  #     else:
  #       # If single job into the cloning queue
  #       if isinstance(Env.CLONING_QUEUE[str(message.chat.id)][0], tuple):
  #         Env.TERMINATE_CLONING[str(message.chat.id)] = False
  #         Env.CLONING_QUEUE.pop(str(message.chat.id))
  #       break


  # # Estimated time
  # def eta_calculate(new_file_size: 'int', total_file_size: 'int', old_file_size: 'int') -> tuple['int', 'str']:
  #   if new_file_size != old_file_size:
  #     d_speed = int(new_file_size - old_file_size)
  #     eta = int(Env.REFRESH_TIME / d_speed * (total_file_size - new_file_size))
  #   else:
  #     d_speed = 0
  #     eta = -1
  #   return (eta, file_size_converter(d_speed))


  # # progress writter
  # def progress(current, total, rand_file_id, type, user_id, smsg = None):
  #   with open(f'{rand_file_id}.{type}.status.txt', "w") as fileup:
  #     fileup.write(f"{current * 100 / total} {current} {total}")

  #   if Env.TERMINATE_CLONING[str(user_id)]:
  #     if type == "down":
  #       bot.delete_messages(
  #         user_id,
  #         [smsg.id]
  #       )
  #     bot.stop_transmission()


  # # File size converter
  # def file_size_converter(size: 'int') -> 'str':
  #   units = ("B", "KiB", "MiB", "GiB", "TiB", "EiB", "PiB")
  #   i = 0
  #   temp_size = size

  #   while temp_size > 1023:
  #     temp_size /= 1024
  #     i += 1

  #   temp_size = float(f"{temp_size:.2f}")
  #   return f"{temp_size} {units[i]}"


  # # download progress which is shown to the user
  # async def downstatus(statusfile, message):
  #   while True:
  #     if os.path.exists(statusfile):
  #       break

  #   active_block = "█"
  #   inactive_block = "▒"
  #   progress_bar_width = 15
  #   total_time = 3
  #   await asyncio.sleep(total_time)
  #   old_file_size = 0
  #   process_locked_time = 0

  #   while os.path.exists(statusfile):
  #     # Check if floodwait
  #     # if Env.FLOOD_WAIT:
  #     #   time.sleep(Env.FLOOD_WAIT)

  #     # Getting download percentage
  #     with open(statusfile, 'r') as downread:
  #       if r := downread.read().split(" "):
  #         percentage = float(r[0])
  #         current_file_size = int(r[1])
  #         total_file_size = int(r[2])
  #       else:
  #         percentage = 0.1
  #         current_file_size = 0
  #         total_file_size = 0

  #     # If current_file_size is not changing for more than 1 minutes, then terminate the task
  #     if current_file_size == old_file_size and not process_locked_time:
  #       process_locked_time = total_time
  #     elif current_file_size != old_file_size:
  #       process_locked_time = 0
  #     elif current_file_size == old_file_size and process_locked_time:
  #       # If the Download percentage stuck for more than 60 seconds
  #       if (total_time - process_locked_time) > 60:
  #         await bot.edit_message_text(
  #           message.chat.id,
  #           message.id,
  #           "Download failed due to some Server side error, Please try again later."
  #         )
  #         break

  #     try:
  #       # Calculate ETA and processing Speed
  #       eta, process_speed = eta_calculate(current_file_size, total_file_size, old_file_size)

  #       if eta != -1:
  #         if eta >= 60:
  #           eta_time = f"{eta//60} minutes {eta%60} seconds"
  #         else:
  #           eta_time = f"{eta} seconds"
  #       else:
  #         eta_time = "∞"

  #       # Calculate Elapse Time 
  #       total_time += Env.REFRESH_TIME
  #       old_file_size = current_file_size

  #       if total_time >= 60:
  #         elapse_time = f"{total_time//60} minutes {total_time%60} seconds"
  #       else:
  #         elapse_time = f"{total_time} seconds"

  #       # File Size
  #       current_fs = file_size_converter(current_file_size)
  #       total_fs = file_size_converter(total_file_size)
  #       size_msg = f"{current_fs} out of {total_fs}"

  #       # Progress bar
  #       processed = int((progress_bar_width / 100) * percentage)
  #       remaining = progress_bar_width - processed
  #       progress_bar = (active_block * processed) + (inactive_block * remaining)

  #       # Update message
  #       msg_txt = f"**Downloading**: {percentage:.2f}% of 100%\n\n {progress_bar} \n\n**Size**: {size_msg}\n\n**Speed**: {process_speed}\n\n**ETA**: {eta_time}\n\n**Elapse Time**: {elapse_time}"
  #       await bot.edit_message_text(
  #         message.chat.id,
  #         message.id,
  #         msg_txt
  #       )
  #       await asyncio.sleep(Env.REFRESH_TIME)
  #     except Exception:
  #       await asyncio.sleep(Env.REFRESH_TIME)


  # # upload status which is shown to the user
  # async def upstatus(statusfile, message):
  #   while True:
  #     if os.path.exists(statusfile):
  #       break

  #   active_block = "█"
  #   inactive_block = "▒"
  #   progress_bar_width = 15
  #   total_time = 3
  #   await asyncio.sleep(total_time)
  #   old_file_size = 0
  #   process_locked_time = 0

  #   while os.path.exists(statusfile):
  #     # Check if floodwait
  #     # if Env.FLOOD_WAIT:
  #     #   time.sleep(Env.FLOOD_WAIT)

  #     # Getting download percentage
  #     with open(statusfile, 'r') as upread:
  #       if r := upread.read().split(" "):
  #         percentage = float(r[0])
  #         current_file_size = int(r[1])
  #         total_file_size = int(r[2])
  #       else:
  #         percentage = 0.1
  #         current_file_size = 0
  #         total_file_size = 0

  #     # If current_file_size is not changing for more than 1 minutes, then terminate the task
  #     if current_file_size == old_file_size and not process_locked_time:
  #       process_locked_time = total_time
  #     elif current_file_size != old_file_size:
  #       process_locked_time = 0
  #     elif current_file_size == old_file_size and process_locked_time:
  #       # If the upload percentage stuck for more than 60 seconds
  #       if (total_time - process_locked_time) > 60:
  #         await bot.edit_message_text(
  #           message.chat.id,
  #           message.id,
  #           "Upload failed due to some Server side error, Please try again later."
  #         )
  #         break

  #     try:
  #       # Calculate ETA and processing Speed
  #       eta, process_speed = eta_calculate(current_file_size, total_file_size, old_file_size)

  #       if eta != -1:
  #         if eta >= 60:
  #           eta_time = f"{eta//60} minutes {eta%60} seconds"
  #         else:
  #           eta_time = f"{eta} seconds"
  #       else:
  #         eta_time = "∞"

  #       # Calculate Elapse Time 
  #       total_time += Env.REFRESH_TIME
  #       old_file_size = current_file_size

  #       if total_time >= 60:
  #         elapse_time = f"{total_time//60} minutes {total_time%60} seconds"
  #       else:
  #         elapse_time = f"{total_time} seconds"

  #       # File Size
  #       current_fs = file_size_converter(current_file_size)
  #       total_fs = file_size_converter(total_file_size)
  #       size_msg = f"{current_fs} out of {total_fs}"

  #       # Progress bar
  #       processed = int((progress_bar_width / 100) * percentage)
  #       remaining = progress_bar_width - processed
  #       progress_bar = (active_block * processed) + (inactive_block * remaining)

  #       # Update message
  #       msg_txt = f"**Uploading**: {percentage:.2f}% of 100%\n\n {progress_bar} \n\n**Size**: {size_msg}\n\n**Speed**: {process_speed}\n\n**ETA**: {eta_time}\n\n**Elapse Time**: {elapse_time}"
  #       await bot.edit_message_text(
  #         message.chat.id, 
  #         message.id, 
  #         msg_txt
  #       )
  #       await asyncio.sleep(Env.REFRESH_TIME)
  #     except Exception:
  #       await asyncio.sleep(Env.REFRESH_TIME)


  # def if_uploadable(message: 'pyrogram.types.messages_and_media.message.Message') -> 'tuple[bool, str]':
  #   msg_type = get_message_type(message)

  #   def check_text(text: 'str'):
  #     if Env.PREMIUM_ACCOUNT:
  #       if len(text) > 4096:
  #         return (False, "Text message length can't be more than 4096 characters")
  #       else:
  #         return (True, "")
  #     else:
  #       if len(text) > 2048:
  #         return (False, "Text message length can't be more than 2048 characters")
  #       else:
  #         return (True, "")


  #   def check_size(size: 'int', caption: 'str'):
  #     if Env.PREMIUM_ACCOUNT:
  #       # 4GiB
  #       if size > 4294967296:
  #         return (False, "File size can't be more than 4GB")
  #       else:
  #         if caption:
  #           if len(caption) <= 2048:
  #             return (True, "")
  #           else:
  #             return (False, "Message caption can't be more than 2048 chracters")
  #         else:
  #           return (True, "")
  #     else:
  #       # 2GiB
  #       if size > 2147483648:
  #         return (False, "File size can't be more than 2GB")
  #       else:
  #         if caption:
  #           if len(caption) <= 1024:
  #             return (True, "")
  #           else:
  #             return (False, "Message caption can't be more than 1024 chracters")
  #         else:
  #           return (True, "")


  #   match msg_type:
  #     case "Text":
  #       return check_text(message.text)

  #     case "Document":
  #       return check_size(message.document.file_size, message.caption)

  #     case "Video":
  #       return check_size(message.video.file_size, message.caption)

  #     case "Animation":
  #       return check_size(message.animation.file_size, message.caption)

  #     case "Sticker":
  #       return check_size(message.sticker.file_size, message.caption)

  #     case "Voice":
  #       return check_size(message.voice.file_size, message.caption)

  #     case "Audio":
  #       return check_size(message.audio.file_size, message.caption)

  #     case "Photo":
  #       return check_size(message.photo.file_size, message.caption)


  # def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
  #   try:
  #     msg.document.file_id
  #     return "Document"
  #   except: 
  #     pass

  #   try:
  #     msg.video.file_id
  #     return "Video"
  #   except: 
  #     pass

  #   try:
  #     msg.animation.file_id
  #     return "Animation"
  #   except: 
  #     pass

  #   try:
  #     msg.sticker.file_id
  #     return "Sticker"
  #   except: 
  #     pass

  #   try:
  #     msg.voice.file_id
  #     return "Voice"
  #   except: 
  #     pass

  #   try:
  #     msg.audio.file_id
  #     return "Audio"
  #   except: 
  #     pass

  #   try:
  #     msg.photo.file_id
  #     return "Photo"
  #   except: 
  #     pass

  #   try:
  #     msg.text
  #     return "Text"
  #   except:
  #     pass


  # def handle_private_chat(message: pyrogram.types.messages_and_media.message.Message, chatid: int, msgid: int, private: bool = True):
  #   if private:
  #     chatid = int(f"-100{chatid}")

  #     msg: 'pyrogram.types.messages_and_media.message.Message' = await account.get_messages(chatid, msgid)
  #     msg_type = get_message_type(msg)

  #   	# Check if the message is uploadable
  #     if (er := if_uploadable(msg))[0]:
  #       # Send text message (Copy)
  #       if "Text" == msg_type:
  #         output_msg = await bot.send_message(
  #           chat_id = int(Env.GROUP_ID),
  #           reply_to_chat_id = message.id,
  #           message_thread_id = message.message_thread_id,
  #           text = msg.text,
  #           entities = msg.entities
  #         )
  #         return

  #       # Starting download bot message
  #       smsg = await bot.send_message(
  #         chat_id = int(Env.GROUP_ID),
  #         reply_to_chat_id = message.id,
  #         message_thread_id = message.message_thread_id,
  #         text = '__Starting download...__'
  #       )

  #       # Starting download
  #       rand_id = secrets.token_hex(32)
  #       download_progress = asyncio.create_task(downstatus(f"{rand_id}.down.status.txt", smsg))
  #       download_task = asyncio.create_task(downloading_file(f"{rand_id}.down.status.txt", smsg))
  #       upload_progress = asyncio.create_task(downstatus(f"{rand_id}.down.status.txt", smsg))
  #       upload_task = asyncio.create_task(downstatus(f"{rand_id}.down.status.txt", smsg))




  #       # Creating threads
  #       qu = queue.Queue(1)
  #       temp_index = len(Env.CLONING_QUEUE[str(message.chat.id)])
  #       Env.CLONING_QUEUE[str(message.chat.id)].append(
  #         (
  #           qu,
  #           threading.Thread(target=downstatus, args=(f'{rand_id}.down.status.txt', smsg), daemon=True),
  #           threading.Thread(target=downloading_file, args=(smsg, msg, rand_id, qu), daemon=True),
  #           threading.Thread(target=upstatus, args=(f'{rand_id}.up.status.txt', smsg), daemon=True),
  #           threading.Thread(target=uploading_file, args=(msg_type, msg, message, qu, smsg, rand_id), daemon=True)
  #         )
  #       )

  #       # Starting download status thread
  #       Env.CLONING_QUEUE[str(message.chat.id)][temp_index][1].start()

  #       # Starting download thread
  #       Env.CLONING_QUEUE[str(message.chat.id)][temp_index][2].start()
  #       Env.CLONING_QUEUE[str(message.chat.id)][temp_index][2].join()

  #       # Starting upload status thread
  #       Env.CLONING_QUEUE[str(message.chat.id)][temp_index][3].start()

  #       # Starting uploading thread
  #       Env.CLONING_QUEUE[str(message.chat.id)][temp_index][4].start()
  #     else:
  #       bot.send_message(
  #         message.chat.id,
  #         f"Error: {er[1]}",
  #         reply_to_message_id=message.id
  #       )


  @bot.on_message(filters.command("join") & filters.group & filters.chat(int(Env.GROUP_ID)) & filters.create(lambda a, b, msg: msg.message_thread_id == 1) & filters.create(lambda a, b, msg: str(msg.from_user.id) in Env.ADMIN))
  async def join_chat(client: pyrogram.client.Client, message: pyrogram.types.Message):
    try:
      url = str(message.text).split(" ", 1)[1]
    except IndexError:
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
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
    try:
      url = str(message.text).split(" ", 1)[1]
    except IndexError:
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        text = "**Error: Please Provide a Message Link**"
      )
      return

    if pattern_url := re.search("^(https|http):\/\/(t.me|telegram.me)\/c\/(\d+)\/(\d+)\/?(\?single)?$", url):
      # Match Private Chats
      # chat_name = int(pattern_url.group(3))
      # chat_message_id = int(pattern_url.group(4))

      # try:
      #   handle_private_chat(message, chat_name, chat_message_id)
      # except pyrogram.errors.UsernameNotOccupied:
      #   await client.send_message(
      #     chat_id = int(Env.GROUP_ID),
      #     message_thread_id = message.id,
      #     reply_to_message_id = message.id,
      #     text = "**Error: The Chat doesn't exist**"
      #   )
      # except pyrogram.errors.ChannelInvalid:
      #   await client.send_message(
      #     chat_id = int(Env.GROUP_ID),
      #     message_thread_id = message.id,
      #     reply_to_message_id = message.id,
      #     text = "**Error: The chat is not accessible, please send the invitation link of the chat and then try again.**"
      #   )
      # except Exception as e:
      #   await client.send_message(
      #     chat_id = int(Env.GROUP_ID),
      #     message_thread_id = message.id,
      #     reply_to_message_id = message.id,
      #     text = f"**Error: **__{e}__"
      #   )
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = "**Currently the Private Chat Feature is not supported**"
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
            await client.copy_message(
              chat_id = int(Env.GROUP_ID),
              message_thread_id = message.message_thread_id,
              reply_to_message_id = message.id,
              from_chat_id = int(Env.DUMP_CHAT),
              message_id = int(cached_data['cached_data']['message_id'])
            )
          else:
              # When Cache Miss occurs
              # Copy to DUMP_CHAT
              cached = await client.copy_message(
                chat_id = int(Env.DUMP_CHAT),
                from_chat_id = f"https://t.me/{chat_name}",
                message_id = int(chat_message_id)
              )
              
              # Copy from DUMP_CHAT to GROUP_ID
              await client.copy_message(
                chat_id = int(Env.GROUP_ID),
                message_thread_id = message.message_thread_id,
                reply_to_message_id = message.id,
                from_chat_id = int(Env.DUMP_CHAT),
                message_id = cached.id
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
          await client.copy_message(
            chat_id = int(Env.GROUP_ID),
            message_thread_id = message.message_thread_id,
            reply_to_message_id = message.id,
            from_chat_id = f"https://t.me/{chat_name}",
            message_id = chat_message_id
          )

      except pyrogram.errors.UsernameNotOccupied:
        await client.send_message(
          chat_id = int(Env.GROUP_ID),
          message_thread_id = message.id,
          reply_to_message_id = message.id,
          text = "**Error: The Chat doesn't exist**"
        )
      except Exception as e:
        # Handle Public Chats which don't allow copying Content
        # handle_private_chat(message, chat_name, chat_message_id, private = False)
        pass
    
    else:
      # Invalid URL
      await client.send_message(
        chat_id = int(Env.GROUP_ID),
        message_thread_id = message.message_thread_id,
        reply_to_message_id = message.id,
        text = "**Invalid Message URL**"
      )
