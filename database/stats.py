from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import logging
from info import DATABASE_URI, DATABASE_NAME

# Initialize MongoDB client and database
client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]

# Set up logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Save post data to the database
async def save_post_data(post_data):
    try:
        await db.posts.insert_one(post_data)  # Assuming your posts collection is named "posts"
        LOGGER.info("Post saved successfully.")
    except Exception as e:
        LOGGER.error(f"Error saving post: {e}")

# Get post data from the database by message ID
async def get_post_data(message_id):
    try:
        return await db.posts.find_one({"message_id": message_id})
    except Exception as e:
        LOGGER.error(f"Error fetching post data: {e}")

# Delete post data from the database
async def delete_post_data(message_id):
    try:
        await db.posts.delete_one({"message_id": message_id})
        LOGGER.info("Post deleted successfully.")
    except Exception as e:
        LOGGER.error(f"Error deleting post data: {e}")

# Update post data (e.g., updated text)
async def update_post_data(message_id, new_text):
    try:
        await db.posts.update_one({"message_id": message_id}, {"$set": {"text": new_text}})
        LOGGER.info("Post updated successfully.")
    except Exception as e:
        LOGGER.error(f"Error updating post data: {e}")

# Save template settings to the database
async def save_template_data(user_id, parse_mode, privacy_mode, link_preview, buttons):
    try:
        await db.templates.update_one(
            {"user_id": user_id},
            {"$set": {
                "parse_mode": parse_mode,
                "privacy_mode": privacy_mode,
                "link_preview": link_preview,
                "buttons": buttons
            }},
            upsert=True
        )
        LOGGER.info(f"Template settings for user {user_id} saved successfully.")
    except Exception as e:
        LOGGER.error(f"Error saving template settings for user {user_id}: {e}")

# Save channel information to the database
async def save_channel_stats(channel_id, first_added_date, total_users, user_id, link, top_words):
    try:
        channel_data = {
            "channel_id": channel_id,
            "first_added_date": first_added_date,
            "total_users": total_users,
            "user_id": user_id,
            "link": link,
            "top_keywords": top_words,
            "posts": 0  # Initialize posts counter
        }
        await db.channels.update_one({"channel_id": channel_id}, {"$set": channel_data}, upsert=True)
        LOGGER.info(f"Channel {channel_id} added by user {user_id}.")
    except Exception as e:
        LOGGER.error(f"Error while saving channel stats: {e}")

# Get channel data by channel ID
async def get_channel_data(channel_id):
    try:
        return await db.channels.find_one({"channel_id": channel_id})
    except Exception as e:
        LOGGER.error(f"Error fetching channel data: {e}")

# Example of a method to get all channels for a user
async def get_user_channels(user_id):
    try:
        channels = db.channels.find({"user_id": user_id})
        return await channels.to_list(length=100)  # Adjust length as needed
    except Exception as e:
        LOGGER.error(f"Error fetching user channels: {e}")
        return []

# Example to check if a user is connected to a specific channel
async def is_user_connected_to_channel(user_id, channel_id):
    try:
        channel = await db.channels.find_one({"channel_id": channel_id})
        return channel is not None and channel.get("user_id") == user_id
    except Exception as e:
        LOGGER.error(f"Error checking user-channel connection: {e}")
        return False
