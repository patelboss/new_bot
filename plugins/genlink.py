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
    return True  # Anyone can use it now


@Client.on_message(filters.command(['link', 'plink']) & filters.create(allowed))
async def gen_link_s(bot, message):
    vj = await bot.ask(chat_id=message.from_user.id, text="Now send me the message you want to store.")
    file_type = vj.media
    if file_type not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
        return await vj.reply("Send me only video, audio, file, or document.")
    if message.has_protected_content:
        return await message.reply("This file has protected content and cannot be processed.")

    file_id, ref = unpack_new_file_id((getattr(vj, file_type.value)).file_id)
    string = 'filep_' if message.text.lower().strip() == "/plink" else 'file_'
    string += file_id
    outstr = base64.urlsafe_b64encode(string.encode("ascii")).decode().strip("=")
    await message.reply(f"Here is your link:\nhttps://t.me/{temp.U_NAME}?start={outstr}")


@Client.on_message(filters.command(['batch', 'pbatch']) & filters.create(allowed))
async def gen_link_batch(bot, message):
    logger.info("Received batch command from user: %s", message.from_user.id)

    links = message.text.strip().split(" ")
    if len(links) < 3:  # Minimum: Command + at least 2 links
        return await message.reply(
            "Use correct format.\nExample: `/batch https://t.me/c/123456789/1 https://t.me/c/123456789/2`."
        )

    cmd = links[0]
    links = links[1:]  # Remove the command from the links

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

    processed_links = [validate_link(link) for link in links]
    if any(link is None for link in processed_links):
        return await message.reply("Invalid link(s) provided.")

    chat_ids = {chat_id for chat_id, _ in processed_links if chat_id}
    if len(chat_ids) > 1:
        return await message.reply("All links must belong to the same chat.")

    chat_id = next(iter(chat_ids))

    try:
        chat_id = (await bot.get_chat(chat_id)).id
    except (ChannelInvalid, UsernameInvalid, UsernameNotModified):
        return await message.reply("Error accessing chat. Ensure the bot has admin access.")
    except Exception as e:
        return await message.reply(f"Error: {e}")

    await message.reply("Provide a name for this batch and an optional message separated by `|`.")
    response = await bot.listen(message.chat.id)
    if "|" in response.text:
        batch_name, optional_message = map(str.strip, response.text.split("|", 1))
    else:
        batch_name, optional_message = response.text.strip(), ""

    sts = await message.reply("Processing your batch...")
    outlist = []
    links_sent = 0

    for _, msg_id in processed_links:
        try:
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
            await bot.send_document(
                FILE_STORE_CHANNEL,
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

    short_link = f"https://t.me/{temp.U_NAME}?start=BATCH-{batch_id}"
    await sts.edit(f"Batch created successfully!\n"
                   f"Batch Name: {batch_name}\n"
                   f"Contains `{links_sent}` files.\n"
                   f"Link: {short_link}")
    await bot.send_message(
        LOG_CHANNEL,
        f"New Batch Created:\nBatch ID: {batch_id}\nName: {batch_name}\nMessage: {optional_message}\n"
        f"Link: {short_link}"
    )
    logger.info("Batch created successfully. Batch ID: %s, User: %s", batch_id, message.from_user.id)
