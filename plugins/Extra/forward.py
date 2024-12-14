from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant, PeerIdInvalid #, ChatAdminRequired
from database.frwd import save_forward_data, get_forward_data  # Assuming these functions are defined in your database handling
from info import ADMINS
from datetime import datetime
import pytz
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, ChatAdminRequired

# Create bot instance
bot = Client
# Set timezone for India (IST)
IST = pytz.timezone('Asia/Kolkata')

# Command to start forwarding (accessible by everyone)
@bot.on_message(filters.command("forward"))
async def forward_command(client, message: Message):
    try:
        LOGGER(__name__).info(f"Received forward command from user {message.from_user.id}")
        
        # Parse the command input
        args = message.text.split()
        if len(args) < 3:
            await message.reply("Usage: /forward <f/c/pf/cf> <from_channel_id> <to_channel_id>")
            LOGGER(__name__).warning("Forward command usage error: Invalid number of arguments.")
            return
        
        forward_type, from_channel, *to_channels = args[1:]
        LOGGER(__name__).info(f"Forwarding type: {forward_type}, From channel: {from_channel}, To channels: {to_channels}")

        # Check user rights in the source and target channels
        has_permission = await check_user_rights(message.from_user.id, from_channel, to_channels)
        if not has_permission:
            await message.reply("You must be an admin or owner in the source and target channels to set up forwarding.")
            LOGGER(__name__).warning(f"User {message.from_user.id} does not have permission to forward messages.")
            return
        
        # Check if bot is in the target channel(s)
        bot_in_channels = await check_bot_in_channels(from_channel, to_channels)
        if not bot_in_channels:
            await message.reply("Bot must be a member of all target channels.")
            LOGGER(__name__).warning(f"Bot is not a member of all target channels for user {message.from_user.id}.")
            return
        
        # Save the forwarding data in the database
        save_forward_data(from_channel, to_channels, forward_type, message.from_user.id)
        LOGGER(__name__).info(f"Forwarding setup completed by user {message.from_user.id}.")

        # Acknowledge the setup
        await message.reply("Forwarding setup complete! I will start forwarding messages.")
        
        # Start forwarding messages
        await start_forwarding(from_channel, to_channels, forward_type)
    
    except Exception as e:
        LOGGER(__name__).error(f"Error in /forward command: {e}")
        await message.reply("An error occurred while setting up forwarding.")

async def check_user_rights(user_id, from_channel, to_channels):
    """
    Check if the user is an admin or owner in the from_channel and all target channels.
    """
    try:
        LOGGER(__name__).info(f"Checking user rights for {user_id} in channels {from_channel} and {to_channels}.")
        
        # Check if the user is an admin/owner in the 'from' channel
        member_from_channel = await bot.get_chat_member(from_channel, user_id)
        if member_from_channel.status not in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
            LOGGER(__name__).warning(f"User {user_id} is not admin/owner in the 'from' channel {from_channel}.")
            return False

        # Check if the user is an admin/owner in all 'to' channels
        for channel in to_channels:
            member_to_channel = await bot.get_chat_member(channel, user_id)
            if member_to_channel.status not in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
                LOGGER(__name__).warning(f"User {user_id} is not admin/owner in target channel {channel}.")
                return False
        
        LOGGER(__name__).info(f"User {user_id} has required permissions in channels.")
        return True
    except (UserNotParticipant, PeerIdInvalid, ChatAdminRequired) as e:
        LOGGER(__name__).error(f"Permission check error: {str(e)}")
        return False
    except Exception as e:
        LOGGER(__name__).error(f"Unexpected error checking user rights: {str(e)}")
        return False

async def check_bot_in_channels(from_channel, to_channels):
    """
    Check if the bot is a member of the given channels
    """
    try:
        LOGGER(__name__).info(f"Checking if the bot is a member of {from_channel} and {to_channels}.")
        
        # Check if the bot is a member of the "from" channel
        bot_in_from_channel = await bot.get_chat_member(from_channel, bot.id)
        if bot_in_from_channel.status not in ["member", "administrator"]:
            LOGGER(__name__).warning(f"Bot is not a member of the 'from' channel {from_channel}.")
            return False
        
        # Check if the bot is a member of all "to" channels
        for channel in to_channels:
            bot_in_to_channel = await bot.get_chat_member(channel, bot.id)
            if bot_in_to_channel.status not in ["member", "administrator"]:
                LOGGER(__name__).warning(f"Bot is not a member of target channel {channel}.")
                return False
        
        LOGGER(__name__).info(f"Bot is a member of all required channels.")
        return True
    except Exception as e:
        LOGGER(__name__).error(f"Error checking bot's membership in channels: {e}")
        return False

async def start_forwarding(from_channel, to_channels, forward_type):
    """
    Forward messages from the 'from_channel' to the 'to_channels'
    """
    @bot.on_message(filters.chat(from_channel))
    async def forward_message(client, message: Message):
        try:
            LOGGER(__name__).info(f"Forwarding message {message.message_id} from {from_channel} to {to_channels}.")
            
            # Forward message based on the selected forward type
            if forward_type == "f":
                await message.forward(to_channels)
                LOGGER(__name__).info(f"Message {message.message_id} forwarded with tag to {to_channels}.")
            elif forward_type == "c":
                await message.copy(to_channels)
                LOGGER(__name__).info(f"Message {message.message_id} copied without tag to {to_channels}.")
            elif forward_type == "pf":
                # Implement privacy mode forwarding here
                await message.forward(to_channels)
                LOGGER(__name__).info(f"Message {message.message_id} forwarded with privacy mode to {to_channels}.")
            elif forward_type == "cf":
                # Implement privacy mode forwarding here
                await message.copy(to_channels)
                LOGGER(__name__).info(f"Message {message.message_id} copied with privacy mode to {to_channels}.")

            # Update the forwarded message count in the database
            save_forward_data(from_channel, to_channels, forward_type)
            LOGGER(__name__).info(f"Message {message.message_id} forwarded successfully.")

        except Exception as e:
            LOGGER(__name__).error(f"Error forwarding message {message.message_id}: {e}")

# Command to show forward stats (only accessible by admins)
@bot.on_message(filters.command("frwd_stats"))
async def frwd_stats_command(client, message: Message):
    if message.from_user.id not in ADMINS:
        await message.reply("You do not have permission to use this command.")
        LOGGER(__name__).warning(f"User {message.from_user.id} tried to access /frwd_stats without permission.")
        return

    forward_data = get_forward_data()
    if forward_data:
        data_message = "Forwarding Data:\n"
        for data in forward_data:
            added_date = data['added_date'].astimezone(IST).strftime('%Y-%m-%d %H:%M:%S')
            data_message += (f"From: {data['from_channel']} To: {data['to_channels']} Type: {data['forward_type']}\n"
                             f"Added by: {data['added_by']} User: {data['user_id']} Added on: {added_date}\n"
                             f"Messages Forwarded: {data['messages_forwarded']}\n\n")
        await message.reply(data_message)
        LOGGER(__name__).info(f"Admin {message.from_user.id} requested forwarding stats.")
    else:
        await message.reply("No forwarding data found.")
        LOGGER(__name__).info(f"No forwarding data found for admin {message.from_user.id}.")
