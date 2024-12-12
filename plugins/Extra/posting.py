from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import asyncio
from database.posts import save_user_channel, get_user_channels, save_post
from pyrogram.enums import ParseMode
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from info import DATABASE_URI, DATABASE_NAME
import logging

# Initialize MongoDB connection
client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]
sessions_col = db['post_sessions']

# Ensure indexes for performance
sessions_col.create_index('user_id', unique=True)

logger = logging.getLogger(__name__)

class PostSessionManager:
    @staticmethod
    def create_session(user_id):
        """
        Create a session for a user and store it in the database.
        """
        try:
            session = {
                "user_id": user_id,
                "channel_ids": [],
                "channel_names": [],
                "parse_mode": "HTML",
                "message": None,
                "buttons": None,
                "photo": None,
                "schedule_time": None,
                "step": None,
                "created_at": datetime.now(),
            }
            sessions_col.update_one(
                {"user_id": user_id},
                {"$set": session},
                upsert=True  # Insert if not exists
            )
            logger.info(f"Session created for user ID {user_id}.")
        except Exception as e:
            logger.error(f"Error creating session for user ID {user_id}: {e}")

    @staticmethod
    def get_session(user_id):
        """
        Retrieve the session for a user from the database.
        """
        try:
            return sessions_col.find_one({"user_id": user_id})
        except Exception as e:
            logger.error(f"Error fetching session for user ID {user_id}: {e}")
            return None

    @staticmethod
    def update_session(user_id, updates):
        """
        Update the session for a user in the database.
        """
        try:
            sessions_col.update_one(
                {"user_id": user_id},
                {"$set": updates}
            )
            logger.info(f"Session updated for user ID {user_id}. Updates: {updates}")
        except Exception as e:
            logger.error(f"Error updating session for user ID {user_id}: {e}")

    @staticmethod
    def remove_session(user_id):
        """
        Remove a user's session from the database.
        """
        try:
            sessions_col.delete_one({"user_id": user_id})
            logger.info(f"Session removed for user ID {user_id}.")
        except Exception as e:
            logger.error(f"Error removing session for user ID {user_id}: {e}")
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from datetime import datetime
import asyncio
from database.posts import save_post, get_user_channels
from post_session_manager import PostSessionManager

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
    PostSessionManager.update_session(user_id, {
        "channel_ids": channel_ids,
        "channel_names": channel_names,
        "step": "parse_mode"
    })

    await message.reply("What is the parse mode? (HTML/Markdown/None) [Default: HTML]")

@Client.on_message(filters.private & ~filters.command("cancel_post"))
async def post_workflow(client, message):
    user_id = message.from_user.id
    session = PostSessionManager.get_session(user_id)

    if not session:
        return

    step = session.get("step")
    if step == "parse_mode":
        parse_mode = message.text.upper() if message.text.upper() in ["HTML", "MARKDOWN", "NONE"] else "HTML"
        PostSessionManager.update_session(user_id, {"parse_mode": parse_mode, "step": "message"})
        await message.reply("Send me the message content.")
    elif step == "message":
        PostSessionManager.update_session(user_id, {"message": message.text, "step": "buttons"})
        await message.reply("Send me button/link in HTML format or type 'None' to skip.")
    elif step == "buttons":
        buttons = message.text if message.text.lower() != "none" else None
        PostSessionManager.update_session(user_id, {"buttons": buttons, "step": "photo"})
        await message.reply("Send me a photo or type 'None' to skip.")
    elif step == "photo":
        photo = message.photo.file_id if message.photo else None
        PostSessionManager.update_session(user_id, {"photo": photo, "step": "schedule"})
        await message.reply("Do you want to post now or schedule? (Send 'Now' or a date like DD/MM/YYYY)")
    elif step == "schedule":
        if message.text.lower() == "now":
            PostSessionManager.update_session(user_id, {"schedule_time": None})
            await message.reply("Post sent successfully!")
            await finalize_post(client, user_id)
        else:
            try:
                schedule_time = datetime.strptime(message.text, '%d/%m/%Y')
                PostSessionManager.update_session(user_id, {"schedule_time": schedule_time, "step": "time"})
                await message.reply("Send me the time in HH:MM format (24-hour).")
            except ValueError:
                await message.reply("Invalid date format. Please send a valid date like DD/MM/YYYY.")
    elif step == "time":
        try:
            time = datetime.strptime(message.text, '%H:%M').time()
            schedule_time = datetime.combine(session["schedule_time"], time)
            PostSessionManager.update_session(user_id, {"schedule_time": schedule_time})
            await message.reply("Post scheduled successfully!")
            await finalize_post(client, user_id)
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

async def finalize_post(client, user_id):
    session = PostSessionManager.get_session(user_id)
    if session:
        await save_post(
            user_id=user_id,
            channel_id=session["channel_ids"][0],
            message=session["message"],
            photo=session["photo"],
            buttons=session["buttons"],
            schedule_time=session.get("schedule_time")
        )
        PostSessionManager.remove_session(user_id)
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
        
