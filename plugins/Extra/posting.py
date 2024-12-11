from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import asyncio
from database.posts import save_user_channel, get_user_channels, save_post

# Store temporary data during the posting workflow
user_sessions = {}

async def send_preview(client, user_id, channel_name, message, photo, buttons, schedule_time):
    preview_text = (
        f"<b>Preview:</b>\n"
        f"Message: {message}\n"
        f"Buttons: {buttons}\n"
        f"Scheduled for: {schedule_time if schedule_time else 'Now'}\n"
        f"Channel: {channel_name}"
    )
    if photo:
        await client.send_photo(user_id, photo, caption=preview_text, parse_mode="html")
    else:
        await client.send_message(user_id, preview_text, parse_mode="html")


async def post_to_channel(client, channel_id, message, photo, buttons):
    if photo:
        await client.send_photo(
            channel_id,
            photo=photo,
            caption=message,
            parse_mode="html",
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
        )
    else:
        await client.send_message(
            channel_id,
            text=message,
            parse_mode="html",
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
        )


@Client.on_message(filters.command("post") & filters.private)
async def post_command(client, message):
    user_id = message.from_user.id
    user_channels = get_user_channels(user_id)

    if not user_channels:
        # If no channel is connected, prompt for a channel ID
        prompt_message = await message.reply(
            "You are not connected to any channel.\n"
            "Please send me your **channel ID**.\n\n"
            "If you don't know your channel ID, **forward any message** from your channel here and reply with `/id` to get it.\n\n"
            "You have 60 seconds to provide the channel ID. If no input is received, this process will be aborted."
        )

        try:
            # Wait for user input
            user_response = await client.listen(message.chat.id, timeout=60)
            channel_identifier = user_response.text.strip()

            # Validate and connect the channel
            await connect_channel(client, message, channel_identifier)
        except asyncio.TimeoutError:
            await message.reply("No response received within 60 seconds. The process has been aborted.")
        finally:
            await prompt_message.delete()  # Clean up the prompt message
        return

    # If the user is connected, proceed with the post creation process
    channel_names = [channel['channel_name'] for channel in user_channels]
    channel_ids = [channel['channel_id'] for channel in user_channels]
    user_sessions[user_id] = {'channel_ids': channel_ids, 'channel_names': channel_names}

    await message.reply("What is the parse mode? (HTML/Markdown/None)")
    user_sessions[user_id]['step'] = 'parse_mode'


@Client.on_message(filters.private & ~filters.command("cancel_post"))
async def post_workflow(client, message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)

    if not session:
        return  # No active session

    step = session.get('step')

    if step == 'parse_mode':
        session['parse_mode'] = message.text.upper()
        session['step'] = 'message'
        await message.reply("Send me the message content.")
    elif step == 'message':
        session['message'] = message.text
        session['step'] = 'buttons'
        await message.reply("Send me button/link in HTML format or type 'None' to skip.")
    elif step == 'buttons':
        buttons = message.text
        session['buttons'] = buttons if buttons.lower() != 'none' else None
        session['step'] = 'photo'
        await message.reply("Send me a photo or type 'None' to skip.")
    elif step == 'photo':
        if message.photo:
            session['photo'] = message.photo.file_id
        else:
            session['photo'] = None

        session['step'] = 'schedule'
        await message.reply("Do you want to post now or schedule? (Send 'Now' or a date like DD/MM/YYYY)")
    elif step == 'schedule':
        if message.text.lower() == 'now':
            session['schedule_time'] = None
            session['step'] = None
            await send_preview(
                client, user_id, session['channel_names'][0], session['message'], 
                session['photo'], session['buttons'], session['schedule_time']
            )
            await post_to_channel(
                client, session['channel_ids'][0], session['message'], 
                session['photo'], session['buttons']
            )
            await save_post(user_id, session['channel_ids'][0], session['message'], session['photo'], session['buttons'])
            await message.reply("Post sent successfully!")
            user_sessions.pop(user_id, None)
        else:
            try:
                schedule_date = datetime.strptime(message.text, '%d/%m/%Y')
                session['schedule_time'] = schedule_date
                session['step'] = 'time'
                await message.reply("Send me the time in HH:MM format (24-hour).")
            except ValueError:
                await message.reply("Invalid date format. Please send a valid date like DD/MM/YYYY.")
    elif step == 'time':
        try:
            schedule_time = datetime.strptime(message.text, '%H:%M').time()
            session['schedule_time'] = datetime.combine(session['schedule_time'], schedule_time)
            session['step'] = None

            await send_preview(
                client, user_id, session['channel_names'][0], session['message'], 
                session['photo'], session['buttons'], session['schedule_time']
            )
            await save_post(user_id, session['channel_ids'][0], session['message'], session['photo'], session['buttons'], session['schedule_time'])
            await message.reply("Post scheduled successfully!")
            user_sessions.pop(user_id, None)
        except ValueError:
            await message.reply("Invalid time format. Please send a valid time like HH:MM.")


