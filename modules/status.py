from pyrogram import Client, types
from pyrogram.filters import regex
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job

from utils.filters import f_cmd
from utils.res_header import res_header
from constants import battle_time


def add_handlers(user):
    client: Client = user.client
    scheduler: AsyncIOScheduler = user.scheduler

    @client.on_message(f_cmd & regex(r'^\+status$'))
    async def status(c: Client, m: types.Message):
        job = scheduler.get_job(f'{c.name}/vfarm')
        is_paused = user.state.get('is_farm_paused')

        body = 'Автопатруль: '
        match job, is_paused:
            case None, False: body += '⏹Отключен\n'
            case None, True: body += '⏸Пауза\n'
            case Job, False: body += '▶️Работает\n'
            case _: body += '🚫Некорректное состояние. Для устранения перезапустите автопатруль. Сообщите разработчикам о том, каким образом вы получили это сообщение.\n'

        body += 'Автопог: '
        match user.state.get('autopog_started'):
            case None: body += '❌Отключен\n'
            case _: body += '✅Включен\n'

        quest_msg = user.cache.get('quests_msg')

        body += 'ID сообщения квестов: '
        match quest_msg:
            case None: body += 'Нет ID!\n'
            case _: body += (str(quest_msg) + '\n')

        plan = user.cache.get('plan')

        body += 'План на битвы:\n'
        match plan:
            case list(): body += ('\n'.join([f'   {battle_time[index]}: {plan[index]}' for index in range(len(battle_time))]) + '\n')
            case _: body += '   Нет приказов!\n'

        equip_for_battle = user.cache.get('equip_for_battle')
        equip_after_battle = user.cache.get('equip_after_battle')

        body += 'Способности на битвы: '
        match equip_for_battle:
            case list(): body += (', '.join(equip_for_battle) + '\n')
            case _: body += 'Не установлено!\n'

        body += 'Способности на перемирие: '
        match equip_after_battle:
            case list(): body += (', '.join(equip_after_battle) + '\n')
            case _: body += 'Не установлено!\n'

        await m.edit(res_header(c.name, m.text) + body)
