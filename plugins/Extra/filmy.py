from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup
from pyrogram.enums import ParseMode, ChatMemberStatus
import random
import asyncio
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Sticker IDs
sticker_ids = [
    "CAACAgUAAxkBAAEBgq9hJ6PmdQ9HRgmxkj_vu8R6DbD8FQACwQoAAlv_dlxK3_P-cMy4el_9MwE",
    "CAACAgUAAxkBAAEBgqVhJ6PmbWqI_hggjjz5qx3JmtDiHEwACwwoAAlv_dllzEkeX44X7UeyOMeQ",
    "CAACAgIAAxkBAAIs1GdbWBhGfsD2U3Z2pGiR-d64z08mAAJvAAPb234AAZlbUKh7k4B0HgQ",
    "CAACAgIAAxkBAAIsz2dbV_286mg26Vx67MOWmyG-WvK7AAJtAAPb234AAXUe7IXy-0SlHgQ"
]

def get_random_sticker():
    return random.choice(sticker_ids)


@Client.on_message(filters.command("tpost"))
async def channel_post(client, message):
    random_sticker = get_random_sticker()
    try:
        m = await message.reply_sticker(random_sticker)
        await asyncio.sleep(3)
        await m.delete()
    except Exception as e:
        await message.reply(f"Failed to send sticker: {e}")
        return

    command_parts = message.text.split()
    if len(command_parts) < 2 or not message.reply_to_message:
        await message.reply("Provide a valid channel ID and reply to a message using /cpost <channel_id>.")
        return

    channel_id = command_parts[1]
    if not channel_id.startswith("-100"):
        await message.reply("Invalid channel ID. It must start with '-100'.")
        return

    user_id = message.from_user.id
    if not await is_user_admin_or_owner(client, channel_id, user_id):
        await message.reply("You don't have permission to post in this channel.")
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
                reply_markup=reply_markup
            )
        elif replied_message.video:
            await client.send_video(
                chat_id=channel_id,
                video=replied_message.video.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        elif replied_message.document:
            await client.send_document(
                chat_id=channel_id,
                document=replied_message.document.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        elif replied_message.text:
            await client.send_message(
                chat_id=channel_id,
                text=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            await message.reply("Unsupported media type.")
        await message.reply(f"Message posted to channel {channel_id} successfully!")
    except Exception as e:
        await message.reply(f"Failed to post the message: {e}")

async def is_user_admin_or_owner(client, channel_id, user_id):
    """
    Check if the user is an admin or the owner of the channel.
    Returns True if the user is an admin or owner, False otherwise.
    """
    try:
        # Get the chat member information
        member = await client.get_chat_member(channel_id, user_id)
        
        # Check if the member is an admin or the owner
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return True
        return False
    except Exception as e:
        # Handle any errors (e.g., user is not a member of the channel)
        #logger.error(f"Error checking user permissions: {str(e)}")
        return False


def extract_buttons_from_caption(caption: str):
    """
    Extracts buttons in the format: {BUTTON_TEXT}-{URL}
    """
    button_links = []
    pattern = r"\{(.*?)\}\-{(https?:\/\/[^\s]+)}"  # Correct pattern to match button text and URL
#    logger.info(f"Button extraction pattern: {pattern}")
    
    # Using re.findall() to find all matches
    matches = re.findall(pattern, caption)
#    logger.info(f"Matches found: {matches}")
    
    for text, url in matches:
 #       logger.info(f"Creating button: {text} - {url}")
        button_links.append([InlineKeyboardButton(text=text, url=url)])
    
  #  logger.info(f"Extracted inline buttons: {button_links}")
    return button_links

def remove_button_links(caption: str):
    """
    Removes button links in the format: {BUTTON_TEXT}-{URL} from the caption
    """
    pattern = r"\{(.*?)\}\-{(https?:\/\/[^\s]+)}"
    cleaned_caption = re.sub(pattern, "", caption).strip()
    return cleaned_caption
