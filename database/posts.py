from pymongo import MongoClient
from info import DATABASE_URI, DATABASE_NAME
from datetime import datetime

# Initialize MongoDB connection
client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]
channels_col = db['user_channels']
posts_col = db['scheduled_posts']


# Save user's channel connection
def save_user_channel(user_id, channel_id, channel_name):
    channels_col.update_one(
        {'user_id': user_id},
        {'$set': {'channel_id': channel_id, 'channel_name': channel_name}},
        upsert=True
    )


# Fetch user's connected channel
def get_user_channel(user_id):
    return channels_col.find_one({'user_id': user_id})


# Save post details
def save_post(user_id, channel_id, message, photo, buttons, schedule_time=None):
    post = {
        'user_id': user_id,
        'channel_id': channel_id,
        'message': message,
        'photo': photo,
        'buttons': buttons,
        'schedule_time': schedule_time,
        'created_at': datetime.now()
    }
    return posts_col.insert_one(post)


# Fetch posts to send
def get_scheduled_posts():
    now = datetime.now()
    return posts_col.find({'schedule_time': {'$lte': now}})


# Delete post after sending
def delete_post(post_id):
    posts_col.delete_one({'_id': post_id})
