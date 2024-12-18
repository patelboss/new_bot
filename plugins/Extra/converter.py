from pyrogram import Client, filters
from pyrogram.enums import ParseMode
import re
import markdown
# Initialize the bot with your credentials

# Enhanced function to convert Telegram-style Markdown to HTML
def telegram_md_to_html(md_text):
    # If the message has no markdown-style formatting (plain text), return it as-is
    if not re.search(r'[\*\_\~`\|]', md_text):  # No markdown-like characters
        return md_text  # Return plain text without any additional formatting
    
    # Convert bold text: *bold* => <b>bold</b> and **bold** => <b>bold</b>
    md_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', md_text)  # **bold**
    md_text = re.sub(r'\*(.*?)\*', r'<b>\1</b>', md_text)      # *bold*
    
    # Convert italic text: _italic_ => <i>italic</i> and __italic__ => <i>italic</i>
    md_text = re.sub(r'\_\_(.*?)\_\_', r'<i>\1</i>', md_text)  # __italic__
    md_text = re.sub(r'\_(.*?)\_', r'<i>\1</i>', md_text)      # _italic_
    
    # Convert strikethrough text: ~strikethrough~ => <s>strikethrough</s>
    md_text = re.sub(r'~(.*?)~', r'<s>\1</s>', md_text)
    
    # Inline code: `code` => <code>code</code>
    md_text = re.sub(r'`(.*?)`', r'<code>\1</code>', md_text)

    # Code blocks: ```code``` => <pre>code</pre>
    md_text = re.sub(r'```(.*?)```', r'<pre>\1</pre>', md_text, flags=re.DOTALL)

    # Links: [text](http://link.com) => <a href="http://link.com">text</a>
    md_text = re.sub(r'([^]+)(http[^]+)', r'<a href="\2">\1</a>', md_text)

    # Telegram spoiler: ||spoiler|| => <span class="tg-spoiler">spoiler</span>
    md_text = re.sub(r'\|\|(.*?)\|\|', r'<span class="tg-spoiler">\1</span>', md_text)

    # Mention format: @username => <a href="tg://user?id=username">@username</a>
    md_text = re.sub(r'@([a-zA-Z0-9_]+)', r'<a href="tg://user?id=\1">@\1</a>', md_text)

    # Handle hyperlinks with mentions: [@username](tg://user?id=username)
    md_text = re.sub(r'@([a-zA-Z0-9_]+)tg://user\?id=([a-zA-Z0-9_]+)', r'<a href="tg://user?id=\2">@\1</a>', md_text)

    # Handle custom inline markdown links: [some text](www.example.com)
    md_text = re.sub(r'([^]+)(http[^]+)', r'<a href="\2">\1</a>', md_text)

    # Return the HTML formatted text
    return md_text

@Client.on_message(filters.command("convertmd"))
async def convert_markdown_to_html(client, message):
    # Check if the message is a reply
    if not message.reply_to_message:
        await message.reply("Please reply to a message containing Markdown to convert!")
        return

    # Get the text of the replied message
    md_text = message.reply_to_message.text

    if not md_text:
        await message.reply("The replied message doesn't contain any text to convert!")
        return

    # Convert Telegram-style Markdown to HTML
    try:
        html_text = telegram_md_to_html(md_text)
        await message.reply(html_text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"Error during conversion: {e}")

