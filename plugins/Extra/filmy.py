from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import re
from pyrogram.enums import ParseMode

@Client.on_message(filters.command("ppost"))
async def post_reply(client, message):
    command_parts = message.text.split()
    if len(command_parts) < 2 or not message.reply_to_message:
        await message.reply("Please provide a valid channel ID and reply to a message using /ppost <channel_id>.")
        return

    channel_id = command_parts[1]

    if not channel_id.startswith("-100"):
        await message.reply("Invalid channel ID. Please provide a valid channel ID starting with '-100'.")
        return

    replied_message = message.reply_to_message
    caption = replied_message.text if replied_message.text else "No caption provided."
    button_links = parse_buttons_from_caption(caption)
    caption_without_buttons = remove_markdown_links(caption)
    inline_buttons = InlineKeyboardMarkup(button_links) if button_links else None

    try:
        if replied_message.photo:
            await client.send_photo(
                chat_id=channel_id,
                photo=replied_message.photo.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=inline_buttons
            )
        elif replied_message.text:
            await client.send_message(
                chat_id=channel_id,
                text=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=inline_buttons
            )
        else:
            await client.send_message(
                chat_id=channel_id,
                text="Unsupported media type to forward.",
                reply_markup=inline_buttons
            )
        await message.reply(f"Message posted to channel {channel_id} successfully!")
    except Exception as e:
        await message.reply(f"Failed to post the message. Error: {e}")

def parse_buttons_from_caption(caption: str):
    """
    Parse markdown-style links from the caption and convert them into buttons.

    Args:
        caption (str): The caption containing markdown-style links.

    Returns:
        List[List[InlineKeyboardButton]]: Inline buttons structured for Telegram.
    """
    button_links = []
    pattern = r"(.*?)(https?://.*?)"  # Regex pattern for markdown links

    # Find all matches for the markdown links
    matches = re.findall(pattern, caption)
    for text, url in matches:
        button_links.append([InlineKeyboardButton(text=text, url=url)])  # Each button in a separate row

    return button_links


def remove_markdown_links(caption: str):
    """
    Remove markdown-style links from the caption text.

    Args:
        caption (str): The caption containing markdown-style links.

    Returns:
        str: Caption text without markdown links.
    """
    return re.sub(r"(.*?)(https?://.*?)", "", caption).strip()
from pyrogram import Client, filters
from pyrogram.enums import ParseMode

@Client.on_message(filters.command("chelp"))
async def chelp(client, message):
    help_text = """
<b>Telegram Markdown & Formatting Guide:</b>

<i>You can use these formatting methods in your messages:</i>

<b>1. Bold:</b>
<code>*Your Text*</code> → <b>Your Text</b>

<b>2. Italic:</b>
<code>_Your Text_</code> → <i>Your Text</i>

<b>3. Underline:</b>
<code>__Your Text__</code> → <u>Your Text</u>

<b>4. Strikethrough:</b>
<code>~Your Text~</code> → <s>Your Text</s>

<b>5. Monospace:</b>
<code>`Your Text`</code> → <code>Your Text</code>

<b>6. Preformatted Block:</b>
<code>```Your Text```</code> → 
<pre>Your Text</pre>

<b>7. Spoiler:</b>
<code>||Your Text||</code> → <tg-spoiler>Your Text</tg-spoiler>

<b>8. Quote:</b>
Simply type <code>&gt;</code> at the beginning of a line:
<code>&gt; Your Text</code> → 
<blockquote>Your Text</blockquote>

<b>9. Inline Link:</b>
<code>[Text](https://example.com)</code> → [Text](https://example.com)

<b>10. Custom Inline Code:</b>
<code>```
<code>Custom text or programming code</code>
```</code> → Displays a block of code.

<b>11. Inline Buttons:</b>
Used programmatically by bots to create interactive messages.

<i>Note:</i>
Ensure you use the correct <b>ParseMode</b> (Markdown or HTML) when sending messages. Some formats like **Spoiler** only work in MarkdownV2.
"""
    await message.reply(help_text, parse_mode=ParseMode.HTML)
