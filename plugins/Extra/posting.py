from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import asyncio
from database.posts import save_user_channel, get_user_channels, save_post
from pyrogram.enums import ParseMode
# Store temporary data during the posting workflow
class PostSessionManager:
    _sessions = {}

    @classmethod
    def create_session(cls, user_id):
        cls._sessions[user_id] = PostSession(user_id)

    @classmethod
    def get_session(cls, user_id):
        return cls._sessions.get(user_id)

    @classmethod
    def remove_session(cls, user_id):
        if user_id in cls._sessions:
            del cls._sessions[user_id]

class PostSession:
    def __init__(self, user_id):
        self.user_id = user_id
        self.channel_ids = []
        self.channel_names = []
        self.parse_mode = "HTML"  # Default parse mode
        self.message = None
        self.buttons = None
        self.photo = None
        self.schedule_time = None
        self.step = None

    async def send_preview(self, client, channel_name):
        preview_text = (
            f"<b>Preview:</b>\n"
            f"Message: {self.message}\n"
            f"Buttons: {self.buttons}\n"
            f"Scheduled for: {self.schedule_time if self.schedule_time else 'Now'}\n"
            f"Channel: {channel_name}"
        )
        if self.photo:
            await client.send_photo(self.user_id, self.photo, caption=preview_text, parse_mode=ParseMode.HTML)
        else:
            await client.send_message(self.user_id, preview_text, parse_mode=ParseMode.HTML)

    async def post_to_channel(self, client, channel_id):
        try:
            if self.photo:
                await client.send_photo(
                    channel_id,
                    photo=self.photo,
                    caption=self.message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(self.buttons) if self.buttons else None
                )
            else:
                await client.send_message(
                    channel_id,
                    text=self.message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup(self.buttons) if self.buttons else None
                )
        except Exception as e:
            logging.error(f"Failed to post to channel {channel_id}: {e}")
            raise e

@Client.on_message(filters.command("post") & filters.private)
async def post_command(client, message):
    user_id = message.from_user.id
    user_channels = get_user_channels(user_id)

    if not user_channels:
        await message.reply(
            "You are not connected to any channel.\n"
            "Please forward a message from your channel or send its username/ID to connect."
        )
        return

    channel_names = [channel['channel_name'] for channel in user_channels]
    channel_ids = [channel['channel_id'] for channel in user_channels]

    PostSessionManager.create_session(user_id)
    session = PostSessionManager.get_session(user_id)
    session.channel_ids = channel_ids
    session.channel_names = channel_names
    session.step = "parse_mode"

    await message.reply("What is the parse mode? (HTML/Markdown/None) [Default: HTML]")

@Client.on_message(filters.private & ~filters.command("cancel_post"))
async def post_workflow(client, message):
    user_id = message.from_user.id
    session = PostSessionManager.get_session(user_id)

    if not session:
        return

    step = session.step

    if step == "parse_mode":
        session.parse_mode = message.text.upper() if message.text.upper() in ["HTML", "MARKDOWN", "NONE"] else "HTML"
        session.step = "message"
        await message.reply("Send me the message content.")
    elif step == "message":
        session.message = message.text
        session.step = "buttons"
        await message.reply("Send me button/link in HTML format or type 'None' to skip.")
    elif step == "buttons":
        session.buttons = message.text if message.text.lower() != "none" else None
        session.step = "photo"
        await message.reply("Send me a photo or type 'None' to skip.")
    elif step == "photo":
        session.photo = message.photo.file_id if message.photo else None
        session.step = "schedule"
        await message.reply("Do you want to post now or schedule? (Send 'Now' or a date like DD/MM/YYYY)")
    elif step == "schedule":
        if message.text.lower() == "now":
            session.schedule_time = None
            await session.send_preview(client, session.channel_names[0])
            await session.post_to_channel(client, session.channel_ids[0])
            await save_post(user_id, session.channel_ids[0], session.message, session.photo, session.buttons)
            await message.reply("Post sent successfully!")
            PostSessionManager.remove_session(user_id)
        else:
            try:
                session.schedule_time = datetime.strptime(message.text, '%d/%m/%Y')
                session.step = "time"
                await message.reply("Send me the time in HH:MM format (24-hour).")
            except ValueError:
                await message.reply("Invalid date format. Please send a valid date like DD/MM/YYYY.")
    elif step == "time":
        try:
            schedule_time = datetime.strptime(message.text, '%H:%M').time()
            session.schedule_time = datetime.combine(session.schedule_time, schedule_time)
            await session.send_preview(client, session.channel_names[0])
            await save_post(
                user_id, session.channel_ids[0], session.message, session.photo,
                session.buttons, session.schedule_time
            )
            await message.reply("Post scheduled successfully!")
            PostSessionManager.remove_session(user_id)
        except ValueError:
            await message.reply("Invalid time format. Please send a valid time like HH:MM.")

