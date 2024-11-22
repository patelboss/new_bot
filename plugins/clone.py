# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

# Clone Code Credit : YT - @Tech_VJ / TG - @VJ_Bots / GitHub - @VJBots

from info import API_ID, API_HASH, CLONE_MODE, LOG_CHANNEL
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from database.users_chats_db import db
import re
from Script import script

@Client.on_message(filters.command('clone'))
async def clone_menu(client, message):
    if CLONE_MODE == False:
        return 
    if await db.is_clone_exist(message.from_user.id):
        return await message.reply("*Not Available Yet*")
    else:
        pass
    techvj = await client.ask(message.chat.id, "<b>Not Available Yet</b>")
    if techvj.text == '/cancel':
        await techvj.delete()
        return await message.reply('<b>ᴄᴀɴᴄᴇʟᴇᴅ ᴛʜɪs ᴘʀᴏᴄᴇss 🚫</b>')
    if techvj.forward_from and techvj.forward_from.id == 93372553:
        try:
            bot_token = re.findall(r"\b(\d+:[A-Za-z0-9_-]+)\b", techvj.text)[0]
        except:
            return await message.reply('<b>sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ 😕</b>')
    else:
        return await message.reply('<b>ɴᴏᴛ ꜰᴏʀᴡᴀʀᴅᴇᴅ ꜰʀᴏᴍ @BotFather 😑</b>')
    user_id = message.from_user.id
    msg = await message.reply_text("**👨‍💻 ᴡᴀɪᴛ ᴀ ᴍɪɴᴜᴛᴇ ɪ ᴀᴍ ᴄʀᴇᴀᴛɪɴɢ ʏᴏᴜʀ ʙᴏᴛ ❣️**")
    try:
        vj = Client(
            f"{bot_token}", API_ID, API_HASH,
            bot_token=bot_token,
            plugins={"root": "CloneTechVJ"}
        )
        await vj.start()
        bot = await vj.get_me()
        await db.add_clone_bot(bot.id, user_id, bot_token)
        await msg.edit_text(f"<b>sᴜᴄᴄᴇssғᴜʟʟʏ ᴄʟᴏɴᴇᴅ ʏᴏᴜʀ ʙᴏᴛ: @{bot.username}.\n\nʏᴏᴜ ᴄᴀɴ ᴄᴜsᴛᴏᴍɪsᴇ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ ʙʏ /settings ᴄᴏᴍᴍᴀɴᴅ ɪɴ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ</b>")
    except BaseException as e:
        await msg.edit_text(f"⚠️ <b>Bot Error:</b>\n\n<code>{e}</code>\n\n**Kindly forward this message to  to get assistance.**")

@Client.on_message(filters.command('deleteclone'))
async def delete_clone_menu(client, message):
    if await db.is_clone_exist(message.from_user.id):
        await db.delete_clone(message.from_user.id)
        await message.reply("**sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ʏᴏᴜʀ ᴄʟᴏɴᴇ ʙᴏᴛ, ʏᴏᴜ ᴄᴀɴ ᴄʀᴇᴀᴛᴇ ᴀɢᴀɪɴ ʙʏ /clone**")
    else:
        await message.reply("**ɴᴏ ᴄʟᴏɴᴇ ʙᴏᴛ ғᴏᴜɴᴅ**")

async def restart_bots():
    bots_cursor = await db.get_all_bots()
    bots = await bots_cursor.to_list(None)
    for bot in bots:
        bot_token = bot['bot_token']
        try:
            vj = Client(
                f"{bot_token}", API_ID, API_HASH,
                bot_token=bot_token,
                plugins={"root": "CloneTechVJ"},
            )
            await vj.start()
        except Exception as e:
            print(f"Error while restarting bot with token {bot_token}: {e}")
        
