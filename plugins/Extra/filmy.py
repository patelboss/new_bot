from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode
import re
import logging

# Setup logger for detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@Client.on_message(filters.command("ppost"))
async def post_reply(client, message):
    # Ensure the user provided a channel ID and replied to a message
    logger.info(f"Received /ppost command: {message.text}")
    
    command_parts = message.text.split()
    if len(command_parts) < 2 or not message.reply_to_message:
        await message.reply("Please provide a valid channel ID and reply to a message using /ppost <channel_id>.")
        logger.error("Invalid command or no replied message found.")
        return

    channel_id = command_parts[1]  # Extract the channel ID from the command
    logger.info(f"Extracted channel_id: {channel_id}")

    # Ensure channel_id is valid (e.g., it starts with '-100' for Telegram channels)
    if not channel_id.startswith("-100"):
        await message.reply("Invalid channel ID. Please provide a valid channel ID starting with '-100'.")
        logger.error(f"Invalid channel ID: {channel_id}")
        return

    # Get the original message's media or text
    replied_message = message.reply_to_message
    caption = replied_message.text if replied_message.text else "No caption provided."
    logger.info(f"Replied message caption: {caption}")

    # Extract inline buttons separately
    inline_buttons = extract_buttons_from_caption(caption)
    logger.info(f"Extracted inline buttons: {inline_buttons}")

    # Remove button-related parts from the caption
    caption_without_buttons = remove_button_links(caption)
    logger.info(f"Caption without buttons: {caption_without_buttons}")

    # Prepare the inline keyboard for buttons
    reply_markup = InlineKeyboardMarkup(inline_buttons) if inline_buttons else None
    logger.info(f"Prepared reply_markup: {reply_markup}")

    try:
        if replied_message.photo:
            # If the replied message is a photo
            logger.info(f"Sending photo with caption: {caption_without_buttons}")
            await client.send_photo(
                chat_id=channel_id,
                photo=replied_message.photo.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        elif replied_message.text:
            # If the replied message is text
            logger.info(f"Sending text message: {caption_without_buttons}")
            await client.send_message(
                chat_id=channel_id,
                text=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        elif replied_message.document:
            # If the replied message is a document
            logger.info(f"Sending document with caption: {caption_without_buttons}")
            await client.send_document(
                chat_id=channel_id,
                document=replied_message.document.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            # Handle unsupported media types
            logger.error("Unsupported media type in replied message.")
            await client.send_message(
                chat_id=channel_id,
                text="Unsupported media type to forward",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        await message.reply(f"Message posted to channel {channel_id} successfully!")
        logger.info(f"Message posted to channel {channel_id} successfully.")
    except Exception as e:
        await message.reply(f"Failed to post the message. Error: {str(e)}")
        logger.error(f"Error occurred while posting the message: {str(e)}")


def extract_buttons_from_caption(caption: str):
    """
    Extracts buttons in the format: [button text](button url)
    and returns them as InlineKeyboardButton objects.

    Args:
        caption (str): The caption containing button information.

    Returns:
        List[List[InlineKeyboardButton]]: A list of inline buttons.
    """
    button_links = []
    pattern = r"([^]+)(https?://[^]+)"  # Custom pattern for extracting buttons

    # Find all matches for button text and URL
    matches = re.findall(pattern, caption)
    logger.info(f"Button extraction pattern: {pattern}")
    logger.info(f"Matches found: {matches}")

    for text, url in matches:
        logger.info(f"Creating button: {text} - {url}")
        button_links.append([InlineKeyboardButton(text=text, url=url)])  # Create a button for each match

    return button_links


def remove_button_links(caption: str):
    """
    Removes button-related text (e.g., [button text]:(button url)) from the caption.

    Args:
        caption (str): The caption to remove button links from.

    Returns:
        str: The caption with button information removed.
    """
    logger.info(f"Removing button links from caption: {caption}")
    clean_caption = re.sub(r"([^]+)(https?://[^]+)", "", caption).strip()
    logger.info(f"Cleaned caption: {clean_caption}")
    return clean_caption
