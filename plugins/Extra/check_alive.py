
import time
import random
from pyrogram import Client, filters

CMD = ["/", "."]

@Client.on_message(filters.command("alive", CMD))
async def check_alive(_, message):
    await message.reply_text("**You are very lucky 🤞 I am alive ❤️ Press /start to use me**")


@Client.on_message(filters.command("ping", CMD))
async def ping(_, message):
    start_t = time.time()
    rm = await message.reply_text("...")
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rm.edit(f"Pong!\n{time_taken_s:.3f} ms")

from info import LOG_CHANNEL  # Assuming LOG_CHANNEL is defined in info.py

import asyncio
from pyrogram import Client
from pyrogram.types import ParseMode
from datetime import datetime
import pytz
from config import LOG_CHANNEL  # Assuming LOG_CHANNEL is defined in info.py

# Define the IST timezone
IST = pytz.timezone('Asia/Kolkata')

import asyncio
from pyrogram import Client
from pyrogram.types import ParseMode
from datetime import datetime
import pytz
#from config import LOG_CHANNEL  # Assuming LOG_CHANNEL is defined in info.py

# Define the IST timezone
IST = pytz.timezone('Asia/Kolkata')

# Function to send alive message every 5 minutes
async def send_alive_message(client: Client):
    while True:
        # Get the current time in IST
        current_time = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')

        # Calculate response time by recording start and end time
        start_time = time.time()
        message = f"Bot is alive! Current time (IST): {current_time}"
        await client.send_message(LOG_CHANNEL, message, parse_mode=ParseMode.MARKDOWN)
        end_time = time.time()

        # Calculate the response time
        response_time = round((end_time - start_time) * 1000, 2)  # in milliseconds
        await client.send_message(LOG_CHANNEL, f"Response Time: {response_time}ms", parse_mode=ParseMode.MARKDOWN)

        # Wait for 5 minutes (300 seconds) before sending the next message
        await asyncio.sleep(300)  # 5 minutes (asynchronous sleep)


# Assuming this is added to your already running bot
async def main(client: Client):
    # Start the periodic alive message
    await send_alive_message(client)
