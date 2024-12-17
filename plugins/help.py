from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from plugins.Extra.Cscript import TEXTS

@Client.on_message(filters.command('command_help'))
async def command_help(client, message: Message):
    help_text = """
<b>🔌 Command Connection Management 🔌</b>
Here are the commands to connect and manage groups with your private messages:

🔹 <b>/connect [group_id]</b> - <i>Connect your group to your private chat</i>
    ➡️ Use this command to connect your group with your private chat. This will allow you to receive group updates directly in your PM. You can use it in both private chats and groups. 
    ➡️ For private chats, simply use `/connect [group_id]`, and for groups, the bot will automatically connect to the group you're using it in.

🔹 <b>/connections</b> or <b>/connection</b> - <i>Check or manage all connected groups in PM</i>
    ➡️ These commands allow you to view the list of all groups currently connected to your private chat. You can see which groups are linked and monitor your connections.
    ➡️ You can also use these commands to manage your connections, like deleting them if needed.

🔹 <b>/disconnect</b> - <i>Disconnect a group from your private chat</i>
    ➡️ If you want to stop receiving messages from a connected group, simply use `/disconnect [group_id]` to disconnect that group from your PM. The bot will no longer forward messages from that group to you.

🔹 <b>/id</b> - <i>Get the ID of the group, user, or channel</i>
    ➡️ This command is useful for fetching IDs:
    - If used in a group, you’ll get the group’s ID.
    - If used in a private message, you’ll get the user’s Telegram ID.
    - If replying to a forwarded message from a channel, it will return the channel’s ID.

✨ These commands help you manage your group connections easily and keep your private messages organized! ✨
"""
    await message.reply_text(help_text, parse_mode=ParseMode.HTML)
    

@Client.on_message(filters.command('filters_help'))
async def filters_help(client, message: Message):
    help_text = """
<b>🎛️ Group Filter Management 🎛️</b>
Welcome to the powerful filter system! Here’s a detailed guide on how to manage filters for your group:

🔹 <b>/addf [keyword] [response]</b> - <i>Add a new filter to your group</i>
    ➡️ This command allows you to add a custom filter with a specific keyword and a response. Whenever the keyword is mentioned in the group, the bot will reply with the custom response you set.

🔹 <b>/totalf</b> or <b>/viewf</b> - <i>View all the filters currently active in your group</i>
    ➡️ Use this command to see a list of all the filters running in your group. You’ll get a breakdown of each active filter with its keyword and response.

🔹 <b>/delf [keyword]</b> - <i>Delete a specific filter by keyword</i>
    ➡️ Use this command to remove a filter from your group by simply specifying the keyword. The bot will stop responding to that keyword.

🔹 <b>/delallf</b> - <i>Delete all filters in your group (except global filters)</i>
    ➡️ If you want to remove all filters from your group, this command will delete everything except the global filters. Use this if you want to clean up your group’s filter list quickly.

✨ These commands help you manage your group's filters with ease. Make your group experience smoother with smart filter management! ✨
"""
    await message.reply_text(help_text, parse_mode=ParseMode.HTML)
  
@Client.on_message(filters.command('Global_Filter') & filters.user(ADMINS))
async def global_filter_help(client, message: Message):
    help_text = """
<b>🌟 Global Filter Management 🌟</b>
Here are the commands you can use:

🔹 <b>/addg [keyword]</b> - Add a new global filter  
🔹 <b>/delg [keyword]</b> - Delete a specific global filter  
🔹 <b>/gfilters</b> - View all active global filters  
🔹 <b>/delallg</b> - Remove all global filters  

✨ Make your bot smarter with global filters! ✨
"""
    await message.reply_text(help_text, parse_mode=ParseMode.HTML)
  
def get_random_sticker():
    return random.choice(TEXTS["random_sticker"])

@Client.on_message(filters.command("chelp"))
async def chelp(client, message):
    # Check if the user added "m" after the command
    command_parts = message.text.split()
    use_html = len(command_parts) > 1 and command_parts[1].lower() == "m"

    # Send the sticker first
    sticker_id = get_random_sticker()
    
    m = await message.reply_sticker(sticker_id, 'CAACAgIAAxkBAAEWouFnYZdWgByiIdBga-j3bXRMK7sL3QACYgADTlzSKU6iwxhIxCtxHgQ')  # Default sticker ID if missing
    await asyncio.sleep(2)  # Wait for 2 seconds
    await m.delete()  # Delete the sticker message

    if use_html:
        # Log and send the help text in HTML format
      #  client.LOGGER(__name__).info("Sending help text in HTML format.")
        await message.reply(
            TEXTS.get("HELP_TEXT", "<b>Help text not available.</b>"),
            parse_mode=ParseMode.HTML
        )
    else:
        # Log and display available text methods in Markdown format
        #client.LOGGER(__name__).info("Sending available text methods in Markdown format.")
        await message.reply(
            TEXTS.get("AVAILABLE_TEXT_METHODS", "**Available methods not found.**"),
            parse_mode=ParseMode.MARKDOWN
        )        
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

