import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, ChatAdminRequired
from database.frwd import save_forward_data, get_forward_data, save_user_in_channel, get_channel_data_by_id, get_all_channels  # Assuming these functions are defined in your database handling
from info import ADMINS
from datetime import datetime
import pytz

# Set timezone for India (IST)
IST = pytz.timezone('Asia/Kolkata')
logger = logging.getLogger("Forward")

# Command to start forwarding (accessible by everyone)

#logger = logging.getLogger(__name__)

@Client.on_message(filters.command("forward"))
async def forward_command(client: Client, message: Message):
    try:
        logger.info(f"Received forward command from user {message.from_user.id}")
        
        # Parse the command input
        args = message.text.split()
        if len(args) < 3:
            await message.reply(
                "Usage: <code>/forward &lt;f/c/pf/cf&gt; &lt;from_channel_id&gt; &lt;to_channel_id&gt;</code>",
                parse_mode=ParseMode.HTML  # Correctly using ParseMode.HTML
            )
            logger.warning("Forward command usage error: Invalid number of arguments.")
            return
        
        forward_type, from_channel, *to_channels = args[1:]
        logger.info(f"Forwarding type: {forward_type}, From channel: {from_channel}, To channels: {to_channels}")

        # Check if bot is in the target channel(s)
        bot_in_channels = await check_bot_in_channels(client, from_channel, to_channels)
        if not bot_in_channels:
            await message.reply(
                "<b>Bot must be a member of all target channels.</b>",
                parse_mode=ParseMode.HTML  # Correctly using ParseMode.HTML
            )
            logger.warning(f"Bot is not a member of all target channels for user {message.from_user.id}.")
            return
        
        # Check user rights in the source and target channels
        has_permission = await check_user_rights(client, message.from_user.id, from_channel, to_channels)
        if not has_permission:
            await message.reply(
                "<b>You must be an admin or owner in the source and target channels to set up forwarding.</b>",
                parse_mode=ParseMode.HTML  # Correctly using ParseMode.HTML
            )
            logger.warning(f"User {message.from_user.id} does not have permission to forward messages.")
            return
        
        # Fetch channel data and save to the database for both source and target channels
        await fetch_and_save_channel_data(client, message.from_user.id, from_channel)
        for channel in to_channels:
            await fetch_and_save_channel_data(client, message.from_user.id, channel)
        
        # Save the forwarding data in the database
        #save_forward_data(from_channel, to_channels, forward_type, added_by=message.from_user.id, user_id=message.from_user.id)
        #logger.info(f"Forwarding setup completed by user {message.from_user.id}.")

        # Acknowledge the setup
        await message.reply(
            "<b>Forwarding setup complete! I will start forwarding messages.</b>",
            parse_mode=ParseMode.HTML  # Correctly using ParseMode.HTML
        )
        
        # Start forwarding messages
        await start_forwarding(client, from_channel, to_channels, forward_type)
        logger.info(f"awaiting start forwarding function")
        
        
    
    except Exception as e:
        logger.error(f"Error in /forward command: {e}")
        await message.reply(
            "<b>An error occurred while setting up forwarding.</b>",
            parse_mode=ParseMode.HTML  # Correctly using ParseMode.HTML
        )


async def fetch_and_save_channel_data(client, user_id, channel):
    """
    Fetch and save channel data for the specified channel.
    """
    try:
        # Fetch channel information
        chat = await client.get_chat(channel)

        # Extract necessary details
        channel_id = chat.id
        channel_name = chat.title
        channel_type = "private" if chat.type == "private" else "public"
        invite_link = await client.export_chat_invite_link(channel)  # This requires bot to be an admin
        members_count = await client.get_chat_members_count(channel)

        # Calculate average views (this is a placeholder for the actual logic)
        average_views = await calculate_average_views(client, channel)

        # Save the channel and user data
        save_user_in_channel(
            user_id=user_id,
            channel=channel,
            channel_id=channel_id,
            channel_name=channel_name,
            channel_type=channel_type,
            invite_link=invite_link,
            members_count=members_count,
            average_views=average_views
        )

    except Exception as e:
        logger.error(f"Error fetching and saving data for channel {channel}: {e}")


