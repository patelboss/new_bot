from pyrogram import Client, filters
from info import ADMINS
from database.users_chats_db import db
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
        # Ask admin for broadcast type
        choice_msg = await bot.ask(chat_id=message.from_user.id, text="Send 1 to forward a message or 2 to type a new one.")
        if choice_msg.text.strip() == "1":
            forward_msg = await bot.ask(chat_id=message.from_user.id, text="Please forward the message you want to broadcast.")
            if not forward_msg.forward_from and not forward_msg.forward_from_chat:
                await message.reply_text("You need to forward a valid message. Aborting broadcast.")
                logging.warning("Invalid forward message for PM broadcast. Aborted.")
                return
            await start_pm_broadcast(bot, forward_msg=forward_msg)
        elif choice_msg.text.strip() == "2":
            text_msg = await bot.ask(chat_id=message.from_user.id, text="Now type the message you want to broadcast.")
            if not text_msg.text.strip():
                await message.reply_text("Broadcast message cannot be empty. Aborting broadcast.")
                logging.warning("Empty typed message for PM broadcast. Aborted.")
                return
            await start_pm_broadcast(bot, text_msg=text_msg)
        else:
            await message.reply_text("Invalid choice. Please restart the broadcast command.")
            logging.warning("Invalid choice for PM broadcast. Aborted.")
    except Exception as e:
        logging.error(f"Error in pm_broadcast: {e}")
        await message.reply_text("An error occurred during the PM broadcast.")

async def start_pm_broadcast(bot, forward_msg=None, text_msg=None):
    try:
        # Await the result of get_all_users, it returns a list of users (after awaiting it)
        users = await db.get_all_users()  # Awaiting the coroutine to get the users
        sts = await bot.send_message(chat_id=ADMINS[0], text='Broadcasting your messages to PM users...')
        start_time = time.time()
        total_users = await db.total_users_count()

        done = success = blocked = deleted = failed = 0
        semaphore = asyncio.Semaphore(10)  # Limit concurrency to 10

        # Make sure you use 'async for' only after getting the result
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

        # Use async for after getting the actual list of users
        await asyncio.gather(*(broadcast_user(user) for user in users))

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
        # Ask admin for broadcast type
        choice_msg = await bot.ask(chat_id=message.from_user.id, text="Send 1 to forward a message or 2 to type a new one.")
        if choice_msg.text.strip() == "1":
            forward_msg = await bot.ask(chat_id=message.from_user.id, text="Please forward the message you want to broadcast to groups.")
            if not forward_msg.forward_from and not forward_msg.forward_from_chat:
                await message.reply_text("You need to forward a valid message. Aborting broadcast.")
                logging.warning("Invalid forward message for group broadcast. Aborted.")
                return
            await start_group_broadcast(bot, forward_msg=forward_msg)
        elif choice_msg.text.strip() == "2":
            text_msg = await bot.ask(chat_id=message.from_user.id, text="Now type the message you want to broadcast to groups.")
            if not text_msg.text.strip():
                await message.reply_text("Broadcast message cannot be empty. Aborting broadcast.")
                logging.warning("Empty typed message for group broadcast. Aborted.")
                return
            await start_group_broadcast(bot, text_msg=text_msg)
        else:
            await message.reply_text("Invalid choice. Please restart the broadcast command.")
            logging.warning("Invalid choice for group broadcast. Aborted.")
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
