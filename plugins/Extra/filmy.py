from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import re
from pyrogram.enums import ParseMode

@Client.on_message(filters.command("ppost"))
async def post_reply(client, message):
    # Ensure the user provided a channel ID and replied to a message
    command_parts = message.text.split()
    if len(command_parts) < 2 or not message.reply_to_message:
        await message.reply("Please provide a valid channel ID and reply to a message using /ppost <channel_id>.")
        return

    channel_id = command_parts[1]  # Extract the channel ID from the command

    # Ensure channel_id is valid (e.g., it starts with '-100' for Telegram channels)
    if not channel_id.startswith("-100"):
        await message.reply("Invalid channel ID. Please provide a valid channel ID starting with '-100'.")
        return

    # Get the original message's media or text
    replied_message = message.reply_to_message
    caption = replied_message.text if replied_message.text else "No caption provided."

    # Parse the caption and extract inline buttons in the correct format
    inline_buttons = parse_buttons_from_caption(caption)

    # Remove button links from the caption to avoid display errors
    caption_without_buttons = remove_button_links(caption)

    # Prepare inline buttons only if there are any
    reply_markup = None
    if inline_buttons:
        reply_markup = InlineKeyboardMarkup(inline_buttons)  # Properly formatted InlineKeyboardMarkup

    # Send message with inline buttons at the bottom
    try:
        if replied_message.photo:
            # If the replied message is a photo
            await client.send_photo(
                chat_id=channel_id,
                photo=replied_message.photo.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        elif replied_message.text:
            # If the replied message is text
            await client.send_message(
                chat_id=channel_id,
                text=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            # Handle unsupported media types
            await client.send_message(
                chat_id=channel_id,
                text="Unsupported media type to forward",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        await message.reply(f"Message posted to channel {channel_id} successfully!")
    except Exception as e:
        await message.reply(f"Failed to post the message. Error: {str(e)}")


def parse_buttons_from_caption(caption: str):
    """
    Parse custom button format `[Button Text](URL)` from the caption and convert them into inline buttons.

    Args:
        caption (str): The caption containing the button format.

    Returns:
        List[List[InlineKeyboardButton]]: Inline buttons structured for Telegram.
    """
    button_links = []
    pattern = r"([^]+)(https?://[^]+)"  # Correct regex pattern for inline buttons

    # Find all matches for the custom button format
    matches = re.findall(pattern, caption)
    for text, url in matches:
        button_links.append([InlineKeyboardButton(text=text, url=url)])  # Each button in a separate row

    return button_links


def remove_button_links(caption: str):
    """
    Remove the custom button format `[Button Text](URL)` from the caption text.

    Args:
        caption (str): The caption containing the button format.

    Returns:
        str: Caption text without the button links.
    """
    return re.sub(r"([^]+)(https?://[^]+)", "", caption).strip()
    
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