async def calculate_average_views(client, channel):
    """
    Dummy function to calculate average views for posts in the channel.
    Replace this with the actual logic for tracking views per post.
    """
    # Placeholder for the actual average views calculation logic
    return 100  # Return a fixed value for now


def saving_user_in_channel(user_id, channel, channel_id, channel_name, channel_type, invite_link, members_count, average_views):
    """
    Save the user and channel data in the database.
    """
    try:
        # Define the data to be saved
        user_data = {
            'user_id': user_id,
            'channel': channel,
            'channel_id': channel_id,
            'channel_name': channel_name,
            'channel_type': channel_type,
            'invite_link': invite_link,
            'members_count': members_count,
            'average_views': average_views,
            'saved_date': datetime.now(),
            'updated_date': datetime.now()  # Save the date of saving
        }
        
        # Save data in your collection (replace with your actual database call)
        Forward_data.insert_one(user_data)
        logger.info(f"User {user_id} data saved for channel {channel}.")
    
    except Exception as e:
        logger.error(f"Error saving user {user_id} data for channel {channel}: {e}")
        
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
        if bot_in_from_channel.status not in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER}:
            logger.warning(f"Bot is not a member of the 'from' channel {from_channel}.")
            return False
        
        # Check if the bot is a member of all "to" channels
        for channel in to_channels:
            bot_in_to_channel = await client.get_chat_member(channel, (await client.get_me()).id)
            if bot_in_to_channel.status not in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER}:
                logger.warning(f"Bot is not a member of target channel {channel}.")
                return False
        
        logger.info(f"Bot is a member of all required channels.")
        return True
    except Exception as e:
        logger.error(f"Error checking bot's membership in channels: {e}")
        return False

async def start_forwarding(client: Client, from_channel, to_channels, forward_type):
    logger.info(f"awaited successfully start forwarding function")
        
    
    #Forward messages from the 'from_channel' to the 'to_channels'
    
    @Client.on_message(filters.chat(from_channel) & filter.incoming)
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






@Client.on_message(filters.command("frwd_stats") & filters.user(ADMINS))
async def frwd_stats(client: Client, message: Message):
    """
    Command to view forwarding statistics and user/channel data for a specific channel ID,
    available only to admins.
    """
    try:
        # Extract the channel_id argument from the message (if provided)
        args = message.text.split()
        if len(args) == 2:
            channel_id = args[1]
        else:
            # If no channel_id is provided, list all channels
            channel_id = None

        if channel_id:
            # Fetch data for the specified channel ID
            channel_data = get_channel_data_by_id(channel_id)

            if not channel_data:
                await message.reply(f"No data available for channel ID: {channel_id}.")
                return

            # Format and display the specific channel data
            response = f"Forwarding Stats for Channel ID: {channel_id}\n\n"
            for user_data in channel_data:
                user_id = user_data['user_id']
                first_added_date = user_data['first_added_date']
                last_updated_date = user_data['last_updated_date']
                members_count = user_data['members_count']
                average_views = user_data['average_post_views']

                # Constructing the formatted response
                response += f"User ID: {user_id}\n"
                response += f"First Added: {first_added_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                response += f"Last Updated: {last_updated_date.strftime('%Y-%m-%d %H:%M:%S')}\n"
                response += f"Members Count: {members_count}\n"
                response += f"Average Views per Post: {average_views}\n\n"

            await message.reply(response)

        else:
            # Fetch all channels if no channel_id is provided
            channel_info = get_all_channels()

            if not channel_info:
                await message.reply("No channels found.")
                return

            # List all added channels with their ID and member count
            response = "List of Added Channels:\n\n"
            for channel in channel_info:
                channel_id = channel['channel_id']
                channel_name = channel['channel_name']
                members_count = channel['members_count']

                # Construct the formatted response
                response += f"Channel: {channel_name} (ID: {channel_id})\n"
                response += f"Members Count: {members_count}\n\n"

            await message.reply(response)

    except Exception as e:
        await message.reply(f"Error fetching forwarding statistics: {str(e)}")
        logger.error(f"Error in frwd_stats command: {e}")
