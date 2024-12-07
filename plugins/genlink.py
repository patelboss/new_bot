import re
import os
import json
import base64
import logging
import hashlib
from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from info import LOG_CHANNEL, FILE_STORE_CHANNEL, PUBLIC_FILE_STORE
from database.ia_filterdb import *
from utils import temp

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Remove admin verification: Allow everyone
async def allowed(_, __, message):
    logger.info("Access granted to user: %s", message.from_user.id)
    return True  # Anyone can use it now


@Client.on_message(filters.command(['link', 'plink']) & filters.create(allowed))
async def gen_link_s(bot, message):
    logger.info("Received link generation request from user: %s", message.from_user.id)
    
    vj = await bot.ask(chat_id=message.from_user.id, text="Now send me the message you want to store.")
    logger.info("Waiting for message from user: %s", message.from_user.id)

    file_type = vj.media
    if file_type not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
        logger.warning("Invalid media type received: %s", file_type)
        return await vj.reply("Send me only video, audio, file, or document.")
    
    if message.has_protected_content:
        logger.warning("Protected content detected, cannot process file")
        return await message.reply("This file has protected content and cannot be processed.")

    file_id, ref = unpack_new_file_id((getattr(vj, file_type.value)).file_id)
    string = 'filep_' if message.text.lower().strip() == "/plink" else 'file_'
    string += file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    
    logger.info("Generated link for file ID: %s", file_id)
    await message.reply(f"Here is your link:\nhttps://t.me/{temp.U_NAME}?start={outstr}")
    logger.info("Reply sent to user with generated link")


@Client.on_message(filters.command(['batch', 'pbatch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    logger.info("Received batch command from user: %s", message.from_user.id)

    links = message.text.strip().split(" ")
    logger.info("Parsing batch links from user: %s", message.from_user.id)
    
    if len(links) < 3:  # Minimum: Command + at least 2 links
        logger.warning("Incorrect batch command format from user: %s", message.from_user.id)
        return await message.reply(
            "Use correct format.\nExample: `/batch https://t.me/c/123456789/1 https://t.me/c/123456789/2`."
        )

    cmd = links[0]
    links = links[1:]  # Remove the command from the links

    def validate_link(link):
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(link)
        if not match:
            logger.warning("Invalid link format: %s", link)
            return None, None
        chat_id = match.group(4)
        msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int("-100" + chat_id)
        return chat_id, msg_id

    processed_links = [validate_link(link) for link in links]
    logger.info("Validated links: %s", processed_links)

    if any(link is None for link in processed_links):
        logger.warning("Invalid link(s) provided by user: %s", message.from_user.id)
        return await message.reply("Invalid link(s) provided.")

    chat_ids = {chat_id for chat_id, _ in processed_links if chat_id}
    if len(chat_ids) > 1:
        logger.warning("Links from different chats detected: %s", message.from_user.id)
        return await message.reply("All links must belong to the same chat.")

    chat_id = next(iter(chat_ids))
    logger.info("Resolved chat ID: %s", chat_id)

    try:
        logger.info("Fetching chat details for chat ID: %s", chat_id)
        chat_id = (await bot.get_chat(chat_id)).id
        logger.info("Chat ID resolved: %s", chat_id)
    except (ChannelInvalid, UsernameInvalid, UsernameNotModified) as e:
        logger.error("Error accessing chat: %s", str(e))
        return await message.reply("Error accessing chat. Ensure the bot has admin access.")
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return await message.reply(f"Error: {e}")

    await message.reply("Provide a name for this batch and an optional message separated by `|`.")
    logger.info("Waiting for batch name and optional message from user: %s", message.from_user.id)
    response = await bot.listen(message.chat.id)
    logger.info("Received user input for batch name and message: %s", response.text)

    if "|" in response.text:
        batch_name, optional_message = map(str.strip, response.text.split("|", 1))
    else:
        batch_name, optional_message = response.text.strip(), ""

    sts = await message.reply("Processing your batch...")
    logger.info("Sending processing status update to user")

    outlist = []
    links_sent = 0

    for _, msg_id in processed_links:
        try:
            logger.info("Fetching message with ID: %s", msg_id)
            msg = await bot.get_messages(chat_id=chat_id, message_ids=msg_id)
            if not msg or msg.empty or not msg.media:
                continue

            file = getattr(msg, msg.media.value)
            caption = getattr(msg, 'caption', '') or ''
            outlist.append({
                "file_id": file.file_id,
                "caption": caption,
                "title": getattr(file, "file_name", ''),
                "size": getattr(file, "file_size", 0),
                "protect": cmd.lower() == "/pbatch",
            })

            # Send the file without a forward tag
            logger.info("Sending file ID: %s to PUBLIC_FILE_CHANNEL", file.file_id)
            await bot.send_document(
                PUBLIC_FILE_CHANNEL,
                file.file_id,
                caption=caption,
                file_name=getattr(file, "file_name", "File"),
                protect_content=False
            )
            links_sent += 1
        except Exception as e:
            logger.warning("Error processing message %s: %s", msg_id, str(e))

    sequence = get_latest_batch_sequence()
    batch_id = hashlib.sha256(batch_name.encode()).hexdigest()[:15] + f"{sequence:03d}"

    await save_batch_details(batch_id, outlist, batch_name, optional_message)
    logger.info("Batch details saved in db for Batch ID: %s", batch_id)

    short_link = f"https://t.me/{temp.U_NAME}?start=BATCH-{batch_id}"
    await sts.edit(f"Batch created successfully!\n"
                   f"Batch Name: {batch_name}\n"
                   f"Contains `{links_sent}` files.\n"
                   f"Link: {short_link}")
    logger.info("Batch creation status sent to user")

    await bot.send_message(
        LOG_CHANNEL,
        f"New Batch Created:\nBatch ID: {batch_id}\nName: {batch_name}\nMessage: {optional_message}\n"
        f"Link: {short_link}"
    )
    logger.info("Batch creation log sent to LOG_CHANNEL")

    logger.info("Batch created successfully. Batch ID: %s, User: %s", batch_id, message.from_user.id)
