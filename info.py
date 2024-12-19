import re
from os import environ
from database.envs import fetch_config  # Ensure this function fetches the MongoDB config properly
import os

config = fetch_config("env_config")

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
DATABASE_URI = environ.get('DATABASE_URI', "")
# Fetch config from MongoDB or fallback to environment variable
DLTTM = config.get("dlttm") if config.get("dlttm") else environ.get("DLTTM", "4200")

# Bot settings with MongoDB fallback
CACHE_TIME = config.get("cache_time") if config.get("cache_time") else environ.get("CACHE_TIME", "1800")
PICS = config.get("pics") if config.get("pics") else (environ.get("PICS", "https://graph.org/file/ce1723991756e48c35aa1.jpg")).split()
NOR_IMG = config.get("nor_img") if config.get("nor_img") else environ.get("NOR_IMG", "https://graph.org/file/b69af2db776e4e85d21ec.jpg")
MELCOW_VID = environ.get("MELCOW_VID", "https://t.me/How_To_Open_Linkl")
WELCOME_VIDEO_ID = config.get("welcome_video_id") if config.get("welcome_video_id") else environ.get("MELCOW_VID", "BAACAgQAAxkBAAEWWw5nXJ_bgRy9MY3ZNxpLzbIaysGuswAC2hoAAuLv4VIyB40_JD42Hh4E")
SPELL_IMG = config.get("spell_img") if config.get("spell_img") else environ.get("SPELL_IMG", "https://te.legra.ph/file/15c1ad448dfe472a5cbb8.jpg")
NRF_CHANNEL = config.get("nrf_channel") if config.get("nrf_channel") else int(environ.get('NRF_CHANNEL', '-1001886419650'))
BOT_LOG_CHANNEL = config.get("bot_log_channel") if config.get("bot_log_channel") else int(environ.get('BOT_LOG_CHANNEL', '-1001886419650'))

# Admins, Channels & Users (Admin & Auth Users handled with MongoDB & fallback logic)
LOG_CHANNEL = config.get("log_channel") if config.get("log_channel") else int(environ.get('LOG_CHANNEL', '-1001886419650'))

# Fetch Admins from MongoDB (or environment variables if not available)
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in config.get("admins", "").split()] if config.get("admins") else [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '').split()]

# Channels (fetch from config or fallback to env)
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in config.get("channels", "").split()] if config.get("channels") else [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '').split()]

