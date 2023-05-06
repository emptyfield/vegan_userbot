import json
from pyrogram import Client, types
from pyrogram.filters import regex, user
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.filters import f_cmd
from utils.res_header import res_header
import modules


class User:
    def __init__(self, client: Client, scheduler: AsyncIOScheduler) -> None:
        self.client = client
        self.scheduler = scheduler
        self.state = {'is_farm_paused': False, 'is_rathunt_paused': False}

        with open(f'userdata/{self.client.name}/data.json', 'a+', encoding='utf-8') as f:
            f.seek(0)
            text = f.read()
            if len(text) == 0:
                self.cache = {}
            else:
                self.cache = json.loads(text)

        @client.on_message(user('me') & regex(r'^\+chid$'))
        async def chid(c: Client, m: types.Message):
            await m.edit(res_header(c.name, m.text) + f'ID этого чата: {m.chat.id}')

    def dump_userdata(self):
        with open(f'userdata/{self.client.name}/data.json', 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False)

    def register_handlers(self):
        modules.farm.add_handlers(self)
        modules.battle.add_handlers(self)
        modules.help.add_handlers(self)
        modules.status.add_handlers(self)
