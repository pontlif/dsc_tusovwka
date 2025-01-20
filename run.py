from init import bot, Mafia
import disnake
from variables import *
from functions.mafia import mafia_crush, mafia_reg_crush
import asyncio
from secret import TOKEN

import functions.verify as verify
import functions.support as support
import functions.update as update
import functions.console as console
import functions.mafia as mafia
import functions.lofi as lofi
import functions.report as report
###################################################################################
###################################################################################
###################################################################################


# Check
@bot.event
async def on_ready():
    print(f'Бот запущен. Я - {bot.user}')
    await bot.change_presence(
        activity=disnake.Activity(type=disnake.ActivityType.custom, name="tusovwka", state="Тестируется"))
    chat_chat = await bot.fetch_channel(CHAT)
    # await chat_chat.send("## Всем привет! Я снова в сети и служу Наша Туса.")
    mfgame_object = Mafia.get_or_none(crush_status="Crush me")
    while mfgame_object is not None:
        if (mfgame_object.status == "Registration_open") or (mfgame_object.status == "Registration_private_open"):
            mafia_chat_object = await bot.fetch_channel(MAFIA)
            # await mafia_chat_object.send("## Всем привет! Я снова в сети и служу Наша Туса.")
            await mafia_reg_crush(mfgame_object)
        else:
            await mafia_crush(mfgame_object)
        mfgame_object = Mafia.get_or_none(crush_status="Crush me")

###################################################################################
###################################################################################
###################################################################################


# Run
bot.run(TOKEN)