auth_users = [int(user) if id_pattern.search(user) else user for user in config.get('auth_users', "").split()] if config.get('auth_users') else [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else ADMINS

# Admin-related settings
REQUEST_TO_JOIN_MODE = is_enabled(config.get('request_to_join_mode', "false"), False) if config.get('request_to_join_mode') else False
TRY_AGAIN_BTN = is_enabled(config.get('try_again_btn', "false"), False) if config.get('try_again_btn') else False

# Force subscribe channel (optional)
auth_channel = config.get('auth_channel', '') if config.get('auth_channel') else environ.get('AUTH_CHANNEL', '')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
AUTH_CHANNELS = environ.get("AUTH_CHANNELS", "").split() if config.get("auth_channels") else []

# MongoDB settings for handling databases and collections
MULTIPLE_DATABASE = bool(config.get('multiple_database', False))

DATABASE_URI = environ.get('DATABASE_URI', "") if MULTIPLE_DATABASE else config.get('database_uri', "")
USER_DB_URI = DATABASE_URI if MULTIPLE_DATABASE is False else environ.get('USER_DB_URI', "")
OTHER_DB_URI = environ.get('OTHER_DB_URI', "") if MULTIPLE_DATABASE else DATABASE_URI

# Payment and Referral related settings (adjusted as per your need)
PREMIUM_AND_REFERAL_MODE = is_enabled(config.get("premium_and_referal_mode", "false"), False)
REFERAL_COUNT = int(config.get("referal_count", "20"))
REFERAL_PREMEIUM_TIME = config.get("referal_premium_time", "1month")

OWNER_USERNAME = environ.get('OWNER_USERNAME', 'Pankaj_patel_p')

# Clone-related settings


# Bot and Database Configurations
CLONE_MODE = bool(config.get('clone_mode')) if config.get('clone_mode') else bool(environ.get('CLONE_MODE', False))
CLONE_DATABASE_URI = config.get('clone_database_uri') if config.get('clone_database_uri') else environ.get('CLONE_DATABASE_URI', '')
PUBLIC_FILE_CHANNEL = config.get('public_file_channel') if config.get('public_file_channel') else environ.get('PUBLIC_FILE_CHANNEL', '')
BATCH_FILE_CHANNEL = config.get('batch_file_channel') if config.get('batch_file_channel') else environ.get('BATCH_FILE_CHANNEL', '')

# Links
GRP_LNK = config.get('grp_lnk') if config.get('grp_lnk') else environ.get('GRP_LNK', 'https://t.me/Filmykeedha/306')
CHNL_LNK = config.get('chnl_lnk') if config.get('chnl_lnk') else environ.get('CHNL_LNK', 'https://t.me/filmykeedha')
Share_msg = config.get('share_msg') if config.get('share_msg') else environ.get('Share_msg', 'https://t.me/share/url??start=share&text=🎥%20Discover%20the%20Ultimate%20Telegram%20Media%20Bot!%0A%0ALooking%20for%20movies,%20web%20series,%20and%20much%20more?%20%F0%9F%93%9A%20With%20the%20biggest%20media%20database%20on%20Telegram,%20we%27ve%20been%20serving%20users%20since%202021%20and%20promise%20to%20stay%20completely%20free%20in%20the%20future!%0A%0A💻%20Try%20it%20now!%0A👉%20%0A%0A🔗%20Share%20this%20bot%20with%20your%20friends%20and%20let%20them%20enjoy%20unlimited%20access%20to%20premium%20content!%20[Click%20here%20to%20explore%20endless%20entertainment](https://t.me/Rashmika_mandanana_bot?start=share)')
OFR_CNL = config.get('ofr_cnl') if config.get('ofr_cnl') else environ.get('OFR_CNL', 'https://t.me/+4dWp2gDjwC43YmJl')
TUTORIAL = config.get('tutorial') if config.get('tutorial') else environ.get('TUTORIAL', 'https://bit.ly/3OOoNpP')
SUPPORT_CHAT = config.get('support_chat') if config.get('support_chat') else environ.get('SUPPORT_CHAT', 'iAmRashmibot')

# True or False Configurations
AI_SPELL_CHECK = bool(config.get('ai_spell_check')) if config.get('ai_spell_check') else bool(environ.get('AI_SPELL_CHECK', True))
PM_SEARCH = bool(config.get('pm_search')) if config.get('pm_search') else bool(environ.get('PM_SEARCH', False))
IS_SHORTLINK = bool(config.get('is_shortlink')) if config.get('is_shortlink') else bool(environ.get('IS_SHORTLINK', False))
MAX_BTN = is_enabled(config.get('max_btn') if config.get('max_btn') else environ.get('MAX_BTN', "True"), True)
IS_TUTORIAL = bool(config.get('is_tutorial')) if config.get('is_tutorial') else bool(environ.get('IS_TUTORIAL', False))
P_TTI_SHOW_OFF = is_enabled(config.get('p_tti_show_off') if config.get('p_tti_show_off') else environ.get('P_TTI_SHOW_OFF', "False"), False)
IMDB = bool(config.get('imdb')) if config.get('imdb') else bool(environ.get('IMDB', "False"))
AUTO_FFILTER = bool(config.get('auto_ffilter')) if config.get('auto_ffilter') else bool(environ.get('AUTO_FFILTER', True))
AUTO_DELETE = bool(config.get('auto_delete')) if config.get('auto_delete') else bool(environ.get('AUTO_DELETE', "False"))
SINGLE_BUTTON = bool(config.get('single_button')) if config.get('single_button') else bool(environ.get('SINGLE_BUTTON', True))
LONG_IMDB_DESCRIPTION = bool(config.get('long_imdb_description')) if config.get('long_imdb_description') else bool(environ.get('LONG_IMDB_DESCRIPTION', False))
SPELL_CHECK_REPLY = bool(config.get('spell_check_reply')) if config.get('spell_check_reply') else bool(environ.get("SPELL_CHECK_REPLY", "True"))
MELCOWE_NEW_USER = is_enabled(config.get('melcow_new_users') if config.get('melcow_new_users') else environ.get('MELCOW_NEW_USERS', "True"), True)
PROTECT_CONTENT = bool(config.get('protect_content')) if config.get('protect_content') else bool(environ.get('PROTECT_CONTENT', "False"))
PUBLIC_FILE_STORE = bool(config.get('public_file_store')) if config.get('public_file_store') else bool(environ.get('PUBLIC_FILE_STORE', "True"))
NO_RESULTS_MSG = bool(config.get('no_results_msg')) if config.get('no_results_msg') else bool(environ.get("NO_RESULTS_MSG", True))
USE_CAPTION_FILTER = bool(config.get('use_caption_filter')) if config.get('use_caption_filter') else bool(environ.get('USE_CAPTION_FILTER', True))

# Token Verification Info
VERIFY = bool(config.get('verify')) if config.get('verify') else bool(environ.get('VERIFY', False))
VERIFY_SECOND_SHORTNER = bool(config.get('verify_second_shortner')) if config.get('verify_second_shortner') else bool(environ.get('VERIFY_SECOND_SHORTNER', False))
VERIFY_SHORTLINK_URL = config.get('verify_shortlink_url') if config.get('verify_shortlink_url') else environ.get('VERIFY_SHORTLINK_URL', '')
VERIFY_SHORTLINK_API = config.get('verify_shortlink_api') if config.get('verify_shortlink_api') else environ.get('VERIFY_SHORTLINK_API', '')
VERIFY_SND_SHORTLINK_URL = config.get('verify_snd_shortlink_url') if config.get('verify_snd_shortlink_url') else environ.get('VERIFY_SND_SHORTLINK_URL', '')
VERIFY_SND_SHORTLINK_API = config.get('verify_snd_shortlink_api') if config.get('verify_snd_shortlink_api') else environ.get('VERIFY_SND_SHORTLINK_API', '')
VERIFY_TUTORIAL = config.get('verify_tutorial') if config.get('verify_tutorial') else environ.get('VERIFY_TUTORIAL', 'https://t.me/How_To_Open_Linkl')

# Shortlink Info
SHORTLINK_MODE = bool(config.get('shortlink_mode')) if config.get('shortlink_mode') else bool(environ.get('SHORTLINK_MODE', False))
SHORTLINK_URL = config.get('shortlink_url') if config.get('shortlink_url') else environ.get('SHORTLINK_URL', '')
SHORTLINK_API = config.get('shortlink_api') if config.get('shortlink_api') else environ.get('SHORTLINK_API', '')

# Other Configurations
MAX_B_TN = int(config.get("max_b_tn")) if config.get("max_b_tn") else int(environ.get("MAX_B_TN", "10"))
PORT = int(config.get("port")) if config.get("port") else int(environ.get("PORT", "8080"))
MSG_ALRT = config.get('msg_alrt') if config.get('msg_alrt') else environ.get('MSG_ALRT', 'Hello My Dear Friends ❤️')
CUSTOM_FILE_CAPTION = config.get("custom_file_caption") if config.get("custom_file_caption") else environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")
BATCH_FILE_CAPTION = config.get("batch_file_caption") if config.get("batch_file_caption") else environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
IMDB_TEMPLATE = config.get("imdb_template") if config.get("imdb_template") else environ.get("IMDB_TEMPLATE", f"{script.IMDB_TEMPLATE_TXT}")
MAX_LIST_ELM = config.get("max_list_elm") if config.get("max_list_elm") else environ.get("MAX_LIST_ELM", None)

# Choose Option Settings 
LANGUAGES = ["malayalam", "mal", "tamil", "tam" ,"english", "eng", "hindi", "hin", "telugu", "tel", "kannada", "kan"]
SEASONS = ["season 1", "season 2", "season 3", "season 4", "season 5", "season 6", "season 7", "season 8", "season 9", "season 10"]
EPISODES = ["E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10", "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E19", "E20", "E21", "E22", "E23", "E24", "E25", "E26", "E27", "E28", "E29", "E30", "E31", "E32", "E33", "E34", "E35", "E36", "E37", "E38", "E39", "E40"]
QUALITIES = ["360p", "480p", "720p", "1080p", "1440p", "2160p"]
YEARS = ["1900", "1991", "1992", "1993", "1994", "1995", "1996", "1997", "1998", "1999", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]


                  

# Online Stream and Download
STREAM_MODE = bool(environ.get('STREAM_MODE', False)) # Set True or False

# If Stream Mode Is True Then Fill All Required Variable, If False Then Don't Fill.
MULTI_CLIENT = False
SLEEP_THRESHOLD = int(environ.get('SLEEP_THRESHOLD', '60'))
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))  # 20 minutes
if 'DYNO' in environ:
    ON_HEROKU = True
