from datetime import datetime, timedelta
from pymongo import MongoClient, UpdateOne
from info import DATABASE_URI, DATABASE_NAME

client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]

users_collection = db["user_stats"]
channels_collection = db["channel_stats"]


async def save_user_stats(user_id, channel_id):
    users_collection.update_one(
        {"user_id": user_id},
        {"$inc": {f"channels.{channel_id}": 1, "message_count": 1}},
        upsert=True
    )


async def save_channel_stats(client, channel_id):
    chat = await client.get_chat(channel_id)
    members = chat.members_count
    date = datetime.utcnow()

    channel = channels_collection.find_one({"channel_id": channel_id})

    if not channel:
        channels_collection.insert_one({
            "channel_id": channel_id,
            "members": members,
            "first_added": date,
            "messages_posted": 1,
            "last_updated": date
        })
    else:
        days = max((date - channel["first_added"]).days, 1)
        avg = (channel["messages_posted"] + 1) / days

        channels_collection.update_one(
            {"channel_id": channel_id},
            {"$set": {"members": members, "last_updated": date, "daily_avg": avg},
             "$inc": {"messages_posted": 1}}
        )


async def get_user_stats():
    return list(users_collection.find())


async def get_channel_stats():
    return list(channels_collection.find())