@Client.on_message(filters.command("cancel_post") & filters.private)
async def cancel_post(client, message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        user_sessions.pop(user_id, None)
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
    """
    Command to connect a new channel for the user to post.
    """
    user_id = message.from_user.id
    logger.info(f"User ID {user_id} initiated connect_post_channel command.")

    # Prompt user for channel information
    try:
        prompt_message = await message.reply(
            "Please send me your channel ID or username.\n"
            "You must be an admin in the channel to connect it."
        )
        logger.info(f"Prompt sent to User ID {user_id} asking for channel ID or username.")

        # Wait for user response to get channel identifier (ID or username)
        user_response = await client.listen(message.chat.id, timeout=60)
        channel_identifier = user_response.text.strip()
        logger.info(f"User ID {user_id} provided channel identifier: {channel_identifier}")

        # Connect channel
        await connect_channel(client, message, channel_identifier)
        logger.info(f"User ID {user_id} processed channel connection.")
        
    except asyncio.TimeoutError:
        logger.warning(f"User ID {user_id} did not respond within 60 seconds.")
        await message.reply("No response received within 60 seconds. The process has been aborted.")
    except Exception as e:
        logger.error(f"Error processing channel connection for User ID {user_id}: {str(e)}")
        await message.reply(f"An error occurred while connecting the channel. Please try again later.")
    finally:
        try:
            # Delete prompt message to clean up
            await prompt_message.delete()
            logger.info(f"Prompt message for User ID {user_id} deleted.")
        except Exception as e:
            logger.error(f"Error deleting prompt message for User ID {user_id}: {str(e)}")

from pyrogram import Client
from pyrogram.enums import ChatType, ChatMemberStatus
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def connect_channel(client, message, channel_identifier):
    """
    Handle connecting a channel for a user.
    """
    user_id = message.from_user.id

    try:
        # Check if the channel identifier starts with -100 (valid channel ID)
        if not channel_identifier.startswith("-100"):
            await message.reply("Invalid channel ID. Please provide a valid channel ID that starts with '-100'.")
            logger.warning(f"User ID {user_id} provided an invalid channel ID: {channel_identifier}")
            return
        
        # Fetch channel information
        chat = await client.get_chat(channel_identifier)

        # Log the fetched chat details
        logger.info(f"User ID {user_id} fetched channel details for {channel_identifier}, Chat Type: {chat.type}")

        # Verify that the chat type is a channel
        if chat.type != ChatType.CHANNEL:
            await message.reply("This is not a valid channel. Please provide a valid channel ID or username.")
            logger.warning(f"User ID {user_id} tried to connect to a non-channel: {channel_identifier} (Type: {chat.type})")
            return

        # Verify if user is an admin or the owner (creator) of the channel
        member = await client.get_chat_member(chat.id, user_id)

        # Log the user status in the channel
        logger.info(f"User ID {user_id} has status '{member.status}' in the channel: {chat.title} ({chat.id})")

        # Check if the user is an admin or owner (creator)
        if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            await message.reply("You must be an admin or creator in the channel to connect it.")
            logger.warning(f"User ID {user_id} is not an admin or creator in the channel: {chat.title} ({chat.id})")
            return

        # Save the channel to the database
        await save_user_channel(user_id, chat.id, chat.title)
        await message.reply(f"Channel '{chat.title}' connected successfully! You can now use /post to manage posts.")
        logger.info(f"User ID {user_id} successfully connected to channel: {chat.title} ({chat.id})")

    except Exception as e:
        await message.reply(f"Failed to connect the channel. Error: {str(e)}")
        logger.error(f"User ID {user_id} failed to connect to channel {channel_identifier}. Error: {str(e)}")
