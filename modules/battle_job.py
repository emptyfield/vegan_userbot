from pytz import timezone
from datetime import datetime, timedelta
from asyncio import sleep

from constants import battle_time, battle_targets, vegan_id, items


async def battle_job(user):
    current_time = datetime.now(timezone('Europe/Moscow'))
    current_battle = (current_time + timedelta(hours=1)).hour

    if not isinstance(user.cache.get('plan'), list):
        default = None
        user.cache['plan'] = [default, default, default]
        user.dump_userdata()

    target = user.cache['plan'][battle_time.index(current_battle)]

    if target == None:
        return

    farm_job = user.scheduler.get_job(f'{user.client.name}/farm')
    if farm_job != None:
        farm_job.pause()

    patrol_pause_lock = False
    rathunt_pause_lock = False

    if user.state['is_farm_paused'] == True:
        # WARNING: it loses the "full energy" event if it appears during the lockout
        user.state['is_farm_paused'] = False
        patrol_pause_lock = True

    if user.state['is_rathunt_paused'] == True:
        # WARNING: it loses the "full energy" event if it appears during the lockout
        user.state['is_rathunt_paused'] = False
        rathunt_pause_lock = True

    await user.client.send_message(vegan_id, target)

    craft_for = user.cache.get('craft_for_battle')

    arm_after = user.cache.get('arm_after_battle')
    arm_for = user.cache.get('arm_for_battle')

    equip_after = user.cache.get('equip_after_battle')
    equip_for = user.cache.get('equip_for_battle')

    if arm_after != None:
        await user.client.send_message(vegan_id, '/woff_' + arm_after[0])

    for skill in equip_after if equip_after != None else []:
        await user.client.send_message(vegan_id, '/off_' + skill)

    await sleep(5)

    if arm_for != None:
        await user.client.send_message(vegan_id, '/on_' + arm_for[0])

    for skill in equip_for if equip_for != None else []:
        await user.client.send_message(vegan_id, '/use_' + skill)

    if user.state.get('autopog_started') == False:
        user.state['autopog_started'] = True
        await user.client.send_message(vegan_id, '/c_100')

    # ----- Item crafting and wearing -----
    for item in craft_for if craft_for != None else []:
        await user.client.send_message(vegan_id, '/c_' + str(items[item]))

    await sleep(3)

    for item in craft_for if craft_for != None else []:
        await user.client.send_message(vegan_id, '/takeitem_' + item)
    # -------------------------------------

    await sleep(300)

    if arm_for != None:
        await user.client.send_message(vegan_id, '/woff_' + arm_for[0])

    for skill in equip_for if equip_for != None else []:
        await user.client.send_message(vegan_id, '/off_' + skill)

    await sleep(5)

    if arm_after != None:
        await user.client.send_message(vegan_id, '/on_' + arm_after[0])

    for skill in equip_after if equip_after != None else []:
        await user.client.send_message(vegan_id, '/use_' + skill)

    if farm_job != None:
        farm_job.resume()

    if patrol_pause_lock == True:
        user.state['is_farm_paused'] = True

    if rathunt_pause_lock == True:
        user.state['is_rathunt_paused'] = True
