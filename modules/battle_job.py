from pytz import timezone
from datetime import datetime, timedelta
from asyncio import sleep

from constants import battle_time, battle_targets, vegan_id


async def battle_job(user):
    current_time = datetime.now(timezone('Europe/Moscow'))
    current_battle = (current_time + timedelta(hours=1)).hour

    if not isinstance(user.cache.get('plan'), list):
        default = battle_targets['def']
        user.cache['plan'] = [default, default, default]
        user.dump_userdata()

    target = user.cache['plan'][battle_time.index(current_battle)]

    farm_job = user.scheduler.get_job(f'{user.client.name}/vfarm')
    if farm_job != None:
        farm_job.pause()

    farm_pause_lock = False
    if user.state.get('is_farm_paused') == True:
        # WARNING: it loses the "full energy" event if it appears during the lockout
        user.state['is_farm_paused'] = False
        farm_pause_lock = True

    await sleep(182)

    await user.client.send_message(vegan_id, target)

    equip_after = user.cache.get('equip_after_battle')
    equip_for = user.cache.get('equip_for_battle')

    for skill in equip_after if equip_after != None else []:
        await user.client.send_message(vegan_id, '/off_' + skill)

    for skill in equip_for if equip_for != None else []:
        await user.client.send_message(vegan_id, '/use_' + skill)

    if user.state.get('autopog_started') == False:
        user.state['autopog_started'] = True
        await user.client.send_message(vegan_id, '/c_100')

    await sleep(240)

    for skill in equip_for if equip_for != None else []:
        await user.client.send_message(vegan_id, '/off_' + skill)

    for skill in equip_after if equip_after != None else []:
        await user.client.send_message(vegan_id, '/use_' + skill)

    if farm_job != None:
        farm_job.resume()

    if farm_pause_lock == True:
        user.state['is_farm_paused'] = True
