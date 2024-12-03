import re, os, json, base64, logging
from utils import temp
from pyrogram import filters, Client, enums
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from info import ADMINS, LOG_CHANNEL, FILE_STORE_CHANNEL, PUBLIC_FILE_STORE
from database.ia_filterdb import unpack_new_file_id

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

async def allowed(_, __, message):
    if PUBLIC_FILE_STORE:
        return True
    if message.from_user and message.from_user.id in ADMINS:
        return True
    return False

@Client.on_message(filters.command(['link', 'plink']) & filters.create(allowed))
async def gen_link_s(bot, message):
    vj = await bot.ask(chat_id = message.from_user.id, text = "Now Send Me Your Message Which You Want To Store.")
    file_type = vj.media
    if file_type not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
        return await vj.reply("Send me only video,audio,file or document.")
    if message.has_protected_content and message.chat.id not in ADMINS:
        return await message.reply("okDa")
    file_id, ref = unpack_new_file_id((getattr(vj, file_type.value)).file_id)
    string = 'filep_' if message.text.lower().strip() == "/plink" else 'file_'
    string += file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    await message.reply(f"Here is your Link:\nhttps://t.me/{temp.U_NAME}?start={outstr}")    

import os
import json
import re
import base64
from pyrogram.errors import ChannelInvalid, UsernameInvalid, UsernameNotModified
from logging import getLogger

logger = getLogger(__name__)

@Client.on_message(filters.command(['batch', 'pbatch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    logger.info("Received batch command from user: %s", message.from_user.id)

    # Validate the command format
    links = message.text.strip().split(" ")
    if len(links) < 3:  # Minimum: Command + Start + End
        logger.warning("Incorrect format provided by user: %s", message.from_user.id)
        return await message.reply(
            "Use correct format.\nExample: <code>/batch https://t.me/c/123456789/1 https://t.me/c/123456789/50</code>."
        )

    cmd, first, last = links[:3]

    # Validate links
    def validate_link(link):
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(link)
        if not match:
            return None, None
        chat_id = match.group(4)
        msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int("-100" + chat_id)
        return chat_id, msg_id

    f_chat_id, f_msg_id = validate_link(first)
    l_chat_id, l_msg_id = validate_link(last)

    if not (f_chat_id and l_chat_id):
        logger.error("Invalid links provided by user: %s", message.from_user.id)
        return await message.reply("Invalid link(s) provided.")

    if f_chat_id != l_chat_id:
        logger.error("Chat IDs do not match for user: %s", message.from_user.id)
        return await message.reply("Chat IDs do not match.")

    # Verify chat
    try:
        chat_id = (await bot.get_chat(f_chat_id)).id
        logger.info("Verified chat ID: %s for user: %s", chat_id, message.from_user.id)
    except (ChannelInvalid, UsernameInvalid, UsernameNotModified) as e:
        logger.error("Chat verification failed for user %s: %s", message.from_user.id, str(e))
        return await message.reply("Error accessing chat. Ensure the bot has admin access.")
    except Exception as e:
        logger.exception("Unexpected error during chat verification for user %s: %s", message.from_user.id, str(e))
        return await message.reply(f"Error: {e}")

    # Start Processing
    sts = await message.reply("Generating links for your messages. This may take some time.")
    outlist = []
    links_sent = 0

    # Iterate through messages using iter_messages
    current_id = f_msg_id
    while current_id <= l_msg_id:
        try:
            messages = await bot.get_messages(chat_id=f_chat_id, message_ids=list(range(current_id, min(l_msg_id + 1, current_id + 100))))
            for msg in messages:
                if msg.empty or msg.service:
                    continue
                if not msg.media:
                    continue

                try:
                    file_type = msg.media
                    file = getattr(msg, file_type.value, None)
                    caption = getattr(msg, 'caption', '') or ''
                    if file:
                        outlist.append({
                            "file_id": file.file_id,
                            "caption": caption.html if caption else '',
                            "title": getattr(file, "file_name", ''),
                            "size": getattr(file, "file_size", 0),
                            "protect": cmd.lower() == "/pbatch",
                        })
                        links_sent += 1
                except Exception as e:
                    logger.warning("Error processing message %s: %s", msg.id, str(e))
            current_id += 100  # Increment to the next batch
        except Exception as e:
            logger.exception("Error iterating messages for user %s: %s", message.from_user.id, str(e))
            break

    # Save Results
    json_file = f"batch_{message.from_user.id}.json"
    with open(json_file, "w") as f:
        json.dump(outlist, f)

    # Upload to LOG_CHANNEL
    try:
        upload = await bot.send_document(
            LOG_CHANNEL, json_file, file_name="Batch.json", caption="Generated batch file."
        )
        logger.info("Batch file uploaded for user: %s. Links Sent: %d", message.from_user.id, links_sent)
        os.remove(json_file)
        await sts.edit(f"Link generated! Contains `{links_sent}` files: https://t.me/{temp.U_NAME}?start=BATCH-{upload.document.file_id}")
    except Exception as e:
        logger.exception("Failed to upload batch file for user: %s", message.from_user.id)
        await sts.edit("Failed to upload the batch file. Please try again.")
