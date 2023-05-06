from asyncio import sleep
from pyrogram import Client, types
from pyrogram.filters import regex
from pyrogram.handlers import MessageHandler, EditedMessageHandler

from utils.res_header import res_header
from utils.filters import f_vegan
from constants import vegan_id, melee_weapon_text, time_for_regen


async def inline_callback(c: Client, *args):
    try:
        await c.request_callback_answer(*args)
    except:
        pass


async def attackselect_handler(c: Client, m: types.Message):
    try:
        await m.click('Крыса 1|🐭', timeout=1)
    except:
        pass


async def patrol(c: Client, m: types.Message, user):
    quest_message_id = user.cache.get('quests_msg')

    args = (vegan_id, quest_message_id,
            "quest_select?castle_protect", 1)

    user.scheduler.add_job(inline_callback, 'interval',
                           (c, *args), id=f'{c.name}/farm', seconds=182)

    await inline_callback(c, *args)

    if m != None:
        await m.edit(res_header(c.name, m.text) + 'Автопатруль запущен')


async def rathunt(c: Client, m: types.Message, user):
    quest_message_id = user.cache.get('quests_msg')

    args = (vegan_id, quest_message_id,
            "quest_select?rathunt", 1)

    handlers = []
    user_weapon_type = []

    attackselect = c.add_handler(EditedMessageHandler(
        attackselect_handler, f_vegan & regex(f'^Выберите цель для атаки:$')))

    async def result_handler(c: Client, m: types.Message):
        if m.text.startswith('Вы одержали победу над крысой!'):
            await inline_callback(c, *args)
        else:
            await sleep(time_for_regen * 2)
            await inline_callback(c, *args)

    result = c.add_handler(MessageHandler(result_handler, f_vegan & regex(
        r'^(Вы одержали победу над крысой!|Вы не смогли одолеть крысу, и вернулись в замок залечивать раны.)\n')))

    async def turn_handler(c: Client, m: types.Message):
        await sleep(1)
        try:
            if m.text.startswith('Ход 1\n'):
                await sleep(1)
                cr = m.click(
                    'Подойти') if 'melee' == user_weapon_type[0] else m.click('Атака')
                await cr
            elif '0 энергии' not in m.text:
                await m.click('Атака', timeout=1)
            else:
                await m.click('Перезарядка', timeout=1)
        except:
            pass

    turn = c.add_handler(MessageHandler(
        turn_handler, f_vegan & regex(r'^Ход \d+\n')))

    def weaponselect_handler(c: Client, m: types.Message):
        user_selection = m.text.split('\n')[1].split(' ', 1)[1][:-6]

        if user_selection in melee_weapon_text:
            user_weapon_type.clear()
            user_weapon_type.append('melee')
        else:
            user_weapon_type.clear()
            user_weapon_type.append('long-range')

    weaponselect = c.add_handler(MessageHandler(
        weaponselect_handler, f_vegan & regex(r'^Выбор оружия:\n')))

    handlers.extend([attackselect, result, turn, weaponselect])
    user.state['rathunt_handlers'] = handlers

    await inline_callback(c, *args)
    if m != None:
        await m.edit(res_header(c.name, m.text) + 'Автоохота на крыс запущена')
