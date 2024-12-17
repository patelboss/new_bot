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
