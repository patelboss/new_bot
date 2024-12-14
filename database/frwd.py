from pymongo import MongoClient
from datetime import datetime
from info import DATABASE_URI, DATABASE_NAME, ADMINS

# Initialize MongoDB client and database
client = MongoClient(DATABASE_URI)
db = client[DATABASE_NAME]
collection = db['Forward_data']  # Store forward-related data here

def save_forward_data(from_channel, to_channels, forward_type, added_by, user_id):
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
        collection.insert_one(forward_data)
        LOGGER(__name__).info(f"Forward data saved for {from_channel} to {to_channels}")
    except Exception as e:
        LOGGER(__name__).error(f"Error saving forward data: {e}")

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
