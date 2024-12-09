from pyrogram import Client, filters
from info import ADMINS  # import the ADMINS list from info

# Define a dictionary to store secret codes (could be persisted in a database if needed)
secret_codes = {}

@Client.on_message(filters.command('feedback') & filters.private)
async def feedback(client, message):
    """
    Handle feedback or issue reporting.
    """
    await message.reply("Please type your feedback or issue. It will be sent directly to the admin.")
    feedback_message = await client.listen(message.chat.id)
    # Send feedback to the admin(s)
    for admin in ADMINS:
        await client.send_message(admin, f"Feedback from {message.from_user.username} ({message.from_user.id}):\n{feedback_message.text}")
    await message.reply("Your feedback has been sent to the admin. Thank you!")

@Client.on_message(filters.command('talk') & filters.private)
async def talk(client, message):
    """
    Command to interact using a secret code or talk to admin.
    """
    # Ensure the message contains a secret code
    command_parts = message.text.split()
    
    if len(command_parts) < 2:
        return await message.reply("Please provide a secret code after the /talk command. Example: `/talk secretcode123`")
    
    secret_code = command_parts[1]
    
    # Validate the secret code
    if secret_code not in secret_codes:
        return await message.reply("Invalid secret code. Please try again.")
    
    # Check if the user has replied to a message
    if not message.reply_to_message:
        return await message.reply("Please reply to a message with your secret code to send it to the admin.")
    
    # Get the message that the user replied to
    user_message = message.reply_to_message.text
    user_id = message.from_user.id
    
    # Send the message to the admin(s) with user ID
    for admin in ADMINS:
        await client.send_message(admin, f"Message from {message.from_user.username} (ID: {user_id}):\n{user_message}")
    
    # Notify the user that their message has been delivered
    await message.reply("Your message has been delivered to the admin. Please be patient, the admin will reply soon.")

@Client.on_message(filters.command('create_code') & filters.private)
async def create_code(client, message):
    """
    Admin command to create a new secret code.
    """
    if message.from_user.id not in ADMINS:
        return await message.reply("You are not authorized to create a secret code.")
    
    await message.reply("Please provide the name for the new secret code.")
    response = await client.listen(message.chat.id)
    new_code = response.text.strip()
    
    if new_code in secret_codes:
        return await message.reply("This secret code already exists.")

    # Generate a unique secret code (simple example)
    secret_codes[new_code] = True  # You can also add expiration or validation if needed
    await message.reply(f"New secret code '{new_code}' has been created successfully!")

@Client.on_message(filters.command('delete_code') & filters.private)
async def delete_code(client, message):
    """
    Admin command to delete a secret code.
    """
    if message.from_user.id not in ADMINS:
        return await message.reply("You are not authorized to delete a secret code.")
    
    await message.reply("Please provide the secret code you want to delete.")
    response = await client.listen(message.chat.id)
    code_to_delete = response.text.strip()

    if code_to_delete not in secret_codes:
        return await message.reply("This secret code does not exist.")

    del secret_codes[code_to_delete]
    await message.reply(f"Secret code '{code_to_delete}' has been deleted successfully!")
