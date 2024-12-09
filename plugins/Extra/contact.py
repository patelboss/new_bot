from pyrogram import Client, filters
from info import ADMINS  # import the ADMINS list from info

# Define a dictionary to store secret codes (could be persisted in a database if needed)
secret_codes = {}

@Client.on_message(filters.command('feedback') & filters.private)
async def feedback(client, message):
    """
    Handle feedback or issue reporting with optional file attachments.
    User should reply to a message to send feedback or issues.
    """
    # Ensure the message contains a feedback message
    if not message.reply_to_message:
        return await message.reply("Please reply to a message with your feedback or issue.")

    feedback_message = message.reply_to_message.text
    user_details = f"Feedback from {message.from_user.username} (ID: {message.from_user.id})"
    
    # Prepare the feedback message to send
    feedback_text = f"{user_details}\n\n{feedback_message}"

    # Check if the user has attached a file (photo, video, document, etc.)
    if message.reply_to_message.document:
        # If the message contains a document (e.g., file), forward it to admin
        document = message.reply_to_message.document
        for admin in ADMINS:
            await client.send_document(admin, document.file_id, caption=feedback_text)
    elif message.reply_to_message.photo:
        # If the message contains a photo, forward it to admin
        photo = message.reply_to_message.photo
        for admin in ADMINS:
            await client.send_photo(admin, photo.file_id, caption=feedback_text)
    elif message.reply_to_message.video:
        # If the message contains a video, forward it to admin
        video = message.reply_to_message.video
        for admin in ADMINS:
            await client.send_video(admin, video.file_id, caption=feedback_text)
    elif message.reply_to_message.audio:
        # If the message contains an audio, forward it to admin
        audio = message.reply_to_message.audio
        for admin in ADMINS:
            await client.send_audio(admin, audio.file_id, caption=feedback_text)
    elif message.reply_to_message.voice:
        # If the message contains a voice message, forward it to admin
        voice = message.reply_to_message.voice
        for admin in ADMINS:
            await client.send_voice(admin, voice.file_id, caption=feedback_text)
    elif message.reply_to_message.sticker:
        # If the message contains a sticker, forward it to admin
        sticker = message.reply_to_message.sticker
        for admin in ADMINS:
            await client.send_sticker(admin, sticker.file_id, caption=feedback_text)
    else:
        # If no file is attached, just send the feedback text
        for admin in ADMINS:
            await client.send_message(admin, feedback_text)
    
    # Notify the user that their feedback has been delivered
    await message.reply("Your feedback has been sent to the admin. Please be patient, the admin will reply soon.")

@Client.on_message(filters.command('talk') & filters.private)
async def talk(client, message):
    """
    Command to interact using a secret code or talk to admin.
    User should reply to a message to send the message.
    """
    # Ensure the message contains a secret code
    command_parts = message.text.split()
    
    if len(command_parts) < 2:
        return await message.reply("Please provide a secret code after the /talk command. Example: `/talk secretcode123`")
    
    secret_code = command_parts[1]
    
    # Validate the secret code
    if secret_code not in secret_codes:
        return await message.reply("Invalid secret code. Please try again.")
    
    # Ensure the user is replying to a message
    if not message.reply_to_message:
        return await message.reply("Please reply to a message with your secret code to send it to the admin.")
    
    # Get the message that the user replied to
    user_message = message.reply_to_message.text
    user_id = message.from_user.id
    user_details = f"Message from {message.from_user.username} (ID: {user_id})"
    
    # Prepare the message to be forwarded to the admin(s)
    forwarded_message = f"{user_details}\n\n{user_message}"

    # Check if the user has attached a file (photo, video, document, etc.)
    if message.reply_to_message.document:
        # If the message contains a document (e.g., file), forward it to admin
        document = message.reply_to_message.document
        for admin in ADMINS:
            await client.send_document(admin, document.file_id, caption=forwarded_message)
    elif message.reply_to_message.photo:
        # If the message contains a photo, forward it to admin
        photo = message.reply_to_message.photo
        for admin in ADMINS:
            await client.send_photo(admin, photo.file_id, caption=forwarded_message)
    elif message.reply_to_message.video:
        # If the message contains a video, forward it to admin
        video = message.reply_to_message.video
        for admin in ADMINS:
            await client.send_video(admin, video.file_id, caption=forwarded_message)
    elif message.reply_to_message.audio:
        # If the message contains an audio, forward it to admin
        audio = message.reply_to_message.audio
        for admin in ADMINS:
            await client.send_audio(admin, audio.file_id, caption=forwarded_message)
    elif message.reply_to_message.voice:
        # If the message contains a voice message, forward it to admin
        voice = message.reply_to_message.voice
        for admin in ADMINS:
            await client.send_voice(admin, voice.file_id, caption=forwarded_message)
    elif message.reply_to_message.sticker:
        # If the message contains a sticker, forward it to admin
        sticker = message.reply_to_message.sticker
        for admin in ADMINS:
            await client.send_sticker(admin, sticker.file_id, caption=forwarded_message)
    else:
        # If no file is attached, just send the text message
        for admin in ADMINS:
            await client.send_message(admin, forwarded_message)
    
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
    await message.reply(f"New secret code has been created successfully:\n\n`{new_code}`")  # In monospace text for easy copy

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
