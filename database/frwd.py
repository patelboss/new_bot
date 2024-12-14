from pymongo import MongoClient
from datetime import datetime
from info import DATABASE_URI, DATABASE_NAME, ADMINS

# Initialize MongoDB client and database
client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]
collection = db['Forward_data']  # Store forward-related data here

async def save_forward_data(from_channel, to_channels, forward_type, added_by, user_id):
    """
    Save forward data when the user sets up forwarding
    """
    try:
        forward_data = {
            'from_channel': from_channel,
            'to_channels': to_channels,
            'forward_type': forward_type,
            'added_by': added_by,
            'user_id': user_id,
            'added_date': datetime.now(),
            'messages_forwarded': 0  # Initially no messages forwarded
        }

        # Save the data for the 'from_channel' as well
        collection.insert_one(forward_data)
        LOGGER(__name__).info(f"Forward data saved for {from_channel} to {to_channels}")

        # Now, save user in all target channels
        for channel in to_channels:
            save_user_in_channel(user_id, channel)

        LOGGER(__name__).info(f"User {user_id} saved in all target channels.")

    except Exception as e:
        LOGGER(__name__).error(f"Error saving forward data: {e}")

from datetime import datetime
from pymongo import UpdateOne

def save_user_in_channel(user_id, channel, channel_id, channel_name, channel_type, invite_link, members_count, average_views=None):
    """
    Save user in a specific channel along with channel details and average views per post.
    The data is updated with the last updated date and time.
    """
    try:
        # Current date and time for both first added and last updated
        current_time = datetime.now()

        # Channel data structure
        channel_data = {
            'channel_id': channel_id,
            'channel_name': channel_name,
            'channel_type': channel_type,
            'invite_link': invite_link,
            'members_count': members_count,
            'first_added_date': current_time,
            'last_updated_date': current_time,
            'average_post_views': average_views if average_views is not None else 0,  # Default to 0 if not provided
        }

        # User data structure
        user_data = {
            'user_id': user_id,
            'channel': channel,
            'saved_date': current_time,
            'channel_data': channel_data,  # Embed the channel data within the user document
        }

        # Check if the user already exists in the channel
        existing_user = user_collection.find_one({'user_id': user_id, 'channel': channel})
        if existing_user:
            # If the user exists, update the channel data and last updated date
            update_data = {
                '$set': {
                    'channel_data': channel_data,  # Update the channel data
                    'saved_date': current_time,  # Update saved date
                },
                '$currentDate': {'last_updated_date': True},  # Use currentDate for updating the last_updated_date field
            }
            user_collection.update_one({'user_id': user_id, 'channel': channel}, update_data)
            LOGGER(__name__).info(f"User {user_id} updated in channel {channel}.")
        else:
            # If the user doesn't exist, insert the new user data
            user_collection.insert_one(user_data)
            LOGGER(__name__).info(f"User {user_id} saved in channel {channel}.")

    except Exception as e:
        LOGGER(__name__).error(f"Error saving user {user_id} in channel {channel}: {e}")

def get_forward_data():
    """
    Get all forward data stored in the database
    """
    try:
        data = list(collection.find())
        return data
    except Exception as e:
        LOGGER(__name__).error(f"Error retrieving forward data: {e}")
        return []
from datetime import datetime
from pymongo import MongoClient

# Assuming you have a collection where channel data is stored
client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]
user_collection = db["user_data"]

def get_all_channels():
    """
    Retrieve a list of all added channels along with their ID and member count.
    """
    try:
        channels = user_collection.distinct('channel_data.channel_id')  # Get distinct channel IDs
        channel_info = []

        for channel_id in channels:
            channel = user_collection.find_one({'channel_data.channel_id': channel_id})
            if channel:
                channel_data = channel.get('channel_data')
                channel_info.append({
                    'channel_id': channel_data['channel_id'],
                    'channel_name': channel_data['channel_name'],
                    'members_count': channel_data['members_count']
                })

        return channel_info

    except Exception as e:
        LOGGER(__name__).error(f"Error fetching channels from database: {str(e)}")
        return []

def get_channel_data_by_id(channel_id):
    """
    Fetch data for a specific channel by its ID.
    """
    try:
        # Fetch all users for the specified channel ID
        users_in_channel = user_collection.find({'channel_data.channel_id': channel_id})
        user_data_list = []

        for user in users_in_channel:
            user_data = {
                'user_id': user.get('user_id'),
                'channel': user.get('channel'),
                'first_added_date': user['channel_data'].get('first_added_date'),
                'last_updated_date': user['channel_data'].get('last_updated_date'),
                'members_count': user['channel_data'].get('members_count'),
                'average_post_views': user['channel_data'].get('average_post_views')
            }
            user_data_list.append(user_data)

        return user_data_list

    except Exception as e:
        LOGGER(__name__).error(f"Error fetching data for channel ID {channel_id}: {str(e)}")
        return []
