import logging
from pyrogram import Client, emoji, filters
from pyrogram.errors.exceptions.bad_request_400 import QueryIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument, InlineQuery
from database.ia_filterdb import get_search_results
from utils import is_subscribed, get_size, temp
from info import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION
from database.connections_mdb import active_connection

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
  
from pyrogram import Client, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.types import CallbackQuery
import asyncio
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Time delay for deleting the sent file
DELETE_FILE_DELAY = 600  # 10 minutes in seconds

@Client.on_inline_query()
async def answer(bot, query):
    """Show search results for the given inline query."""
    logger.info(f"Inline query received from user {query.from_user.id}: {query.query}")

    chat_id = await active_connection(str(query.from_user.id))

    if not await inline_users(query):
        logger.info(f"User {query.from_user.id} is not allowed to use the bot.")
        await query.answer(results=[],
                           cache_time=0,
                           switch_pm_text='Unauthorized user',
                           switch_pm_parameter="unauthorized")
        return

    if AUTH_CHANNEL and not await is_subscribed(bot, query):
        logger.info(f"User {query.from_user.id} is not subscribed to the required channel.")
        await query.answer(results=[],
                           cache_time=0,
                           switch_pm_text='You must subscribe to use this bot',
                           switch_pm_parameter="subscribe")
        return

    results = []
    string = query.query.strip()

    offset = int(query.offset or 0)
    logger.info(f"Query offset: {offset}")

    try:
        files, next_offset, total_results = await get_search_results(
            chat_id,
            string,
            max_results=10,
            offset=offset
        )
        logger.info(f"Search results: {len(files)} found for query '{string}' (Total: {total_results}).")
    except Exception as e:
        logger.exception(f"Error fetching search results: {e}")
        await query.answer(results=[], cache_time=cache_time, switch_pm_text="Error occurred", switch_pm_parameter="error")
        return

    for idx, file in enumerate(files):
        try:
            title = file.get("file_name", "Unknown Title")
            size = get_size(file.get("file_size", 0))
            f_caption = file.get("caption", "")
            button = InlineKeyboardButton(
                text=f"Send {title}",
                callback_data=f"send_{file['file_id']}"
            )

            results.append(
                InlineQueryResultArticle(
                    id=str(idx),
                    title=title,
                    description=f"{size} - {f_caption}",
                    input_message_content=InputTextMessageContent(f"File selected: {title}"),
                    reply_markup=InlineKeyboardMarkup([[button]])
                )
            )
        except Exception as e:
            logger.exception(f"Error processing file: {file}. Exception: {e}")

    if results:
        try:
            await query.answer(
                results=results,
                is_personal=True,
                cache_time=cache_time,
                switch_pm_text=f"Results for '{string}'",
                switch_pm_parameter="start",
                next_offset=str(next_offset)
            )
        except QueryIdInvalid:
            logger.error("Query ID invalid error occurred.")
        except Exception as e:
            logger.exception(f"Error sending query answer: {e}")
    else:
        # When no results are found
        switch_pm_text = f"No results found for '{string}'."
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('Request in Support Group', url="https://t.me/iAmRashmibot")
                ]
            ]
        )
        await query.answer(
            results=[],
            is_personal=True,
            cache_time=cache_time,
            switch_pm_text=switch_pm_text,
            switch_pm_parameter="no_results"
        )
        await query.message.reply_text(
            text=f"We couldn't find any results for '{string}'. You can request the movie in our [Support Group](https://t.me/iAmRashmibot).",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )

# Handle callback queries when user selects a file
@Client.on_callback_query()
async def handle_callback_query(bot, query: CallbackQuery):
    """Handle user selecting a file from the inline query results."""
    file_id = query.data.replace("send_", "")  # Extract file_id from callback_data
    user_id = query.from_user.id

    # Retrieve file information based on file_id
    file = await get_file_by_id(file_id)  # Your method to get file info by file_id

    if not file:
        await bot.answer_callback_query(query.id, text="File not found!", show_alert=True)
        return

    try:
        # Send the selected file
        title = file.get("file_name", "Unknown Title")
        size = get_size(file.get("file_size", 0))
        caption = file.get("caption", title)

        # Send the file (video/document)
        if file.get("mime_type", "").startswith("video/"):
            message = await bot.send_video(user_id, file["file_id"], caption=caption)
        else:
            message = await bot.send_document(user_id, file["file_id"], caption=caption)

        # Delete the file after 10 minutes
        await asyncio.sleep(DELETE_FILE_DELAY)
        await bot.delete_message(user_id, message.message_id)
        logger.info(f"File {title} deleted after 10 minutes.")

        await bot.answer_callback_query(query.id, text="File sent and will be deleted after 10 minutes.", show_alert=True)

    except Exception as e:
        logger.exception(f"Error sending file: {e}")
        await bot.answer_callback_query(query.id, text="Error occurred while sending the file.", show_alert=True)
