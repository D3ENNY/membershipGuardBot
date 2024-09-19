from pyrogram import Client, filters, emoji
from pyrogram.types import InlineKeyboardButton as keybutton
from pyrogram.types import InlineKeyboardMarkup as keymarkup
from pyrogram.errors import PeerIdInvalid, FloodWait, UserNotParticipant, ChatAdminRequired
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from jsoncomment import JsonComment

import logging, sys, traceback

#global variable
scheduler = AsyncIOScheduler()
jsonc_parser = JsonComment()

logger = logging.basicConfig(
    filename="./log/bot.log",
    level = logging.WARNING, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S' 
)

#File
with open("./assets/config/config.json", "r") as file:
    conf = jsonc_parser.load(file)
    
with open("./assets/target/group.jsonc", "r") as file:
    group_access_rules = jsonc_parser.load(file)

with open("./assets/config/message.json", "r") as file:
    msg = jsonc_parser.load(file)

#initialize client
app = Client(
    conf['telegram']['name'],
    api_id = conf['telegram']['api_id'],
    api_hash = conf['telegram']['api_hash'],
    bot_token = conf['telegram']['bot_token']
)

#function

async def check_group_exist(chat_id):
    '''
    function that check if a group exist, based on the group id
     
    args: 
        chat_id (str): the group id
        
    '''
    try:
        app.get_chat(chat_id)
        return true
    except PeerIdInvalid:
        return False
    except FloodWait as e:
        # rate limiting from Telegram API
        await asyncio.sleep(e.x)
        return await check_group_exists(chat_id)
    except Exception as e:
        return False

async def get_group_link(chat_id):
    '''
    function that return the join group link, based on the group id
    
    args: 
        chat_id (str): the group id
    '''
    if await check_group_exist(chat_id):
        invite = await app.create_chat_invite_link(chat_id)
        print(invite)
        return invite.invite_link
    print("fuck")
    
async def is_user_in_group(chat_id, user_id):
    '''
    function that check if the user is in a specific group, based on group and user id
    
    args:
        chat_id (str): the group id
        user_id (str): the user id
    '''
    try:
        member = await app.get_chat_member(chat_id, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        return False
    except UserNotParticipant as e:
        return False
    except ChatAdminRequired as e:
        log(str(e), traceback.format_exc(), logging.WARN)

def log(error, stacktrace, level):
    '''
    function that log error in a logfile
    
    args: 
        error (str): the error message
        stacktrace (str): the stacktrace of the message
        level (int): level of gravity of the error
            map: 
                30 -> logging.WARN
                40 -> logging.ERROR
                50 -> logging.CRITICAL
    '''
    
    if(level not in [logging.WARN, logging.ERROR, logging.CRITICAL]):
        sys.stderr.write(f"error level not valid\n--------\n{message}")
        return 

    logging.log(level, f"{error}\n{stacktrace}")

#bot function

@app.on_message(filters.command("start", prefixes=['!', '.', '&', '/']) & filters.text)
async def start(bot, message):
    print("--start--")
    try:
        for j,i in group_access_rules["groups"].items():
            print(i)
            print(j)
        await message.reply(
            text=msg["message"]["caption"]["enter_groups"] % (emoji.BACKHAND_INDEX_POINTING_DOWN),
            reply_markup=keymarkup([[keybutton(i["name"], url=await get_group_link(i["id"]) if group_name == "required" else "https://example.com")] for group_name, group in group_access_rules["groups"].items() for i in group]),
            disable_web_page_preview = True
        )
    except Exception as e:
        log(str(e), traceback.format_exc(), logging.ERROR)
        await bot.send_message(message.chat.id, msg["message"]["error"]["invalid_url_error"])
    
    print("-end start-")
    
@app.on_message(filters.command("ping", prefixes=['','!', '.', '&', '/']) & filters.text & filters.private)
async def ping(bot, message):
    print('---ping---')
    await message.reply(msg["message"]["caption"]["ping"] % emoji.PING_PONG)    
    print('---end ping---')

# start
scheduler.start()
app.run()
