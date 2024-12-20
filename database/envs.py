import logging
from struct import pack
import re
import base64
from pyrogram.file_id import FileId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
#from info import FILE_DB_URI, SEC_FILE_DB_URI, DATABASE_NAME, MULTIPLE_DATABASE, USE_CAPTION_FILTER, MAX_B_TN
from utils import get_settings, save_group_settings
from pymongo.errors import PyMongoError
from datetime import datetime
import hashlib
from pymongo.errors import PyMongoError
from pymongo import UpdateOne
import hashlib
import json
from datetime import datetime

# Function to generate a unique batch ID (e.g., BATCH-XXXXXXXXXX-01)
from pymongo import MongoClient
from datetime import datetime
import hashlib
import logging
FILE_DB_URI = ""
DATABASE_NAME = ""
COLLECTIONB_NAME = ""
# Ensure that MongoDB client and collections are initialized properly
client = MongoClient(FILE_DB_URI)
db = client[DATABASE_NAME]
col = db[COLLECTIONB_NAME]

    
def save_env(config_name, key, value):
    """Save the environment variable to MongoDB."""
    try:
        env_config_collection.update_one(
            {"config_name": config_name},
            {"$set": {key: value}},
            upsert=True
        )
        print(f"Environment variable {key} saved successfully under {config_name}.")
    except Exception as e:
        print(f"Error saving environment variable: {e}")

def get_env(config_name):
    """Retrieve the environment configuration from MongoDB."""
    try:
        config = env_config_collection.find_one({"config_name": config_name})
        if config:
            return config
        else:
            return {}
    except Exception as e:
        print(f"Error fetching environment configuration: {e}")
        return {}

def fetch_config(config_name):
    """Fetch configuration from MongoDB or return empty dict if not found."""
    try:
        config = env_config_collection.find_one({"config_name": config_name})
        if config:
            return config
        else:
   #         logging.warning(f"Configuration {config_name} not found in database. Using default values.")
            return {}
    except Exception as e:
        print(f"Error fetching environment configuration: {e}")
 #       logging.error(f"Error fetching {config_name} configuration: {e}")
        return {}


def fetch_all_configs():
    """Fetch all environment configurations from MongoDB."""
    try:
        configs = env_config_collection.find()
        return list(configs)
    except Exception as e:
        # logging.error(f"Error fetching all configurations: {e}")
        return []

async def update_config(config_name, key, value):
    """
    Update a specific key-value pair in the environment configuration.
    """
    try:
        # Find the configuration document by config_name
        config_data = db.collection.find_one({"config_name": config_name})
        
        if config_data:
            # Update the key-value pair
            db.collection.update_one(
                {"config_name": config_name},
                {"$set": {key: value}}  # Update the value of the key
            )
            return True
        else:
            # If config_name doesn't exist, create it
            db.collection.insert_one({
                "config_name": config_name,
                key: value
            })
            return True
    except Exception as e:
        print(f"Error while updating config: {e}")
        return False
