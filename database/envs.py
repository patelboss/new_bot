# MongoDB connection and configuration collection setup
from pymongo import MongoClient
#from info import EDATABASE_URI, DATABASE_NAME

client = MongoClient("mongodb+srv://TelegramBot:TelegramBot@cluster0.42rlp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # Adjust as per your setup
db = client["database_name"]
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
   #         logging.warning(f"Configuration {config_name} not found in database. Using default values.")
            return {}
    except Exception as e:
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
