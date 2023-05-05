from pyrogram import Client, types
from constants import command_chats, vegan_id
from utils.res_header import res_header


async def patrol_callback(c: Client, *args):
    try:
        await c.request_callback_answer(*args)
    except:
        pass


async def patrol(c: Client, m: types.Message, user):
    quest_message_id = user.cache.get('quests_msg')

    args = (vegan_id, quest_message_id,
            "quest_select?castle_protect", 1)

    user.scheduler.add_job(patrol_callback, 'interval', (c, args),
                           id=f'{c.name}/farm', seconds=182)

    await patrol_callback(c, *args)

    if m != None:
        await m.edit(res_header(c.name, m.text) + 'Автопатруль запущен')
