from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired
from pyrogram.enums import ChatMemberStatus
from datetime import datetime
from pytz import timezone
from database.stats import save_channel_stats, save_template_data
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from pytz import timezone
from database.stats import save_post_data, get_user_channels, delete_post_data, update_post_data
import re
from collections import Counter

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


# Handle the post command - allow users to select a message they want to post
@Client.on_message(filters.command('post'))
async def post_command(client, message):
    user_id = message.from_user.id
    
    # Check if the user has any connected channels
    connected_channels = await get_user_channels(user_id)  # Assuming this function returns the list of connected channels
    
    if not connected_channels:
        await message.reply("You haven't connected any channels yet. Please add a channel using /add_channel.")
        return

    # Ask user to reply to the message they want to post
    await message.reply("Please reply to the message you want to post in your channel(s).")

# Handle the reply to message for posting - user chooses channels
@Client.on_message(filters.reply)
async def handle_reply_for_post(client, message):
    user_id = message.from_user.id
    
    # Check if the user has any connected channels
    connected_channels = await get_user_channels(user_id)
    
    if not connected_channels:
        await message.reply("You haven't connected any channels yet. Please add a channel using /add_channel.")
        return

    # Create inline buttons for each connected channel
    inline_buttons = []
    for channel in connected_channels:
        inline_buttons.append([InlineKeyboardButton(f"Post to {channel}", callback_data=f"post_to_{channel}")])

    inline_buttons.append([InlineKeyboardButton("Post to All", callback_data="post_to_all")])

    # Create the inline keyboard markup
    reply_markup = InlineKeyboardMarkup(inline_buttons)

    # Send a message asking user to choose a channel to post
    await message.reply("Please choose the channel(s) to post this message to:", reply_markup=reply_markup)

# Handle user selecting a channel to post to
@Client.on_callback_query(filters.regex("post_to_"))
async def post_to_channel(client, callback_query):
    user_id = callback_query.from_user.id
    channel_id = callback_query.data.split("_")[2]  # Extract channel ID from callback data

    # Get the message user is replying to
    replied_message = callback_query.message.reply_to_message
    if not replied_message:
        await callback_query.answer("No message to post.")
        return

    message_text = replied_message.text or replied_message.caption

    # Get template data
    template_data = await db.templates.find_one({'user_id': user_id})
    parse_mode = template_data['parse_mode'] if template_data else "Markdown"
    privacy_mode = template_data['privacy_mode'] if template_data else "off"
    link_preview = template_data['link_preview'] if template_data else "off"
    buttons = template_data['buttons'] if template_data else []

    # Create inline buttons if any
    inline_buttons = [[InlineKeyboardButton(label, url=url) for label, url in buttons]]

    # Prepare the message options
    message_options = {
        "parse_mode": parse_mode,
        "disable_web_page_preview": link_preview == "off",
        "reply_markup": InlineKeyboardMarkup(inline_buttons) if inline_buttons else None
    }

    # Send the post to the selected channel
    try:
        await client.send_message(channel_id, message_text, **message_options)
        await callback_query.answer(f"Message posted to {channel_id} successfully!")
    except Exception as e:
        await callback_query.answer(f"Error posting to {channel_id}: {str(e)}")

# Function to save post data to the database
async def save_post_data(user_id, channel_id, message_id, message_text):
    try:
        post_data = {
            "user_id": user_id,
            "channel_id": channel_id,
            "message_id": message_id,
            "message_text": message_text,
            "date": datetime.now(IST)
        }
        await db.posts.insert_one(post_data)
    except Exception as e:
        print(f"Error saving post data: {str(e)}")
#### **4. Broadcast Functionality (Post to All Channels)**

#```python
@Client.on_callback_query(filters.regex(r"^post_to_all"))
async def post_to_all_channels(client, callback_query):
    user_id = callback_query.from_user.id
    message = callback_query.message.reply_to_message  # Get the original message to post
    
    connected_channels = await get_user_channels(user_id)  # Get all connected channels
    
    if not connected_channels:
        await callback_query.answer("You don't have any connected channels to post to.")
        return

    # Send the message to all channels
    for channel in connected_channels:
        sent_message = await client.send_message(channel['id'], message.text, parse_mode="Markdown")
        
        # Save the post data in the database
        post_data = {
            "user_id": user_id,
            "channel_id": channel['id'],
            "message_id": sent_message.message_id,
            "original_message_id": message.message_id,
            "timestamp": datetime.now(IST),
            "edit_timestamp": datetime.now(IST) + timedelta(hours=6),  # Set to auto delete after 6 hours
        }
        await save_post_data(post_data)
    
    await callback_query.answer("Post sent to all channels!")

@Client.on_callback_query(filters.regex(r"^edit_"))
async def edit_post(client, callback_query):
    message_id = int(callback_query.data.split("_")[1])
    
    # Fetch post data from DB
    post_data = await get_post_data(message_id)  # Get post data from the database
    
    # Ensure the post is within 6 hours of posting time
    if datetime.now(IST) > post_data["edit_timestamp"]:
        await callback_query.answer("This post cannot be edited after 6 hours.")
        return

    # Proceed to edit the post (e.g., prompt the user to send the updated message)
    await callback_query.answer("You can now edit your post.")
    await callback_query.message.reply("Send the new text to update your post:")

@Client.on_message(filters.reply)
async def handle_edit_message(client, message):
    if message.reply_to_message and message.reply_to_message.text.startswith("Send the new text"):
        # Edit the post in the channel
        original_message_id = message.reply_to_message.text.split(":")[1]
        updated_text = message.text
        
        post_data = await get_post_data_by_original_message_id(original_message_id)  # Get the original post data from DB
        sent_message = await client.edit_message_text(post_data['channel_id'], post_data['message_id'], updated_text, parse_mode="Markdown")
        
        # Update the database with the new content
        await update_post_data(post_data['message_id'], updated_text)
        await message.reply("Your post has been updated!")

@Client.on_callback_query(filters.regex(r"^delete_"))
async def delete_post(client, callback_query):
    message_id = int(callback_query.data.split("_")[1])
    
    # Fetch post data from DB
    post_data = await get_post_data(message_id)  # Get post data from the database
    
    # Ensure the post is within 6 hours of posting time
    if datetime.now(IST) > post_data["edit_timestamp"]:
        await callback_query.answer("This post cannot be deleted after 6 hours.")
        return

    # Delete the post from the channel
    await client.delete_messages(post_data['channel_id'], post_data['message_id'])
    
    # Remove the post data from the database
    await delete_post_data(post_data['message_id'])
    
    await callback_query.answer("Your post has been deleted.")
    

def extract_common_words(posts):
    # Combine all post texts into one large string
    combined_text = " ".join([post.text for post in posts])
    
    # Remove non-alphanumeric characters and split text into words
    words = re.findall(r'\b\w+\b', combined_text.lower())
    
    # Define a set of common stop words to exclude
    stop_words = {"the", "and", "a", "to", "is", "of", "in", "for", "on", "it"}
    
    # Filter out stop words
    filtered_words = [word for word in words if word not in stop_words]
    
    # Count frequency of each word
    word_counts = Counter(filtered_words)
    
    # Get top 5 most common words
    top_words = word_counts.most_common(5)
    
    return top_words
