from pyrogram import Client, types
from pyrogram.filters import regex
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from modules.farm_variants import patrol, rathunt

from utils.filters import f_cmd, f_vegan
from utils.res_header import res_header
from constants import command_chats, vegan_id


def add_handlers(user):
    client: Client = user.client
    scheduler: AsyncIOScheduler = user.scheduler

    @client.on_message(f_cmd & regex(r'^\+farm( rat)?( pog)?$'))
    async def farm(c: Client, m: types.Message = None, unpause_args: list = None):
        args = m.text.split(' ') if m is not None else unpause_args
        quest_message_id = user.cache.get('quests_msg')

        job = scheduler.get_job(f'{c.name}/farm')
        rathunt_handlers = user.state.get('rathunt_handlers')

        if job != None or user.state['is_farm_paused'] == True or user.state['is_rathunt_paused'] == True or rathunt_handlers != None:
            if job != None:
                job.remove()

            if rathunt_handlers != None:
                for handler in rathunt_handlers:
                    c.remove_handler(*handler)
                del user.state['rathunt_handlers']

            user.state['is_farm_paused'] = False
            user.state['is_rathunt_paused'] = False
            user.state['autopog_started'] = None

            if m != None:
                await m.edit(res_header(c.name, m.text) + 'Автофарм остановлен')
            return

        if quest_message_id == None:
            if m != None:
                await m.edit(res_header(c.name, m.text) + 'Сообщение с квестами не зарегистрировано! Бот должен его отправить')
        else:
            user.state['autopog_started'] = False if 'pog' in args else None

            if 'rat' in args:
                await rathunt(c, m, user)
            else:
                await patrol(c, m, user)

    @client.on_message(f_vegan & regex(r'^Недостаточно выносливости\!$'))
    async def pause_farm(c: Client, m: types.Message):
        job = scheduler.get_job(f'{c.name}/farm')
        rathunt_handlers = user.state.get('rathunt_handlers')

        if job != None:
            job.remove()
            user.state['is_farm_paused'] = True
            await c.send_message(command_chats[0], 'Автопатруль на паузе')

        if rathunt_handlers != None:
            for handler in rathunt_handlers:
                c.remove_handler(*handler)
            del user.state['rathunt_handlers']

            user.state['is_rathunt_paused'] = True
            await c.send_message(command_chats[0], 'Автоохота на паузе')

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
        unpause_args = []
        if user.state.get('autopog_started') == False:
            unpause_args.append['pog']

        if user.state.get('is_farm_paused') == True:
            user.state['is_farm_paused'] = False
            await farm(c, unpause_args=unpause_args)

        if user.state.get('is_rathunt_paused') == True:
            user.state['is_rathunt_paused'] = False
            unpause_args.append('rat')
            await farm(c, unpause_args=unpause_args)

    @client.on_message(f_vegan & regex(r'^Выберите квест:'))
    async def update_quests_msg(c: Client, m: types.Message):
        user.cache['quests_msg'] = m.id
        user.dump_userdata()
