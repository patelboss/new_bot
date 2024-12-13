from pymongo import MongoClient
from datetime import datetime
from info import DATABASE_URI, DATABASE_NAME
from pyrogram import Client
import asyncio

client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]

# Save user posting data

# Save post data to the database
async def save_post_data(post_data):
    try:
        db.posts.insert_one(post_data)  # Assuming your posts collection is named "posts"
        print("Post saved successfully.")
    except Exception as e:
        print(f"Error saving post: {e}")

# Get post data from the database by message ID
async def get_post_data(message_id):
    try:
        return db.posts.find_one({"message_id": message_id})
    except Exception as e:
        print(f"Error fetching post data: {e}")

# Delete post data from the database
async def delete_post_data(message_id):
    try:
        db.posts.delete_one({"message_id": message_id})
        print("Post deleted successfully.")
    except Exception as e:
        print(f"Error deleting post data: {e}")

# Update post data (e.g., updated text)
async def update_post_data(message_id, new_text):
    try:
        db.posts.update_one({"message_id": message_id}, {"$set": {"text": new_text}})
        print("Post updated successfully.")
    except Exception as e:
        print(f"Error updating post data: {e}")

from umongo import Document, fields
from pymongo import MongoClient
from datetime import datetime
from pytz import timezone

client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]

# Channel Data Schema
@instance.register
class ChannelData(Document):
    id = fields.StrField(attribute='_id')
    channel_id = fields.StrField(unique=True)
    first_added_date = fields.DateTimeField()
    total_users = fields.IntField()
    user_id = fields.StrField()
    link = fields.StrField()
    top_keywords = fields.ListField(fields.StrField())
    posts = fields.IntField()  # Track the total posts made in the channel

    class Meta:
        collection_name = 'channels'

# Template Data Schema
@instance.register
class TemplateData(Document):
    id = fields.StrField(attribute='_id')
    user_id = fields.StrField(unique=True)
    parse_mode = fields.StrField(default="Markdown")  # Default: Markdown
    privacy_mode = fields.StrField(default="off")    # Default: off
    link_preview = fields.StrField(default="off")    # Default: off
    buttons = fields.ListField(fields.TupleField([fields.StrField(), fields.StrField()]))

    class Meta:
        collection_name = 'templates'

# Save template settings to the database
async def save_template_data(user_id, parse_mode, privacy_mode, link_preview, buttons):
    await TemplateData.update_one(
        {'user_id': user_id},
        {'$set': {'parse_mode': parse_mode, 'privacy_mode': privacy_mode, 'link_preview': link_preview, 'buttons': buttons}},
        upsert=True
)

# Save channel information to the database
async def save_channel_stats(channel_id, first_added_date, total_users, user_id, link, top_words):
    try:
        # Save the channel data along with the user who added it
        channel_data = {
            'channel_id': channel_id,
            'first_added_date': first_added_date,
            'total_users': total_users,
            'user_id': user_id,
            'link': link,
            'top_keywords': top_words,
            'posts': 0,  # Initialize posts counter
        }
        await db.channels.update_one({'channel_id': channel_id}, {'$set': channel_data}, upsert=True)
        LOGGER(__name__).info(f"Channel {channel_id} added by user {user_id}.")
    except Exception as e:
        LOGGER(__name__).error(f"Error while saving channel stats: {e}")
        
