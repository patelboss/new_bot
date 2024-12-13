from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
import re
import logging
import random
import asyncio

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Sticker IDs
sticker_ids = [
    "CAACAgIAAxkBAAItAmdbY-9IY20HNfLFeeboOOex74M0AAL9AQACFkJrCqSvYaKm6vLJHgQ",
    "CAACAgIAAxkBAAIs1GdbWBhGfsD2U3Z2pGiR-d64z08mAAJvAAPb234AAZlbUKh7k4B0HgQ",
    "CAACAgIAAxkBAAIsz2dbV_286mg26Vx67MOWmyG-WvK7AAJtAAPb234AAXUe7IXy-0SlHgQ",
    "CAACAgQAAxkBAAIs_mdbY-Zk1JR7yRLoWsi8NbJEMFerAALVGAACOqGIUIer-Up9iv5aHgQ",
    "CAACAgQAAxkBAAIs-mdbY96brNo0bbqiAT0h9aHmGjfZAAISDgACQln9BFRvgD6jmKybHgQ"
]

def get_random_sticker():
    return random.choice(sticker_ids)


from pyrogram import Client
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, ChatAdminRequired
from pyrogram.types import InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus, ParseMode

async def is_user_admin_or_owner(client: Client, channel_id: str, user_id: int):
    """
    Check if the user is an admin or the owner of the channel.
    Returns:
        - True if the user is an admin or owner
        - False if the user is neither admin nor owner
        - Error message if an exception occurs
    """
    try:
        # Get the chat member information
        member = await client.get_chat_member(channel_id, user_id)
        
        # Check if the member is an admin or the owner
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return True
        
        return False

    except UserNotParticipant:
        return {"error": "Bot is not a member of the channel"}
    
    except PeerIdInvalid:
        return {"error": "The bot's access to the channel is invalid. Please add the bot to the group again. If the bot is already in the group, try removing and re-adding it."}

    except ChatAdminRequired:
        return {"error": "The bot needs to be an admin in the group & channel to perform this action."}
    
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

@Client.on_message(filters.command("tpost"))
async def cpost(client, message):
    command_parts = message.text.split()
    if len(command_parts) < 2 or not message.reply_to_message:
        await message.reply(
            "<b>Please provide a valid channel ID and reply to a message using /cpost <channel_id>.\nUse /chelp to know about formatting\nIf you Don't Know Your Channel Id\nJust Forward Me Any Message From Your Channel And Reply That Message /id .</b>", 
            parse_mode=ParseMode.HTML
        )
        return

    channel_id = command_parts[1]

    if not channel_id.startswith("-100"):
        await message.reply(
            "<b>Invalid channel ID. Please provide a valid channel ID starting with '-100'.</b>", 
            parse_mode=ParseMode.HTML
        )
        return

    # Check if the user is admin or owner of the target channel
    user_id = message.from_user.id
    result = await is_user_admin_or_owner(client, channel_id, user_id)

    if isinstance(result, bool):
        if not result:
            await message.reply("<b>You don't have permission to post in this channel.</b>", parse_mode=ParseMode.HTML)
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
            await message.reply("<b>Unsupported media type to forward.</b>", parse_mode=ParseMode.HTML)

        await message.reply(f"Message posted to channel {channel_id} successfully!")
    except Exception as e:
        await message.reply(f"Failed to post the message. Error: {str(e)}")

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
