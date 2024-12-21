import re
from os import environ
from database.envs import fetch_config # Ensure this function fetches the MongoDB config properly
#import os
from Script import script 


config_name = "env_config"
config = fetch_config(config_name)
print(config)


id_pattern = re.compile(r'^.\d+$')

# Default function for enabling/disabling based on custom text (true/false)
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot information with MongoDB and fallback
SESSION = environ.get('SESSION', 'TechVJBot')
API_ID = int(environ.get('API_ID', ''))
API_HASH = environ.get('API_HASH', '')
BOT_TOKEN = environ.get('BOT_TOKEN', "")
EDATABASE_URI = environ.get('EDATABASE_URI', "")

config_name = "env_config"
config = fetch_config(config_name)
#ALIVE_FREQUENCY
SEND_ALIVE = bool(config.get('SEND_ALIVE')) if config.get('SEND_ALIVE') else bool(environ.get('SEND_ALIVE', False))
print(f"SEND_ALIVE: {config.get('SEND_ALIVE')}")
ALIVE_FREQUENCY = int(config.get("ALIVE_FREQUENCY")) if config.get("ALIVE_FREQUENCY") else int(environ.get("ALIVE_FREQUENCY", "600"))
print(f"ALIVE_FREQUENCY: {config.get('ALIVE_FREQUENCY')}")



DLT2 = int(config.get("DLT2")) if config.get("DLT2") else int(environ.get("DLT2", "4200"))
print(f"DLT2: {config.get('DLT2')}")

# Fetch config from MongoDB or fallback to environment variable
DLTTM = int(config.get("DLTTM")) if config.get("DLTTM") else int(environ.get("DLTTM", "4200"))
print(f"DLTTM: {config.get('DLTTM')}")
#print(f"Environment variable DLTTM: {environ.get('DLTTM')}")
# Bot settings with MongoDB fallback
CACHE_TIME = config.get("CACHE_TIME") if config.get("CACHE_TIME") else environ.get("CACHE_TIME", "1800")
print(f"CACHE_TIME value: {config.get('CACHE_TIME')}")
PICS = config.get("PICS") if config.get("PICS") else (environ.get("PICS", "https://graph.org/file/ce1723991756e48c35aa1.jpg")).split()

NOR_IMG = config.get("NOR_IMG") if config.get("NOR_IMG") else environ.get("NOR_IMG", "https://graph.org/file/b69af2db776e4e85d21ec.jpg")

MELCOW_VID = environ.get("MELCOW_VID", "https://t.me/How_To_Open_Linkl")

WELCOME_VIDEO_ID = config.get("WELCOME_VIDEO_ID") if config.get("WELCOME_VIDEO_ID") else environ.get("MELCOW_VID", "BAACAgQAAxkBAAEWWw5nXJ_bgRy9MY3ZNxpLzbIaysGuswAC2hoAAuLv4VIyB40_JD42Hh4E")

SPELL_IMG = config.get("SPELL_IMG") if config.get("SPELL_IMG") else environ.get("SPELL_IMG", "https://te.legra.ph/file/15c1ad448dfe472a5cbb8.jpg")

NRF_CHANNEL = config.get("NRF_CHANNEL") if config.get("NRF_CHANNEL") else int(environ.get('NRF_CHANNEL', '-1001886419650'))

BOT_LOG_CHANNEL = config.get("BOT_LOG_CHANNEL") if config.get("BOT_LOG_CHANNEL") else int(environ.get('BOT_LOG_CHANNEL', '-1001886419650'))

# Admins, Channels & Users (Admin & Auth Users handled with MongoDB & fallback logic)

LOG_CHANNEL = config.get("LOG_CHANNEL") if config.get("LOG_CHANNEL") else int(environ.get('LOG_CHANNEL', '-1001886419650'))

# Fetch Admins from MongoDB (or environment variables if not available)
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in config.get("ADMINS", "").split()] if config.get("ADMINS") else [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '').split()]


# Channels (fetch from config or fallback to env)
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in config.get("CHANNELS", "").split()] if config.get("CHANNELS") else [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '').split()]


