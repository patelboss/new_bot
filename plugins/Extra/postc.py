from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import re
from pyrogram.enums import ParseMode

@Client.on_message(filters.command("cpost"))
async def post_reply(client, message):
    user_id = message.from_user.id

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

    # Prepare inline buttons if any
    inline_buttons = None
    if button_links:
        # Create rows of buttons (Telegram allows max 8 buttons per row)
        rows = [
            [InlineKeyboardButton(text=link["text"], url=link["url"])] for link in button_links
        ]
        inline_buttons = InlineKeyboardMarkup(rows)

    # Send message with inline buttons
    try:
        if replied_message.photo:
            # If the replied message is a photo
            await client.send_photo(
                channel_id,
                replied_message.photo.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=inline_buttons
            )
        elif replied_message.text:
            # If the replied message is text
            await client.send_message(
                channel_id,
                caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=inline_buttons
            )
        else:
            # Handle other media types (audio, video, etc.) if needed
            await client.send_message(
                channel_id,
                "Unsupported media type to forward",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=inline_buttons
            )
        await message.reply(f"Message posted to channel {channel_id} successfully!")
    except Exception as e:
        await message.reply(f"Failed to post the message. Error: {str(e)}")


def parse_buttons_from_caption(caption: str):
    """
    Parse markdown-style links from the caption and convert them into buttons.
    """
    button_links = []
    pattern = r"(.*?)(https?://.*?)"  # Correct markdown-style link pattern

    matches = re.findall(pattern, caption)
    for text, url in matches:
        button_links.append({"text": text, "url": url})

    return button_links


def remove_markdown_links(caption: str):
    """
    Remove markdown-style links from the caption text.
    """
    return re.sub(r"(.*?)(https?://.*?)", "", caption)
