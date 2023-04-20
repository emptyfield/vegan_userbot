from pyrogram.filters import chat, user, bot

from constants import command_chats, vegan_id

f_cmd = chat(command_chats) & user('me')
f_vegan = chat(vegan_id) & bot
