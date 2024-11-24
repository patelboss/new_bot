from pyrogram import Client, filters
from info import ADMINS
from database.users_chats_db import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import time
import asyncio
import logging

# Enable logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# PM Broadcast
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def pm_broadcast(bot, message):
    logging.info("PM Broadcast initiated by admin.")
    try:
        # Show inline buttons for broadcast method
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Forward Message", callback_data="pm_broadcast_forward"),
             InlineKeyboardButton("Type New Message", callback_data="pm_broadcast_type")]
        ])
        ask_msg = await message.reply_text("Choose how you want to broadcast your message to PM users:", reply_markup=buttons)

        @Client.on_callback_query(filters.regex(r"pm_broadcast_"))
        async def handle_pm_choice(bot, query):
            await query.message.delete()  # Remove buttons after selection
            if query.data == "pm_broadcast_forward":
                forward_msg = await bot.ask(chat_id=query.from_user.id, text="Please forward the message you want to broadcast.")
                if not forward_msg.forward_from and not forward_msg.forward_from_chat:
                    await query.message.reply_text("You need to forward a valid message. Aborting broadcast.")
                    logging.warning("Invalid forward message for PM broadcast. Aborted.")
                    return
                await start_pm_broadcast(bot, forward_msg=forward_msg)
            elif query.data == "pm_broadcast_type":
                text_msg = await bot.ask(chat_id=query.from_user.id, text="Now type the message you want to broadcast.")
                if not text_msg.text.strip():
                    await query.message.reply_text("Broadcast message cannot be empty. Aborting broadcast.")
                    logging.warning("Empty typed message for PM broadcast. Aborted.")
                    return
                await start_pm_broadcast(bot, text_msg=text_msg)

    except Exception as e:
        logging.error(f"Error in pm_broadcast: {e}")
        await message.reply_text("An error occurred during the PM broadcast.")

async def start_pm_broadcast(bot, forward_msg=None, text_msg=None):
    try:
        users_cursor = db.get_all_users()  # Cursor for all users
        sts = await bot.send_message(chat_id=ADMINS[0], text='Broadcasting your messages to PM users...')
        start_time = time.time()
        total_users = await db.total_users_count()

        done = success = blocked = deleted = failed = 0
        semaphore = asyncio.Semaphore(10)  # Limit concurrency to 10

        async def broadcast_user(user):
            nonlocal done, success, blocked, deleted, failed
            async with semaphore:
                try:
                    if forward_msg:  # Forwarding the message
                        await bot.forward_messages(chat_id=int(user['id']), from_chat_id=forward_msg.chat.id, message_ids=forward_msg.message_id)
                        success += 1
                    elif text_msg:  # Sending a typed message
                        pti, sh = await broadcast_messages(int(user['id']), text_msg)
                        if pti:
                            success += 1
                        elif sh == "Blocked":
                            blocked += 1
                        elif sh == "Deleted":
                            deleted += 1
                        else:
                            failed += 1
                except Exception as e:
                    logging.error(f"Error broadcasting to user {user.get('id')}: {e}")
                    failed += 1
                done += 1
                if done % 20 == 0:
                    await update_status(sts, done, total_users, success, blocked, deleted, failed)

        await asyncio.gather(*(broadcast_user(user) async for user in users_cursor))

        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        completion_msg = (
            f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\n"
            f"Total Users: {total_users}\nCompleted: {done} / {total_users}\n"
            f"Success: {success}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}"
        )
        await sts.edit(completion_msg)
        logging.info(completion_msg)
    except Exception as e:
        logging.error(f"Error in start_pm_broadcast: {e}")
        await bot.send_message(chat_id=ADMINS[0], text="An error occurred during the PM broadcast.")

# Group Broadcast
@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS))
async def group_broadcast(bot, message):
    logging.info("Group Broadcast initiated by admin.")
    try:
        # Show inline buttons for broadcast method
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Forward Message", callback_data="grp_broadcast_forward"),
             InlineKeyboardButton("Type New Message", callback_data="grp_broadcast_type")]
        ])
        ask_msg = await message.reply_text("Choose how you want to broadcast your message to Groups:", reply_markup=buttons)

        @Client.on_callback_query(filters.regex(r"grp_broadcast_"))
        async def handle_grp_choice(bot, query):
            await query.message.delete()  # Remove buttons after selection
            if query.data == "grp_broadcast_forward":
                forward_msg = await bot.ask(chat_id=query.from_user.id, text="Please forward the message you want to broadcast to groups.")
                if not forward_msg.forward_from and not forward_msg.forward_from_chat:
                    await query.message.reply_text("You need to forward a valid message. Aborting broadcast.")
                    logging.warning("Invalid forward message for group broadcast. Aborted.")
                    return
                await start_group_broadcast(bot, forward_msg=forward_msg)
            elif query.data == "grp_broadcast_type":
                text_msg = await bot.ask(chat_id=query.from_user.id, text="Now type the message you want to broadcast to groups.")
                if not text_msg.text.strip():
                    await query.message.reply_text("Broadcast message cannot be empty. Aborting broadcast.")
                    logging.warning("Empty typed message for group broadcast. Aborted.")
                    return
                await start_group_broadcast(bot, text_msg=text_msg)

    except Exception as e:
        logging.error(f"Error in group_broadcast: {e}")
        await message.reply_text("An error occurred during the Group broadcast.")

async def start_group_broadcast(bot, forward_msg=None, text_msg=None):
    try:
        groups_cursor = db.get_all_chats()  # Cursor for all groups
        sts = await bot.send_message(chat_id=ADMINS[0], text='Broadcasting your messages to Groups...')
        start_time = time.time()
        total_groups = await db.total_chat_count()

        done = success = failed = 0
        semaphore = asyncio.Semaphore(10)  # Limit concurrency to 10

        async def broadcast_group(group):
            nonlocal done, success, failed
            async with semaphore:
                try:
                    if forward_msg:  # Forwarding the message
                        await bot.forward_messages(chat_id=int(group['id']), from_chat_id=forward_msg.chat.id, message_ids=forward_msg.message_id)
                        success += 1
                    elif text_msg:  # Sending a typed message
                        pti, sh = await broadcast_messages_group(int(group['id']), text_msg)
                        if pti:
                            success += 1
                        else:
                            failed += 1
                except Exception as e:
                    logging.error(f"Error broadcasting to group {group.get('id')}: {e}")
                    failed += 1
                done += 1
                if done % 20 == 0:
                    await update_status(sts, done, total_groups, success, failed=failed)

        await asyncio.gather(*(broadcast_group(group) async for group in groups_cursor))

        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        completion_msg = (
            f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\n"
            f"Total Groups: {total_groups}\nCompleted: {done} / {total_groups}\n"
            f"Success: {success}\nFailed: {failed}"
        )
        await sts.edit(completion_msg)
        logging.info(completion_msg)
    except Exception as e:
        logging.error(f"Error in start_group_broadcast: {e}")
        await bot.send_message(chat_id=ADMINS[0], text="An error occurred during the Group broadcast.")
