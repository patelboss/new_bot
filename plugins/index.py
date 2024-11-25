import logging
import asyncio
import time
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import (
    ChannelInvalid,
    ChatAdminRequired,
    UsernameInvalid,
    UsernameNotModified,
)
from info import ADMINS
from info import INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import temp
import re
from pymongo.errors import AutoReconnect

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()


async def retry_async(func, *args, retries=5, delay=2, **kwargs):
    """Retry a coroutine function in case of specific exceptions."""
    for attempt in range(retries):
        try:
            return await func(*args, **kwargs)
        except AutoReconnect as e:
            if attempt < retries - 1:
                logger.warning(f"Retry {attempt + 1}/{retries} for {func.__name__} due to: {e}")
                await asyncio.sleep(delay)
            else:
                logger.error(f"Failed after {retries} attempts for {func.__name__}. Error: {e}")
                raise


@Client.on_callback_query(filters.regex(r"^index"))
async def index_files(bot, query):
    if query.data.startswith("index_cancel"):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing")
    _, raju, chat, lst_msg_id, from_user = query.data.split("#")
    if raju == "reject":
        await query.message.delete()
        await bot.send_message(
            int(from_user),
            f"Your Submission for indexing {chat} has been declined by our moderators.",
            reply_to_message_id=int(lst_msg_id),
        )
        return

    if lock.locked():
        return await query.answer("Wait until the previous process completes.", show_alert=True)
    msg = query.message

    await query.answer("Processing...⏳", show_alert=True)
    if int(from_user) not in ADMINS:
        await bot.send_message(
            int(from_user),
            f"Your Submission for indexing {chat} has been accepted by our moderators and will be added soon.",
            reply_to_message_id=int(lst_msg_id),
        )
    await msg.edit(
        "Starting Indexing",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Cancel", callback_data="index_cancel")]]
        ),
    )
    try:
        chat = int(chat)
    except:
        pass
    await index_files_to_db(int(lst_msg_id), chat, msg, bot)


@Client.on_message(
    (
        filters.forwarded
        | (
            filters.regex(
                r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$"
            )
            & filters.text
        )
    )
    & filters.private
    & filters.incoming
)
async def send_for_index(bot, message):
    # (This section remains unchanged, same as before.)
    pass


@Client.on_message(filters.command("setskip") & filters.user(ADMINS))
async def set_skip_number(bot, message):
    # (This section remains unchanged, same as before.)
    pass


async def index_files_to_db(lst_msg_id, chat, msg, bot):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    start_time = time.time()

    async with lock:
        try:
            current = temp.CURRENT
            temp.CANCEL = False
            async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):
                if temp.CANCEL:
                    break
                current += 1
                if current % 20 == 0:
                    elapsed_time = round(time.time() - start_time)
                    await msg.edit_text(
                        text=f"Total messages fetched: <code>{current}</code>\n"
                        f"Total messages saved: <code>{total_files}</code>\n"
                        f"Duplicate Files Skipped: <code>{duplicate}</code>\n"
                        f"Deleted Messages Skipped: <code>{deleted}</code>\n"
                        f"Non-Media messages skipped: <code>{no_media + unsupported}</code> "
                        f"(Unsupported Media - `{unsupported}`)\n"
                        f"Errors Occurred: <code>{errors}</code>\n"
                        f"Elapsed Time: <code>{elapsed_time} seconds</code>",
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton("Cancel", callback_data="index_cancel")]]
                        ),
                    )
                if message.empty:
                    deleted += 1
                    continue
                elif not message.media:
                    no_media += 1
                    continue
                elif message.media not in [
                    enums.MessageMediaType.VIDEO,
                    enums.MessageMediaType.AUDIO,
                    enums.MessageMediaType.DOCUMENT,
                ]:
                    unsupported += 1
                    continue
                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue
                media.file_type = message.media.value
                media.caption = message.caption
                try:
                    aynav, vnay = await retry_async(save_file, media)
                    if aynav:
                        total_files += 1
                    elif vnay == 0:
                        duplicate += 1
                    elif vnay == 2:
                        errors += 1
                except Exception as e:
                    errors += 1
                    logger.exception(f"Failed to save file: {e}")
        except Exception as e:
            logger.exception(e)
            await msg.edit(f"Error: {e}")
        else:
            elapsed_time = round(time.time() - start_time)
            await msg.edit(
                f"Successfully saved <code>{total_files}</code> files to the database!\n"
                f"Duplicate Files Skipped: <code>{duplicate}</code>\n"
                f"Deleted Messages Skipped: <code>{deleted}</code>\n"
                f"Non-Media messages skipped: <code>{no_media + unsupported}</code> "
                f"(Unsupported Media - `{unsupported}`)\n"
                f"Errors Occurred: <code>{errors}</code>\n"
                f"Total Running Time: <code>{elapsed_time} seconds</code>"
            )
