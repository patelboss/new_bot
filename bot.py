import sys, glob, importlib, logging, logging.config, pytz, asyncio, time
from pathlib import Path

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("cinemagoer").setLevel(logging.ERROR)

from pyrogram import Client, idle
from pyrogram.enums import ParseMode
from database.users_chats_db import db
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from Script import script
from datetime import date, datetime
from aiohttp import web
from plugins import web_server
from plugins.clone import restart_bots

from TechVJ.bot import TechVJBot
from TechVJ.util.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients

ppath = "plugins/*.py"
files = glob.glob(ppath)
TechVJBot.start()
loop = asyncio.get_event_loop()


async def send_alive_message(client: Client):
    while True:
        try:
            logging.info("Preparing to send alive message...")
            
            # Get the current time in IST
            IST = pytz.timezone('Asia/Kolkata')
            current_time = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
            logging.info(f"Current IST time: {current_time}")
            
            # Calculate response time
            start_time = time.time()
            message = f"#alive\n\nCurrent time: {current_time}\nMy response time: calculating..."
            sent_message = await client.send_message(
                chat_id=BOT_LOG_CHANNEL,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
            logging.info(f"Sent initial alive message to BOT_LOG_CHANNEL: {sent_message.message.id}")
            
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)  # in milliseconds
            await asyncio.sleep(1)
            logging.info(f"Calculated response time: {response_time}ms")
            
            # Edit the message with the final response time
            final_message = f"#alive\n\nCurrent time: {current_time}\nMy response time: {response_time}ms\nThank you 😊"
            await client.edit_message_text(
                chat_id=LOG_CHANNEL,
                message_id=sent_message.message.id,
                text=final_message,
                parse_mode=ParseMode.MARKDOWN
            )
            logging.info(f"Edited alive message in LOG_CHANNEL: {sent_message.id}")
        except Exception as e:
            logging.error(f"Error in send_alive_message: {e}")

        # Wait for 5 minutes (300 seconds)
        logging.info("Waiting for 5 minutes before sending the next alive message...")
        await asyncio.sleep(300)


async def start():
    print('\n')
    print('Initalizing Your Bot')
    bot_info = await TechVJBot.get_me()
    await initialize_clients()
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print("Tech VJ Imported => " + plugin_name)
    if ON_HEROKU:
        asyncio.create_task(ping_server())
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    me = await TechVJBot.get_me()
    temp.BOT = TechVJBot
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    logging.info(LOG_STR)
    logging.info(script.LOGO)
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    await TechVJBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))
    if CLONE_MODE == True:
        print("Restarting All Clone Bots.......")
        await restart_bots()
        print("Restarted All Clone Bots.")
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()

    # Start send_alive_message as a background task
    asyncio.create_task(send_alive_message(TechVJBot))

    await idle()


if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')   #     logging.info('Service Stopped Bye 👋')