@Client.on_message(filters.command("cancel_post") & filters.private)
async def cancel_post(client, message):
    user_id = message.from_user.id
    if PostSessionManager.get_session(user_id):
        PostSessionManager.remove_session(user_id)
        await message.reply("Post creation process has been canceled.")
    else:
        await message.reply("No active post process to cancel.")

import logging
import asyncio
from pyrogram import Client, filters

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@Client.on_message(filters.command("connect_postchannel") & filters.private)
async def connect_post_channel(client, message):
    user_id = message.from_user.id
    try:
        await message.reply("Please forward a message from the channel or send its username/ID to connect.")
        user_response = await client.listen(message.chat.id, timeout=60)
        channel_identifier = user_response.text.strip()
        await connect_channel(client, message, channel_identifier)
    except asyncio.TimeoutError:
        await message.reply("No response received within 60 seconds. Process aborted.")
    except Exception as e:
        logging.error(f"Error connecting channel: {e}")
        await message.reply(f"Failed to connect the channel. Error: {str(e)}")
from pyrogram import Client
from pyrogram.enums import ChatType, ChatMemberStatus
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from pyrogram.enums import ChatMemberStatus, ChatType

async def connect_channel(client, message, channel_identifier):
    """
    Handle connecting a channel for a user.

    Args:
        client (pyrogram.Client): The Pyrogram client instance.
        message (pyrogram.types.Message): The message containing the user's input.
        channel_identifier (str): The identifier of the channel (ID or username).
    """
    user_id = message.from_user.id

    try:
        # Validate channel identifier format
        if not channel_identifier.startswith("-100"):
            await message.reply("Invalid channel ID. Please provide a valid ID that starts with '-100'.")
            logger.warning(f"User ID {user_id} provided an invalid channel ID: {channel_identifier}")
            return

        # Fetch channel details
        chat = await client.get_chat(channel_identifier)

        # Verify the chat is a channel
        if chat.type != ChatType.CHANNEL:
            await message.reply("This is not a valid channel. Please provide a valid channel ID or username.")
            logger.warning(f"User ID {user_id} tried to connect a non-channel: {channel_identifier} (Type: {chat.type})")
            return

        # Check user's membership and role in the channel
        member = await client.get_chat_member(chat.id, user_id)
        if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            await message.reply("You must be an admin or creator in the channel to connect it.")
            logger.warning(f"User ID {user_id} is not an admin or creator in channel: {chat.title} ({chat.id})")
            return

        # Save channel in the database
        save_user_channel(user_id, chat.id, chat.title)
        await message.reply(f"Channel '{chat.title}' connected successfully! You can now use /post to manage posts.")
        logger.info(f"User ID {user_id} connected channel: {chat.title} ({chat.id}) successfully.")

    except Exception as e:
        # Handle any unexpected errors
        await message.reply(f"Failed to connect the channel. Error: {str(e)}")
        logger.error(f"User ID {user_id} failed to connect channel {channel_identifier}. Error: {str(e)}")
