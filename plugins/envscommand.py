from pyrogram import Client, filters

#bot = Client("my_bot")

@Client.on_message(filters.command('add_env') & filters.user([ADMINS]))  # Replace with admin IDs
async def add_env(client, message):
    args = message.text.split()
    if len(args) < 3:
        await message.reply("Usage: /add_env {config_name} {key} {value}")
        return
    
    config_name, key, value = args[1], args[2], " ".join(args[3:])
    
    save_env(config_name, key, value)  # Save the environment variable to the DB
    await message.reply(f"Environment variable {key} added to {config_name}.")

@Client.on_message(filters.command('get_envs') & filters.user([ADMINS]))  # Replace with admin IDs
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
        env_str = "\n".join([f"{key}: {value}" for key, value in env_data.items()])
        await message.reply(f"Current environment variables for {config_name}:\n{env_str}")

#bot.run()
