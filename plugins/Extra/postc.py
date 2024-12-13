from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
from database.stats import save_user_stats, save_channel_stats, get_user_stats, get_channel_stats  # Database operations
from config import ADMINS

# ------------------ Command Handler ------------------

@Client.on_message(filters.command("cpost"))
async def cpost_filmykeedha(client, message):
    await handle_post(client, message, protect_content=False)


@Client.on_message(filters.command("ppost"))
async def ppost_filmykeedha(client, message):
    await handle_post(client, message, protect_content=True)


async def handle_post(client, message, protect_content):
    command_parts = message.text.split()

    if len(command_parts) < 2 or not message.reply_to_message:
        await message.reply("Please reply to a message to post and provide the channel ID.")
        return

    channel_id = command_parts[1]

    if not channel_id.startswith("-100"):
        await message.reply("Invalid channel ID. Please provide a valid ID starting with -100.")
        return

    user_id = message.from_user.id
    result = await is_user_admin_or_owner(client, channel_id, user_id)

    if isinstance(result, bool):
        if not result:
            await message.reply("You don't have permission to post in this channel.")
            return
    elif isinstance(result, dict) and "error" in result:
        await message.reply(f"Error: {result['error']}")
        return

    # Prepare the message
    replied_message = message.reply_to_message
    caption = replied_message.caption or replied_message.text or ""
    inline_buttons = extract_buttons_from_caption(caption)
    caption_without_buttons = remove_button_links(caption)
    reply_markup = InlineKeyboardMarkup(inline_buttons) if inline_buttons else None

    try:
        # Send the message based on the type
        if replied_message.photo:
            await client.send_photo(
                chat_id=channel_id,
                photo=replied_message.photo.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                protect_content=protect_content
            )
        elif replied_message.video:
            await client.send_video(
                chat_id=channel_id,
                video=replied_message.video.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                protect_content=protect_content
            )
        elif replied_message.document:
            await client.send_document(
                chat_id=channel_id,
                document=replied_message.document.file_id,
                caption=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                protect_content=protect_content
            )
        elif replied_message.text:
            await client.send_message(
                chat_id=channel_id,
                text=caption_without_buttons,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                protect_content=protect_content
            )
        else:
            await message.reply("Unsupported media type.")
            return

        # Log stats
        await save_user_stats(user_id, channel_id)
        await save_channel_stats(client, channel_id)

        await message.reply(f"Message successfully posted to channel ID: {channel_id}")
    except Exception as e:
        await message.reply(f"Failed to post message. Error: {str(e)}")


@Client.on_message(filters.command("cstats"))
async def cstats_filmykeedha(client, message):
    if message.from_user.id not in ADMINS:
        return await message.reply("This command is for admins only.")
    
    user_stats = await get_user_stats()
    channel_stats = await get_channel_stats()

    # Format and send the stats
    user_stats_text = "\n".join([f"User {stat['user_id']} posted {stat['message_count']} messages in {len(stat['channels'])} channels." for stat in user_stats])
    channel_stats_text = "\n".join([f"Channel {stat['channel_id']} has {stat['members']} members. First added on {stat['first_added']}. Daily avg: {stat['daily_avg']}." for stat in channel_stats])

    await message.reply(f"<b>User Stats:</b>\n{user_stats_text}\n\n<b>Channel Stats:</b>\n{channel_stats_text}", parse_mode=ParseMode.HTML)


# ------------------ Button Extraction and Caption Cleaning ------------------

def extract_buttons_from_caption(caption: str):
    pattern = r"\{(.*?)\}\-{(https?:\/\/[^\s]+)}"
    matches = re.findall(pattern, caption)
    return [[InlineKeyboardButton(text=text, url=url)] for text, url in matches]


def remove_button_links(caption: str):
    pattern = r"\{(.*?)\}\-{(https?:\/\/[^\s]+)}"
    return re.sub(pattern, "", caption).strip()


# ------------------ Admin and Owner Check ------------------

async def is_user_admin_or_owner(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception as e:
        return {"error": str(e)}
