from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode
from plugins.Extra.Cscript import TEXTS
from database.stats import save_user_post_data, save_channel_stats, get_channel_data, get_user_post_data
from info import ADMINS
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, ChatAdminRequired
from plugins.Extra.Cscript import TEXTS
import random
import re
# ------------------------ Command Handler ------------------------

@Client.on_message(filters.command("ppost"))
async def ppost(client, message):
    command_parts = message.text.split()
    
    if len(command_parts) < 2 or not message.reply_to_message:
        await message.reply(TEXTS["no_message_to_post"], parse_mode=ParseMode.HTML)
        return

    channel_id = command_parts[1]

    if not channel_id.startswith("-100"):
        await message.reply(TEXTS["invalid_channel_id"], parse_mode=ParseMode.HTML)
        return

    user_id = message.from_user.id
    result = await is_user_admin_or_owner(client, channel_id, user_id)

    if isinstance(result, bool):
        if not result:
            await message.reply(TEXTS["permission_denied"], parse_mode=ParseMode.HTML)
            return
    elif isinstance(result, dict) and "error" in result:
        await message.reply(f"<b>{result['error']}</b>", parse_mode=ParseMode.HTML)
        return

    replied_message = message.reply_to_message
    caption = replied_message.caption or replied_message.text or ""
    
    inline_buttons = extract_buttons_from_caption(caption)
    caption_without_buttons = remove_button_links(caption)
    reply_markup = InlineKeyboardMarkup(inline_buttons) if inline_buttons else None

    try:
        if replied_message.photo:
            await client.send_photo(
                chat_id=channel_id,
                photo=replied_message.photo.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                protect_content=True
            )
        elif replied_message.video:
            await client.send_video(
                chat_id=channel_id,
                video=replied_message.video.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                protect_content=True
            )
        elif replied_message.document:
            await client.send_document(
                chat_id=channel_id,
                document=replied_message.document.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                protect_content=True
            )
        elif replied_message.text:
            await client.send_message(
                chat_id=channel_id,
                text=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                protect_content=True
                
            )
        else:
            await message.reply(TEXTS["unsupported_media"], parse_mode=ParseMode.HTML)

        # Save user post data and channel stats
        channel_url = f"https://t.me/{channel_id}"  # Assuming the URL is derived from the channel ID
        await save_user_post_data(message.from_user.id, channel_id)
        await save_channel_stats(channel_id, message.from_user.id, url=channel_url)

        await message.reply(TEXTS["post_success"].format(channel_id=channel_id), parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply(TEXTS["failed_to_post"].format(error=str(e)), parse_mode=ParseMode.HTML)



@Client.on_message(filters.command("cpost"))
async def cpost(client, message):
    command_parts = message.text.split()
    
    if len(command_parts) < 2 or not message.reply_to_message:
        await message.reply(TEXTS["no_message_to_post"], parse_mode=ParseMode.HTML)
        return

    channel_id = command_parts[1]

    if not channel_id.startswith("-100"):
        await message.reply(TEXTS["invalid_channel_id"], parse_mode=ParseMode.HTML)
        return

    user_id = message.from_user.id
    result = await is_user_admin_or_owner(client, channel_id, user_id)

    if isinstance(result, bool):
        if not result:
            await message.reply(TEXTS["permission_denied"], parse_mode=ParseMode.HTML)
            return
    elif isinstance(result, dict) and "error" in result:
        await message.reply(f"<b>{result['error']}</b>", parse_mode=ParseMode.HTML)
        return

    replied_message = message.reply_to_message
    caption = replied_message.caption or replied_message.text or ""
    
    inline_buttons = extract_buttons_from_caption(caption)
    caption_without_buttons = remove_button_links(caption)
    reply_markup = InlineKeyboardMarkup(inline_buttons) if inline_buttons else None

    try:
        if replied_message.photo:
            await client.send_photo(
                chat_id=channel_id,
                photo=replied_message.photo.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        elif replied_message.video:
            await client.send_video(
                chat_id=channel_id,
                video=replied_message.video.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        elif replied_message.document:
            await client.send_document(
                chat_id=channel_id,
                document=replied_message.document.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        elif replied_message.text:
            await client.send_message(
                chat_id=channel_id,
                text=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        else:
            await message.reply(TEXTS["unsupported_media"], parse_mode=ParseMode.HTML)

        # Save user post data and channel stats
        channel_url = f"https://t.me/{channel_id}"  # Assuming the URL is derived from the channel ID
        await save_user_post_data(message.from_user.id, channel_id)
        await save_channel_stats(channel_id, message.from_user.id, url=channel_url)

        await message.reply(TEXTS["post_success"].format(channel_id=channel_id), parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply(TEXTS["failed_to_post"].format(error=str(e)), parse_mode=ParseMode.HTML)
                
# Command to fetch channel stats
@Client.on_message(filters.command("cstats"))
async def cstats(client, message):
    if message.from_user.id not in ADMINS:
        await message.reply(TEXTS["admin_only"], parse_mode=ParseMode.HTML)
        return

    command_parts = message.text.split()
    if len(command_parts) < 2:
        await message.reply(TEXTS["channel_not_specified"], parse_mode=ParseMode.HTML)
        return

    channel_id = command_parts[1]

    # Fetch channel data
    channel_data = await get_channel_data(channel_id)
    if not channel_data:
        await message.reply(TEXTS["channel_not_found"], parse_mode=ParseMode.HTML)
        return

    await message.reply(TEXTS["channel_stats"].format(
        channel_id=channel_data['channel_id'],
        first_added_date=channel_data['first_added_date'],
        member_count=channel_data['member_count'],
        average_posts_per_day=channel_data['average_posts_per_day']
    ), parse_mode=ParseMode.HTML)

# Command to fetch user post data
@Client.on_message(filters.command("cuserinfo"))
async def cuserinfo(client, message):
    if message.from_user.id not in ADMINS:
        await message.reply(TEXTS["admin_only"], parse_mode=ParseMode.HTML)
        return

    command_parts = message.text.split()
    if len(command_parts) < 2:
        await message.reply(TEXTS["user_not_specified"], parse_mode=ParseMode.HTML)
        return

    user_id = int(command_parts[1])

    # Fetch user post data
    user_data = await get_user_post_data(user_id)
    if not user_data:
        await message.reply(TEXTS["user_not_found"], parse_mode=ParseMode.HTML)
        return

    # Format the user post data
    post_details = "\n".join([f"Channel: {data['channel_id']} - Posts: {data['post_count']}" for data in user_data])

    await message.reply(TEXTS["user_post_data"].format(user_id=user_id, posts=post_details), parse_mode=ParseMode.HTML)

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
import asyncio
from plugins.Extra.Cscript import TEXTS  # Import the TEXTS dictionary

@Client.on_message(filters.command("chelp"))
async def chelp(client, message):
    # Use the imported texts directly from TEXTS dictionary
    m = await message.reply_sticker(TEXTS["STICKER_ID"])  # Send the sticker
    await asyncio.sleep(2)  # Wait for 2 seconds
    await m.delete()  # Delete the sticker message
    await message.reply(TEXTS["HELP_TEXT"], parse_mode=ParseMode.HTML)  # Send the help text

async def is_user_admin_or_owner(client, chat_id, user_id):
    """
    Check if the given user is an admin or the owner of a chat (channel or group).

    Args:
        client (Client): The Pyrogram client instance.
        chat_id (str): The ID of the chat to check.
        user_id (int): The ID of the user to check.

    Returns:
        bool: True if the user is an admin or the owner, False otherwise.
        dict: Error message if something goes wrong.
    """
    try:
        # Get chat member information
        member = await client.get_chat_member(chat_id, user_id)

        # Check if the user is an admin or the owner
        if member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
            return True
        return False
    except UserNotParticipant:
        return {"error": TEXTS["error_messages"]["UserNotParticipant"]}
    except PeerIdInvalid:
        return {"error": TEXTS["error_messages"]["PeerIdInvalid"]}
    except ChatAdminRequired:
        return {"error": TEXTS["error_messages"]["ChatAdminRequired"]}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def extract_buttons_from_caption(caption: str):
    """
    Extracts buttons in the format: {BUTTON_TEXT}-{URL}
    """
    button_links = []
    pattern = r"\{(.*?)\}\-{(https?:\/\/[^\s]+)}"
    
    # Using re.findall() to find all matches
    matches = re.findall(pattern, caption)
    
    for text, url in matches:
        button_links.append([InlineKeyboardButton(text=text, url=url)])
    
    return button_links


def remove_button_links(caption: str):
    """
    Removes button links in the format: {BUTTON_TEXT}-{URL} from the caption
    """
    pattern = r"\{(.*?)\}\-{(https?:\/\/[^\s]+)}"
    cleaned_caption = re.sub(pattern, "", caption).strip()
    return cleaned_caption

def get_random_sticker():
    return random.choice(TEXTS["random_sticker"])
