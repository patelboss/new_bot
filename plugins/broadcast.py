from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def pm_broadcast(bot, message):
    logging.info("Broadcast initiated by admin.")
    try:
        # Show inline buttons to choose message type
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Forward Message", callback_data="broadcast_forward"),
             InlineKeyboardButton("Type New Message", callback_data="broadcast_type")]
        ])
        ask_msg = await message.reply_text("Choose how you want to broadcast your message:", reply_markup=buttons)

        @Client.on_callback_query(filters.regex(r"broadcast_"))
        async def handle_broadcast_choice(bot, query: CallbackQuery):
            await query.message.delete()  # Remove the inline buttons after selection
            if query.data == "broadcast_forward":
                forward_msg = await bot.ask(chat_id=query.from_user.id, text="Please forward the message you want to broadcast.")
                if not forward_msg.forward_from and not forward_msg.forward_from_chat:
                    await query.message.reply_text("You need to forward a valid message. Aborting broadcast.")
                    logging.warning("Invalid forward message. Broadcast aborted.")
                    return
                await start_pm_broadcast(bot, forward_msg=forward_msg)
            elif query.data == "broadcast_type":
                text_msg = await bot.ask(chat_id=query.from_user.id, text="Now type the message you want to broadcast.")
                if not text_msg.text.strip():
                    await query.message.reply_text("Broadcast message cannot be empty. Aborting broadcast.")
                    logging.warning("Empty broadcast message. Broadcast aborted.")
                    return
                await start_pm_broadcast(bot, text_msg=text_msg)

    except Exception as e:
        logging.error(f"Error in pm_broadcast: {e}")
        await message.reply_text("An error occurred during the broadcast.")

async def start_pm_broadcast(bot, forward_msg=None, text_msg=None):
    try:
        users_cursor = db.get_all_users()  # Get the cursor
        sts = await bot.send_message(chat_id=ADMINS[0], text='Broadcasting your messages...')
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
                        logging.debug(f"Message forwarded to user {user['id']}")
                    elif text_msg:  # Sending a typed message
                        pti, sh = await broadcast_messages(int(user['id']), text_msg)
                        if pti:
                            success += 1
                            logging.debug(f"Message sent successfully to user {user['id']}")
                        elif sh == "Blocked":
                            blocked += 1
                            logging.warning(f"User {user['id']} has blocked the bot.")
                        elif sh == "Deleted":
                            deleted += 1
                            logging.warning(f"Chat with user {user['id']} has been deleted.")
                        else:
                            failed += 1
                            logging.error(f"Failed to send message to user {user['id']}")
                except Exception as e:
                    logging.error(f"Error broadcasting to user {user.get('id')}: {e}")
                    failed += 1
                done += 1
                if done % 20 == 0:
                    await update_status(sts, done, total_users, success, blocked, deleted, failed)

        # Use async for to iterate over the cursor
        await asyncio.gather(*(broadcast_user(user) async for user in users_cursor))

        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        completion_msg = (
            f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\n"
            f"Total Users: {total_users}\nCompleted: {done} / {total_users}\n"
            f"Success: {success}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}"
        )
        await sts.edit(completion_msg)
        logging.info("Broadcast completed successfully.")
        logging.info(completion_msg)
    except Exception as e:
        logging.error(f"Error in start_pm_broadcast: {e}")
        await bot.send_message(chat_id=ADMINS[0], text="An error occurred during the broadcast.")

# Similar approach can be applied for group broadcasts as well.
