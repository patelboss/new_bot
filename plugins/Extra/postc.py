from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, ChatAdminRequired
from plugins.Extra.Cscript import TEXTS
import random
import re

# ------------------------ Command Handler ------------------------

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

    # Check if the user is admin or owner of the target channel
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

        await message.reply(TEXTS["post_success"].format(channel_id=channel_id), parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply(TEXTS["failed_to_post"].format(error=str(e)), parse_mode=ParseMode.HTML)
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

    # Check if the user is admin or owner of the target channel
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

        await message.reply(TEXTS["post_success"].format(channel_id=channel_id), parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply(TEXTS["failed_to_post"].format(error=str(e)), parse_mode=ParseMode.HTML)


# ------------------------ Button Extraction and Caption Removal ------------------------

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
