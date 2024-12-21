from pyrogram import Client
import logger
import time

async def send_alive_message(client: Client):
    while True:
        if SEND_ALIVE :
            try:
                IST = pytz.timezone('Asia/Kolkata')
                current_time = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')

            # Calculate response time
                start_time = time.time()
                message = f"#alive\n\nCurrent time: {current_time}\nMy response time: calculating..."
                sent_message = await client.send_message(
                    chat_id=BOT_LOG_CHANNEL,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN
                )

                end_time = time.time()
                response_time = round((end_time - start_time) * 1000, 2)  # in milliseconds
                await asyncio.sleep(1)

            # Edit the message with the final response time
                final_message = f"#alive\n\nCurrent time: {current_time}\nMy response time: {response_time}ms\nThank you 😊"
                await client.edit_message_text(
                    chat_id=BOT_LOG_CHANNEL,
                    message_id=sent_message.id,
                    text=final_message,
                    parse_mode=ParseMode.MARKDOWN
                )

            except PeerIdInvalid:
            # Handle the PeerIdInvalid error and continue
                logging.warning("PeerIdInvalid error occurred, skipping this iteration.")
                pass  # Simply skip this iteration without interrupting the loop

            except Exception as e:
                logging.error(f"Error in send_alive_message: {e}")
                await asyncio.sleep(60)  # Retry after a delay if another exception occurs
        # Wait for 5 minutes (300 seconds)
        #logging.info("Waiting for 5 minutes before sending the next alive message...")
            await asyncio.sleep(1800)
              