else:
    ON_HEROKU = False
URL = environ.get("URL", "https://testofvjfilter-1fa60b1b8498.herokuapp.com/")


# Rename Info : If True Then Bot Rename File Else Not
RENAME_MODE = bool(environ.get('RENAME_MODE', False)) # Set True or False

# Auto Approve Info : If True Then Bot Approve New Upcoming Join Request Else Not
AUTO_APPROVE_MODE = bool(environ.get('AUTO_APPROVE_MODE', False)) # Set True or False

LOG_STR = "Current Cusomized Configurations are:-\n"
LOG_STR += ("IMDB Results are enabled, Bot will be showing imdb details for you queries.\n" if IMDB else "IMBD Results are disabled.\n")
LOG_STR += ("P_TTI_SHOW_OFF found , Users will be redirected to send /start to Bot PM instead of sending file file directly\n" if P_TTI_SHOW_OFF else "P_TTI_SHOW_OFF is disabled files will be send in PM, instead of sending start.\n")
LOG_STR += ("SINGLE_BUTTON is Found, filename and files size will be shown in a single button instead of two separate buttons\n" if SINGLE_BUTTON else "SINGLE_BUTTON is disabled , filename and file_sixe will be shown as different buttons\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION enabled with value {CUSTOM_FILE_CAPTION}, your files will be send along with this customized caption.\n" if CUSTOM_FILE_CAPTION else "No CUSTOM_FILE_CAPTION Found, Default captions of file will be used.\n")
LOG_STR += ("Long IMDB storyline enabled." if LONG_IMDB_DESCRIPTION else "LONG_IMDB_DESCRIPTION is disabled , Plot will be shorter.\n")
LOG_STR += ("Spell Check Mode Is Enabled, bot will be suggesting related movies if movie not found\n" if SPELL_CHECK_REPLY else "SPELL_CHECK_REPLY Mode disabled\n")
LOG_STR += (f"MAX_LIST_ELM Found, long list will be shortened to first {MAX_LIST_ELM} elements\n" if MAX_LIST_ELM else "Full List of casts and crew will be shown in imdb template, restrict them by adding a value to MAX_LIST_ELM\n")
LOG_STR += f"Your current IMDB template is {IMDB_TEMPLATE}"

