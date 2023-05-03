from pyrogram import Client, types
from pyrogram.filters import regex

from utils.filters import f_cmd
from utils.res_header import res_header
from constants import skills, battle_time, battle_targets, items


def add_handlers(user):
    client: Client = user.client

    @client.on_message(f_cmd & regex(r'^\+help( [a-z]+)?$'))
    async def help(c: Client, m: types.Message = None):
        words = m.text.split(' ')

        if len(words) == 1:
            await m.edit(res_header(c.name, m.text) + 'Список команд:\n' +
                         '<code>+status</code> - показать текущее состояние\n' +
                         '<code>+farm [pog]</code> - включить или выключить автопатруль\n'
                         '<code>+plan (time) (target)</code> - установить цель на автобитву\n' +
                         '<code>+equip for|after (skills...)</code> - установить способности для автопереодевания к битве\n' +
                         '<code>+arm for|after (weapon_code)</code> - установить оружие для автопереодевания к битве\n' +
                         '<code>+craft for (items...)</code> - установить предметы для автоматического создания и взятия на битву'
                         '<code>+chid</code> - показать ID чата, в котором была вызвана команда\n' +
                         '<code>+help [(command)]</code> - показать список команд или показать объяснение команды, если указан параметр command (первое слово команды)')
        else:
            body = ''
            match words[1]:
                case 'farm':
                    body = '<code>+farm [pog]</code> - включить или выключить автопатруль с возможностью автоматического создания мешков с золотом.\n' +\
                        'Если указано pog, то после окончания энергии золото по возможности упакуется в мешки (автопог).'
                case 'equip':
                    body = '<code>+equip for|after (skills...)</code> - установить способности для автопереодевания перед и после битвы.\n' +\
                        'Если выбрано for - надевается перед битвой (на битву), если after - надевается после битвы (на перемирие).\n' +\
                        'Вместо (skills...) через пробел указываются способности. Список способностей (каждая способность копируется по клику):\n' +\
                        ', '.join(
                            [f'<code>{skill}</code>' for skill in skills])
                case 'plan':
                    body = '<code>+plan (time) (target)</code> - установить приказ (цель) на битву, которая проходит в определенный час.\n' +\
                        'time - час, в который начинается одна из битв. Часы начала битв (по МСК): ' +\
                        ', '.join([str(hour) for hour in battle_time]) + '.\n' +\
                        'target - цель, которая будет установлена. По умолчанию 🛡Защита. Список целей и их коды:\n' +\
                        '\n'.join([f'   {value}: <code>{key}</code>' for key, value in battle_targets.items()]) +\
                        '\n‼️Подготовка к битве начинается за 5 минут до битвы и заканчивается через 2 минуты после битвы. ' +\
                        'Квестовые действия в этот период могут помешать правильной работе программы.\n' +\
                        'Автопатруль временно отключается чтобы не мешать подготовке к битве. ' +\
                        'Если автоматическое создание мешков с золотом включено - перед битвой золото по возможности будет упаковано.'
                case 'craft':
                    body = '<code>+craft for (items...)</code> - установить предметы, которые будут создаваться и экипироваться перед битвой.\n' +\
                        'Вместо (items...) через пробел указываются способности. Список способностей (каждая способность копируется по клику):\n' +\
                        ', '.join(
                            [f'<code>{item}</code>' for item in items.keys()])

                case _: body = 'Документации по такой команде нет!'

            await m.edit(res_header(c.name, m.text) + body)
