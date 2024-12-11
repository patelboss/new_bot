from pymongo import MongoClient
from bson import ObjectId
from info import DATABASE_URI, DATABASE_NAME
from datetime import datetime

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
        channels_col.update_one(
            {'user_id': user_id},
            {'$set': {'channel_id': channel_id, 'channel_name': channel_name}},
            upsert=True
        )
    except Exception as e:
        print(f"Error saving user channel: {e}")


# Fetch user's connected channel
def get_user_channel(user_id):
    try:
        return channels_col.find_one({'user_id': user_id})
    except Exception as e:
        print(f"Error fetching user channel: {e}")
        return None


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


# Fetch posts to send
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
