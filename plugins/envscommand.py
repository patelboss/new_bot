from pyrogram import Client, filters
from info import *
#bot = Client("my_bot")
from database.envs import fetch_config, get_env, save_env, fetch_all_configs, update_config
from pyrogram.types import Message
from pymongo import UpdateOne
import logging
from pyrogram.enums import ParseMode
# Set up logger
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

@Client.on_message(filters.command('add_env') & filters.user(ADMINS))  # Replace with admin IDs
async def add_env(client, message):
    args = message.text.split()
    if len(args) < 3:
        await message.reply("Usage: /add_env {config_name} {key} {value}")
        return
    
    config_name, key, value = args[1], args[2], " ".join(args[3:])
    
    save_env(config_name, key, value)  # Save the environment variable to the DB
    await message.reply(f"Environment variable <pre> {key} = {value} </pre> added to {config_name}.", parse_mode=ParseMode.HTML)

@Client.on_message(filters.command('get_envs') & filters.user(ADMINS))  # Replace with admin IDs
async def get_envs(client, message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Usage: /get_envs {config_name}")
        return

    config_name = args[1]
    env_data = get_env(config_name)

    if not env_data:
        await message.reply(f"No environment variables found for {config_name}.")
    else:
        env_str = "\n\n".join([f"{key} = {value}" for key, value in env_data.items()])
        await message.reply(f"Current environment variables for {config_name}:\n<pre>{env_str}</pre>", parse_mode=ParseMode.HTML)

@Client.on_message(filters.command("all_envs") & filters.user(ADMINS))
async def envs_command(client: Client, message: Message):
    """
    Handle the /envs command to fetch and display all environment configurations.
    """
    try:
        # Fetch all configurations
        configs = fetch_all_configs()

        if configs:
            # Format all configurations
            response = "Current Environment Configurations:\n\n"
            for config in configs:
                config_name = config.get("config_name", "Unknown")
                details = "\n\n".join(f"{key} = {value}" for key, value in config.items() if key != "_id")
                response += f"<b>{config_name}</b>:\n<pre>{details}</pre>\n\n"
            
            # Send the formatted response
            await message.reply(response)
        else:
            await message.reply("No environment configurations found.")
    
    except Exception as e:
        await message.reply(f"An error occurred while fetching configurations: {e}")



@Client.on_message(filters.command('update_env') & filters.user(ADMINS))  # Only admins can use this
async def update_env(client, message):
    args = message.text.split()
    
    if len(args) < 4:
        await message.reply("Usage: /update_env {config_name} {key} {value}")
        return

    config_name = args[1]
    key = args[2]
    value = " ".join(args[3:])  # In case value has spaces

    # Update the environment variable in the DB
    success = await update_config(config_name, key, value)
    
    if success:
        await message.reply(f"Environment variable {key} updated to {value} in {config_name}.")
    else:
        await message.reply(f"Failed to update environment variable {key} in {config_name}.")
