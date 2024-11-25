from pyrogram import Client, emoji, filters
from pyrogram.errors.exceptions.bad_request_400 import QueryIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument, InlineQuery
from database.ia_filterdb import get_search_results
from utils import is_subscribed, get_size, temp
from info import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION
from database.connections_mdb import active_connection
import asyncio

cache_time = 0 if AUTH_USERS or AUTH_CHANNEL else CACHE_TIME

async def inline_users(query: InlineQuery):
    """Check if the user is allowed to use the inline query."""
    if AUTH_USERS:
        if query.from_user and query.from_user.id in AUTH_USERS:
            return True
        else:
            return False
    return query.from_user and query.from_user.id not in temp.BANNED_USERS

async def delete_message_after_delay(bot, user_id, message_id, delay=600):
    """Deletes a message after the specified delay (default is 10 minutes)."""
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(user_id, message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

@Client.on_inline_query()
async def answer(bot, query):
    """Show search results for the given inline query."""
    chat_id = await active_connection(str(query.from_user.id))

    if not await inline_users(query):
        await query.answer(results=[],
                           cache_time=0,
                           switch_pm_text='Unauthorized user',
                           switch_pm_parameter="unauthorized")
        return

    if AUTH_CHANNEL and not await is_subscribed(bot, query):
        await query.answer(results=[],
                           cache_time=0,
                           switch_pm_text='You must subscribe to use this bot',
                           switch_pm_parameter="subscribe")
        return

    results = []
    if '|' in query.query:
        string, file_type = query.query.split('|', maxsplit=1)
        string = string.strip()
        file_type = file_type.strip().lower()
    else:
        string = query.query.strip()
        file_type = None

    offset = int(query.offset or 0)

    reply_markup = get_reply_markup(query=string)

    try:
        files, next_offset, total_results = await get_search_results(
            chat_id,
            string,
            file_type=file_type,
            max_results=10,
            offset=offset
        )
    except Exception as e:
        await query.answer(results=[], cache_time=cache_time, switch_pm_text="Error occurred", switch_pm_parameter="error")
        return

    for file in files:
        try:
            title = file.get("file_name", "Unknown Title")
            size = get_size(file.get("file_size", 0))
            f_caption = file.get("caption", "")
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(
                        file_name=title,
                        file_size=size,
                        file_caption=f_caption
                    )
                except Exception:
                    pass
            if not f_caption:
                f_caption = title

            results.append(
                InlineQueryResultCachedDocument(
                    title=title,
                    document_file_id=file["file_id"],
                    caption=f_caption,
                    description=f"Size: {size}\nType: {file.get('file_type', 'Unknown')}",
                    reply_markup=reply_markup
                )
            )
        except Exception:
            continue

    if results:
        switch_pm_text = f"{emoji.FILE_FOLDER} Results - {total_results}"
        if string:
            switch_pm_text += f" for '{string}'"
        try:
            query_result = await query.answer(
                results=results,
                is_personal=True,
                cache_time=cache_time,
                switch_pm_text=switch_pm_text,
                switch_pm_parameter="start",
                next_offset=str(next_offset)
            )
            
            # Start a task to delete the file after 10 minutes (if sent)
            if query_result:
                message_id = query_result.result_id  # The message sent with the results
                await delete_message_after_delay(bot, query.from_user.id, message_id, 600)
                
        except QueryIdInvalid:
            pass
    else:
        # When no results are found
        switch_pm_text = f"{emoji.CROSS_MARK} No results"
        if string:
            switch_pm_text += f" for '{string}'"

        await query.answer(
            results=[],
            is_personal=True,
            cache_time=cache_time,
            switch_pm_text=switch_pm_text,
            switch_pm_parameter="no_results"
        )

        # Send message about support group when no results
        support_group_url = "https://t.me/iAmRashmibot"  # Updated with your support group link
        await query.message.reply_text(
            text=f"We couldn't find any results for '{string}'. You can request the movie in our [Support Group]({support_group_url}).",
            disable_web_page_preview=True
        )

def get_reply_markup(query):
    """Generate reply markup for inline results."""
    buttons = [
        [
            InlineKeyboardButton('Search again', switch_inline_query_current_chat=query)
        ]
    ]
    return InlineKeyboardMarkup(buttons)  # Fixed unmatched ']'
