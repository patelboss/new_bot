import datetime, time, asyncio
from pyrogram import Client, filters
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages, broadcast_messages_group

async def update_status(sts, done, total, success, blocked=0, deleted=0, failed=0, is_group=False):
    entity = "Groups" if is_group else "Users"
    status_text = (
        f"Broadcast in progress:\n\n"
        f"Total {entity}: {total}\n"
        f"Completed: {done} / {total}\n"
        f"Success: {success}\n"
        f"Blocked: {blocked}\n"
        f"Deleted: {deleted}\n"
        f"Failed: {failed}"
    )
    await sts.edit(status_text)

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def pm_broadcast(bot, message):
    try:
        choice_msg = await bot.ask(
            chat_id=message.from_user.id,
            text="Do you want to forward a message or type a new one?\n\nReply with:\n"
                 "`1` to forward an existing message.\n"
                 "`2` to type a new message.",
            timeout=60
        )
        
        if choice_msg.text == "1":
            forward_msg = await bot.ask(chat_id=message.from_user.id, text="Please forward the message you want to broadcast.")
            if not forward_msg.forward_from and not forward_msg.forward_from_chat:
                await message.reply_text("You need to forward a valid message. Aborting broadcast.")
                return
        elif choice_msg.text == "2":
            text_msg = await bot.ask(chat_id=message.from_user.id, text="Now type the message you want to broadcast.")
            if not text_msg.text.strip():
                await message.reply_text("Broadcast message cannot be empty. Aborting broadcast.")
                return
        else:
            await message.reply_text("Invalid choice. Please use `/broadcast` again.")
            return

        users = await db.get_all_users()
        sts = await message.reply_text('Broadcasting your messages...')
        start_time = time.time()
        total_users = await db.total_users_count()

        done = success = blocked = deleted = failed = 0
        semaphore = asyncio.Semaphore(10)  # Limit concurrency to 10

        async def broadcast_user(user):
            nonlocal done, success, blocked, deleted, failed
            async with semaphore:
                try:
                    if choice_msg.text == "1":  # Forwarding the message
                        await bot.forward_messages(chat_id=int(user['id']), from_chat_id=forward_msg.chat.id, message_ids=forward_msg.message_id)
                        success += 1
                    else:  # Sending a typed message
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
                    print(f"Error broadcasting to user {user.get('id')}: {e}")
                    failed += 1
                done += 1
                if done % 20 == 0:
                    await update_status(sts, done, total_users, success, blocked, deleted, failed)

        await asyncio.gather(*(broadcast_user(user) for user in users))

        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        await sts.edit(
            f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\n"
            f"Total Users: {total_users}\nCompleted: {done} / {total_users}\n"
            f"Success: {success}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}"
        )
    except Exception as e:
        print(f"Error in pm_broadcast: {e}")
        await message.reply_text("An error occurred during the broadcast.")

@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS))
async def broadcast_group(bot, message):
    try:
        choice_msg = await bot.ask(
            chat_id=message.from_user.id,
            text="Do you want to forward a message or type a new one?\n\nReply with:\n"
                 "`1` to forward an existing message.\n"
                 "`2` to type a new message.",
            timeout=60
        )

        if choice_msg.text == "1":
            forward_msg = await bot.ask(chat_id=message.from_user.id, text="Please forward the message you want to broadcast.")
            if not forward_msg.forward_from and not forward_msg.forward_from_chat:
                await message.reply_text("You need to forward a valid message. Aborting broadcast.")
                return
        elif choice_msg.text == "2":
            text_msg = await bot.ask(chat_id=message.from_user.id, text="Now type the message you want to broadcast.")
            if not text_msg.text.strip():
                await message.reply_text("Broadcast message cannot be empty. Aborting broadcast.")
                return
        else:
            await message.reply_text("Invalid choice. Please use `/grp_broadcast` again.")
            return

        groups = await db.get_all_chats()
        sts = await message.reply_text('Broadcasting your messages to groups...')
        start_time = time.time()
        total_groups = await db.total_chat_count()

        done = success = failed = 0
        semaphore = asyncio.Semaphore(10)  # Limit concurrency to 10

        async def broadcast_group_chat(group):
            nonlocal done, success, failed
            async with semaphore:
                try:
                    if choice_msg.text == "1":  # Forwarding the message
                        await bot.forward_messages(chat_id=int(group['id']), from_chat_id=forward_msg.chat.id, message_ids=forward_msg.message_id)
                        success += 1
                    else:  # Sending a typed message
                        pti, sh = await broadcast_messages_group(int(group['id']), text_msg)
                        if pti:
                            success += 1
                        else:
                            failed += 1
                except Exception as e:
                    print(f"Error broadcasting to group {group.get('id')}: {e}")
                    failed += 1
                done += 1
                if done % 20 == 0:
                    await update_status(sts, done, total_groups, success, failed=failed, is_group=True)

        await asyncio.gather(*(broadcast_group_chat(group) for group in groups))

        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        await sts.edit(
            f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\n"
            f"Total Groups: {total_groups}\nCompleted: {done} / {total_groups}\n"
            f"Success: {success}\nFailed: {failed}"
        )
    except Exception as e:
        print(f"Error in broadcast_group: {e}")
        await message.reply_text("An error occurred during the group broadcast.")
