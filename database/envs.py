# MongoDB connection and configuration collection setup
from pymongo import MongoClient
from info import *

client = MongoClient(DATABASE_URI)  # Adjust as per your setup
db = client[DATABASE_NAME]
env_config_collection = db["env_config"]  # Collection for environment variables

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
            logging.warning(f"Configuration {config_name} not found in database. Using default values.")
            return {}
    except Exception as e:
        logging.error(f"Error fetching {config_name} configuration: {e}")
        return {}
        
