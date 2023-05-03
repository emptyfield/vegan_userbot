from pyrogram import Client, types
from pyrogram.filters import regex
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from html import escape

from utils.filters import f_cmd, f_vegan
from utils.res_header import res_header
from constants import skills, items, battle_time, battle_targets
from .battle_job import battle_job


def add_handlers(user):
    client: Client = user.client
    scheduler: AsyncIOScheduler = user.scheduler

    job_start_hours = map(lambda hour: (datetime.now().replace(
        hour=int(hour)) - timedelta(hours=1)).hour.__str__(), battle_time)

    scheduler.add_job(battle_job, 'cron', [
                      user], id=f'{client.name}/battle', minute='55', hour=','.join(job_start_hours))

    @client.on_message(f_cmd & regex(r'^\+((arm (for|after)( \w+)+)|(craft|equip) (for|after)( [a-z_]+)+)$'))
    async def equip(c: Client, m: types.Message = None):
        words = m.text.split(' ')
        specified_command = words[0][1:]
        multiple_args = set(words[2:])

        what_changed_text = None
        match specified_command:
            case 'equip': what_changed_text = 'Скиллы'
            case 'craft': what_changed_text = 'Предметы'
            case 'arm': what_changed_text = 'Оружие'

        if len(multiple_args) == 1 and '_' in multiple_args:
            if user.cache.get(f'{specified_command}_{words[1]}_battle') != None:
                del user.cache[f'{specified_command}_{words[1]}_battle']
                user.dump_userdata()

            await m.edit(res_header(c.name, m.text) + f"{what_changed_text} {'для' if words[1] == 'for' else 'после'} битвы убраны")
            return

        diff = None
        match specified_command:
            case 'equip': diff = multiple_args - skills
            case 'craft': diff = multiple_args - items

        if diff != None and len(diff) > 0:
            await m.edit(res_header(c.name, m.text) + f'Этих {what_changed_text[:-1].lower()}ов не существует: ' + escape(', '.join(diff)))
            return

        user.cache[f'{specified_command}_{words[1]}_battle'] = [*multiple_args]
        user.dump_userdata()

        await m.edit(res_header(c.name, m.text) + f"Нов{'ое' if specified_command == 'arm' else 'ые'} {what_changed_text.lower()} " +
                     f"{'для' if words[1] == 'for' else 'после'} битвы установлен{'о'if specified_command == 'arm' else 'ы'}")

    @client.on_message(f_cmd & regex(r'^\+plan \d{1,2} [a-z_]+$'))
    async def plan(c: Client, m: types.Message = None):
        words = m.text.split(' ')

        time = int(words[1])
        target = words[2]

        err_body = ''
        error = False

        if time not in battle_time:
            error = True
            err_body += 'В этот час нет битвы\n'

        if battle_targets.get(target) == None and target != '_':
            error = True
            err_body += 'Такой цели не существует\n'

        if error:
            await m.edit(res_header(c.name, m.text) + err_body)
        else:
            if user.cache.get('plan') == None:
                default = None
                user.cache['plan'] = [default, default, default]

            user.cache['plan'][battle_time.index(
                time)] = battle_targets.get(target) if target != None else None
            user.dump_userdata()

            await m.edit(res_header(c.name, m.text) + 'Цель назначена')
