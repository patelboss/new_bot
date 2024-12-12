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
    try:
        # Check if user already has a channel connected
        user_data = channels_col.find_one({'user_id': user_id})
        if user_data:
            # Append new channel if not already present
            if not any(c['channel_id'] == channel_id for c in user_data.get('channels', [])):
                channels_col.update_one(
                    {'user_id': user_id},
                    {'$push': {'channels': {'channel_id': channel_id, 'channel_name': channel_name}}},
                    upsert=True
                )
        else:
            channels_col.insert_one({'user_id': user_id, 'channels': [{'channel_id': channel_id, 'channel_name': channel_name}]})
    except Exception as e:
        print(f"Error saving user channel: {e}")

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
