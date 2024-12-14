import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, ChatAdminRequired
from database.frwd import save_forward_data, get_forward_data  # Assuming these functions are defined in your database handling
from info import ADMINS
from datetime import datetime
import pytz

# Set timezone for India (IST)
IST = pytz.timezone('Asia/Kolkata')
logger = logging.getLogger("Forward")

# Command to start forwarding (accessible by everyone)
@Client.on_message(filters.command("forward"))
async def forward_command(client: Client, message: Message):
    try:
        logger.info(f"Received forward command from user {message.from_user.id}")
        
        # Parse the command input
        args = message.text.split()
        if len(args) < 3:
            await message.reply(
                "Usage: <code>/forward &lt;f/c/pf/cf&gt; &lt;from_channel_id&gt; &lt;to_channel_id&gt;</code>",
                parse_mode=ParseMode.HTML
            )
            logger.warning("Forward command usage error: Invalid number of arguments.")
            return
        
        forward_type, from_channel, *to_channels = args[1:]
        logger.info(f"Forwarding type: {forward_type}, From channel: {from_channel}, To channels: {to_channels}")

        # Check user rights in the source and target channels
        has_permission = await check_user_rights(client, message.from_user.id, from_channel, to_channels)
        if not has_permission:
            await message.reply(
                "<b>You must be an admin or owner in the source and target channels to set up forwarding.</b>",
                parse_mode=ParseMode.HTML
            )
            logger.warning(f"User {message.from_user.id} does not have permission to forward messages.")
            return
        
        # Check if bot is in the target channel(s)
        bot_in_channels = await check_bot_in_channels(client, from_channel, to_channels)
        if not bot_in_channels:
            await message.reply(
                "<b>Bot must be a member of all target channels.</b>",
                parse_mode=ParseMode.HTML
            )
            logger.warning(f"Bot is not a member of all target channels for user {message.from_user.id}.")
            return
        
        # Save the forwarding data in the database
        save_forward_data(from_channel, to_channels, forward_type, message.from_user.id)
        logger.info(f"Forwarding setup completed by user {message.from_user.id}.")

        # Acknowledge the setup
        await message.reply(
            "<b>Forwarding setup complete! I will start forwarding messages.</b>",
            parse_mode=ParseMode.HTML
        )
        
        # Start forwarding messages
        await start_forwarding(client, from_channel, to_channels, forward_type)
    
    except Exception as e:
        logger.error(f"Error in /forward command: {e}")
        await message.reply(
            "<b>An error occurred while setting up forwarding.</b>",
            parse_mode=ParseMode.HTML
        )

async def check_user_rights(client: Client, user_id, from_channel, to_channels):
    """
    Check if the user is an admin or owner in the from_channel and all target channels.
    """
    try:
        logger.info(f"Checking user rights for {user_id} in channels {from_channel} and {to_channels}.")
        
        # Check if the user is an admin/owner in the 'from' channel
        member_from_channel = await client.get_chat_member(from_channel, user_id)
        if member_from_channel.status not in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
            logger.warning(f"User {user_id} is not admin/owner in the 'from' channel {from_channel}.")
            return False

        # Check if the user is an admin/owner in all 'to' channels
        for channel in to_channels:
            member_to_channel = await client.get_chat_member(channel, user_id)
            if member_to_channel.status not in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
                logger.warning(f"User {user_id} is not admin/owner in target channel {channel}.")
                return False
        
        logger.info(f"User {user_id} has required permissions in channels.")
        return True
    except (UserNotParticipant, PeerIdInvalid, ChatAdminRequired) as e:
        logger.error(f"Permission check error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error checking user rights: {str(e)}")
        return False

async def check_bot_in_channels(client: Client, from_channel, to_channels):
    """
    Check if the bot is a member of the given channels
    """
    try:
        logger.info(f"Checking if the bot is a member of {from_channel} and {to_channels}.")
        
        # Check if the bot is a member of the "from" channel
        bot_in_from_channel = await client.get_chat_member(from_channel, (await client.get_me()).id)
        if bot_in_from_channel.status not in ["member", "administrator"]:
            logger.warning(f"Bot is not a member of the 'from' channel {from_channel}.")
            return False
        
        # Check if the bot is a member of all "to" channels
        for channel in to_channels:
            bot_in_to_channel = await client.get_chat_member(channel, (await client.get_me()).id)
            if bot_in_to_channel.status not in ["member", "administrator"]:
                logger.warning(f"Bot is not a member of target channel {channel}.")
                return False
        
        logger.info(f"Bot is a member of all required channels.")
        return True
    except Exception as e:
        logger.error(f"Error checking bot's membership in channels: {e}")
        return False

async def start_forwarding(client: Client, from_channel, to_channels, forward_type):
    """
    Forward messages from the 'from_channel' to the 'to_channels'
    """
    @Client.on_message(filters.chat(from_channel))
    async def forward_message(client, message: Message):
        try:
            logger.info(f"Forwarding message {message.message_id} from {from_channel} to {to_channels}.")
            
            # Forward message based on the selected forward type
            if forward_type == "f":
                await message.forward(to_channels)
            elif forward_type == "c":
                await message.copy(to_channels)
            elif forward_type == "pf":
                await message.forward(to_channels)
            elif forward_type == "cf":
                await message.copy(to_channels)
            
            logger.info(f"Message {message.message_id} forwarded successfully.")
        
        except Exception as e:
            logger.error(f"Error forwarding message {message.message_id}: {e}")    
