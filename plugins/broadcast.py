import logging
import time
import datetime
import asyncio
from pyrogram import Client, filters
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages, broadcast_messages_group

logging.basicConfig(level=logging.INFO)

# Function to update the status message during broadcast
async def update_status(sts, done, total, success, blocked, deleted, failed):
    await sts.edit(f"Broadcast in progress:\n\nTotal: {total}\n"
                    f"Completed: {done} / {total}\n"
                    f"Success: {success}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}")

# PM Broadcast
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def pm_broadcast(bot, message):
    try:
        b_msg = await bot.ask(chat_id=message.from_user.id, text="Now send me your broadcast message.")

        # Get all users and handle async cursor properly
        users = await db.get_all_users().to_list(length=None)  # Convert cursor to list
        sts = await message.reply_text('Broadcasting your messages...')
        start_time = time.time()
        total_users = await db.total_users_count()

        done = success = blocked = deleted = failed = 0
        semaphore = asyncio.Semaphore(10)  # Limit concurrency to 10

        # Function to broadcast to a user
        async def broadcast_user(user):
            nonlocal done, success, blocked, deleted, failed
            async with semaphore:
                try:
                    if b_msg.reply_to_message:  # Forward message
                        await bot.forward_messages(chat_id=int(user['id']), from_chat_id=b_msg.chat.id, message_ids=b_msg.message_id)
                        success += 1
                    else:  # Send a typed message
                        pti, sh = await broadcast_messages(int(user['id']), b_msg.text)
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

        # Start broadcasting to all users
        await asyncio.gather(*(broadcast_user(user) for user in users))

        # Send completion message
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
        await message.reply_text("An error occurred during the PM broadcast.")

# Group Broadcast
@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS))
async def broadcast_group(bot, message):
    try:
        b_msg = await bot.ask(chat_id=message.from_user.id, text="Now send me your broadcast message.")

        # Get all groups and handle async cursor properly
        groups = await db.get_all_chats().to_list(length=None)  # Convert cursor to list
        sts = await message.reply_text('Broadcasting your messages to groups...')
        start_time = time.time()
        total_groups = await db.total_chat_count()

        done = success = failed = 0
        semaphore = asyncio.Semaphore(5)  # Limit concurrency to 5

        # Function to broadcast to a group
        async def broadcast_group_func(group):
            nonlocal done, success, failed
            async with semaphore:
                try:
                    pti, sh = await broadcast_messages_group(int(group['id']), b_msg.text)
                    if pti:
                        success += 1
                    elif sh == "Error":
                        failed += 1
                except Exception as e:
                    logging.error(f"Error broadcasting to group {group.get('id')}: {e}")
                    failed += 1
                done += 1
                if done % 20 == 0:
                    await update_status(sts, done, total_groups, success, 0, 0, failed)

        # Start broadcasting to all groups
        await asyncio.gather(*(broadcast_group_func(group) for group in groups))

        # Send completion message
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
        await message.reply_text("An error occurred during the group broadcast.")
