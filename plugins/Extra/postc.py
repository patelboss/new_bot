from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode, ChatMemberStatus
import re
import logging
import random
import asyncio
# Initialize the logger
#logger = logging.getLogger(__name__)
#logging.basicConfig(level=logging.INFO)
sticker_ids = [
    "CAACAgIAAxkBAAItAmdbY-9IY20HNfLFeeboOOex74M0AAL9AQACFkJrCqSvYaKm6vLJHgQ",
    "CAACAgIAAxkBAAIs1GdbWBhGfsD2U3Z2pGiR-d64z08mAAJvAAPb234AAZlbUKh7k4B0HgQ",
    "CAACAgIAAxkBAAIsz2dbV_286mg26Vx67MOWmyG-WvK7AAJtAAPb234AAXUe7IXy-0SlHgQ",
    "CAACAgQAAxkBAAIs_mdbY-Zk1JR7yRLoWsi8NbJEMFerAALVGAACOqGIUIer-Up9iv5aHgQ",
    "CAACAgQAAxkBAAIs-mdbY96brNo0bbqiAT0h9aHmGjfZAAISDgACQln9BFRvgD6jmKybHgQ"
]

#def get_random_sticker():
#    return random.choice(sticker_ids)

@Client.on_message(filters.command("cpost"))
async def cpost(client, message):
#    random_sticker = get_random_sticker()
#    m = await message.reply_sticker(random_sticker)
#    await asyncio.sleep(1)
#    await m.delete()
    command_parts = message.text.split()
    if len(command_parts) < 2 or not message.reply_to_message:
#        logger.warning("Command is missing required parts or no reply message found.")
        await message.reply(f"<b>Please provide a valid channel ID and reply to a message using /cpost <channel_id>.\nUse /chelp to know about formatting\nIf you Dont Know Your Channel Id\nJust Forward Me Any Message From Your Channel And Reply That Message /id .</b>", parse_mode=ParseMode.HTML)
        return

    channel_id = command_parts[1]
#    logger.info(f"Extracted channel_id: {channel_id}")

    if not channel_id.startswith("-100"):
#        logger.error(f"Invalid channel ID: {channel_id}")
        await message.reply(f"<b>Invalid channel ID. Please provide a valid channel ID starting with '-100'.\nIf you Dont Know Your Channel Id\nJust Forward Me Any Message From Your Channel And Reply That Message /id .</b>", parse_mode=ParseMode.HTML)
        return

    # Check if the user is admin or owner of the target channel
    user_id = message.from_user.id  # Get the user ID of the person issuing the command
    if not await is_user_admin_or_owner(client, channel_id, user_id):
        await message.reply(f"<b>You don't have permission to post in this channel.</b>", parse_mode=ParseMode.HTML)
        return

    replied_message = message.reply_to_message
    caption = replied_message.caption or replied_message.text or ""
 #   logger.info(f"Replied message caption: {caption}")

    inline_buttons = extract_buttons_from_caption(caption)
    caption_without_buttons = remove_button_links(caption)
    reply_markup = InlineKeyboardMarkup(inline_buttons) if inline_buttons else None

#    random_sticker = get_random_sticker()
    m = await message.reply_sticker("CAACAgIAAxkBAAItiGdbfpaxWep4EM9_-96N_gop6O0VAAJiAANOXNIpTqLDGEjEK3EeBA")
    await asyncio.sleep(2)
    await m.delete()
        #continue 

    try:
        if replied_message.photo:
#            logger.info("Replied message is a photo. Sending to the channel...")
            await client.send_photo(
                chat_id=channel_id,
                photo=replied_message.photo.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        elif replied_message.video:
#            logger.info("Replied message is a video. Sending to the channel...")
            await client.send_video(
                chat_id=channel_id,
                video=replied_message.video.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        elif replied_message.document:
#            logger.info("Replied message is a document. Sending to the channel...")
            await client.send_document(
                chat_id=channel_id,
                document=replied_message.document.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        elif replied_message.text:
#            logger.info("Replied message is text. Sending to the channel...")
            await client.send_message(
                chat_id=channel_id,
                text=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        else:
#            logger.error("Unsupported media type in the replied message.")
            await client.send_message(
                chat_id=message.chat.id,
                text="Unsupported media type to forward.",
            )

        await message.reply(f"Message posted to channel {channel_id} successfully!")
#        logger.info(f"Message posted to channel {channel_id} successfully.")
    except Exception as e:
#        logger.exception(f"Failed to post the message. Error: {str(e)}")
        await message.reply(f"Failed to post the message. Error: {str(e)}")



@Client.on_message(filters.command("ppost"))
async def private_cpost(client, message):
#    random_sticker = get_random_sticker()
#    m = await message.reply_sticker(random_sticker)
#    await asyncio.sleep(1)
#    await m.delete()
    command_parts = message.text.split()
    if len(command_parts) < 2 or not message.reply_to_message:
#        logger.warning("Command is missing required parts or no reply message found.")
        await message.reply(f"<b>Please provide a valid channel ID and reply to a message using /cpost <channel_id>.\nUse /chelp to know about formatting\nIf you Dont Know Your Channel Id\nJust Forward Me Any Message From Your Channel And Reply That Message /id .</b>", parse_mode=ParseMode.HTML)
        return

    channel_id = command_parts[1]
#    logger.info(f"Extracted channel_id: {channel_id}")

    if not channel_id.startswith("-100"):
#        logger.error(f"Invalid channel ID: {channel_id}")
        await message.reply(f"<b>Invalid channel ID. Please provide a valid channel ID starting with '-100'.\nIf you Dont Know Your Channel Id\nJust Forward Me Any Message From Your Channel And Reply That Message /id .</b>", parse_mode=ParseMode.HTML)
        return

    # Check if the user is admin or owner of the target channel
    user_id = message.from_user.id  # Get the user ID of the person issuing the command
    if not await is_user_admin_or_owner(client, channel_id, user_id):
        await message.reply(f"<b>You don't have permission to post in this channel.</b>", parse_mode=ParseMode.HTML)
        return

    replied_message = message.reply_to_message
    caption = replied_message.caption or replied_message.text or ""
 #   logger.info(f"Replied message caption: {caption}")

    inline_buttons = extract_buttons_from_caption(caption)
    caption_without_buttons = remove_button_links(caption)
    reply_markup = InlineKeyboardMarkup(inline_buttons) if inline_buttons else None

#    random_sticker = get_random_sticker()
    m = await message.reply_sticker("CAACAgIAAxkBAAItiGdbfpaxWep4EM9_-96N_gop6O0VAAJiAANOXNIpTqLDGEjEK3EeBA")
    await asyncio.sleep(2)
    await m.delete()
        #continue 

    try:
        if replied_message.photo:
#            logger.info("Replied message is a photo. Sending to the channel...")
            await client.send_photo(
                chat_id=channel_id,
                photo=replied_message.photo.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                protect_content=True
            )
        elif replied_message.video:
#            logger.info("Replied message is a video. Sending to the channel...")
            await client.send_video(
                chat_id=channel_id,
                video=replied_message.video.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                protect_content=True
            )
        elif replied_message.document:
#            logger.info("Replied message is a document. Sending to the channel...")
            await client.send_document(
                chat_id=channel_id,
                document=replied_message.document.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                protect_content=True
            )
        elif replied_message.text:
#            logger.info("Replied message is text. Sending to the channel...")
            await client.send_message(
                chat_id=channel_id,
                text=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                protect_content=True
            )
        else:
#            logger.error("Unsupported media type in the replied message.")
            await client.send_message(
                chat_id=message.chat.id,
                text="Unsupported media type to forward.",
            )

        await message.reply(f"<b>Message posted to channel {channel_id} successfully!</b>", parse_mode=ParseMode.HTML)
#        logger.info(f"Message posted to channel {channel_id} successfully.")
    except Exception as e:
#        logger.exception(f"Failed to post the message. Error: {str(e)}")
        await message.reply(f"Failed to post the message. Error: {str(e)}")


async def is_user_admin_or_owner(client, channel_id, user_id):
    """
    Check if the user is an admin or the owner of the channel.
    Returns True if the user is an admin or owner, False otherwise.
    """
    try:
        # Get the chat member information
        member = await client.get_chat_member(channel_id, user_id)
        
        # Check if the member is an admin or the owner
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return True
        return False
    except Exception as e:
        # Handle any errors (e.g., user is not a member of the channel)
        #logger.error(f"Error checking user permissions: {str(e)}")
        return False


def extract_buttons_from_caption(caption: str):
    """
    Extracts buttons in the format: {BUTTON_TEXT}-{URL}
    """
    button_links = []
    pattern = r"\{(.*?)\}\-{(https?:\/\/[^\s]+)}"  # Correct pattern to match button text and URL
#    logger.info(f"Button extraction pattern: {pattern}")
    
    # Using re.findall() to find all matches
    matches = re.findall(pattern, caption)
#    logger.info(f"Matches found: {matches}")
    
    for text, url in matches:
 #       logger.info(f"Creating button: {text} - {url}")
        button_links.append([InlineKeyboardButton(text=text, url=url)])
    
  #  logger.info(f"Extracted inline buttons: {button_links}")
    return button_links

def remove_button_links(caption: str):
    """
    Removes button links in the format: {BUTTON_TEXT}-{URL} from the caption
    """
    pattern = r"\{(.*?)\}\-{(https?:\/\/[^\s]+)}"
    cleaned_caption = re.sub(pattern, "", caption).strip()
    return cleaned_caption

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
<code>{BUTTON TEXT}-{URL}</code>
<i>Note:</i> Don't Use <b>Wrong URL</b> &amp; Don't Add <b>Extra Spaces</b> 
<b> Use Command 
<b> /cpost to post in channel & </b>
<b> /ppost to post private post (that can't be forwarded) </b>
<b> Join @Filmykeedha For More Updates.</b>
"""
#    random_sticker = get_random_sticker()
    m = await message.reply_sticker("CAACAgIAAxkBAAIMU2dBzBWjzGCg_x2tFumZ76z5l5JiAAJiAANOXNIpTqLDGEjEK3EeBA")
    await asyncio.sleep(2)
    await m.delete()
    await message.reply(help_text, parse_mode=ParseMode.HTML)
