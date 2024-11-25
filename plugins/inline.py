import logging
from pyrogram import Client, emoji, filters
from pyrogram.errors.exceptions.bad_request_400 import QueryIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument, InlineQuery
from database.ia_filterdb import *
from utils import is_subscribed, get_size, temp
from info import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION
from database.connections_mdb import active_connection

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
cache_time = 0 if AUTH_USERS or AUTH_CHANNEL else CACHE_TIME

async def inline_users(query: InlineQuery):
    logger.info(f"Checking access for user: {query.from_user.id}")
    if AUTH_USERS:
        if query.from_user and query.from_user.id in AUTH_USERS:
            logger.info(f"User {query.from_user.id} is authorized.")
            return True
        else:
            logger.warning(f"Unauthorized access attempt by user {query.from_user.id}")
            return False
    if query.from_user and query.from_user.id not in temp.BANNED_USERS:
        logger.info(f"User {query.from_user.id} is not banned.")
        return True
    logger.warning(f"User {query.from_user.id} is banned.")
    return False

@Client.on_inline_query()
async def answer(bot, query):
    """Show search results for given inline query"""
    logger.info(f"Inline query received from user {query.from_user.id}: {query.query}")
    chat_id = await active_connection(str(query.from_user.id))
    logger.debug(f"Active connection for user {query.from_user.id}: {chat_id}")
    
    if not await inline_users(query):
        logger.info(f"Access denied for user {query.from_user.id}. Sending restricted message.")
        await query.answer(results=[],
                           cache_time=0,
                           switch_pm_text='okDa',
                           switch_pm_parameter="hehe")
        return

    if AUTH_CHANNEL and not await is_subscribed(bot, query):
        logger.info(f"User {query.from_user.id} is not subscribed to the required channel.")
        await query.answer(results=[],
                           cache_time=0,
                           switch_pm_text='You have to subscribe to my channel to use the bot',
                           switch_pm_parameter="subscribe")
        return

    results = []
    if '|' in query.query:
        string, file_type = query.query.split('|', maxsplit=1)
        string = string.strip()
        file_type = file_type.strip().lower()
        logger.debug(f"Query split into string: {string}, file_type: {file_type}")
    else:
        string = query.query.strip()
        file_type = None
        logger.debug(f"Query string: {string}")

    offset = int(query.offset or 0)
    logger.info(f"Query offset: {offset}")
    reply_markup = get_reply_markup(query=string)
    
    try:
        files, next_offset, total = await get_search_results(
            chat_id,
            string,
            file_type=file_type,
            max_results=10,
            offset=offset
        )
        logger.info(f"Search results: {total} found for query '{string}'")
    except Exception as e:
        logger.error(f"Error while fetching search results: {e}")
        files, next_offset, total = [], 0, 0

    for file in files:
        title = file.file_name
        size = get_size(file.file_size)
        f_caption = file.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(
                    file_name='' if title is None else title,
                    file_size='' if size is None else size,
                    file_caption='' if f_caption is None else f_caption
                )
            except Exception as e:
                logger.exception(f"Error formatting custom caption: {e}")
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{file.file_name}"
        results.append(
            InlineQueryResultCachedDocument(
                title=file.file_name,
                document_file_id=file.file_id,
                caption=f_caption,
                description=f'Size: {get_size(file.file_size)}\nType: {file.file_type}',
                reply_markup=reply_markup
            )
        )

    if results:
        switch_pm_text = f"{emoji.FILE_FOLDER} Results - {total}"
        if string:
            switch_pm_text += f" for {string}"
        try:
            await query.answer(
                results=results,
                is_personal=True,
                cache_time=cache_time,
                switch_pm_text=switch_pm_text,
                switch_pm_parameter="start",
                next_offset=str(next_offset)
            )
            logger.info(f"Query results sent to user {query.from_user.id}")
        except QueryIdInvalid:
            logger.warning(f"Query ID invalid for user {query.from_user.id}")
        except Exception as e:
            logger.exception(f"Error sending query results: {e}")
    else:
        switch_pm_text = f'{emoji.CROSS_MARK} No results'
        if string:
            switch_pm_text += f' for "{string}"'
        logger.info(f"No results found for query: {string}")
        await query.answer(
            results=[],
            is_personal=True,
            cache_time=cache_time,
            switch_pm_text=switch_pm_text,
            switch_pm_parameter="okay"
        )

def get_reply_markup(query):
    logger.debug(f"Generating reply markup for query: {query}")
    buttons = [
        [
            InlineKeyboardButton('Search again', switch_inline_query_current_chat=query)
        ]
    ]
    return InlineKeyboardMarkup(buttons)
