from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import re
from pyrogram.enums import ParseMode

@Client.on_message(filters.command("ppost"))
async def post_reply(client, message):
    # Ensure the user provided a channel ID and replied to a message
    command_parts = message.text.split()
    if len(command_parts) < 2 or not message.reply_to_message:
        await message.reply("Please provide a valid channel ID and reply to a message using /ppost <channel_id>.")
        return

    channel_id = command_parts[1]  # Extract the channel ID from the command

    # Ensure channel_id is valid (e.g., it starts with '-100' for Telegram channels)
    if not channel_id.startswith("-100"):
        await message.reply("Invalid channel ID. Please provide a valid channel ID starting with '-100'.")
        return

    # Get the original message's media or text
    replied_message = message.reply_to_message
    caption = replied_message.text if replied_message.text else "No caption provided."

    # Parse the caption and extract markdown-style links
    button_links = parse_buttons_from_caption(caption)

    # Replace markdown links in the caption with placeholders
    caption_without_buttons = remove_markdown_links(caption)

    # Prepare inline buttons only if there are any
    inline_buttons = None
    if button_links:
        inline_buttons = InlineKeyboardMarkup(button_links)  # Properly formatted InlineKeyboardMarkup

    # Send message with inline buttons
    try:
        if replied_message.photo:
            # If the replied message is a photo
            await client.send_photo(
                chat_id=channel_id,
                photo=replied_message.photo.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=inline_buttons
            )
        elif replied_message.text:
            # If the replied message is text
            await client.send_message(
                chat_id=channel_id,
                text=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=inline_buttons
            )
        else:
            # Handle unsupported media types
            await client.send_message(
                chat_id=channel_id,
                text="Unsupported media type to forward",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=inline_buttons
            )
        await message.reply(f"Message posted to channel {channel_id} successfully!")
    except Exception as e:
        await message.reply(f"Failed to post the message. Error: {str(e)}")


def parse_buttons_from_caption(caption: str):
    """
    Parse markdown-style links from the caption and convert them into buttons.

    Args:
        caption (str): The caption containing markdown-style links.

    Returns:
        List[List[InlineKeyboardButton]]: Inline buttons structured for Telegram.
    """
    button_links = []
    pattern = r"(.*?)(https?://.*?)"  # Regex pattern for markdown links

    # Find all matches for the markdown links
    matches = re.findall(pattern, caption)
    for text, url in matches:
        button_links.append([InlineKeyboardButton(text=text, url=url)])  # Each button in a separate row

    return button_links


def remove_markdown_links(caption: str):
    """
    Remove markdown-style links from the caption text.

    Args:
        caption (str): The caption containing markdown-style links.

    Returns:
        str: Caption text without markdown links.
    """
    return re.sub(r"(.*?)(https?://.*?)", "", caption).strip()
