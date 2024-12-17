from pyrogram import Client, filters
from pyrogram.enums import ParseMode
import markdown
import re

# Initialize the bot
# app = Client("my_bot")

# Command to convert Markdown to HTML
@Client.on_message(filters.command("convertmd"))
async def convert_markdown(client, message):
    # Check if the message is a reply
    if not message.reply_to_message:
        await message.reply("Please reply to a message that contains Markdown to convert!")
        return

    # Get the text of the replied message
    md_text = message.reply_to_message.text

    if not md_text:
        await message.reply("The replied message does not contain any text to convert!")
        return

    # Convert Markdown to HTML
    try:
        html_text = markdown.markdown(md_text)

        # Convert advanced formatting like quotes and spoilers
        html_text = re.sub(r'```(.*?)```', r'<pre>\1</pre>', html_text, flags=re.DOTALL)  # Code block handling
        html_text = re.sub(r'`(.*?)`', r'<code>\1</code>', html_text)  # Inline code handling
        html_text = re.sub(r'(\*\*|__)(.*?)\1', r'<b>\2</b>', html_text)  # Bold handling
        html_text = re.sub(r'(\*|_)(.*?)\1', r'<i>\2</i>', html_text)  # Italic handling
        html_text = re.sub(r'~~(.*?)~~', r'<s>\1</s>', html_text)  # Strikethrough handling
        html_text = re.sub(r'__(.*?)__', r'<u>\1</u>', html_text)  # Underline handling
        html_text = re.sub(r'([^]+)(http[^]+)', r'<a href="\2">\1</a>', html_text)  # Link handling

        # Convert spoiler text
        html_text = re.sub(r'\|\|(.*?)\|\|', r'<span class="tg-spoiler">\1</span>', html_text)  # Spoiler handling

        # Reply with the HTML formatted message using ParseMode.HTML
        await message.reply(html_text, parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.reply(f"Error during conversion: {e}")

# Command to convert HTML to Markdown
@Client.on_message(filters.command("convertht"))
async def convert_html(client, message):
    # Check if the message is a reply
    if not message.reply_to_message:
        await message.reply("Please reply to a message that contains HTML to convert!")
        return

    # Get the text of the replied message
    html_text = message.reply_to_message.text

    if not html_text:
        await message.reply("The replied message does not contain any text to convert!")
        return

    # Convert HTML back to Markdown (simplified version)
    try:
        # A simple HTML to Markdown conversion for known tags like <b>, <i>, etc.
        markdown_text = html_text.replace("<b>", "**").replace("</b>", "**") \
                                 .replace("<i>", "*").replace("</i>", "*") \
                                 .replace("<u>", "__").replace("</u>", "__") \
                                 .replace("<s>", "~~").replace("</s>", "~~") \
                                 .replace("<code>", "`").replace("</code>", "`") \
                                 .replace("<a href=", "[").replace("</a>", "]") \
                                 .replace(">", "(").replace("<", ")") \
                                 .replace("<span class=\"tg-spoiler\">", "||").replace("</span>", "||")

        # Reply with the Markdown formatted message using ParseMode.MARKDOWN
        await message.reply(markdown_text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply(f"Error during conversion: {e}")

# Start the bot
# app.run()
