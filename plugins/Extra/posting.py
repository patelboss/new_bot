from pyrogram import Client, filters
from datetime import datetime
from database.posts import save_post, get_user_channels  # Importing necessary DB functions
from utils import send_preview  # Assuming a helper function for previewing posts

# Dictionary to store session states per user
user_sessions = {}

@Client.on_message(filters.command("connect_postchannel") & filters.private)
async def connect_postchannel(client, message):
    user_id = message.from_user.id
    channel_identifier = message.text.split(" ", 1)[1].strip()  # Extract channel identifier from message

    try:
        # Fetch channel information
        chat = await client.get_chat(channel_identifier)

        # Verify that the chat is a channel
        if chat.type != "channel":
            await message.reply("This is not a valid channel. Please send a valid channel username or ID.")
            return

        # Verify user is an admin in the channel
        member = await client.get_chat_member(chat.id, user_id)
        if member.status not in ("administrator", "creator"):
            await message.reply("You must be an admin in the channel to connect it.")
            return

        # Save the channel
        await save_user_channel(user_id, chat.id, chat.title)
        await message.reply(f"Channel '{chat.title}' connected successfully! You can now post to this channel using /post.")

    except Exception as e:
        await message.reply(f"Failed to connect the channel. Error: {str(e)}")


@Client.on_message(filters.command("post") & filters.private)
async def post_command(client, message):
    user_id = message.from_user.id
    user_channels = get_user_channels(user_id)  # Get all connected channels

    if not user_channels:
        await message.reply("You are not connected to any channel. Please connect a channel first using /connect_postchannel.")
        return

    # List all connected channels
    channel_list = "\n".join([f"{channel['channel_name']} (ID: {channel['channel_id']})" for channel in user_channels])
    await message.reply(f"You have the following channels connected:\n{channel_list}\n\nPlease send the channel name to post to.")

    user_sessions[user_id] = {'step': 'select_channel'}


@Client.on_message(filters.private & ~filters.command("cancel_post"))
async def post_workflow(client, message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)

    if not session:
        return  # No active session

    step = session.get('step')

    if step == 'select_channel':
        user_channels = get_user_channels(user_id)
        selected_channel_name = message.text.strip()

        # Find the channel by name
        selected_channel = next((channel for channel in user_channels if channel['channel_name'].lower() == selected_channel_name.lower()), None)
        if not selected_channel:
            await message.reply(f"Channel '{selected_channel_name}' not found in your connected channels. Please send a valid channel name.")
            return

        session['channel_id'] = selected_channel['channel_id']
        session['channel_name'] = selected_channel['channel_name']
        session['step'] = 'parse_mode'

        await message.reply(f"You are about to post to the channel: {session['channel_name']}\nWhat is the parse mode? (HTML/Markdown/None)")

    elif step == 'parse_mode':
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
