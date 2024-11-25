from pyrogram import Client, emoji, filters
from pyrogram.errors.exceptions.bad_request_400 import QueryIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument, InlineQuery
from database.ia_filterdb import get_search_results
from utils import is_subscribed, get_size, temp
from info import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION
from database.connections_mdb import active_connection

cache_time = 0 if AUTH_USERS or AUTH_CHANNEL else CACHE_TIME

async def inline_users(query: InlineQuery):
    """Check if the user is allowed to use the inline query."""
    if AUTH_USERS:
        if query.from_user and query.from_user.id in AUTH_USERS:
            return True
        else:
            return False
    return query.from_user and query.from_user.id not in temp.BANNED_USERS

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
            await query.answer(
                results=results,
                is_personal=True,
                cache_time=cache_time,
                switch_pm_text=switch_pm_text,
                switch_pm_parameter="start",
                next_offset=str(next_offset)
            )
        except QueryIdInvalid:
            pass
    else:
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

def get_reply_markup(query):
    """Generate reply markup for inline results."""
    buttons = [
        [
            InlineKeyboardButton('Search again', switch_inline_query_current_chat=query)
        ]
    ]
    return InlineKeyboardMarkup(buttons)
