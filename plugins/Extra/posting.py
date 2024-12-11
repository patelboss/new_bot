from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.posts import save_user_channel, get_user_channel, save_post
import asyncio
from datetime import datetime

# Store temporary data during the posting workflow
user_sessions = {}


async def send_preview(client, user_id, channel_name, message, photo, buttons, schedule_time):
    preview_text = (
        f"<b>Preview:</b>\n"
        f"Message: {message}\n"
        f"Buttons: {buttons}\n"
        f"Scheduled for: {schedule_time if schedule_time else 'Now'}\n"
        f"Channel: {channel_name}"
    )
    if photo:
        await client.send_photo(user_id, photo, caption=preview_text, parse_mode="html")
    else:
        await client.send_message(user_id, preview_text, parse_mode="html")


async def post_to_channel(client, channel_id, message, photo, buttons):
    if photo:
        await client.send_photo(
            channel_id,
            photo=photo,
            caption=message,
            parse_mode="html",
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
        )
    else:
        await client.send_message(
            channel_id,
            text=message,
            parse_mode="html",
            reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
        )


@Client.on_message(filters.command("post") & filters.private)
async def post_command(client, message):
    user_id = message.from_user.id
    user_channel = await get_user_channel(user_id)

    if not user_channel:
        # If no channel is connected, prompt for a channel ID
        prompt_message = await message.reply(
            "You are not connected to any channel.\n"
            "Please send me your **channel ID**.\n\n"
            "If you don't know your channel ID, **forward any message** from your channel here and reply with `/id` to get it.\n\n"
            "You have 60 seconds to provide the channel ID. If no input is received, this process will be aborted."
        )

        try:
            # Wait for user input
            user_response = await client.listen(message.chat.id, timeout=60)
            channel_identifier = user_response.text.strip()

            # Validate and connect the channel
            await connect_channel(client, message, channel_identifier)
        except asyncio.TimeoutError:
            await message.reply("No response received within 60 seconds. The process has been aborted.")
        finally:
            await prompt_message.delete()  # Clean up the prompt message
        return

    # If the user is connected, proceed with the post creation process
    channel_name = user_channel['channel_name']
    channel_id = user_channel['channel_id']
    user_sessions[user_id] = {'channel_id': channel_id, 'channel_name': channel_name}

    await message.reply("What is the parse mode? (HTML/Markdown/None)")
    user_sessions[user_id]['step'] = 'parse_mode'


@Client.on_message(filters.private & ~filters.command("cancel_post"))
async def post_workflow(client, message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)

    if not session:
        return  # No active session

    step = session.get('step')

    if step == 'parse_mode':
        session['parse_mode'] = message.text.upper()
        session['step'] = 'message'
        await message.reply("Send me the message content.")
    elif step == 'message':
        session['message'] = message.text
        session['step'] = 'buttons'
        await message.reply("Send me button/link in HTML format or type 'None' to skip.")
    elif step == 'buttons':
        buttons = message.text
        session['buttons'] = buttons if buttons.lower() != 'none' else None
        session['step'] = 'photo'
        await message.reply("Send me a photo or type 'None' to skip.")
    elif step == 'photo':
        if message.photo:
            session['photo'] = message.photo.file_id
        else:
            session['photo'] = None

        session['step'] = 'schedule'
        await message.reply("Do you want to post now or schedule? (Send 'Now' or a date like DD/MM/YYYY)")
    elif step == 'schedule':
        if message.text.lower() == 'now':
            session['schedule_time'] = None
            session['step'] = None
            await send_preview(
                client, user_id, session['channel_name'], session['message'], 
                session['photo'], session['buttons'], session['schedule_time']
            )
            await post_to_channel(
                client, session['channel_id'], session['message'], 
                session['photo'], session['buttons']
            )
            await save_post(user_id, session['channel_id'], session['message'], session['photo'], session['buttons'])
            await message.reply("Post sent successfully!")
            user_sessions.pop(user_id, None)
        else:
            try:
                schedule_date = datetime.strptime(message.text, '%d/%m/%Y')
                session['schedule_time'] = schedule_date
                session['step'] = 'time'
                await message.reply("Send me the time in HH:MM format (24-hour).")
            except ValueError:
                await message.reply("Invalid date format. Please send a valid date like DD/MM/YYYY.")
    elif step == 'time':
        try:
            schedule_time = datetime.strptime(message.text, '%H:%M').time()
            session['schedule_time'] = datetime.combine(session['schedule_time'], schedule_time)
            session['step'] = None

            await send_preview(
                client, user_id, session['channel_name'], session['message'], 
                session['photo'], session['buttons'], session['schedule_time']
            )
            await save_post(user_id, session['channel_id'], session['message'], session['photo'], session['buttons'], session['schedule_time'])
            await message.reply("Post scheduled successfully!")
            user_sessions.pop(user_id, None)
        except ValueError:
            await message.reply("Invalid time format. Please send a valid time like HH:MM.")


@Client.on_message(filters.command("cancel_post") & filters.private)
async def cancel_post(client, message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        user_sessions.pop(user_id, None)
        await message.reply("Post creation process has been canceled.")
    else:
        await message.reply("No active post process to cancel.")


async def connect_channel(client, message, channel_identifier):
    """
    Handle connecting a channel for a user.
    """
    user_id = message.from_user.id

    try:
        # Fetch channel information
        chat = await client.get_chat(channel_identifier)
        if chat.type != "channel":
            await message.reply("This is not a valid channel. Please send a channel username, ID, or invite link.")
            return

        # Verify user is an admin in the channel
        member = await client.get_chat_member(chat.id, user_id)
        if member.status not in ("administrator", "creator"):
            await message.reply("You must be an admin in the channel to connect it.")
            return

        # Save the channel to the database
        await save_user_channel(user_id, chat.id, chat.title)
        await message.reply(f"Channel '{chat.title}' connected successfully! You can now use /post to manage posts.")
    except Exception as e:
        await message.reply(f"Failed to connect the channel. Error: {str(e)}")