auth_users = [int(user) if id_pattern.search(user) else user for user in config.get('AUTH_USERS', "").split()] if config.get('AUTH_USERS') else [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else ADMINS

# Admin-related settings
REQUEST_TO_JOIN_MODE = is_enabled(config.get('REQUEST_TO_JOIN_MODE', "false"), False) if config.get('REQUEST_TO_JOIN_MODE') else False

TRY_AGAIN_BTN = is_enabled(config.get('TRY_AGAIN_BTN', "false"), False) if config.get('TRY_AGAIN_BTN') else False


# Force subscribe channel (optional)
auth_channel = config.get('AUTH_CHANNEL', '') if config.get('AUTH_CHANNEL') else environ.get('AUTH_CHANNEL', '')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None

AUTH_CHANNELS = environ.get("AUTH_CHANNELS", "").split() if config.get("AUTH_CHANNELS") else []

reqst_channel = config.get("REQST_CHANNEL_ID") if config.get("REQST_CHANNEL_ID") else environ.get('REQST_CHANNEL_ID', '')
REQST_CHANNEL = int(reqst_channel) if reqst_channel and id_pattern.search(reqst_channel) else None

support_chat_id = config.get("SUPPORT_CHAT_ID") if config.get("SUPPORT_CHAT_ID") else environ.get('SUPPORT_CHAT_ID', '')
SUPPORT_CHAT_ID = int(support_chat_id) if support_chat_id and id_pattern.search(support_chat_id) else None

INDEX_REQ_CHANNEL = int(config.get("INDEX_REQ_CHANNEL")) if config.get("INDEX_REQ_CHANNEL") else int(environ.get('INDEX_REQ_CHANNEL', '-1001886419650'))

raw_file_store_channel = (config.get("FILE_STORE_CHANNEL").split() if config.get("FILE_STORE_CHANNEL") else environ.get('FILE_STORE_CHANNEL', '').split())
FILE_STORE_CHANNEL = [int(ch) for ch in raw_file_store_channel]

raw_delete_channels = (config.get("DELETE_CHANNELS").split() if config.get("DELETE_CHANNELS")  else environ.get('DELETE_CHANNELS', '0').split())
DELETE_CHANNELS = [int(dch) if id_pattern.search(dch) else dch for dch in raw_delete_channels]


# MongoDB settings for handling databases and collections
MULTIPLE_DATABASE = bool(config.get('MULTIPLE_DATABASE', False))  # Read from config
print(f"MULTIPLE DATABASE value: {config.get('MULTIPLE_DATABASE')}")

DATABASE_URI = config.get('DATABASE_URI') if config.get('DATABASE_URI') else environ.get('DATABASE_URI', "")
print(f"DATABASE_URI: {config.get('DATABASE_URI')}")

USER_DB_URI = config.get('USER_DB_URI', "") if MULTIPLE_DATABASE else DATABASE_URI

OTHER_DB_URI = config.get('OTHER_DB_URI', "") if MULTIPLE_DATABASE else DATABASE_URI

FILE_DB_URI = config.get('FILE_DB_URI', "") if MULTIPLE_DATABASE else DATABASE_URI

SEC_FILE_DB_URI = config.get("SEC_FILE_DB_URI", "") if MULTIPLE_DATABASE else environ.get('SEC_FILE_DB_URI', "")

DATABASE_NAME = config.get("DATABASE_NAME") if config.get("DATABASE_NAME") else environ.get('DATABASE_NAME', "Telegram Bot")

COLLECTION_NAME = config.get("COLLECTION_NAME") if config.get("COLLECTION_NAME") else environ.get('COLLECTION_NAME', "Telegram Bot")


# Payment and Referral related settings (adjusted as per your need)
PREMIUM_AND_REFERAL_MODE = is_enabled(config.get("PREMIUM_AND_REFERAL_MODE", "false"), False)

REFERAL_COUNT = int(config.get("REFERAL_COUNT", "20"))

PAYMENT_QR = config.get("PAYMENT_QR") if config.get("PAYMENT_QR") else environ.get('PAYMENT_QR', 'https://envs.sh/3wu.jpg')

PAYMENT_TEXT = config.get("PAYMENT_TEXT") if config.get("PAYMENT_TEXT") else environ.get('PAYMENT_TEXT', '<b> Thank You For Donating Us \nYou can Donate any amount you want. your donation amount will be used in bots future.</b>')

REFERAL_PREMEIUM_TIME = config.get("REFERAL_PREMEIUM_TIME", "1month") 

OWNER_USERNAME = config.get("OWNER_USERNAME") if config.get("OWNER_USERNAME") else environ.get('OWNER_USERNAME', 'Pankaj_patel_p')

# Clone-related settings


# Bot and Database Configurations
CLONE_MODE = bool(config.get('CLONE_MODE')) if config.get('CLONE_MODE') else bool(environ.get('CLONE_MODE', False))

CLONE_DATABASE_URI = config.get('CLONE_DATABASE_URI') if config.get('CLONE_DATABASE_URI') else environ.get('CLONE_DATABASE_URI', '')

PUBLIC_FILE_CHANNEL = config.get('PUBLIC_FILE_CHANNEL') if config.get('PUBLIC_FILE_CHANNEL') else environ.get('PUBLIC_FILE_CHANNEL', '')

BATCH_FILE_CHANNEL = config.get('BATCH_FILE_CHANNEL') if config.get('BATCH_FILE_CHANNEL') else environ.get('BATCH_FILE_CHANNEL', '')


# Links
GRP_LNK = config.get('GRP_LNK') if config.get('GRP_LNK') else environ.get('GRP_LNK', 'https://t.me/Filmykeedha/306')

CHNL_LNK = config.get('CHNL_LNK') if config.get('CHNL_LNK') else environ.get('CHNL_LNK', 'https://t.me/filmykeedha')

Share_msg = config.get('Share_msg') if config.get('Share_msg') else environ.get('Share_msg', 'https://t.me/share/url??start=share&text=🎥%20Discover%20the%20Ultimate%20Telegram%20Media%20Bot!%0A%0ALooking%20for%20movies,%20web%20series,%20and%20much%20more?%20%F0%9F%93%9A%20With%20the%20biggest%20media%20database%20on%20Telegram,%20we%27ve%20been%20serving%20users%20since%202021%20and%20promise%20to%20stay%20completely%20free%20in%20the%20future!%0A%0A💻%20Try%20it%20now!%0A👉%20%0A%0A🔗%20Share%20this%20bot%20with%20your%20friends%20and%20let%20them%20enjoy%20unlimited%20access%20to%20premium%20content!%20[Click%20here%20to%20explore%20endless%20entertainment](https://t.me/Rashmika_mandanana_bot?start=share)')

OFR_CNL = config.get('OFR_CNL') if config.get('OFR_CNL') else environ.get('OFR_CNL', 'https://t.me/+4dWp2gDjwC43YmJl')

TUTORIAL = config.get('TUTORIAL') if config.get('TUTORIAL') else environ.get('TUTORIAL', 'https://bit.ly/3OOoNpP')

SUPPORT_CHAT = config.get('SUPPORT_CHAT') if config.get('SUPPORT_CHAT') else environ.get('SUPPORT_CHAT', 'iAmRashmibot')


# True or False Configurations
AI_SPELL_CHECK = bool(config.get('AI_SPELL_CHECK')) if config.get('AI_SPELL_CHECK') else bool(environ.get('AI_SPELL_CHECK', True))

PM_SEARCH = bool(config.get('PM_SEARCH')) if config.get('PM_SEARCH') else bool(environ.get('PM_SEARCH', False))

IS_SHORTLINK = bool(config.get('IS_SHORTLINK')) if config.get('IS_SHORTLINK') else bool(environ.get('IS_SHORTLINK', False))

MAX_BTN = is_enabled(config.get('MAX_BTN') if config.get('MAX_BTN') else environ.get('MAX_BTN', "True"), True)

IS_TUTORIAL = bool(config.get('IS_TUTORIAL')) if config.get('IS_TUTORIAL') else bool(environ.get('IS_TUTORIAL', False))

P_TTI_SHOW_OFF = is_enabled(config.get('P_TTI_SHOW_OFF') if config.get('P_TTI_SHOW_OFF') else environ.get('P_TTI_SHOW_OFF', "False"), False)

IMDB = bool(config.get('IMDB')) if config.get('IMDB') else bool(environ.get('IMDB', "False"))

AUTO_FFILTER = bool(config.get('AUTO_FFILTER')) if config.get('AUTO_FFILTER') else bool(environ.get('AUTO_FFILTER', True))

AUTO_DELETE = bool(config.get('AUTO_DELETE')) if config.get('AUTO_DELETE') else bool(environ.get('AUTO_DELETE', "False"))

SINGLE_BUTTON = bool(config.get('SINGLE_BUTTON')) if config.get('SINGLE_BUTTON') else bool(environ.get('SINGLE_BUTTON', True))

LONG_IMDB_DESCRIPTION = bool(config.get('LONG_IMDB_DESCRIPTION')) if config.get('LONG_IMDB_DESCRIPTION') else bool(environ.get('LONG_IMDB_DESCRIPTION', False))

SPELL_CHECK_REPLY = bool(config.get('SPELL_CHECK_REPLY')) if config.get('SPELL_CHECK_REPLY') else bool(environ.get("SPELL_CHECK_REPLY", "True"))

MELCOW_NEW_USERS = is_enabled(config.get('MELCOW_NEW_USERS') if config.get('MELCOW_NEW_USERS') else environ.get('MELCOW_NEW_USERS', "True"), True)

PROTECT_CONTENT = bool(config.get('PROTECT_CONTENT')) if config.get('PROTECT_CONTENT') else bool(environ.get('PROTECT_CONTENT', "False"))

PUBLIC_FILE_STORE = bool(config.get('PUBLIC_FILE_STORE')) if config.get('PUBLIC_FILE_STORE') else bool(environ.get('PUBLIC_FILE_STORE', "True"))

NO_RESULTS_MSG = bool(config.get('NO_RESULTS_MSG')) if config.get('NO_RESULTS_MSG') else bool(environ.get("NO_RESULTS_MSG", True))

USE_CAPTION_FILTER = bool(config.get('USE_CAPTION_FILTER')) if config.get('USE_CAPTION_FILTER') else bool(environ.get('USE_CAPTION_FILTER', True))


# Token Verification Info
VERIFY = bool(config.get('VERIFY')) if config.get('VERIFY') else bool(environ.get('VERIFY', False))

VERIFY_SECOND_SHORTNER = bool(config.get('VERIFY_SECOND_SHORTNER')) if config.get('VERIFY_SECOND_SHORTNER') else bool(environ.get('VERIFY_SECOND_SHORTNER', False))

VERIFY_SHORTLINK_URL = config.get('VERIFY_SHORTLINK_URL') if config.get('VERIFY_SHORTLINK_URL') else environ.get('VERIFY_SHORTLINK_URL', '')

VERIFY_SHORTLINK_API = config.get('VERIFY_SHORTLINK_API') if config.get('VERIFY_SHORTLINK_API') else environ.get('VERIFY_SHORTLINK_API', '')

VERIFY_SND_SHORTLINK_URL = config.get('VERIFY_SND_SHORTLINK_URL') if config.get('VERIFY_SND_SHORTLINK_URL') else environ.get('VERIFY_SND_SHORTLINK_URL', '')

VERIFY_SND_SHORTLINK_API = config.get('VERIFY_SND_SHORTLINK_API') if config.get('VERIFY_SND_SHORTLINK_API') else environ.get('VERIFY_SND_SHORTLINK_API', '')

VERIFY_TUTORIAL = config.get('VERIFY_TUTORIAL') if config.get('VERIFY_TUTORIAL') else environ.get('VERIFY_TUTORIAL', 'https://t.me/How_To_Open_Linkl')


# Shortlink Info
SHORTLINK_MODE = bool(config.get('SHORTLINK_MODE')) if config.get('SHORTLINK_MODE') else bool(environ.get('SHORTLINK_MODE', False))

SHORTLINK_URL = config.get('SHORTLINK_URL') if config.get('SHORTLINK_URL') else environ.get('SHORTLINK_URL', '')

SHORTLINK_API = config.get('SHORTLINK_API') if config.get('SHORTLINK_API') else environ.get('SHORTLINK_API', '')


# Other Configurations
MAX_B_TN = int(config.get("MAX_B_TN")) if config.get("MAX_B_TN") else int(environ.get("MAX_B_TN", "10"))

PORT = int(config.get("PORT")) if config.get("PORT") else int(environ.get("PORT", "8080"))

MSG_ALRT = config.get('MSG_ALRT') if config.get('MSG_ALRT') else environ.get('MSG_ALRT', 'Hello My Dear Friends ❤️')

CUSTOM_FILE_CAPTION = config.get("CUSTOM_FILE_CAPTION") if config.get("CUSTOM_FILE_CAPTION") else environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")

BATCH_FILE_CAPTION = config.get("BATCH_FILE_CAPTION") if config.get("BATCH_FILE_CAPTION") else environ.get("BATCH_FILE_CAPTION", f"{script.CAPTION}")

IMDB_TEMPLATE = config.get("IMDB_TEMPLATE") if config.get("IMDB_TEMPLATE") else environ.get("IMDB_TEMPLATE", f"{script.IMDB_TEMPLATE_TXT}")

MAX_LIST_ELM = config.get("MAX_LIST_ELM") if config.get("MAX_LIST_ELM") else environ.get("MAX_LIST_ELM", None)


# Choose Option Settings 
LANGUAGES = ["malayalam", "mal", "tamil", "tam" ,"english", "eng", "hindi", "hin", "telugu", "tel", "kannada", "kan"]

SEASONS = ["season 1", "season 2", "season 3", "season 4", "season 5", "season 6", "season 7", "season 8", "season 9", "season 10"]

EPISODES = ["E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10", "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E19", "E20", "E21", "E22", "E23", "E24", "E25", "E26", "E27", "E28", "E29", "E30", "E31", "E32", "E33", "E34", "E35", "E36", "E37", "E38", "E39", "E40"]

QUALITIES = ["360p", "480p", "720p", "1080p", "1440p", "2160p"]

YEARS = ["1900", "1991", "1992", "1993", "1994", "1995", "1996", "1997", "1998", "1999", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]


                  

# Online Stream and Download
STREAM_MODE = bool(config.get('STREAM_MODE', False)) # Set True or False

# If Stream Mode Is True Then Fill All Required Variable, If False Then Don't Fill.
MULTI_CLIENT = bool(config.get('MULTI_CLIENT', False))

SLEEP_THRESHOLD = int(config.get('SLEEP_THRESHOLD', '60'))

PING_INTERVAL = int(config.get("PING_INTERVAL", "1200"))  # 20 minutes
if 'DYNO' in environ:
    ON_HEROKU = True
else:
    ON_HEROKU = False
URL = config.get("URL", "https://testofvjfilter-1fa60b1b8498.herokuapp.com/")


# Rename Info : If True Then Bot Rename File Else Not
RENAME_MODE = bool(config.get('RENAME_MODE', False)) # Set True or False


# Auto Approve Info : If True Then Bot Approve New Upcoming Join Request Else Not
AUTO_APPROVE_MODE = bool(config.get('AUTO_APPROVE_MODE', False)) # Set True or False


LOG_STR = "Current Cusomized Configurations are:-\n"
LOG_STR += ("IMDB Results are enabled, Bot will be showing imdb details for you queries.\n" if IMDB else "IMBD Results are disabled.\n")
LOG_STR += ("P_TTI_SHOW_OFF found , Users will be redirected to send /start to Bot PM instead of sending file file directly\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF is disabled files will be send in PM, instead of sending start.\n")
LOG_STR += ("SINGLE_BUTTON is Found, filename and files size will be shown in a single button instead of two separate buttons\n" if SINGLE_BUTTON else "SINGLE_BUTTON is disabled , filename and file_sixe will be shown as different buttons\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}, your files will be send along with this customized caption.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION Found, Default captions of file will be used.\n")
LOG_STR += ("Long IMDB storyline enabled." if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION is disabled , Plot will be shorter.\n")
LOG_STR += ("Spell Check Mode Is Enabled, bot will be suggesting related movies if movie not found\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY Mode disabled\n")
LOG_STR += (f"MAX_LIST_ELM Found, long list will be shortened to first {MAX_LIST_ELM} elements\n" if MAX_LIST_ELM else "Full List of casts and crew will be shown in imdb template, restrict them by adding a value to MAX_LIST_ELM\n")
LOG_STR += f"Your current IMDB template is {IMDB_TEMPLATE}"

