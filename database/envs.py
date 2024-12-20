from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo import UpdateOne
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from pymongo.errors import PyMongoError
##
import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def connect_to_mongo():
    uri = "mongodb+srv://TelegramBot:TelegramBot@cluster0.42rlp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    retries = 5
    for i in range(retries):
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            db = client["database_name"]
            env_config_collection = db["env_config"]
            print("Connected to MongoDB successfully.")
            return client, db, env_config_collection
        except ConnectionFailure as e:
            print(f"Attempt {i + 1} failed: {e}")
            time.sleep(5)  # Wait 5 seconds before retrying
    print("All attempts to connect to MongoDB failed.")
    return None, None, None

# Call the function to connect
client, db, env_config_collection = connect_to_mongo()
##
    
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
