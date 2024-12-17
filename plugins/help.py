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
  
