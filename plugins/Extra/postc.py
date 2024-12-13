from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired
from pyrogram.enums import ChatMemberStatus
from datetime import datetime
from pytz import timezone
from database import save_channel_stats, extract_common_words, save_template_data

IST = timezone('Asia/Kolkata')

@Client.on_message(filters.command("add_channel"))
async def add_channel(client, message):
    # Check if there are multiple channel IDs provided
    if len(message.command) < 2:
        await message.reply("Please provide the channel ID(s): `/add_channel <channel_id1> <channel_id2> ...`")
        return

    # Extract channel IDs from the message
    channel_ids = message.command[1:]

    # Loop through each channel ID provided
    for channel_id in channel_ids:
        try:
            # Verify the bot's admin rights in the channel
            channel_info = await client.get_chat(channel_id)
            bot_permissions = await client.get_chat_member(channel_id, client.me.id)
            if bot_permissions.status != ChatMemberStatus.ADMINISTRATOR:
                await message.reply(f"The bot needs admin rights to fetch data for channel {channel_id}.")
                return
            
            # Check if the user is either an admin or the owner of the channel
            user_permissions = await client.get_chat_member(channel_id, message.from_user.id)
            if user_permissions.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                await message.reply(f"You need admin or owner rights in the channel {channel_id} to add it.")
                return

            # Collect channel data
            total_users = channel_info.members_count
            channel_name = channel_info.title
            link = await client.export_chat_invite_link(channel_id)
            
            # Perform posts analysis and extract common words
            posts = await client.get_chat_history(channel_id, limit=100)  # Modify limit as needed
            top_words = extract_common_words(posts)

            # Get current IST time for first_added_date
            first_added_date = datetime.now(IST)

            # Save to the database
            await save_channel_stats(channel_id, first_added_date, total_users, message.from_user.id, link, top_words)
            
            # After successful addition, send instructions for posting
            await message.reply(f"Channel {channel_name} (ID: {channel_id}) added successfully!\n"
                                 f"Link: {link}\n"
                                 f"Total Users: {total_users}\n"
                                 f"Top Keywords: {top_words}\n\n"
                                 "You can now post to this channel. Use the `/post <channel_id> <message>` command to post.")
            
        except ChatAdminRequired:
            await message.reply(f"The bot does not have admin rights in the channel {channel_id}.")
        except Exception as e:
            await message.reply(f"Error while adding channel {channel_id}: {str(e)}")

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@Client.on_message(filters.command("set_template"))
async def set_template(client, message):
    if len(message.command) < 2:
        await message.reply("Please provide template data in the format:\n"
                             "`Parse mode=<HTML/Markdown>`\n"
                             "`privacy_mode=<on/off>`\n"
                             "`Link_preview=<on/off>`\n"
                             "`Button 1=<link>` `Button 2=<link>`...")
        return
    
    # Extract template settings from the message
    template_data = ' '.join(message.command[1:])
    parse_mode = "Markdown"  # Default value
    privacy_mode = "off"     # Default value
    link_preview = "off"     # Default value
    buttons = []

    # Parsing user input for settings
    for part in template_data.split():
        if part.lower().startswith("parse mode="):
            parse_mode = part.split("=")[1].upper()
        elif part.lower().startswith("privacy_mode="):
            privacy_mode = part.split("=")[1].lower()
        elif part.lower().startswith("link_preview="):
            link_preview = part.split("=")[1].lower()
        elif part.lower().startswith("button"):
            button_data = part.split("=")
            button_label = button_data[0].strip()
            button_link = button_data[1].strip()
            buttons.append((button_label, button_link))

    # Save the template to the database
    await save_template_data(message.from_user.id, parse_mode, privacy_mode, link_preview, buttons)
    
    await message.reply("Template updated successfully!")

# Preview command to show the post before sending
@Client.on_message(filters.command("preview"))
async def preview_post(client, message):
    if len(message.command) < 3:
        await message.reply("Please provide the channel ID and message to preview: `/preview <channel_id> <message>`.")
        return
    
    channel_id = message.command[1]
    message_text = ' '.join(message.command[2:])  # The actual message to be previewed
    
    # Get template data from the database
    template_data = await db.templates.find_one({'user_id': message.from_user.id})
    if template_data:
        parse_mode = template_data['parse_mode']
        privacy_mode = template_data['privacy_mode']
        link_preview = template_data['link_preview']
        buttons = template_data['buttons']
    else:
        parse_mode = "Markdown"
        privacy_mode = "off"
        link_preview = "off"
        buttons = []

    # Create the inline buttons if any
    inline_buttons = []
    for label, url in buttons:
        inline_buttons.append([InlineKeyboardButton(label, url=url)])

    # Prepare the message options
    message_options = {
        "parse_mode": parse_mode,
        "disable_web_page_preview": link_preview == "off",
        "reply_markup": InlineKeyboardMarkup(inline_buttons) if inline_buttons else None
    }

    # Send the preview back to the user
    await message.reply(message_text, **message_options)

# Send the message with the template settings
async def send_post_with_template(client, channel_id, message_text, user_id):
    # Get template data from the database
    template_data = await db.templates.find_one({'user_id': user_id})
    if template_data:
        parse_mode = template_data['parse_mode']
        privacy_mode = template_data['privacy_mode']
        link_preview = template_data['link_preview']
        buttons = template_data['buttons']
    else:
        parse_mode = "Markdown"
        privacy_mode = "off"
        link_preview = "off"
        buttons = []

    # Create the inline buttons if any
    inline_buttons = []
    for label, url in buttons:
        inline_buttons.append([InlineKeyboardButton(label, url=url)])

    # Prepare the message options
    message_options = {
        "parse_mode": parse_mode,
        "disable_web_page_preview": link_preview == "off",
        "reply_markup": InlineKeyboardMarkup(inline_buttons) if inline_buttons else None
    }

    # Send the post to the channel
    await client.send_message(channel_id, message_text, **message_options)

