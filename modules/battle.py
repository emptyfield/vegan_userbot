from pyrogram import Client, types
from pyrogram.filters import regex
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from html import escape

from utils.filters import f_cmd, f_vegan
from utils.res_header import res_header
from constants import skills, battle_time, battle_targets
from .battle_job import battle_job


def add_handlers(user):
    client: Client = user.client
    scheduler: AsyncIOScheduler = user.scheduler

    job_start_hours = map(lambda hour: (datetime.now().replace(
        hour=int(hour)) - timedelta(hours=1)).hour.__str__(), battle_time)
    
    scheduler.add_job(battle_job, 'cron', [
                      user], id=f'{client.name}/battle', minute='55', hour=','.join(job_start_hours))

    @client.on_message(f_cmd & regex(r'^\+equip (for|after)( [a-z_]+)+$'))
    async def equip(c: Client, m: types.Message = None):
        words = m.text.split(' ')
        choosed_skills = set(words[2::])

        diff = choosed_skills - skills

        if len(diff) > 0:
            await m.edit(res_header(c.name, m.text) + "Этих скиллов не существует: " + escape(', '.join(diff)))
            return

        user.cache[f'equip_{words[1]}_battle'] = [*choosed_skills]
        user.dump_userdata()

        await m.edit(res_header(c.name, m.text) + f"Новые скиллы {'для' if words[1] == 'for' else 'после'} битвы установлены")

    @client.on_message(f_cmd & regex(r'^\+plan \d{1,2} [a-z]+$'))
    async def plan(c: Client, m: types.Message = None):
        words = m.text.split(' ')

        time = int(words[1])
        target = words[2]

        err_body = ''
        error = False

        if time not in battle_time:
            error = True
            err_body += 'В этот час нет битвы\n'

        if battle_targets.get(target) == None:
            error = True
            err_body += 'Такой цели не существует\n'

        if error:
            await m.edit(res_header(c.name, m.text) + err_body)
        else:
            if user.cache.get('plan') == None:
                default = battle_targets['def']
                user.cache['plan'] = [default, default, default]

            user.cache['plan'][battle_time.index(
                time)] = battle_targets.get(target)
            user.dump_userdata()

            await m.edit(res_header(c.name, m.text) + 'Цель назначена')