@Client.on_message(filters.command('misc'))
async def misc_help(client, message: Message):
    help_text = """
<b>⚙️ Miscellaneous Commands ⚙️</b>
Here are some useful commands to interact with the bot and gather information:

🔹 <b>/Info</b> - <i>Get detailed information about yourself</i>
    ➡️ This command provides you with information such as your user ID, username, and other useful details. Perfect for checking your account info.

🔹 <b>/Alive</b> - <i>Check if the bot is online and responsive</i>
    ➡️ Use this command to check if the bot is alive and running smoothly. It will respond with a confirmation message indicating the bot is operational.

🔹 <b>/Ping</b> - <i>Check the bot's ping (latency)</i>
    ➡️ This command checks the bot’s connection speed to the server by sending a ping. It will return the bot's ping in milliseconds, so you can monitor its responsiveness.

🔹 <b>/Telegraph</b> - <i>Get a shareable link for a photo</i>
    ➡️ This command allows you to upload a photo, and the bot will return a shareable link using the Telegraph service. Perfect for sharing images with others.

🔹 <b>/Stickerid</b> - <i>Get the ID of a sticker</i>
    ➡️ When you send a sticker and use this command, the bot will return the unique ID of that sticker, which can be useful for saving or sharing stickers.

🔹 <b>/Getfileid</b> - <i>Get the file ID of any file</i>
    ➡️ If you send any file (image, document, video, etc.), the bot will return its file ID, which you can use to reference or share that file later.

✨ Use these commands to interact with the bot and make the most out of your experience! ✨
"""
    await message.reply_text(help_text, parse_mode=ParseMode.HTML)

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

@Client.on_message(filters.command('contact_help'))
async def contact_help(client, message: Message):
    help_text = """
<b>💬 Contact and Feedback Commands 💬</b>
Here are the commands to help you report issues, communicate with admins, and manage your tokens:

🔹 <b>/Feedback</b> - <i>Report an issue or give feedback</i>
    ➡️ Use this command to report any problems or give feedback to the admin. Simply reply to this message to send your message, and the admin will review it.

🔹 <b>/Talk</b> - <i>Start a conversation with the admin (requires a token)</i>
    ➡️ If you want to talk directly to the admin, you’ll need a special token. If the admin wants to talk to you, they will send you the token.
    ➡️ Use this command with the token to start a private conversation with the admin.

🔹 <b>/create_code</b> - <i>Create a new "Talk" code (Admin only)</i>
    ➡️ Only admins can use this command to create a new token for a user. The token allows the user to start a private conversation with the admin using the `/Talk` command.

🔹 <b>/Delete_code</b> - <i>Delete a "Talk" code (Admin only)</i>
    ➡️ Admins can delete a previously created "Talk" token. This will prevent the user from starting a conversation using that token.

✨ These commands allow you to report issues and communicate directly with admins. Use them wisely! ✨
"""
    await message.reply_text(help_text, parse_mode=ParseMode.HTML)


from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

@Client.on_message(filters.command('Index_help'))
async def index_help(client, message: Message):
    help_text = """
<b>📂 File Indexing Commands 📂</b>
These commands help you manage and request files in the system. Here's how to use them:

🔹 <b>/index</b> - <i>Request a file from the bot</i>
    ➡️ If you have files stored with the bot, you can use this command to request one. The bot will process your request and provide the file you're looking for.

🔹 <b>/Setskip</b> - <i>Set the index skip number</i>
    ➡️ This command allows you to adjust the number of steps the bot will skip when indexing files. You can use this to customize how the bot processes requests and skips files in the indexing system.

✨ Use these commands to manage your files more efficiently and streamline your experience with the bot! ✨
"""
    await message.reply_text(help_text, parse_mode=ParseMode.HTML)



from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

@Client.on_message(filters.command('fsub_help'))
async def fsub_help(client, message: Message):
    help_text = """
<b>🔐 Force Subscribe Commands 🔐</b>
These commands allow you to manage force subscription settings for your group:

🔹 <b>/fsub &lt;channel id&gt;</b> - <i>Set a channel to force subscribe users in your group</i>
    ➡️ Use this command to set a channel that users must subscribe to in order to interact with your group. Simply replace `<channel id>` with the actual channel ID.

🔹 <b>/Nofsub</b> - <i>Delete the force subscribe channel</i>
    ➡️ This command removes the currently set forced subscription channel from your group, allowing users to interact without subscribing to a channel.

🔹 <b>/Id</b> - <i>Get your channel's ID</i>
    ➡️ This command returns the ID of the channel you're using, which can be useful when setting or deleting the force subscribe channel.

✨ Use these commands to manage subscriptions and ensure users are following the channels you set! ✨
"""
    await message.reply_text(help_text, parse_mode=ParseMode.HTML)


from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

@Client.on_message(filters.command('help'))
async def help_command(client, message: Message):
    help_text = """
<b>🆘 Main Help Commands 🆘</b>
Welcome to the bot! Here are the main help commands you can use to explore the bot's features:

🔹 <b>/Index_help</b> - <i>Learn about index-related queries</i>
    ➡️ This command will help you understand how to request files from the bot and manage index settings.

🔹 <b>/Fsub_help</b> - <i>Get help with force subscribe channel</i>
    ➡️ Use this to manage channels that users must subscribe to in order to access your group. Learn how to set, remove, or query the subscription channel.

🔹 <b>/Filter_help</b> - <i>Get help with filters</i>
    ➡️ Learn about how to add, delete, and manage filters in your group or globally.

🔹 <b>/Misc</b> - <i>Access miscellaneous features</i>
    ➡️ Some unique features that may not fit into other categories. This command includes checking the bot's status, user information, and other fun features.

🔹 <b>/Contact_help</b> - <i>Learn how to contact the admin</i>
    ➡️ Know how to report an issue or talk to the admin using tokens, feedback, and more.

🔹 <b>/Chelp</b> - <i>Get help with posting in channels</i>
    ➡️ Learn how to interact with channels and post content through the bot. This will help you post in channels with ease.

✨ Use these commands to explore the bot's features and enhance your experience! ✨
"""
    await message.reply_text(help_text, parse_mode=ParseMode.HTML)
