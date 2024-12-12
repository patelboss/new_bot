from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from info import DATABASE_URI, DATABASE_NAME

# Initialize MongoDB connection
client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]
channels_col = db['user_channels']
posts_col = db['scheduled_posts']

# Ensure indexes for performance
channels_col.create_index('user_id', unique=True)
posts_col.create_index('schedule_time')

# Save user's channel connection
def save_user_channel(user_id, channel_id, channel_name):
    """
    Save the user's connected channel to the database.

    Args:
        user_id (int): The Telegram user ID.
        channel_id (int): The Telegram channel ID.
        channel_name (str): The name of the channel.
    """
    try:
        db.user_channels.update_one(
            {"user_id": user_id, "channel_id": channel_id},
            {"$set": {"channel_name": channel_name}},
            upsert=True  # Insert if not exists
        )
        logger.info(f"Channel '{channel_name}' ({channel_id}) saved for user ID {user_id}.")
    except Exception as e:
        logger.error(f"Error saving channel for user ID {user_id}: {e}")
        
# Fetch user's connected channels
def get_user_channels(user_id):
    try:
        user_data = channels_col.find_one({'user_id': user_id})
        return user_data['channels'] if user_data else []
    except Exception as e:
        print(f"Error fetching user channels: {e}")
        return []

# Save post details
def save_post(user_id, channel_id, message, photo, buttons, schedule_time=None):
    try:
        post = {
            'user_id': user_id,
            'channel_id': channel_id,
            'message': message,
            'photo': photo,
            'buttons': buttons,
            'schedule_time': schedule_time,
            'status': 'scheduled',  # Track post status
            'created_at': datetime.now()
        }
        return posts_col.insert_one(post)
    except Exception as e:
        print(f"Error saving post: {e}")
        return None

# Fetch scheduled posts to send
def get_scheduled_posts():
    try:
        now = datetime.now()
        return posts_col.find({'schedule_time': {'$lte': now}})
    except Exception as e:
        print(f"Error fetching scheduled posts: {e}")
        return []

# Delete post after sending
def delete_post(post_id):
    try:
        posts_col.delete_one({'_id': ObjectId(post_id)})
    except Exception as e:
        print(f"Error deleting post: {e}")
