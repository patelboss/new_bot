from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode, ChatMemberStatus
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Assuming 'client' is your existing bot client instance
# Replace 'client' with your existing instance of pyrogram.Client in your bot

@Client.on_message(filters.command("ppost"))
async def post_reply(client, message: Message):
    user_id = message.from_user.id
    
    # Ensure the user provided a channel ID and replied to a message
    command_parts = message.text.split()

    # Check if the user has provided a channel ID and is replying to a message
    if len(command_parts) < 2 or not message.reply_to_message:
        await message.reply("Please provide a valid channel ID and reply to a message using /ppost <channel_id>.")
        return
    
    channel_id = command_parts[1]  # Extract the channel ID from the command
    
    # Ensure channel_id is valid (e.g., it starts with '-100' for Telegram channels)
    if not channel_id.startswith("-100"):
        await message.reply("Invalid channel ID. Please provide a valid channel ID starting with '-100'.")
        return
    
    # Check if the user is an admin or owner in the specified channel
    try:
        chat_member = await client.get_chat_member(channel_id, user_id)
        if chat_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            await message.reply("You must be an admin or owner in the channel to post.")
            logger.warning(f"User {user_id} is not an admin or owner in channel {channel_id}.")
            return
    except Exception as e:
        await message.reply(f"Failed to verify your role in the channel. Error: {str(e)}")
        logger.error(f"Error checking user role for {user_id} in channel {channel_id}: {e}")
        return

    # Get the original message's text
    replied_message = message.reply_to_message
    if not replied_message:
        await message.reply("Please reply to a message to rewrite and post.")
        return

    original_text = replied_message.text or ""
    if replied_message.caption:
        original_text = replied_message.caption

    # Rewrite text without watermark (no extra text or prefix)
    rewritten_text = original_text

    # Check if the original post has inline buttons
    buttons = []
    if replied_message.reply_markup:
        for row in replied_message.reply_markup.inline_keyboard:
            buttons.append([InlineKeyboardButton(text=btn.text, url=btn.url) for btn in row])

    # Send the rewritten message with inline buttons if any
    try:
        await client.send_message(
            channel_id,  # Send the message to the specified channel
            rewritten_text,  # Use the original text (no watermark or prefix)
            parse_mode=ParseMode.MARKDOWN,  # Markdown parsing mode
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None  # Add buttons if present
        )
        await message.reply(f"Message posted to channel {channel_id} successfully!")
        logger.info(f"User {user_id} successfully posted the rewritten message to channel {channel_id}.")
    except Exception as e:
        await message.reply(f"Failed to post the message. Error: {str(e)}")
        logger.error(f"Error posting message for user {user_id} to channel {channel_id}: {e}")
