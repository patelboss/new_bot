from pymongo import MongoClient
from datetime import datetime
from info import DATABASE_URI, DATABASE_NAME
from pyrogram import Client
import asyncio

client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]

# Save user posting data
async def save_user_post_data(user_id, channel_id):
    """
    Save user post count and channel participation data.
    """
    user_data = db.user_posts.find_one({"user_id": user_id, "channel_id": channel_id})
    
    if user_data:
        db.user_posts.update_one(
            {"user_id": user_id, "channel_id": channel_id},
            {"$inc": {"post_count": 1}},
            upsert=True
        )
    else:
        db.user_posts.insert_one({
            "user_id": user_id,
            "channel_id": channel_id,
            "post_count": 1,
            "first_post_date": datetime.utcnow()
        })

# Save channel statistics
async def save_channel_stats(channel_id, user_id, url=None):
    """
    Save the channel stats like first added date, member count, and an optional URL.
    """
    channel_data = db.channel_stats.find_one({"channel_id": channel_id})
    
    if channel_data:
        # Update the first added date only if it's not already set
        db.channel_stats.update_one(
            {"channel_id": channel_id},
            {"$setOnInsert": {"first_added_date": datetime.utcnow()}},
            upsert=True
        )
    else:
        # Fetch the channel's member count when the channel is first added
        member_count = await get_channel_member_count(channel_id)
        
        # Insert the channel data, including the URL if provided
        channel_stats = {
            "channel_id": channel_id,
            "user_id": user_id,
            "first_added_date": datetime.utcnow(),
            "member_count": member_count,  # Save the member count when first added
            "average_posts_per_day": 0,  # This will be updated later
        }
        
        if url:
            channel_stats["url"] = url  # Save the URL if provided
        
        db.channel_stats.insert_one(channel_stats)

async def get_channel_member_count(channel_id):
    """
    Get the member count of a channel.
    """
    try:
        chat = await Client.get_chat(channel_id)
        return chat.members_count
    except Exception as e:
        return 0  # If there is an error, return 0

# Get channel stats (for admins)
async def get_channel_data(channel_id):
    """
    Fetch channel stats.
    """
    channel_data = db.channel_stats.find_one({"channel_id": channel_id})
    return channel_data

# Get user post data (for admins)
async def get_user_post_data(user_id):
    """
    Fetch user post data across all channels.
    """
    user_data = db.user_posts.find({"user_id": user_id})
    return user_data
