from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode
import re
import logging

# Initialize the logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@Client.on_message(filters.command("ppost"))
async def post_reply(client, message):
    command_parts = message.text.split()
    if len(command_parts) < 2 or not message.reply_to_message:
        logger.warning("Command is missing required parts or no reply message found.")
        await message.reply("Please provide a valid channel ID and reply to a message using /ppost <channel_id>.")
        return

    channel_id = command_parts[1]
    logger.info(f"Extracted channel_id: {channel_id}")

    if not channel_id.startswith("-100"):
        logger.error(f"Invalid channel ID: {channel_id}")
        await message.reply("Invalid channel ID. Please provide a valid channel ID starting with '-100'.")
        return

    replied_message = message.reply_to_message
    caption = replied_message.caption or replied_message.text or ""
    logger.info(f"Replied message caption: {caption}")

    inline_buttons = extract_buttons_from_caption(caption)
    caption_without_buttons = remove_button_links(caption)
    reply_markup = InlineKeyboardMarkup(inline_buttons) if inline_buttons else None

    try:
        if replied_message.photo:
            logger.info("Replied message is a photo. Sending to the channel...")
            await client.send_photo(
                chat_id=channel_id,
                photo=replied_message.photo.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        elif replied_message.video:
            logger.info("Replied message is a video. Sending to the channel...")
            await client.send_video(
                chat_id=channel_id,
                video=replied_message.video.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        elif replied_message.document:
            logger.info("Replied message is a document. Sending to the channel...")
            await client.send_document(
                chat_id=channel_id,
                document=replied_message.document.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        elif replied_message.text:
            logger.info("Replied message is text. Sending to the channel...")
            await client.send_message(
                chat_id=channel_id,
                text=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            logger.error("Unsupported media type in the replied message.")
            await client.send_message(
                chat_id=channel_id,
                text="Unsupported media type to forward.",
            )

        await message.reply(f"Message posted to channel {channel_id} successfully!")
        logger.info(f"Message posted to channel {channel_id} successfully.")
    except Exception as e:
        logger.exception(f"Failed to post the message. Error: {str(e)}")
        await message.reply(f"Failed to post the message. Error: {str(e)}")
def extract_buttons_from_caption(caption: str):
    """
    Extracts buttons in the format: [button text](buttonurl://url)
    """
    button_links = []
    pattern = r"([^]+)buttonurl:(https?:\/\/[^\s]+)"
    matches = re.findall(pattern, caption)
    logger.info(f"Button extraction pattern: {pattern}")
    logger.info(f"Matches found: {matches}")

    for text, url in matches:
        logger.info(f"Creating button: {text} - {url}")
        button_links.append([InlineKeyboardButton(text=text, url=url)])

    logger.info(f"Extracted inline buttons: {button_links}")
    return button_links

def remove_button_links(caption: str):
    """
    Removes button links in the format: [button text](buttonurl://url) from the caption.
    """
    pattern = r"([^]+)buttonurl:(https?:\/\/[^\s]+)"
    cleaned_caption = re.sub(pattern, "", caption).strip()
    logger.info(f"Cleaned caption: {cleaned_caption}")
    return cleaned_caption
