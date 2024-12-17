
import logging
from info import ADMINS
from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.connections_mdb import add_connection, all_connections, if_active, delete_connection

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@Client.on_message((filters.private | filters.group) & filters.command('connect'))
async def addconnection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        try:
            cmd, group_id = message.text.split(" ", 1)
        except:
            await message.reply_text(
                "<b>Enter in correct format!</b>\n\n"
                "<code>/connect groupid</code>\n\n"
                "<i>Get your Group id by adding this bot to your group and use  <code>/id</code></i>",
                quote=True
            )
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

    try:
        st = await client.get_chat_member(group_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and userid not in ADMINS
        ):
            await message.reply_text("You should be an admin in Given group!", quote=True)
            return
    except Exception as e:
        logger.exception(e)
        await message.reply_text(
            "Invalid Group ID!\n\nIf correct, Make sure I'm present in your group!!",
            quote=True,
        )

        return
    try:
        st = await client.get_chat_member(group_id, "me")
        if st.status == enums.ChatMemberStatus.ADMINISTRATOR:
            ttl = await client.get_chat(group_id)
            title = ttl.title

            addcon = await add_connection(str(group_id), str(userid))
            if addcon:
                await message.reply_text(
                    f"Successfully connected to **{title}**\nNow manage your group from my pm !",
                    quote=True,
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                    await client.send_message(
                        userid,
                        f"Connected to **{title}** !",
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
            else:
                await message.reply_text(
                    "You're already connected to this chat!",
                    quote=True
                )
        else:
            await message.reply_text("Add me as an admin in group", quote=True)
    except Exception as e:
        logger.exception(e)
        await message.reply_text('Some error occurred! Try again later.', quote=True)
        return

@Client.on_message((filters.private | filters.group) & filters.command('disconnect'))
async def deleteconnection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        await message.reply_text("Run /connections to view or disconnect from groups!", quote=True)

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

        st = await client.get_chat_member(group_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            return

        delcon = await delete_connection(str(userid), str(group_id))
        if delcon:
            await message.reply_text("Successfully disconnected from this chat", quote=True)
        else:
            await message.reply_text("This chat isn't connected to me!\nDo /connect to connect.", quote=True)

@Client.on_message(filters.private & filters.command(['connections', 'connection']))
async def connections(client, message):
    userid = message.from_user.id

    groupids = await all_connections(str(userid))
    if groupids is None:
        await message.reply_text(
            "There are no active connections!! Connect to some groups first.",
            quote=True
        )
        return
    buttons = []
    for groupid in groupids:
        try:
            ttl = await client.get_chat(int(groupid))
            title = ttl.title
            active = await if_active(str(userid), str(groupid))
            act = " - ACTIVE" if active else ""
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                    )
                ]
            )
        except:
            pass
    if buttons:
        await message.reply_text(
            "Your connected group details ;\n\n",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    else:
        await message.reply_text(
            "There are no active connections!! Connect to some groups first.",
            quote=True
        )
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

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
