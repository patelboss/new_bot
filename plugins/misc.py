
import os, logging, time
from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from info import IMDB_TEMPLATE
from utils import extract_user, get_file_id, get_poster, last_online 
from datetime import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

from pyrogram import Client, filters, enums


@Client.on_message(filters.command('id'))
async def showid(client, message):
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        # Check if the user replied to a forwarded message
        if message.reply_to_message and message.reply_to_message.forward_from_chat:
            forwarded_chat = message.reply_to_message.forward_from_chat
            if forwarded_chat.type == enums.ChatType.CHANNEL:
                # Extract details for forwarded message
                channel_name = forwarded_chat.title
                channel_id = forwarded_chat.id
                user_id = message.from_user.id
                await message.reply_text(
                    f"<b>➲ User ID:</b> <code>{user_id}</code>\n"
                    f"<b>➲ Forwarded Message From Channel ID:</b> <code>{channel_id}</code>",
                    quote=True
                )
            else:
                await message.reply_text("This message is not forwarded from a channel.", quote=True)
        else:
            # For private chat without a forwarded message
            user_id = message.chat.id
            first = message.from_user.first_name
            last = message.from_user.last_name or ""
            username = message.from_user.username
            dc_id = message.from_user.dc_id or ""
            await message.reply_text(
                f"<b>➲ First Name:</b> {first}\n"
                f"<b>➲ Last Name:</b> {last}\n"
                f"<b>➲ Username:</b> {username}\n"
                f"<b>➲ Telegram ID:</b> <code>{user_id}</code>\n"
                f"<b>➲ Data Centre:</b> <code>{dc_id}</code>",
                quote=True
            )

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        # For groups or supergroups
        if message.reply_to_message and message.reply_to_message.forward_from_chat:
            forwarded_chat = message.reply_to_message.forward_from_chat
            if forwarded_chat.type == enums.ChatType.CHANNEL:
                # Extract details for forwarded message
                channel_name = forwarded_chat.title
                channel_id = forwarded_chat.id
                user_id = message.from_user.id
                await message.reply_text(
                    f"<b>➲ User ID:</b> <code>{user_id}</code>\n"
                    f"<b>➲ Forwarded Message From Channel ID:</b> <code>{channel_id}</code>",
                    quote=True
                )
            else:
                await message.reply_text("This message is not forwarded from a channel.", quote=True)
        else:
            # General group or supergroup ID details
            _id = f"<b>➲ Chat ID:</b> <code>{message.chat.id}</code>\n"
            _id += (
                f"<b>➲ User ID:</b> "
                f"<code>{message.from_user.id if message.from_user else 'Anonymous'}</code>\n"
            )
            await message.reply_text(_id, quote=True)        


from pyrogram import Client, filters, enums
from pyrogram.errors import UserNotParticipant, RPCError
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import os


