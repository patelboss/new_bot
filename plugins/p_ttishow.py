
import os, string, logging, random, asyncio, time, datetime, re, sys, json, base64
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import *
from database.ia_filterdb import col, sec_col, get_file_details, unpack_new_file_id, get_bad_files, db as vjdb, sec_db
from database.users_chats_db import db, delete_all_referal_users, get_referal_users_count, get_referal_all_users, referal_add_user
from database.join_reqs import JoinReqs
from info import *
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from utils import get_settings, pub_is_subscribed, get_size, is_subscribed, save_group_settings, temp, verify_user, check_token, check_verification, get_token, get_shortlink, get_tutorial, get_seconds
from database.connections_mdb import active_connection, mydb
import logging

# Configure the logging system (this happens once)
logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    try:
        logger.info(f"Processing new group message in chat {message.chat.id}")
        
        # Check for new members
        r_j_check = [u.id for u in message.new_chat_members]
        logger.info(f"New members added: {[u.id for u in message.new_chat_members]} in chat {message.chat.id}")
        
        if temp.ME in r_j_check:
            # Bot added to the group
            logger.info(f"Bot added to group {message.chat.id}")
            
            # Check if the group is already in the database
            if not await db.get_chat(message.chat.id):
                logger.info(f"Group {message.chat.id} is not in database. Fetching member count.")
                total = await bot.get_chat_members_count(message.chat.id)
                r_j = message.from_user.mention if message.from_user else "Anonymous"
                logger.info(f"Sending log to admin channel with group details: {message.chat.title}, {message.chat.id}, {total}, {r_j}")
                await bot.send_message(
                    LOG_CHANNEL,
                    script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, r_j)
                )
                logger.info(f"Adding group {message.chat.id} to the database.")
                await db.add_chat(message.chat.id, message.chat.title)
            else:
                logger.info(f"Group {message.chat.id} already exists in the database.")
            
            # Check if the chat is in banned list
            if message.chat.id in temp.BANNED_CHATS:
                logger.info(f"Group {message.chat.id} is in banned chats list.")
                
                # Handle banned chats
                buttons = [[
                    InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
                ]]
                reply_markup = InlineKeyboardMarkup(buttons)
                k = await message.reply(
                    text='<b>CHAT NOT ALLOWED 🐞\n\nMy admins have restricted me from working here! '
                         'If you want to know more about it, contact support.</b>',
                    reply_markup=reply_markup,
                )
                try:
                    logger.info(f"Attempting to pin the message in banned group {message.chat.id}")
                    await k.pin()
                except Exception as e:
                    logger.error(f"Error pinning message in banned group {message.chat.id}: {e}")
                logger.info(f"Bot is leaving banned group {message.chat.id}")
                await bot.leave_chat(message.chat.id)
                return
            
            # Send welcome message with buttons
            logger.info(f"Sending welcome message to group {message.chat.id}")
            buttons = [[
                InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
                InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
            ], [
                InlineKeyboardButton("Bᴏᴛ Oᴡɴᴇʀ", url="t.me/Pankaj_jii")
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await message.reply_text(
                text=f"<b>Thank you for adding me to {message.chat.title} ❣️\n\nIf you have any questions or doubts about using me, contact support.</b>",
                reply_markup=reply_markup
            )
        else:
            # Bot not added, handling new members
            logger.info(f"Processing new members in group {message.chat.id}.")
            
            settings = await get_settings(message.chat.id)
            logger.info(f"Settings for chat {message.chat.id}: {settings}")
            
            if settings["welcome"]:
                logger.info(f"Welcome message is enabled for group {message.chat.id}.")
                for u in message.new_chat_members:
                    # Check if there's an existing welcome message to delete
                    if temp.MELCOW.get('welcome') is not None:
                        try:
                            logger.info(f"Deleting previous welcome message for user {u.id} in group {message.chat.id}.")
                            await temp.MELCOW['welcome'].delete()
                        except Exception as e:
                            logger.error(f"Error deleting previous welcome message in group {message.chat.id}: {e}")
                    
                    logger.info(f"Sending welcome video to user {u.id} in group {message.chat.id}.")
                    temp.MELCOW['welcome'] = await message.reply_video(
                        video=WELCOME_VIDEO_ID,  # Correct file ID here
                        caption=(script.MELCOW_ENG.format(u.mention, message.chat.title)),
                        reply_markup=InlineKeyboardMarkup(
                            [[
                                InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
                                InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                            ], [
                                InlineKeyboardButton("Bᴏᴛ Oᴡɴᴇʀ", url="t.me/Pankaj_jii")
                            ]]
                        ),
                        parse_mode=enums.ParseMode.HTML
                    )
            
            if settings["auto_delete"]:
                logger.info(f"Auto delete is enabled for group {message.chat.id}. Waiting 10 minutes before deletion.")
                await asyncio.sleep(600)
                if temp.MELCOW.get('welcome'):
                    logger.info(f"Deleting welcome message after 10 minutes in group {message.chat.id}.")
                    await temp.MELCOW['welcome'].delete()

    except Exception as e:
        logger.error(f"Error processing group {message.chat.id}: {e}")
@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        buttons = [[
            InlineKeyboardButton('Support Group',url=GRP_LNK),
            InlineKeyboardButton("Bᴏᴛ Oᴡɴᴇʀ", url="t.me/Pankaj_jii")
        ],[
            InlineKeyboardButton('Use Me Here', url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat,
            text='<b>Hello Friends, \nMy admin has told me to leave from group, so i go! If you wanna add me again contact my Support Group or My Owner</b>',
            reply_markup=reply_markup,
        )

        await bot.leave_chat(chat)
        await message.reply(f"left the chat `{chat}`")
    except Exception as e:
        await message.reply(f'Error - {e}')

@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    cha_t = await db.get_chat(int(chat_))
    if not cha_t:
        return await message.reply("Chat Not Found In DB")
    if cha_t['is_disabled']:
        return await message.reply(f"This chat is already disabled:\nReason-<code> {cha_t['reason']} </code>")
    await db.disable_chat(int(chat_), reason)
    temp.BANNED_CHATS.append(int(chat_))
    await message.reply('Chat Successfully Disabled')
    try:
        buttons = [[
            InlineKeyboardButton('Support', url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_, 
            text=f'<b>Hello Friends, \nMy admin has told me to leave from group so i go! If you wanna add me again contact my support group.</b> \nReason : <code>{reason}</code>',
            reply_markup=reply_markup)
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply(f"Error - {e}")

@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    sts = await db.get_chat(int(chat))
    if not sts:
        return await message.reply("Chat Not Found In DB !")
    if not sts.get('is_disabled'):
        return await message.reply('This chat is not yet disabled.')
    await db.re_enable_chat(int(chat_))
    temp.BANNED_CHATS.remove(int(chat_))
    await message.reply("Chat Successfully re-enabled")

@Client.on_message(filters.command('stats') & filters.incoming)
async def get_ststs(bot, message):
    rju = await message.reply('Fetching stats..')
    try:
        total_users = await db.total_users_count()
        totl_chats = await db.total_chat_count()
        filesp = col.count_documents({})
        totalsec = sec_col.count_documents({})
        stats = vjdb.command('dbStats')
        used_dbSize = (stats['dataSize']/(1024*1024))+(stats['indexSize']/(1024*1024))
        free_dbSize = 512-used_dbSize
        stats2 = sec_db.command('dbStats')
        used_dbSize2 = (stats2['dataSize']/(1024*1024))+(stats2['indexSize']/(1024*1024))
        free_dbSize2 = 512-used_dbSize2
        stats3 = mydb.command('dbStats')
        used_dbSize3 = (stats3['dataSize']/(1024*1024))+(stats3['indexSize']/(1024*1024))
        free_dbSize3 = 512-used_dbSize3
        await rju.edit(script.STATUS_TXT.format((int(filesp)+int(totalsec)), total_users, totl_chats, filesp, round(used_dbSize, 2), round(free_dbSize, 2), totalsec, round(used_dbSize2, 2), round(free_dbSize2, 2), round(used_dbSize3, 2), round(free_dbSize3, 2)))
    except Exception as e:
        await rju.edit(f"Error - {e}")

@Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def gen_invite(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        return await message.reply('Give Me A Valid Chat ID')
    try:
        link = await bot.create_chat_invite_link(chat)
    except ChatAdminRequired:
        return await message.reply("Invite Link Generation Failed, Iam Not Having Sufficient Rights")
    except Exception as e:
        return await message.reply(f'Error {e}')
    await message.reply(f'Here is your Invite Link {link.invite_link}')

@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure ia have met him before.")
    except IndexError:
        return await message.reply("This might be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if jar['is_banned']:
            return await message.reply(f"{k.mention} is already banned\nReason: {jar['ban_reason']}")
        await db.ban_user(k.id, reason)
        temp.BANNED_USERS.append(k.id)
        await message.reply(f"Successfully banned {k.mention}")
    
@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure ia have met him before.")
    except IndexError:
        return await message.reply("Thismight be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if not jar['is_banned']:
            return await message.reply(f"{k.mention} is not yet banned.")
        await db.remove_ban(k.id)
        temp.BANNED_USERS.remove(k.id)
        await message.reply(f"Successfully unbanned {k.mention}")
    
@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    raju = await message.reply('Getting List Of Users')
    users = await db.get_all_users()
    out = "Users Saved In DB Are:\n\n"
    async for user in users:
        # Include user id in the output
        out += f"User ID: `{user['id']}`\n"
        out += f"Name: <a href=tg://user?id={user['id']}>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            out += ' (Banned User)'
        out += '\n'

    # Save the output to a .txt file
    with open('users.txt', 'w+') as outfile:
        outfile.write(out)

    # Send the .txt file to the user
    await message.reply_document('users.txt', caption="List Of Users")
@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message):
    raju = await message.reply('Getting List Of Chats')
    chats = await db.get_all_chats()
    out = "Chats Saved In DB Are:\n\n"
    async for chat in chats:
        # Include chat id in the output
        out += f"Chat ID: `{chat['id']}`\n"
        out += f"**Title:** `{chat['title']}`\n"
        if chat['chat_status']['is_disabled']:
            out += ' (Disabled Chat)'
        out += '\n'

    # Save the output to a .txt file
    with open('chats.txt', 'w+') as outfile:
        outfile.write(out)

    # Send the .txt file to the user
    await message.reply_document('chats.txt', caption="List Of Chats")
    
@Client.on_message(filters.command("getfileid") & (filters.reply))
async def get_file_id(bot, message):
    # Check if the message is a reply with media
    if message.reply_to_message:
        media = message.reply_to_message.video or \
                message.reply_to_message.photo or \
                message.reply_to_message.document or \
                message.reply_to_message.audio or \
                message.reply_to_message.voice
        
        if media:
            file_id = media.file_id
            file_type = type(media).__name__.capitalize()
            await message.reply(
                f"**File ID:** `{file_id}`\n"
                f"**File Type:** {file_type}\n"
                f"**File Size:** {media.file_size} bytes",
                quote=True
            )
        else:
            await message.reply("Please reply to a media file (video, photo, document, etc.) to get its file ID.", quote=True)
    
    # Handle direct media messages (e.g., channels without replies)
    elif message.video or message.photo or message.document or message.audio or message.voice:
        media = message.video or message.photo or message.document or message.audio or message.voice
        file_id = media.file_id
        file_type = type(media).__name__.capitalize()
        await message.reply(
            f"**File ID:** `{file_id}`\n"
            f"**File Type:** {file_type}\n"
            f"**File Size:** {media.file_size} bytes",
            quote=True
        )
    else:
        await message.reply("Please reply to a media file or send a media message directly to get its file ID.", quote=True)
