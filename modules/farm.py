from pyrogram import Client, types
from pyrogram.filters import regex
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from modules.farm_variants import patrol

from utils.filters import f_cmd, f_vegan
from utils.res_header import res_header
from constants import command_chats, vegan_id


def add_handlers(user):
    client: Client = user.client
    scheduler: AsyncIOScheduler = user.scheduler

    @client.on_message(f_cmd & regex(r'^\+farm( pog)?$'))
    async def farm(c: Client, m: types.Message = None):
        args = m.text.split(' ')
        quest_message_id = user.cache.get('quests_msg')

        job = scheduler.get_job(f'{c.name}/farm')

        if job != None or user.state.get('is_farm_paused') == True:
            if job != None:
                job.remove()

            user.state['is_farm_paused'] = False
            user.state['autopog_started'] = None

            if m != None:
                await m.edit(res_header(c.name, m.text) + 'Автопатруль остановлен')
            return

        if quest_message_id == None:
            if m != None:
                await m.edit(res_header(c.name, m.text) + 'Сообщение с квестами не зарегистрировано! Бот должен его отправить')
        else:
            user.state['autopog_started'] = False if 'pog' in args else None

            await patrol(c, m, user)

    @client.on_message(f_vegan & regex(r'^Недостаточно выносливости\!$'))
    async def pause_farm(c: Client, m: types.Message):
        job = scheduler.get_job(f'{c.name}/farm')

        if job != None:
            job.remove()
            user.state['is_farm_paused'] = True
            await c.send_message(command_chats[0], 'Автопатруль на паузе')

        if user.state.get('autopog_started') == False:
            user.state['autopog_started'] = True
            await m.reply('/c_100')

    @client.on_message(f_vegan & (regex(r'^Создан предмет: "👝Мешок золота"!') | regex(r'^Недостаточно ресурсов!$')))
    async def autopog(c: Client, m: types.Message):
        if user.state.get('autopog_started') != True:
            return

        if m.text == 'Недостаточно ресурсов!':
            user.state['autopog_started'] = False
            await c.send_message(command_chats[0], 'Всё золото упаковано')
        else:
            await m.reply('/c_100')

    @client.on_message(f_vegan & regex(r'^🔋Энергия полностью восстановлена, вы готовы к сражению!$'))
    async def unpause_farm(c: Client, m: types.Message):
        if user.state.get('is_farm_paused') == True:
            user.state['is_farm_paused'] = False
            await farm(c)

    @client.on_message(f_vegan & regex(r'^Выберите квест:'))
    async def update_quests_msg(c: Client, m: types.Message):
        user.cache['quests_msg'] = m.id
        user.dump_userdata()
