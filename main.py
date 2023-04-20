import tomllib
from pyrogram import Client, compose, idle, enums
from os.path import exists
from os import mkdir
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from User import User
from utils.validate_dirname import is_valid_dirname

with open('config.toml', 'rb') as f:
    config = tomllib.load(f)

users = []

global_api_id = config.get('global').get('api_id')
global_api_hash = config.get('global').get('api_hash')

if not exists('userdata'):
    mkdir('userdata')

scheduler = AsyncIOScheduler(timezone=timezone('Europe/Moscow'))
scheduler.start()

for key in config:
    if key == 'global':
        continue

    if not is_valid_dirname(key):
        raise ValueError("Username must be valid directory name")

    api_id = config.get(key).get('api_id')
    api_hash = config.get(key).get('api_hash')

    api_id = api_id if api_id != None else global_api_id
    api_hash = api_hash if api_hash != None else global_api_hash

    if api_id == None or api_hash == None:
        raise ValueError("Api_id and api_hash must be specified in config")

    phone = config.get(key).get('phone')

    if not exists(f'userdata/{key}/'):
        mkdir(f'userdata/{key}')

    user = User(Client(key, api_id, api_hash, phone_number=phone,
                hide_password=True, workdir=f'userdata/{key}/', parse_mode=enums.ParseMode.HTML), scheduler)
    
    user.register_handlers()

    users.append(user)

compose([user.client for user in users])