@Client.on_message(filters.command(["info"]))
async def who_is(client, message):
    status_message = await message.reply_text("`Fetching user info...`")
    await status_message.edit("`Processing user info...`")

    # Extract user ID
    from_user = None
    from_user_id = (
        message.reply_to_message.from_user.id if message.reply_to_message else message.from_user.id
    )
    try:
        from_user = await client.get_users(from_user_id)
    except Exception as error:
        await status_message.edit(str(error))
        return

    if from_user is None:
        return await status_message.edit("No valid user_id / message specified")

    # Build user information string
    message_out_str = ""
    message_out_str += f"<b>➲ First Name:</b> {from_user.first_name}\n"
    last_name = from_user.last_name or "<b>None</b>"
    message_out_str += f"<b>➲ Last Name:</b> {last_name}\n"
    message_out_str += f"<b>➲ Telegram ID:</b> <code>{from_user.id}</code>\n"
    username = from_user.username or "<b>None</b>"
    dc_id = from_user.dc_id or "[User Doesn't Have A Valid DP]"
    message_out_str += f"<b>➲ Data Centre:</b> <code>{dc_id}</code>\n"
    message_out_str += f"<b>➲ User Name:</b> @{username}\n"
    message_out_str += f"<b>➲ User 𝖫𝗂𝗇𝗄:</b> <a href='tg://user?id={from_user.id}'><b>Click Here</b></a>\n"

    # Add joined date if in a group or channel
    if message.chat.type in (enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL):
        try:
            chat_member_p = await message.chat.get_member(from_user.id)
            joined_date = (
                chat_member_p.joined_date or datetime.now()
            ).strftime("%Y.%m.%d %H:%M:%S")
            message_out_str += (
                "<b>➲ Joined this Chat on:</b> <code>"
                f"{joined_date}"
                "</code>\n"
            )
        except UserNotParticipant:
            pass

    # Add First Meet (First interaction date) - Safe handling
    try:
        if message.chat.type == enums.ChatType.PRIVATE:
            message_out_str += "<b>➲ First Meet:</b> <i>Not applicable for private chats</i>\n"
        else:
            first_meet_date = None
            async for history_message in client.get_chat_history(message.chat.id, limit=1000):
                if history_message.from_user and history_message.from_user.id == from_user.id:
                    first_meet_date = history_message.date
                    break

            if first_meet_date:
                first_meet_date_str = first_meet_date.strftime("%Y.%m.%d %H:%M:%S")
                message_out_str += f"<b>➲ First Meet:</b> <code>{first_meet_date_str}</code>\n"
            else:
                message_out_str += "<b>➲ First Meet:</b> <i>Unknown</i>\n"
    except RPCError:
        message_out_str += (
            "<b>➲ First Meet:</b> <i>Could not retrieve due to Telegram restrictions</i>\n"
        )

    # Handle user photo
    chat_photo = from_user.photo
    buttons = [[
        InlineKeyboardButton('🔐 Close', callback_data='close_data')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)

    if chat_photo:
        local_user_photo = await client.download_media(chat_photo.big_file_id)
        await message.reply_photo(
            photo=local_user_photo,
            quote=True,
            reply_markup=reply_markup,
            caption=message_out_str,
            parse_mode=enums.ParseMode.HTML,
            disable_notification=True
        )
        os.remove(local_user_photo)
    else:
        await message.reply_text(
            text=message_out_str,
            reply_markup=reply_markup,
            quote=True,
            parse_mode=enums.ParseMode.HTML,
            disable_notification=True
        )
    await status_message.delete()
    
@Client.on_message(filters.command(["imdb", 'search']))
async def imdb_search(client, message):
    if ' ' in message.text:
        k = await message.reply('Searching ImDB')
        r, title = message.text.split(None, 1)
        movies = await get_poster(title, bulk=True)
        if not movies:
            return await message.reply("No results Found")
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{movie.get('title')} - {movie.get('year')}",
                    callback_data=f"imdb#{movie.movieID}",
                )
            ]
            for movie in movies
        ]
        await k.edit('Here is what i found on IMDb', reply_markup=InlineKeyboardMarkup(btn))
    else:
        await message.reply('Give me a movie / series Name')

@Client.on_callback_query(filters.regex('^imdb'))
async def imdb_callback(bot: Client, quer_y: CallbackQuery):
    i, movie = quer_y.data.split('#')
    imdb = await get_poster(query=movie, id=True)
    btn = [
            [
                InlineKeyboardButton(
                    text=f"{imdb.get('title')}",
                    url=imdb['url'],
                )
            ]
        ]
    message = quer_y.message.reply_to_message or quer_y.message
    if imdb:
        caption = IMDB_TEMPLATE.format(
            query = imdb['title'],
            title = imdb['title'],
            votes = imdb['votes'],
            aka = imdb["aka"],
            seasons = imdb["seasons"],
            box_office = imdb['box_office'],
            localized_title = imdb['localized_title'],
            kind = imdb['kind'],
            imdb_id = imdb["imdb_id"],
            cast = imdb["cast"],
            runtime = imdb["runtime"],
            countries = imdb["countries"],
            certificates = imdb["certificates"],
            languages = imdb["languages"],
            director = imdb["director"],
            writer = imdb["writer"],
            producer = imdb["producer"],
            composer = imdb["composer"],
            cinematographer = imdb["cinematographer"],
            music_team = imdb["music_team"],
            distributors = imdb["distributors"],
            release_date = imdb['release_date'],
            year = imdb['year'],
            genres = imdb['genres'],
            poster = imdb['poster'],
            plot = imdb['plot'],
            rating = imdb['rating'],
            url = imdb['url'],
            **locals()
        )
    else:
        caption = "No Results"
    if imdb.get('poster'):
        try:
            await quer_y.message.reply_photo(photo=imdb['poster'], caption=caption, reply_markup=InlineKeyboardMarkup(btn))
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            await quer_y.message.reply_photo(photo=poster, caption=caption, reply_markup=InlineKeyboardMarkup(btn))
        except Exception as e:
            logger.exception(e)
            await quer_y.message.reply(caption, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=False)
        await quer_y.message.delete()
    else:
        await quer_y.message.edit(caption, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=False)
    await quer_y.answer()
        

        
